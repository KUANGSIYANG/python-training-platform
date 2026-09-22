"""Shared, deliberately small problem schema."""

CHAPTERS = [
    '值、变量与运算', '条件判断', '循环与累积', '字符串', '列表与元组',
    '字典与集合', '函数与参数', '推导式与迭代器', '异常、文件与数据格式',
    '类、模块与类型提示', 'collections、itertools 与 functools', '数学、时间与随机数',
    '正则、路径与数据库', 'NumPy 数组基础', 'NumPy 计算与线性代数',
    'pandas 表格基础', 'pandas 数据分析', '可视化与机器学习入门',
    '机考输入输出与复杂度', '排序与二分查找', '栈、队列与链表',
    '树、堆与并查集', '图与搜索', '递归、贪心与动态规划',
    'SQL 查询与关系数据库', 'Python 后端基础', 'HTTP 与服务器 API',
    'HTML 与 CSS 页面基础', 'JavaScript 与前端交互', '全栈综合练习',
    '数组、哈希与滑动窗口进阶', '二分答案、贪心与区间', '秋招动态规划专题',
    '树、图与综合搜索', '字符串、位运算与数学', '工程场景与笔试综合',
    'ACM 输入输出与基础赛训', '树状数组、线段树与离线查询', '进阶图论',
    '进阶动态规划', '字符串算法', '数论与组合数学',
]


def problem(chapter, number, title, concept, description, parameters, tests,
            solution, hints, explanation, difficulty='入门', requires=None, starter=None,
            language='python', setup_sql=None):
    params = [{'name': p[0], 'type': p[1], 'description': p[2]} for p in parameters]
    cases = [{'args': args, 'expected': expected} for args, expected in tests]
    imports = {'numpy': 'import numpy as np', 'pandas': 'import pandas as pd',
               'matplotlib': 'import matplotlib.pyplot as plt', 'sklearn': '# 按题目需要导入 sklearn 中的工具'}
    prefix = '\n'.join(imports[m] for m in (requires or []) if m in imports)
    default_starter = (prefix + '\n\n' if prefix else '') + 'def solve(' + ', '.join(p['name'] for p in params) + '):\n    # 在这里编写代码；用 return 返回结果\n    pass\n'
    return dict(id=(chapter - 1) * 10 + number, chapter=chapter,
                chapter_title=CHAPTERS[chapter - 1], title=title, concept=concept,
                language=language, setup_sql=setup_sql, execution_mode='function',
                description=description, parameters=params, difficulty=difficulty,
                tags=[CHAPTERS[chapter - 1]] + (requires or []), requires=requires or [],
                starter=starter or default_starter, tests=cases, examples=cases[:2],
                hints=hints, solution=solution.strip() + '\n', explanation=explanation)


def acm_problem(chapter, number, title, concept, description, tests, solution,
                hints, explanation, difficulty='挑战', complexity=None,
                prerequisites=None, skills=None):
    """A real stdin/stdout program, with a fresh input stream for every case."""
    item = problem(chapter, number, title, concept, description, [], [],
                   solution, hints, explanation, difficulty=difficulty,
                   starter='import sys\n\n\ndef main():\n    # 从 input() 或 sys.stdin 读取数据，用 print() 输出答案\n    pass\n\n\nif __name__ == "__main__":\n    main()\n')
    cases = [{'stdin': stdin, 'expected': expected} for stdin, expected in tests]
    item.update(execution_mode='stdin', output_comparison='tokens', tests=cases,
                examples=cases[:2], track='acm', complexity=complexity or {},
                prerequisites=prerequisites or [], skills=skills or [],
                learning_goal=title)
    return item
