"""Regression tests for execution feedback, bounds, real languages and HTTP API."""
from __future__ import annotations

import http.client
import json
from pathlib import Path
import shutil
import sys
import threading
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import runner
from server import LearningServer

CASES = [{"args": [2, 3], "expected": 5}, {"args": [-4, 1], "expected": -3}]
FIXTURE = {"id": 1, "chapter": 1, "chapter_title": "测试", "title": "两数相加", "concept": "return",
           "description": "返回 a + b", "parameters": [{"name": "a"}, {"name": "b"}], "difficulty": "入门",
           "tags": [], "requires": [], "starter": "def solve(a,b):\n    pass", "tests": CASES + [{"args": [0, 0], "expected": 0}],
           "examples": CASES, "hints": ["提示"], "solution": "def solve(a,b):\n    return a+b", "explanation": "相加"}
SQL_CASES = [{"args": [{"items": [[2, "乙", 7], [1, "甲", 3]]}], "expected": [[1, "甲"], [2, "乙"]]}]
SQL_SETUP = "CREATE TABLE items(id INTEGER, name TEXT, price REAL);"


class RunnerTests(unittest.TestCase):
    def test_correct_and_print(self):
        result = runner.execute("def solve(a,b):\n    print('调试', a)\n    return a+b", CASES)
        self.assertEqual(result["status"], "accepted")
        self.assertEqual(result["passed"], 2)
        self.assertIn("调试 2", result["cases"][0]["stdout"])

    def test_wrong_answer_and_missing_return_hint(self):
        result = runner.execute("def solve(a,b):\n    print(a+b)", CASES)
        self.assertEqual(result["status"], "wrong_answer")
        self.assertIn("return", result["cases"][0]["hint"])
        self.assertEqual(result["cases"][0]["actual"], None)

    def test_missing_function(self):
        result = runner.execute("answer = 5", CASES)
        self.assertEqual(result["status"], "runtime_error")
        self.assertIn("solve", result["error"]["message"])

    def test_syntax_line(self):
        result = runner.execute("def solve(a,b):\n    return (a +", CASES)
        self.assertEqual(result["status"], "syntax_error")
        self.assertEqual(result["error"]["line"], 2)

    def test_runtime_line(self):
        result = runner.execute("def solve(a,b):\n    value = a / 0\n    return value", CASES)
        self.assertEqual(result["status"], "runtime_error")
        self.assertEqual(result["error"]["type"], "ZeroDivisionError")
        self.assertEqual(result["error"]["line"], 2)

    def test_input_hint(self):
        result = runner.execute("def solve(a,b):\n    return input()", CASES)
        self.assertEqual(result["error"]["type"], "EOFError")
        self.assertIn("参数", result["error"]["hint"])

    def test_module_missing(self):
        result = runner.execute("import nonexistent_pystep_package\ndef solve(a,b): return a+b", CASES)
        self.assertEqual(result["status"], "missing_dependency")

    def test_globals_fresh_and_input_not_mutated(self):
        cases = [{"args": [[1]], "expected": [1, 2]}, {"args": [[1]], "expected": [1, 2]}]
        result = runner.execute("seen=[]\ndef solve(values):\n    seen.append(2)\n    values.extend(seen)\n    return values", cases)
        self.assertEqual(result["status"], "accepted")
        self.assertEqual(result["cases"][0]["args"], [[1]])

    def test_dataclass_with_future_annotations(self):
        code = "from __future__ import annotations\nfrom dataclasses import dataclass\n@dataclass\nclass Pair:\n    a: int\n    b: int\ndef solve(a,b):\n    pair = Pair(a,b)\n    return pair.a + pair.b"
        self.assertEqual(runner.execute(code, CASES)["status"], "accepted")

    def test_timeout(self):
        start = time.monotonic()
        result = runner.execute("def solve(a,b):\n    while True: pass", CASES, timeout=0.4)
        self.assertEqual(result["status"], "timeout")
        self.assertLess(time.monotonic() - start, 5)

    def test_print_limit(self):
        result = runner.execute("def solve(a,b):\n    while True: print('x' * 1000)", CASES)
        self.assertEqual(result["status"], "runtime_error")
        self.assertEqual(result["error"]["type"], "OutputLimitExceeded")
        self.assertLessEqual(len(result["cases"][0]["stdout"]), runner.MAX_STDOUT_CHARS)

    def test_raw_output_limit(self):
        result = runner.execute("import os\ndef solve(a,b):\n    while True: os.write(1,b'x'*8192)", CASES)
        self.assertEqual(result["error"]["type"], "OutputLimitExceeded")

    def test_float_recursion_and_bool_type(self):
        self.assertTrue(runner.equivalent({"x": [0.1 + 0.2]}, {"x": [0.3]}))
        self.assertFalse(runner.equivalent(True, 1))
        self.assertFalse(runner.equivalent([1, 2], [2, 1]))

    def test_custom_is_execution_only(self):
        result = runner.execute("def solve(a,b): return a+b", [{"args": [100, 3], "custom": True}])
        self.assertEqual(result["cases"][0]["actual"], 103)
        self.assertEqual(result["cases"][0]["label"], "执行成功")
        self.assertTrue(result["cases"][0]["custom"])

    def test_sql_query_and_read_only(self):
        result = runner.execute("SELECT id, name FROM items ORDER BY id", SQL_CASES, language="sql", setup_sql=SQL_SETUP)
        self.assertEqual(result["status"], "accepted")
        for code in ["DELETE FROM items", "ATTACH DATABASE 'test.db' AS extra", "SELECT 1; SELECT 2"]:
            with self.subTest(code=code):
                denied = runner.execute(code, SQL_CASES, language="sql", setup_sql=SQL_SETUP)
                self.assertEqual(denied["status"], "runtime_error")

    def test_sql_wrong_answer_and_bad_input(self):
        wrong = runner.execute("SELECT name,id FROM items ORDER BY id", SQL_CASES, language="sql", setup_sql=SQL_SETUP)
        self.assertEqual(wrong["status"], "wrong_answer")
        bad = runner.execute("SELECT * FROM items", [{"args": [{"items": [[1]]}]}], language="sql", setup_sql=SQL_SETUP)
        self.assertEqual(bad["status"], "runtime_error")

    @unittest.skipUnless(shutil.which("node"), "Node.js 未安装")
    def test_javascript_sync_async_and_errors(self):
        for code in ["function solve(a,b) { return a+b; }", "async function solve(a,b) { console.log('调试'); return await Promise.resolve(a+b); }"]:
            with self.subTest(code=code):
                self.assertEqual(runner.execute(code, CASES, language="javascript")["status"], "accepted")
        syntax = runner.execute("function solve(a,b) {\n return (; }", CASES, language="javascript")
        self.assertEqual(syntax["status"], "syntax_error")
        self.assertEqual(syntax["error"]["line"], 2)
        runtime = runner.execute("function solve(a,b) {\n return missing; }", CASES, language="javascript")
        self.assertEqual(runtime["error"]["line"], 2)
        no_return = runner.execute("function solve(a,b) { console.log(a+b); }", CASES, language="javascript")
        self.assertIn("return", no_return["cases"][0]["hint"])

    @unittest.skipUnless(shutil.which("node"), "Node.js 未安装")
    def test_javascript_timeout_and_output_limit(self):
        timeout = runner.execute("function solve(a,b) { while(true) {} }", CASES, timeout=0.5, language="javascript")
        self.assertEqual(timeout["status"], "timeout")
        output = runner.execute("function solve(a,b) { while(true) console.log('x'.repeat(1000)); }", CASES, language="javascript")
        self.assertEqual(output["error"]["type"], "OutputLimitExceeded")


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = LearningServer(("127.0.0.1", 0), [FIXTURE])
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(2)

    def request(self, method, path, payload=None, headers=None, raw=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=15)
        body = raw if raw is not None else (json.dumps(payload).encode() if payload is not None else None)
        final_headers = {"Content-Type": "application/json"} if body is not None else {}
        final_headers.update(headers or {})
        connection.request(method, path, body=body, headers=final_headers)
        response = connection.getresponse()
        status, data = response.status, response.read()
        connection.close()
        return status, json.loads(data)

    def test_problem_visibility(self):
        status, result = self.request("GET", "/api/problems")
        self.assertEqual(status, 200)
        self.assertEqual(result["total"], 1)
        self.assertNotIn("solution", result["problems"][0])
        self.assertNotIn("tests", result["problems"][0])
        _, detail = self.request("GET", "/api/problems/1")
        self.assertIn("solution", detail)
        self.assertNotIn("tests", detail)
        self.assertEqual(self.request("GET", "/api/problems/999")[0], 404)

    def test_submit_public_and_custom(self):
        payload = {"problem_id": 1, "code": FIXTURE["solution"], "mode": "submit"}
        status, result = self.request("POST", "/api/run", payload)
        self.assertEqual((status, result["total"], result["status"]), (200, 3, "accepted"))
        payload["mode"] = "run"
        self.assertEqual(self.request("POST", "/api/run", payload)[1]["total"], 2)
        payload["custom_args"] = [9, 10]
        self.assertEqual(self.request("POST", "/api/run", payload)[1]["cases"][0]["actual"], 19)

    def test_invalid_payloads(self):
        valid = {"problem_id": 1, "code": FIXTURE["solution"]}
        for payload in [[], {**valid, "custom_args": "[]"}, {**valid, "custom_args": [1]},
                        {**valid, "problem_id": True}, {**valid, "mode": []}, {**valid, "code": "\ud800"},
                        {**valid, "code": "x" * (runner.MAX_CODE_BYTES + 1)}]:
            with self.subTest(payload=str(payload)[:100]):
                self.assertEqual(self.request("POST", "/api/run", payload)[0], 400)
        self.assertEqual(self.request("POST", "/api/run", raw=b'{bad json')[0], 400)
        self.assertEqual(self.request("POST", "/api/run", raw=b'{"problem_id":NaN}')[0], 400)
        self.assertEqual(self.request("POST", "/api/run", valid, {"Content-Type": "text/plain"})[0], 400)

    def test_cross_origin_and_host_rejected(self):
        payload = {"problem_id": 1, "code": FIXTURE["solution"]}
        for headers in [{"Origin": "https://example.com"}, {"Origin": "null"}, {"Host": "evil.example"}, {"Sec-Fetch-Site": "cross-site"}]:
            with self.subTest(headers=headers):
                self.assertEqual(self.request("POST", "/api/run", payload, headers)[0], 403)
        local = {"Origin": f"http://127.0.0.1:{self.server.server_port}"}
        self.assertEqual(self.request("POST", "/api/run", payload, local)[0], 200)

    def test_busy_and_static_assets(self):
        self.server.run_slots.acquire()
        self.server.run_slots.acquire()
        try:
            self.assertEqual(self.request("POST", "/api/run", {"problem_id": 1, "code": FIXTURE["solution"]})[0], 429)
        finally:
            self.server.run_slots.release()
            self.server.run_slots.release()
        self.assertEqual(self.request("GET", "/../server.py")[0], 404)
        self.assertEqual(self.request("GET", "/static/../server.py")[0], 404)
        for path, content_type in (("/", "text/html"), ("/static/app.js", "text/javascript"),
                                   ("/static/styles.css", "text/css"),
                                   ("/static/workbench.css", "text/css")):
            with self.subTest(path=path):
                connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=15)
                connection.request("GET", path)
                response = connection.getresponse()
                body = response.read()
                connection.close()
                self.assertEqual(response.status, 200)
                self.assertIn(content_type, response.getheader("Content-Type", ""))
                self.assertTrue(body)

    def test_demo_real_http(self):
        status, result = self.request("GET", "/api/demo/items?q=Python&limit=1")
        self.assertEqual((status, result["total"], len(result["items"])), (200, 2, 1))
        self.assertEqual(self.request("GET", "/api/demo/items/1")[1]["id"], 1)
        self.assertEqual(self.request("GET", "/api/demo/items/999")[0], 404)
        self.assertEqual(self.request("GET", "/api/demo/items?limit=-1")[0], 400)
        self.assertEqual(self.request("POST", "/api/demo/echo", {"hello": "世界"})[1], {"received": {"hello": "世界"}})

    def test_meta(self):
        status, result = self.request("GET", "/api/meta")
        self.assertEqual(status, 200)
        self.assertIn("node", result["dependencies"])
        self.assertIn("sql", result["languages"])


if __name__ == "__main__":
    unittest.main()
