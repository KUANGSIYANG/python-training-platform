"""Local-only PyStep web server. Run: python server.py [--port 8765]."""
from __future__ import annotations

import argparse
import copy
from functools import lru_cache
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.metadata
import importlib.util
import json
import mimetypes
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading
from urllib.parse import urlsplit, unquote, parse_qs

from runner import execute, EXECUTION_TIMEOUT, MAX_CODE_BYTES

ROOT = Path(__file__).resolve().parent
MAX_BODY_BYTES = 128 * 1024
MAX_CONCURRENT_RUNS = 2
DEMO_ITEMS = [
    {"id": 1, "name": "Python 笔记本", "price": 18.5, "stock": 12},
    {"id": 2, "name": "算法练习册", "price": 32.0, "stock": 0},
    {"id": 3, "name": "代码贴纸", "price": 6.0, "stock": 40},
    {"id": 4, "name": "Python 书签", "price": 4.5, "stock": 25},
]


def load_problems():
    from curriculum.beginner import PROBLEMS as beginner
    from curriculum.advanced import PROBLEMS as advanced
    from curriculum.algorithms import PROBLEMS as algorithms
    from curriculum.web import PROBLEMS as web
    from curriculum.recruitment import PROBLEMS as recruitment
    from curriculum.competitive import PROBLEMS as competitive
    problems = sorted(beginner + advanced + algorithms + web + recruitment + competitive, key=lambda p: p["id"])
    ids = [p["id"] for p in problems]
    if len(ids) != len(set(ids)):
        raise ValueError("题目编号重复")
    return problems


@lru_cache(maxsize=1)
def dependency_info():
    dependencies = {}
    for name, distribution in (("numpy", "numpy"), ("pandas", "pandas"),
                               ("matplotlib", "matplotlib"), ("sklearn", "scikit-learn")):
        try:
            version = importlib.metadata.version(distribution)
            available = importlib.util.find_spec(name) is not None
        except (importlib.metadata.PackageNotFoundError, ImportError, ValueError):
            available, version = False, None
        dependencies[name] = {"available": available, "version": version}
    node = shutil.which("node")
    node_version = None
    if node:
        try:
            flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            node_version = subprocess.check_output([node, "--version"], timeout=3, text=True, creationflags=flags).strip()
        except (OSError, subprocess.SubprocessError):
            node = None
    dependencies["node"] = {"available": bool(node), "version": node_version}
    return {"python": sys.version.split()[0], "dependencies": dependencies,
            "execution_timeout": EXECUTION_TIMEOUT, "sqlite": __import__("sqlite3").sqlite_version,
            "languages": ["python", "sql", "javascript"],
            'execution_modes': ['function', 'stdin'], 'acm_output_comparison': 'tokens',
            "demo_api": [{"method": "GET", "path": "/api/demo/items?q=Python&limit=2", "description": "按名称筛选商品；total 是筛选后、截取前的数量。"},
                         {"method": "GET", "path": "/api/demo/items/1", "description": "按 id 获取商品；不存在返回 404。"},
                         {"method": "POST", "path": "/api/demo/echo", "description": "发送 JSON，返回 {received: 原始 JSON}。"}]}


def parse_json(text):
    def invalid_constant(value):
        raise ValueError(f"JSON 不支持 {value}，请使用 null、数字或字符串。")
    data = json.loads(text, parse_constant=invalid_constant)
    # The JSON decoder accepts lone UTF-16 surrogates; our UTF-8 API does not.
    json.dumps(data, ensure_ascii=False, allow_nan=False).encode("utf-8")
    return data


class LearningServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address, problems=None):
        if address[0] != "127.0.0.1":
            raise ValueError("本平台只能绑定 127.0.0.1")
        self.problems = load_problems() if problems is None else problems
        self.problem_map = {p["id"]: p for p in self.problems}
        self.run_slots = threading.BoundedSemaphore(MAX_CONCURRENT_RUNS)
        super().__init__(address, Handler)


class Handler(BaseHTTPRequestHandler):
    server_version = "PyStep/2.0"

    def setup(self):
        super().setup()
        self.connection.settimeout(10)

    def log_message(self, fmt, *args):
        # Keep the console readable; execution errors are shown inside the app.
        if args and str(args[1] if len(args) > 1 else "") not in {"200", "304"}:
            super().log_message(fmt, *args)

    def reply(self, status, body, content_type="application/json; charset=utf-8"):
        data = json.dumps(body, ensure_ascii=False, allow_nan=False).encode("utf-8") if isinstance(body, (dict, list)) else body
        try:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Cache-Control", "no-store" if content_type.startswith("application/json") else "no-cache")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            pass

    def fail(self, status, message):
        self.reply(status, {"error": {"type": "RequestError", "message": message, "line": None,
                                      "hint": "检查请求内容后重试。", "traceback": ""}})

    def local_request(self, check_origin=False):
        port = self.server.server_port
        hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
        if port == 80:
            hosts.update({"127.0.0.1", "localhost"})
        host = self.headers.get("Host", "").lower()
        if host not in hosts:
            self.fail(403, "仅允许通过本机 127.0.0.1 或 localhost 访问。")
            return False
        if check_origin:
            origin = self.headers.get("Origin")
            if origin is not None and origin.lower() != "http://" + host:
                self.fail(403, "已拒绝来自其他网站的执行请求，请直接打开本地练习平台。")
                return False
            if self.headers.get("Sec-Fetch-Site", "") not in {"", "same-origin", "none"}:
                self.fail(403, "执行请求必须来自当前本地页面。")
                return False
        return True

    def do_GET(self):
        if not self.local_request():
            return
        path = unquote(urlsplit(self.path).path)
        if path == "/api/demo/items":
            query = parse_qs(urlsplit(self.path).query)
            term = query.get("q", [""])[0].casefold()
            try:
                limit = int(query.get("limit", ["100"])[0])
                if not 0 <= limit <= 100:
                    raise ValueError()
            except ValueError:
                self.fail(400, "limit 必须是 0 至 100 的整数。")
                return
            items = [item for item in DEMO_ITEMS if term in item["name"].casefold()]
            self.reply(200, {"items": items[:limit], "total": len(items)})
            return
        demo_match = re.fullmatch(r"/api/demo/items/(\d+)", path)
        if demo_match:
            item = next((item for item in DEMO_ITEMS if item["id"] == int(demo_match.group(1))), None)
            if item is None:
                self.fail(404, "商品不存在。")
            else:
                self.reply(200, item)
            return
        if path == "/api/meta":
            self.reply(200, dependency_info())
            return
        if path == "/api/problems":
            excluded = {"tests", "solution", "explanation", "hints", "concept", "starter"}
            problems = [{k: v for k, v in p.items() if k not in excluded} for p in self.server.problems]
            chapters = {}
            for problem in self.server.problems:
                chapter = chapters.setdefault(problem["chapter"], {"id": problem["chapter"], "title": problem["chapter_title"], "count": 0})
                chapter["count"] += 1
            self.reply(200, {"problems": problems, "chapters": list(chapters.values()), "total": len(problems)})
            return
        match = re.fullmatch(r"/api/problems/(\d+)", path)
        if match:
            problem = self.server.problem_map.get(int(match.group(1)))
            if problem is None:
                self.fail(404, "没有找到这道题。")
            else:
                self.reply(200, {k: v for k, v in problem.items() if k != "tests"})
            return
        if path.startswith("/api/"):
            self.fail(404, "接口不存在。")
            return
        static = (ROOT / "static").resolve()
        # The document refers to assets as /static/app.js and /static/styles.css.
        # Keep the files inside the one allow-listed directory instead of treating
        # "static" as a second nested directory.
        relative = path.lstrip("/")
        if relative.startswith("static/"):
            relative = relative[len("static/"):]
        candidate = (static / (relative or "index.html")).resolve()
        if not candidate.is_relative_to(static) or not candidate.is_file():
            self.fail(404, "页面或文件不存在。")
            return
        mime = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
        if candidate.suffix == ".js":
            mime = "text/javascript"
        if mime.startswith("text/"):
            mime += "; charset=utf-8"
        try:
            self.reply(200, candidate.read_bytes(), mime)
        except OSError:
            self.fail(500, "文件读取失败。")

    def do_OPTIONS(self):
        self.fail(403, "本地平台不允许跨站请求。")

    def do_POST(self):
        if not self.local_request(check_origin=True):
            return
        endpoint = urlsplit(self.path).path
        if endpoint not in {"/api/run", "/api/demo/echo"}:
            self.fail(404, "接口不存在。")
            return
        if self.headers.get_content_type() != "application/json":
            self.fail(400, "请求必须使用 application/json 格式。")
            return
        if self.headers.get("Transfer-Encoding"):
            self.fail(400, "不支持分块请求。")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= MAX_BODY_BYTES:
                self.fail(400, f"请求为空或过大（上限 {MAX_BODY_BYTES // 1024} KB）。")
                return
            data = self.rfile.read(length)
            if len(data) != length:
                raise ValueError("请求未完整传输。")
            payload = parse_json(data.decode("utf-8"))
        except (ValueError, UnicodeError, TimeoutError, RecursionError):
            self.fail(400, "无法读取 JSON；请检查括号、引号、逗号和请求长度。")
            return
        if endpoint == "/api/demo/echo":
            self.reply(200, {"received": payload})
            return
        if not isinstance(payload, dict):
            self.fail(400, "请求应是 JSON 对象。")
            return
        problem_id, code, mode = payload.get("problem_id"), payload.get("code"), payload.get("mode", "run")
        if type(problem_id) is not int:
            self.fail(400, "problem_id 必须是整数。")
            return
        problem = self.server.problem_map.get(problem_id)
        if problem is None:
            self.fail(404, "没有找到这道题。")
            return
        try:
            valid_code = isinstance(code, str) and bool(code.strip()) and len(code.encode("utf-8")) <= MAX_CODE_BYTES
        except UnicodeError:
            valid_code = False
        if not valid_code:
            self.fail(400, f"请填写代码，且代码不得超过 {MAX_CODE_BYTES // 1024} KB。")
            return
        if not isinstance(mode, str) or mode not in {"run", "submit", "trace"}:
            self.fail(400, "mode 必须为 run、submit 或 trace。")
            return
        if mode == 'trace' and problem.get('language', 'python') != 'python':
            self.fail(400, '逐步观察目前支持 Python 题。')
            return
        execution_mode = problem.get('execution_mode', 'function')
        if mode != 'submit' and execution_mode == 'stdin' and 'custom_args' in payload:
            self.fail(400, 'ACM 题请使用 custom_stdin 传入标准输入文本。')
            return
        if mode != 'submit' and execution_mode != 'stdin' and 'custom_stdin' in payload:
            self.fail(400, '函数题请使用 custom_args 传入参数数组。')
            return
        if 'custom_stdin' in payload and mode != 'submit':
            stdin = payload['custom_stdin']
            if not isinstance(stdin, str) or len(stdin.encode('utf-8')) > 64 * 1024:
                self.fail(400, '标准输入必须是字符串，且不能超过 64 KB。')
                return
            cases = [{'stdin': stdin, 'expected': None, 'custom': True}]
        elif "custom_args" in payload and mode != 'submit':
            args = payload["custom_args"]
            if not isinstance(args, list) or len(args) != len(problem["parameters"]):
                self.fail(400, f"自定义输入必须是 JSON 数组，包含 {len(problem['parameters'])} 个参数，顺序与 solve 一致。")
                return
            cases = [{"args": args, "expected": None, "custom": True}]
        else:
            cases = copy.deepcopy(problem["tests"] if mode == "submit" else problem["examples"])
        if mode == 'trace':
            cases = cases[:1]
        if not self.server.run_slots.acquire(blocking=False):
            self.fail(429, "已有两份代码正在运行，请稍后重试。")
            return
        try:
            result = execute(code, cases, mode, language=problem.get("language", "python"),
                             setup_sql=problem.get("setup_sql", ""), execution_mode=execution_mode)
            result.setdefault('execution_mode', execution_mode)
            self.reply(200, result)
        except Exception:
            self.fail(500, "执行服务暂时出错，请重试或重新启动平台。")
            traceback = __import__("traceback")
            traceback.print_exc()
        finally:
            self.server.run_slots.release()


def main():
    parser = argparse.ArgumentParser(description="PyStep 本地 Python 练习平台")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    try:
        server = LearningServer(("127.0.0.1", args.port))
    except OSError as exc:
        print(f"无法启动：{exc}\n可以尝试：python server.py --port 8766", file=sys.stderr)
        return 1
    print(f"PyStep 已启动： http://127.0.0.1:{server.server_port}", flush=True)
    print("请在浏览器中打开上面的地址，按 Ctrl+C 停止服务。只运行你信任的本地代码。", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
