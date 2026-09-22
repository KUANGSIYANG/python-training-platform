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

from runner import evaluate, execute
from server import load_problems
from curriculum.schema import CHAPTERS


def verify(problems, expected_count=None, isolated=False):
    if expected_count is None:
        expected_count = len(CHAPTERS) * 10
    errors = []
    if len(problems) != expected_count:
        errors.append(f"题目数量应为 {expected_count}，实际为 {len(problems)}")
    counts = Counter(problem["chapter"] for problem in problems)
    if expected_count == len(CHAPTERS) * 10 and counts != Counter({n: 10 for n in range(1, len(CHAPTERS) + 1)}):
        errors.append(f"每章应有 10 题，实际为 {dict(counts)}")
    ids = [problem["id"] for problem in problems]
    if expected_count == len(CHAPTERS) * 10 and ids != list(range(1, expected_count + 1)):
        errors.append(f"题目编号应按顺序覆盖 1—{expected_count}")
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
                if problem.get('execution_mode') == 'stdin':
                    if not isinstance(case.get('stdin'), str) or not isinstance(case.get('expected'), str):
                        errors.append(f'{label}：ACM 测试输入与输出必须是字符串')
                elif len(case["args"]) != len(problem["parameters"]):
                    errors.append(f"{label}：测试参数个数不正确")
            if problem['id'] > 300:
                if not problem.get('learning_goal') or not problem.get('skills'):
                    errors.append(f'{label}：缺少学习目标或技能标签')
                if len(problem['tests']) < 7:
                    errors.append(f'{label}：进阶题需要至少 7 个测试')
                if not problem.get('complexity', {}).get('time') or not problem.get('complexity', {}).get('space'):
                    errors.append(f'{label}：缺少时间或空间复杂度')
                if any(type(n) is not int or not 1 <= n < problem['chapter'] for n in problem.get('prerequisites', [])):
                    errors.append(f'{label}：前置章节必须在当前章之前')
            language = problem.get("language", "python")
            execution_mode = problem.get('execution_mode', 'function')
            if execution_mode not in {'function', 'stdin'} or (execution_mode == 'stdin' and language != 'python'):
                errors.append(f'{label}：无效的执行模式')
                continue
            if language not in {"python", "sql", "javascript"}:
                errors.append(f"{label}：不支持的语言 {language}")
                continue
            if language == "javascript":
                javascript.append(problem)
                test_count += len(problem["tests"])
                continue
            if language == "python":
                compile(problem["starter"], f"starter-{problem['id']}", "exec")
            payload = {"code": problem["solution"], "cases": copy.deepcopy(problem["tests"]), "mode": "submit",
                       "language": language, "setup_sql": problem.get("setup_sql", ""),
                       'execution_mode': execution_mode}
            result = execute(**payload) if isolated else evaluate(payload)
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
    parser.add_argument('--track', choices=['recruitment', 'acm'], help='只检查秋招或 ACM 进阶题')
    parser.add_argument('--isolated', action='store_true', help='Python / SQL 参考答案使用真实子进程、超时和输出上限')
    args = parser.parse_args()
    started = time.monotonic()
    try:
        problems = load_problems()
    except ImportError as exc:
        print(f"题库尚未完整生成或导入失败：{exc}")
        return 1
    if args.track:
        problems = [p for p in problems if p.get('track') == args.track]
    if args.chapter is not None:
        problems = [p for p in problems if p["chapter"] == args.chapter]
        if not problems:
            print("没有找到该章节。")
            return 1
    expected = 10 if args.chapter is not None else (60 if args.track else None)
    errors, tests = verify(problems, expected, isolated=args.isolated)
    for error in errors:
        print(error)
    print(f"已检查 {len(problems)} 道题、{tests} 个测试，错误 {len(errors)} 个，用时 {time.monotonic() - started:.2f} 秒。")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
