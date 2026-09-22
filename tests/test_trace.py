"""Teaching trace records real execution without changing the result."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import runner


class TeachingTraceTests(unittest.TestCase):
    def test_loop_values_and_return(self):
        code = 'def solve(nums):\n    total = 0\n    for x in nums:\n        total += x\n    return total'
        result = runner.execute(code, [{'args': [[1, 2]], 'expected': 3}], mode='trace')
        self.assertEqual(result['status'], 'accepted')
        steps = result['cases'][0]['trace']
        before_add = [s for s in steps if s['event'] == 'line' and s['line'] == 4]
        self.assertEqual([s['locals']['total'] for s in before_add], ['0', '1'])
        self.assertEqual([s['locals']['x'] for s in before_add], ['1', '2'])
        self.assertEqual(steps[-1]['value'], '3')

    def test_record_limit_does_not_stop_program(self):
        code = 'def solve(n):\n    s=0\n    for i in range(n):\n        s+=i\n    return s'
        result = runner.execute(code, [{'args': [1000], 'expected': 499500}], mode='trace')
        self.assertEqual(result['status'], 'accepted')
        case = result['cases'][0]
        self.assertTrue(case['trace_truncated'])
        self.assertEqual(len(case['trace']), runner.MAX_TRACE_STEPS)

    def test_preview_does_not_call_user_repr(self):
        code = '''class Box:
    def __repr__(self):
        raise ValueError('must not run')
def solve():
    value=Box()
    return 7
'''
        result = runner.execute(code, [{'args': [], 'expected': 7}], mode='trace')
        self.assertEqual(result['status'], 'accepted')
        self.assertTrue(any(s['locals'].get('value') == '<Box>' for s in result['cases'][0]['trace']))

    def test_stdin_trace_and_exception(self):
        result = runner.execute('n=int(input())\nprint(10//n)', [{'stdin': '2', 'expected': '5'}], mode='trace', execution_mode='stdin')
        self.assertEqual(result['status'], 'accepted')
        self.assertTrue(any(s['locals'].get('n') == '2' for s in result['cases'][0]['trace']))
        result = runner.execute('def solve():\n    return 1/0', [{'args': [], 'expected': 1}], mode='trace')
        self.assertEqual(result['status'], 'runtime_error')
        self.assertTrue(any(s.get('exception') == 'ZeroDivisionError' for s in result['cases'][0]['trace']))


if __name__ == '__main__':
    unittest.main()
