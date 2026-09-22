"""Execute a trusted local learner's Python in a disposable child process.

This is process isolation for mistakes, NOT a security sandbox. Submitted code has
the current user's permissions. Windows timeout terminates the direct child only.
"""
from __future__ import annotations

import contextlib
import copy
import inspect
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import types

EXECUTION_TIMEOUT = 12
MAX_CODE_BYTES = 64 * 1024
MAX_STDOUT_CHARS = 12000
MAX_RESULT_BYTES = 512 * 1024
USER_FILENAME = "你的代码.py"
MAX_TRACE_STEPS = 160


def trace_value(value, depth=0):
    """Bounded plain built-in previews; never call a learner's custom __repr__."""
    kind = type(value)
    if value is None or kind in (bool, int, float, str):
        if kind is int and value.bit_length() > 1000:
            return '<整数，超过 1000 位二进制>'
        return repr(value[:160] if kind is str else value)[:180]
    if depth < 2 and kind in (list, tuple, dict, set, frozenset):
        if kind is dict:
            parts = [f'{trace_value(k, depth+1)}: {trace_value(v, depth+1)}' for _, (k, v) in zip(range(6), value.items())]
            opening, closing = '{', '}'
        else:
            parts = [trace_value(v, depth+1) for _, v in zip(range(6), value)]
            opening, closing = ('[', ']') if kind is list else ('(', ')') if kind is tuple else ('{', '}')
        if len(value) > 6:
            parts.append('…')
        return (opening + ', '.join(parts) + closing)[:300]
    return f'<{kind.__name__}>'


def make_tracer(events, trace_state, include_module=False):
    def trace(frame, event, arg):
        if frame.f_code.co_filename != USER_FILENAME:
            return None
        if not include_module and frame.f_code.co_name == '<module>':
            return None
        if event not in {'line', 'return', 'exception'}:
            return trace
        if len(events) >= MAX_TRACE_STEPS:
            trace_state['truncated'] = True
            sys.settrace(None)
            return None
        local_values = {}
        for name, value in frame.f_locals.items():
            if name.startswith('__') or isinstance(value, (types.ModuleType, types.FunctionType, type)):
                continue
            local_values[name[:80]] = trace_value(value)
            if len(local_values) >= 12:
                break
        entry = {'line': frame.f_lineno, 'event': event, 'function': frame.f_code.co_name,
                 'locals': local_values}
        if event == 'return':
            entry['value'] = trace_value(arg)
        elif event == 'exception':
            entry['exception'] = arg[0].__name__
        size = len(json.dumps(entry, ensure_ascii=False).encode('utf-8'))
        if trace_state.get('bytes', 0) + size > 64000:
            trace_state['truncated'] = True
            sys.settrace(None)
            return None
        trace_state['bytes'] = trace_state.get('bytes', 0) + size
        events.append(entry)
        return trace
    return trace


def load_practice_support():
    """Expose the one bundled fixture despite Python -I removing project paths."""
    if "practice_support" not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            "practice_support", Path(__file__).with_name("practice_support.py"))
        module = importlib.util.module_from_spec(spec)
        sys.modules["practice_support"] = module
        try:
            spec.loader.exec_module(module)
        except BaseException:
            sys.modules.pop("practice_support", None)
            raise


class OutputLimitExceeded(Exception):
    pass


class LimitedOutput(io.TextIOBase):
    def __init__(self):
        self.parts = []
        self.length = 0

    @property
    def encoding(self):
        return "utf-8"

    def write(self, value):
        if not isinstance(value, str):
            raise TypeError("write() 需要字符串")
        if self.length > MAX_STDOUT_CHARS:
            raise OutputLimitExceeded("打印内容超过上限，请检查循环或减少 print()。")
        remaining = MAX_STDOUT_CHARS - self.length
        self.parts.append(value[:max(0, remaining)])
        self.length += len(value)
        if self.length > MAX_STDOUT_CHARS:
            raise OutputLimitExceeded("打印内容超过上限，请检查循环或减少 print()。")
        return len(value)

    def flush(self):
        pass

    def getvalue(self):
        return "".join(self.parts)


def normalize(value, budget=None, depth=0):
    """Convert common scientific values to JSON without silently accepting reprs."""
    if budget is None:
        budget = [25000]
    budget[0] -= 1
    if budget[0] < 0 or depth > 80:
        raise OutputLimitExceeded("返回值太大或嵌套太深，请检查返回的数据。")
    if value is None or isinstance(value, (str, bool, int)):
        if isinstance(value, str) and len(value) > 100000:
            raise OutputLimitExceeded("返回的字符串太长。")
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("返回值包含 NaN 或无穷大，请先处理缺失值或除零。")
        return value
    if isinstance(value, (list, tuple)):
        return [normalize(item, budget, depth + 1) for item in value]
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise TypeError("返回的字典需要使用字符串作为键，才能与 JSON 示例一致。")
        return {key: normalize(item, budget, depth + 1) for key, item in value.items()}
    module = type(value).__module__.split(".")[0]
    if module in {"numpy", "pandas"}:
        if hasattr(value, "tolist"):
            return normalize(value.tolist(), budget, depth + 1)
        if hasattr(value, "item"):
            return normalize(value.item(), budget, depth + 1)
    raise TypeError(f"无法比较 {type(value).__name__} 返回值；请返回数字、字符串、列表或字典。")


def equivalent(actual, expected):
    if isinstance(actual, bool) or isinstance(expected, bool):
        return type(actual) is type(expected) and actual == expected
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        if isinstance(actual, int) and isinstance(expected, int):
            return actual == expected
        return math.isclose(actual, expected, rel_tol=1e-6, abs_tol=1e-8)
    if isinstance(actual, list) and isinstance(expected, list):
        return len(actual) == len(expected) and all(equivalent(a, e) for a, e in zip(actual, expected))
    if isinstance(actual, dict) and isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(equivalent(actual[k], expected[k]) for k in expected)
    return type(actual) is type(expected) and actual == expected


def mismatch_hint(actual, expected, path='结果'):
    """Point to the first observable mismatch without guessing the algorithm."""
    if type(actual) is not type(expected) and not (
        type(actual) in (int, float) and type(expected) in (int, float)
    ):
        return f'{path}的类型应为 {type(expected).__name__}，实际为 {type(actual).__name__}。'
    if isinstance(actual, list) and isinstance(expected, list):
        if len(actual) != len(expected):
            return f'{path}应有 {len(expected)} 个元素，实际有 {len(actual)} 个；检查遗漏、重复与边界。'
        for index, (a, e) in enumerate(zip(actual, expected)):
            if not equivalent(a, e):
                return mismatch_hint(a, e, f'{path}[{index}]')
    if isinstance(actual, dict) and isinstance(expected, dict):
        if actual.keys() != expected.keys():
            return f'{path}的字段不一致；检查缺少或多余的键。'
        for key in expected:
            if not equivalent(actual[key], expected[key]):
                return mismatch_hint(actual[key], expected[key], f'{path}[{key!r}]')
    return f'{path}与预期不一致；用当前输入逐步检查中间值，并留意空输入、重复值和边界。'


def compare_stdout(actual, expected):
    """ACM token comparison: whitespace is flexible, token spelling is exact."""
    actual_tokens, expected_tokens = actual.split(), expected.split()
    for index, (a, e) in enumerate(zip(actual_tokens, expected_tokens), 1):
        if a != e:
            return False, f'第 {index} 个输出项不同：预期 {e[:80]!r}，实际 {a[:80]!r}。检查计算和输出顺序。'
    if len(actual_tokens) != len(expected_tokens):
        return False, f'应输出 {len(expected_tokens)} 项，实际输出 {len(actual_tokens)} 项。检查漏输出或多余调试信息；调试请写到 sys.stderr。'
    return True, ''


def run_stdin_program(compiled, stdin):
    previous_stdin, previous_argv = sys.stdin, sys.argv
    previous_main = sys.modules.get('__main__')
    stream = io.TextIOWrapper(io.BytesIO(stdin.encode('utf-8')), encoding='utf-8')
    module = types.ModuleType('__main__')
    module.__file__ = USER_FILENAME
    try:
        sys.stdin, sys.argv = stream, [USER_FILENAME]
        sys.modules['__main__'] = module
        try:
            exec(compiled, module.__dict__)
        except SystemExit as exc:
            if exc.code is not None and exc.code != 0:
                raise
    finally:
        sys.stdin, sys.argv = previous_stdin, previous_argv
        if previous_main is None:
            sys.modules.pop('__main__', None)
        else:
            sys.modules['__main__'] = previous_main
        stream.close()


def error_details(exc):
    line = exc.lineno if isinstance(exc, SyntaxError) else None
    frames = traceback.extract_tb(exc.__traceback__) if exc.__traceback__ else []
    user_frames = [frame for frame in frames if frame.filename == USER_FILENAME]
    if user_frames:
        line = user_frames[-1].lineno
    hints = {
        "SyntaxError": "检查这一行和上一行：冒号、括号、引号是否完整？Python 使用英文标点。",
        "IndentationError": "同一层级缩进保持一致，函数体通常缩进 4 个空格；不要混用 Tab 和空格。",
        "TabError": "请把缩进统一成空格，每一级使用 4 个空格。",
        "NameError": "这个名字尚未定义：检查拼写，并先赋值或 import，再使用。",
        "UnboundLocalError": "变量可能只在某个 if 分支里赋值；请保证每条执行路径都先赋值。",
        "TypeError": "检查数据类型、函数参数数量和运算对象；输入参数说明与示例可以帮助你定位。",
        "ValueError": "类型可能正确，但值不符合要求；检查转换内容、数组形状或边界条件。",
        "IndexError": "索引从 0 开始，最后一个索引是 len(序列) - 1；也要处理空序列。",
        "KeyError": "字典中没有这个键；检查键名，或根据题意使用 in / get()。",
        "ZeroDivisionError": "分母为 0；按题意先判断分母，或处理空列表。",
        "AttributeError": "该对象没有这个方法或属性；检查对象类型、方法拼写，以及是否误把返回 None 的操作赋值。",
        "ModuleNotFoundError": "所需库尚未安装或导入名拼错。基础题无需第三方库；科学计算题请运行安装依赖脚本。",
        "ImportError": "检查导入名称及依赖是否正确安装。",
        "OutputLimitExceeded": "减少 print()，检查循环能否结束，并只返回题目需要的结果。",
        "RecursionError": "递归需要终止条件；检查每次调用是否更接近终止条件。",
        "EOFError": "平台通过 solve 的参数传入数据，不需要 input()；请直接使用函数参数。",
        "SystemExit": "请直接 return 结果，不要调用 exit() 或 sys.exit()。",
        "NotImplementedError": "请先完成 solve 函数，使用 return 返回结果。",
    }
    kind = type(exc).__name__
    short_trace = "\n".join(f"第 {frame.lineno} 行，{frame.name}" for frame in user_frames)
    message = str(exc)[:2000] or kind
    return {"type": kind, "message": message, "line": line,
            "hint": hints.get(kind, "从报错行开始检查变量值，并用示例输入逐步推演。"),
            "traceback": (short_trace + "\n" if short_trace else "") + kind + ": " + message}


def sql_result(code, args, setup_sql):
    if len(args) != 1 or not isinstance(args[0], dict):
        raise ValueError("SQL 输入应为一个表数据对象，例如 [{\"students\": [[1, \"小明\"]]}]。")
    with contextlib.closing(sqlite3.connect(":memory:")) as database:
        database.executescript(setup_sql)
        tables = {row[0] for row in database.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for table, rows in args[0].items():
            if table not in tables or not isinstance(rows, list):
                raise ValueError(f"表 {table!r} 不存在，或表数据不是数组。")
            quoted = '"' + table.replace('"', '""') + '"'
            width = len(database.execute(f"PRAGMA table_info({quoted})").fetchall())
            for row in rows:
                if not isinstance(row, list) or len(row) != width:
                    raise ValueError(f"表 {table} 每行必须有 {width} 列。")
            if rows:
                placeholders = ",".join("?" for _ in range(width))
                database.executemany(f"INSERT INTO {quoted} VALUES ({placeholders})", rows)
        database.commit()
        allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE}
        def authorize(action, arg1, arg2, db_name, trigger):
            if action == sqlite3.SQLITE_FUNCTION and str(arg2).lower() == "load_extension":
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY
        database.set_authorizer(authorize)
        cursor = database.execute(code)
        rows = cursor.fetchmany(25001)
        if len(rows) > 25000:
            raise OutputLimitExceeded("SQL 返回超过 25000 行，请检查筛选条件或使用 LIMIT。")
        return [list(row) for row in rows]


def evaluate(payload):
    """Run in this process; used only inside the isolated worker and verifier."""
    load_practice_support()
    started = time.monotonic()
    cases = payload["cases"]
    result = {"status": "accepted", "passed": 0, "total": len(cases), "cases": [],
              "error": None, "duration_ms": 0, "mode": payload.get("mode", "run")}
    language = payload.get("language", "python")
    stdin_mode = payload.get('execution_mode') == 'stdin'
    trace_mode = payload.get('mode') == 'trace' and language == 'python'
    result['execution_mode'] = 'stdin' if stdin_mode else 'function'
    try:
        compiled = compile(payload["code"], USER_FILENAME, "exec", dont_inherit=True) if language == "python" else None
    except (SyntaxError, ValueError) as exc:
        result.update(status="syntax_error", error=error_details(exc))
        result["duration_ms"] = round((time.monotonic() - started) * 1000)
        return result
    for case in cases:
        case_started = time.monotonic()
        output = LimitedOutput()
        diagnostic_output = LimitedOutput() if stdin_mode else output
        trace_events, trace_state = [], {'truncated': False}
        previous_trace = sys.gettrace()
        previous_module = sys.modules.get("__learner__")
        record = {"passed": False,
                  "expected": case.get("expected"), "actual": None, "stdout": ""}
        record.update({'stdin': case['stdin']} if stdin_mode else {'args': copy.deepcopy(case['args'])})
        if case.get("custom"):
            record["custom"] = True
        try:
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(diagnostic_output):
                if trace_mode:
                    sys.settrace(make_tracer(trace_events, trace_state, include_module=stdin_mode))
                # Fresh globals prevent one test from leaking variables into the next.
                if stdin_mode:
                    run_stdin_program(compiled, case['stdin'])
                    actual = output.getvalue()
                elif language == "sql":
                    actual = sql_result(payload["code"], copy.deepcopy(case["args"]), payload.get("setup_sql", ""))
                else:
                    module = types.ModuleType("__learner__")
                    module.__file__ = USER_FILENAME
                    sys.modules["__learner__"] = module
                    namespace = module.__dict__
                    exec(compiled, namespace)
                    solve = namespace.get("solve")
                    if not callable(solve):
                        raise NotImplementedError("找不到 solve 函数。请保留 def solve(...)，并在函数里完成代码。")
                    actual = solve(*copy.deepcopy(case["args"]))
                if inspect.isawaitable(actual):
                    if inspect.iscoroutine(actual):
                        actual.close()
                    raise TypeError("本题需要普通 def solve(...) 函数，请移除 async。")
                record["actual"] = normalize(actual)
                if stdin_mode and not case.get('custom'):
                    record['passed'], hint = compare_stdout(actual, case['expected'])
                    if hint:
                        record['hint'] = hint
                else:
                    record["passed"] = bool(case.get("custom")) or equivalent(record["actual"], case.get("expected"))
                if case.get("custom"):
                    record["label"] = "执行成功"
                if not record['passed'] and not stdin_mode:
                    record['hint'] = mismatch_hint(record['actual'], case.get('expected'))
                    if actual is None and case.get("expected") is not None:
                        record["hint"] = "函数返回了 None。print() 只负责显示，请用 return 返回答案；也检查是否有分支漏写 return。"
        except BaseException as exc:
            details = error_details(exc)
            if stdin_mode and isinstance(exc, EOFError):
                details['hint'] = '标准输入已读完；检查是否多调用了 input()，以及测试组数 T、数组长度 n 的读取位置。'
            elif stdin_mode and isinstance(exc, SystemExit):
                details['hint'] = '程序以非零退出码结束；请检查主动退出的位置，正常完成时不需要调用 exit()。'
            if language == "sql":
                details["hint"] = "检查表名、列名、SELECT / WHERE / GROUP BY / ORDER BY 的顺序。这里只允许一条只读查询；结果行顺序需符合题意。"
                if "not authorized" in str(exc) or "authorization denied" in str(exc):
                    details["hint"] = "本练习只允许 SELECT 或 WITH 查询，不允许修改数据或数据库结构。"
            record["error"] = details
            result["error"] = details
            result["status"] = "missing_dependency" if isinstance(exc, (ModuleNotFoundError, ImportError)) else "runtime_error"
            if language == "sql" and "syntax error" in str(exc).lower():
                result["status"] = "syntax_error"
        finally:
            if trace_mode:
                sys.settrace(previous_trace)
            if previous_module is None:
                sys.modules.pop("__learner__", None)
            else:
                sys.modules["__learner__"] = previous_module
        record["stdout"] = output.getvalue()
        record['duration_ms'] = round((time.monotonic() - case_started) * 1000, 2)
        if stdin_mode:
            record['stderr'] = diagnostic_output.getvalue()
        if trace_mode:
            record['trace'] = trace_events
            record['trace_truncated'] = trace_state['truncated']
        result["cases"].append(record)
        if record["passed"]:
            result["passed"] += 1
        elif not record.get("error") and result["status"] == "accepted":
            result["status"] = "wrong_answer"
        if record.get("error"):
            break
    result["duration_ms"] = round((time.monotonic() - started) * 1000)
    return result


def failure(status, kind, message, hint, total, mode, elapsed):
    return {"status": status, "passed": 0, "total": total, "cases": [], "mode": mode,
            "duration_ms": round(elapsed * 1000),
            "error": {"type": kind, "message": message, "hint": hint, "line": None, "traceback": ""}}


def execute(code, cases, mode="run", timeout=EXECUTION_TIMEOUT, language="python", setup_sql="", execution_mode="function"):
    """Enforce wall timeout and bounded pipe reads even for raw os.write output."""
    started = time.monotonic()
    payload = json.dumps({"code": code, "cases": cases, "mode": mode, "language": language,
                          "setup_sql": setup_sql, 'execution_mode': execution_mode}, ensure_ascii=False).encode("utf-8")
    if language == "javascript":
        node = shutil.which("node")
        if not node:
            return failure("missing_dependency", "NodeNotFound", "尚未安装 Node.js，无法运行 JavaScript 题。",
                           "安装 Node.js 后重新启动平台；Python 与 SQL 题不受影响。", len(cases), mode, 0)
        command = [node, str(Path(__file__).with_name("node_runner.js"))]
    else:
        command = [sys.executable, "-I", "-X", "utf8", str(Path(__file__).resolve()), "--worker"]
    env = os.environ.copy()
    env.update(PYTHONIOENCODING="utf-8", MPLBACKEND="Agg", OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
    env.pop("PYTHONSTARTUP", None)
    buffers = {"stdout": bytearray(), "stderr": bytearray()}
    exceeded = threading.Event()
    with tempfile.TemporaryDirectory(prefix="pystep-") as directory:
        env["MPLCONFIGDIR"] = directory
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        process = subprocess.Popen(command,
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   cwd=directory, env=env, creationflags=flags)

        def read_pipe(name, pipe):
            try:
                while True:
                    chunk = os.read(pipe.fileno(), 4096)
                    if not chunk:
                        return
                    room = MAX_RESULT_BYTES - len(buffers[name])
                    buffers[name].extend(chunk[:max(0, room)])
                    if len(chunk) > room:
                        exceeded.set()
                        process.kill()
                        return
            except (OSError, ValueError):
                return

        readers = [threading.Thread(target=read_pipe, args=(name, getattr(process, name)), daemon=True)
                   for name in ("stdout", "stderr")]
        for reader in readers:
            reader.start()
        try:
            process.stdin.write(payload)
            process.stdin.close()
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=3)
            return failure("timeout", "TimeoutError", f"执行超过 {timeout:g} 秒，已停止。",
                           "检查循环更新、递归终止条件与算法复杂度；先用较小的自定义输入定位，再对照题目规模优化。", len(cases), mode,
                           time.monotonic() - started)
        except BrokenPipeError:
            process.wait(timeout=timeout)
        finally:
            for reader in readers:
                reader.join(timeout=0.5)
            for pipe in (process.stdin, process.stdout, process.stderr):
                if pipe and not pipe.closed:
                    pipe.close()
        elapsed = time.monotonic() - started
        if exceeded.is_set():
            return failure("runtime_error", "OutputLimitExceeded", "输出超过平台上限，已停止。",
                           "减少输出内容，并检查是否存在无限打印循环。", len(cases), mode, elapsed)
        try:
            result = json.loads(buffers["stdout"].decode("utf-8"))
            if not isinstance(result, dict) or "status" not in result:
                raise ValueError("invalid worker result")
            result["duration_ms"] = round(elapsed * 1000)
            return result
        except (UnicodeError, ValueError):
            return failure("runtime_error", "WorkerExit", "执行进程提前结束，未能返回结果。",
                           "请不要关闭标准输出、调用 os._exit() 或直接写入系统输出；使用 return 返回结果。",
                           len(cases), mode, elapsed)


def worker_main():
    original_stdout = sys.stdout
    try:
        payload = json.load(sys.stdin)
        sys.stdin = io.StringIO("")
        result = evaluate(payload)
        serialized = json.dumps(result, ensure_ascii=False, allow_nan=False)
        if len(serialized.encode("utf-8")) > MAX_RESULT_BYTES:
            result = failure("runtime_error", "OutputLimitExceeded", "返回结果或打印内容过大。",
                             "只返回题目要求的数据，减少打印。", len(payload["cases"]), payload.get("mode", "run"), 0)
            serialized = json.dumps(result, ensure_ascii=False)
    except BaseException as exc:
        serialized = json.dumps(failure("error", type(exc).__name__, str(exc)[:2000],
                                        "请检查代码后重新运行。", 0, "run", 0), ensure_ascii=False)
    original_stdout.write(serialized)
    original_stdout.flush()


if __name__ == "__main__" and "--worker" in sys.argv:
    worker_main()
