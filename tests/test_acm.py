"""Regression coverage for the actual stdin judging path and its HTTP contract."""
import copy
import http.client
import json
from pathlib import Path
import sys
import threading
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import runner
from curriculum.schema import acm_problem
from server import LearningServer


CASES = [{'stdin': '2 3\n', 'expected': '5\n'},
         {'stdin': '-7 2\n', 'expected': '-5\n'}]
SOLUTION = 'a, b = map(int, input().split())\nprint(a + b)\n'


class StdinRunnerTests(unittest.TestCase):
    def run_code(self, code, cases=None, **kwargs):
        return runner.execute(code, cases or CASES, execution_mode='stdin', **kwargs)

    def test_real_input_print_and_clean_case_streams(self):
        result = self.run_code(SOLUTION)
        self.assertEqual((result['status'], result['passed']), ('accepted', 2))
        self.assertEqual(result['cases'][0]['stdin'], '2 3\n')
        self.assertEqual(result['cases'][1]['actual'], '-5\n')

    def test_binary_stdin_main_guard_and_dataclass(self):
        code = '''from __future__ import annotations
from dataclasses import dataclass
import sys
@dataclass
class Values:
    a: int
    b: int
if __name__ == '__main__':
    v = Values(*map(int, sys.stdin.buffer.read().split()))
    print(v.a + v.b)
'''
        self.assertEqual(self.run_code(code)['status'], 'accepted')

    def test_debug_stderr_is_separate(self):
        result = self.run_code('import sys\nprint("调试", file=sys.stderr)\n' + SOLUTION)
        self.assertEqual(result['status'], 'accepted')
        self.assertEqual(result['cases'][0]['stderr'], '调试\n')
        self.assertNotIn('调试', result['cases'][0]['actual'])

    def test_whitespace_flexible_but_tokens_exact(self):
        case = [{'stdin': '', 'expected': '1 2\n3'}]
        self.assertEqual(self.run_code('print("  1\\n2 3\\n\\n")', case)['status'], 'accepted')
        wrong = self.run_code('print("1.0 2 3")', case)
        self.assertEqual(wrong['status'], 'wrong_answer')
        self.assertIn('第 1 个', wrong['cases'][0]['hint'])
        extra = self.run_code('print("1 2 3 4")', case)
        self.assertIn('实际输出 4 项', extra['cases'][0]['hint'])

    def test_empty_output_can_be_valid(self):
        result = self.run_code('pass', [{'stdin': '', 'expected': ''}])
        self.assertEqual(result['status'], 'accepted')

    def test_eof_and_error_line_feedback(self):
        result = self.run_code('input()\ninput()\n')
        self.assertEqual(result['error']['line'], 2)
        self.assertIn('标准输入已读完', result['error']['hint'])
        syntax = self.run_code('if True\n    print(1)')
        self.assertEqual((syntax['status'], syntax['error']['line']), ('syntax_error', 1))

    def test_exit_zero_and_nonzero(self):
        self.assertEqual(self.run_code(SOLUTION + 'raise SystemExit(0)')['status'], 'accepted')
        result = self.run_code('raise SystemExit(2)')
        self.assertEqual(result['status'], 'runtime_error')
        self.assertIn('非零退出码', result['error']['hint'])

    def test_custom_empty_input_is_execution_only(self):
        result = self.run_code('print(123)', [{'stdin': '', 'expected': None, 'custom': True}])
        self.assertTrue(result['cases'][0]['custom'])
        self.assertEqual(result['cases'][0]['label'], '执行成功')

    def test_timeout_and_output_limit(self):
        self.assertEqual(self.run_code('while True: pass', timeout=0.4)['status'], 'timeout')
        result = self.run_code('print("x" * 15000)')
        self.assertEqual(result['error']['type'], 'OutputLimitExceeded')

    def test_inprocess_verifier_restores_stdin_and_main(self):
        old_stdin, old_main = sys.stdin, sys.modules['__main__']
        cases = copy.deepcopy(CASES)
        result = runner.evaluate({'code': SOLUTION, 'cases': cases, 'execution_mode': 'stdin'})
        self.assertEqual(result['status'], 'accepted')
        self.assertIs(sys.stdin, old_stdin)
        self.assertIs(sys.modules['__main__'], old_main)
        self.assertEqual(cases, CASES)

    def test_function_mismatch_points_to_nested_path(self):
        result = runner.execute('def solve(): return {"data": [1, 9]}',
                                [{'args': [], 'expected': {'data': [1, 2]}}])
        self.assertIn("结果['data'][1]", result['cases'][0]['hint'])


class StdinApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture = acm_problem(37, 1, '测试求和', '教学', '输入两个整数',
                              [(c['stdin'], c['expected']) for c in CASES],
                              SOLUTION, ['提示'] * 3, '解释')
        cls.server = LearningServer(('127.0.0.1', 0), [fixture])
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(2)

    def post(self, extra):
        body = json.dumps({'problem_id': 361, 'code': SOLUTION, 'mode': 'run', **extra})
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=15)
        connection.request('POST', '/api/run', body=body, headers={'Content-Type': 'application/json'})
        response = connection.getresponse()
        result = response.status, json.loads(response.read())
        connection.close()
        return result

    def test_real_custom_input_and_submission_ignores_custom(self):
        status, result = self.post({'custom_stdin': '10 30'})
        self.assertEqual((status, result['cases'][0]['actual']), (200, '40\n'))
        self.assertTrue(result['cases'][0]['custom'])
        status, result = self.post({'mode': 'submit', 'custom_stdin': 'bad input'})
        self.assertEqual((status, result['status'], result['total']), (200, 'accepted', 2))

    def test_custom_input_validation(self):
        for extra in [{'custom_stdin': [2, 3]}, {'custom_args': [2, 3]},
                      {'custom_stdin': 'x' * (64 * 1024 + 1)}]:
            with self.subTest(extra=str(extra)[:50]):
                self.assertEqual(self.post(extra)[0], 400)

    def test_teaching_trace_checks_only_one_case(self):
        status, result = self.post({'mode': 'trace'})
        self.assertEqual((status, result['status'], result['total']), (200, 'accepted', 1))
        self.assertTrue(result['cases'][0]['trace'])


if __name__ == '__main__':
    unittest.main()
