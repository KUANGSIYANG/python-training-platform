"""Verify curriculum structure and every reference answer. No server needed."""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

from runner import evaluate
from server import load_problems


def verify(problems, expected_count=300):
    errors = []
    if len(problems) != expected_count:
        errors.append(f"题目数量应为 {expected_count}，实际为 {len(problems)}")
    counts = Counter(problem["chapter"] for problem in problems)
    if expected_count == 300 and counts != Counter({n: 10 for n in range(1, 31)}):
        errors.append(f"每章应有 10 题，实际为 {dict(counts)}")
    ids = [problem["id"] for problem in problems]
    if expected_count == 300 and ids != list(range(1, 301)):
        errors.append("题目编号应按顺序覆盖 1—300")
    test_count = 0
    javascript = []
    for problem in problems:
        label = f"#{problem['id']} {problem['title']}"
        try:
            json.dumps(problem, ensure_ascii=False, allow_nan=False)
            if len(problem["tests"]) < 5:
                errors.append(f"{label}：测试少于 5 个")
            if len(problem["examples"]) != 2:
                errors.append(f"{label}：需要 2 个公开示例")
            if len(problem["hints"]) != 3:
                errors.append(f"{label}：需要 3 条渐进提示")
            for key in ("concept", "description", "solution", "explanation", "starter"):
                if not problem[key].strip():
                    errors.append(f"{label}：{key} 不能为空")
            for case in problem["tests"]:
                if len(case["args"]) != len(problem["parameters"]):
                    errors.append(f"{label}：测试参数个数不正确")
            language = problem.get("language", "python")
            if language not in {"python", "sql", "javascript"}:
                errors.append(f"{label}：不支持的语言 {language}")
                continue
            if language == "javascript":
                javascript.append(problem)
                test_count += len(problem["tests"])
                continue
            if language == "python":
                compile(problem["starter"], f"starter-{problem['id']}", "exec")
            result = evaluate({"code": problem["solution"], "cases": copy.deepcopy(problem["tests"]), "mode": "submit",
                               "language": language, "setup_sql": problem.get("setup_sql", "")})
            test_count += result["total"]
            if result["status"] != "accepted":
                bad = [case for case in result["cases"] if not case["passed"]]
                errors.append(f"{label}：{result['status']}\n{json.dumps(bad, ensure_ascii=False, indent=2)}\n{result.get('error')}")
            if "matplotlib.pyplot" in sys.modules:
                sys.modules["matplotlib.pyplot"].close("all")
        except Exception as exc:
            errors.append(f"{label}：{type(exc).__name__}: {exc}")
    if javascript:
        node = shutil.which("node")
        if not node:
            errors.append("尚未安装 Node.js，无法检查 JavaScript 参考答案。")
        else:
            payload = {"batch": [{"code": p["solution"], "cases": p["tests"], "mode": "submit"} for p in javascript]}
            try:
                flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
                with tempfile.TemporaryDirectory(prefix="pystep-verify-") as directory:
                    child = subprocess.run([node, str(Path(__file__).with_name("node_runner.js"))],
                                           input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                                           capture_output=True, timeout=60, cwd=directory, creationflags=flags)
                results = json.loads(child.stdout.decode("utf-8"))
                if not isinstance(results, list) or len(results) != len(javascript):
                    raise ValueError(f"Node 返回了异常响应：{results}")
                for problem, result in zip(javascript, results):
                    if result["status"] != "accepted":
                        bad = [case for case in result["cases"] if not case["passed"]]
                        errors.append(f"#{problem['id']} {problem['title']}：{result['status']}\n{json.dumps(bad, ensure_ascii=False, indent=2)}\n{result.get('error')}")
            except Exception as exc:
                errors.append(f"JavaScript 批量检查失败：{type(exc).__name__}: {exc}")
    return errors, test_count


def main():
    parser = argparse.ArgumentParser(description="检查题库结构与全部参考答案")
    parser.add_argument("--chapter", type=int, help="只检查某一章")
    args = parser.parse_args()
    started = time.monotonic()
    try:
        problems = load_problems()
    except ImportError as exc:
        print(f"题库尚未完整生成或导入失败：{exc}")
        return 1
    if args.chapter is not None:
        problems = [p for p in problems if p["chapter"] == args.chapter]
        if not problems:
            print("没有找到该章节。")
            return 1
    errors, tests = verify(problems, 10 if args.chapter is not None else 300)
    for error in errors:
        print(error)
    print(f"已检查 {len(problems)} 道题、{tests} 个测试，错误 {len(errors)} 个，用时 {time.monotonic() - started:.2f} 秒。")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
