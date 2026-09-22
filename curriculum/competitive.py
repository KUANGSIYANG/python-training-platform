"""Sixty stdin/stdout lessons for the ACM track (chapters 37--42).

Expected answers use small independent oracles; reference programs teach
the scalable algorithms. All fixtures are deterministic.
"""

from collections import deque
from itertools import permutations, product
from math import comb, gcd, isqrt
from random import Random
from textwrap import indent, dedent

from .schema import acm_problem

PROBLEMS = []
_counts = {}
_rng = Random(420037)


def _text(*rows):
    return '\n'.join(' '.join(map(str, row)) if isinstance(row, (tuple, list))
                     else str(row) for row in rows) + '\n'


def _case(rows, answer):
    return (_text(*rows), _text(answer))


def _add(ch, title, teach, syntax, spec, cases, body, hints, proof, time, space,
         difficulty='挑战', skills=None):
    _counts[ch] = _counts.get(ch, 0) + 1
    solution = ('import sys\n\n\ndef main():\n' +
                indent(dedent(body).strip(), '    ') +
                '\n\n\nif __name__ == "__main__":\n    main()\n')
    assert len(cases) >= 7
    fence = chr(96) * 3
    PROBLEMS.append(acm_problem(
        ch, _counts[ch], title,
        teach + '\n\n语法小课：\n' + fence + 'python\n' + syntax + '\n' + fence,
        spec + '\n\n请提交完整 Python 程序，从标准输入读取，用 print 或 sys.stdout.write 输出；输出按空白分隔的 token 比较。',
        cases, solution, hints,
        proof + '\n\n复杂度：时间 ' + time + '，额外空间 ' + space +
        '（不计批量读取的输入文本与最终输出）。',
        difficulty=difficulty, complexity={'time': time, 'space': space},
        prerequisites=[19, 20, 21, 22, 23, 24] if ch == 37 else [22, 37],
        skills=skills or [title.split('：')[0]]))


# Chapter 37: console programs and contest-oriented foundations.
_batches = [
    [[3, -1, 8], [5]], [[0, 0], [-8, -3]], [[-10]], [[7, 7, 7]],
    [[9, -9, 4, -4], [100, -100]], [[10**9, -10**9, 2]],
    [list(range(1, 21))], [[], [1, 2], []],
]
_cases = []
for groups in _batches:
    rows, answers = [len(groups)], []
    for i, a in enumerate(groups, 1):
        rows += [len(a), a]
        answers.append(f'Case #{i}: {len(a)} {min(a) if a else 0} '
                       f'{max(a) if a else 0} {sum(a)}')
    _cases.append((_text(*rows), '\n'.join(answers)))
_add(37, '多测试组：带编号的统计报告',
     '真实比赛需要同时管理输入游标和输出格式。先读 T，再逐组消费 n 个整数；空数组的最小值和最大值按题意定义为 0。',
     'it = iter(map(int, sys.stdin.buffer.read().split()))\nT = next(it)\nprint(f"Case #{1}: {3} {0} {9} {12}")',
     '输入首个整数 T（1≤T≤30），每组先给 n（0≤n≤10000），再给 n 个绝对值≤10^9 的整数；总 n≤30000，换行位置任意。输出 T 行，每行严格形如 Case #i: n 最小值 最大值 总和；i 从 1 开始，空数组后三项均为 0。',
     _cases, r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
for case_id in range(1, next(it) + 1):
    n = next(it)
    a = [next(it) for _ in range(n)]
    print(f"Case #{case_id}: {n} {min(a) if a else 0} {max(a) if a else 0} {sum(a)}")
''',
     ['先读取 T，不能把 T 当成数组长度。', '每组只消费声明的 n 个整数；空组不调用 min([])。', '用 f-string 保留 Case、#、冒号及编号。'],
     '游标按 T、n、数组的层级前进，每个整数恰好进入所属组，因此各统计量对应正确的数组。易错点是 n=0 时漏输出，以及把固定行数误当成输入协议。',
     'O(总 n + T)', 'O(最大 n)', '基础')

_baskets = [
    [[(3, 2), (5, 4)], [(7, 1)]], [[(-2, 3), (10, 2)]], [], [[(0, 9)]],
    [[(1, 100), (1, 1)], [(2, 5)]], [[(10**6, 10**6)]],
    [[(-5, 2), (5, 2)]], [[(i, i + 1) for i in range(1, 12)]],
]
_cases = []
for groups in _baskets:
    rows, out = [], []
    for pairs in groups:
        rows += [len(pairs), *pairs]
        out.append(sum(p * q for p, q in pairs))
    rows.append(0)
    _cases.append((_text(*rows), _text(*out) if out else ''))
_add(37, '终止符协议：批量订单结算',
     '终止符是控制记录，不属于业务数据。每笔订单以商品种类数 n 开始；读到 n=0 就结束。把输入切成 token 后，记录仍可以跨行。',
     'while True:\n    n = next(it)\n    if n == 0:\n        break',
     '输入若干订单。每单先给 n（1≤n≤1000），随后 n 对整数 price quantity，其中 -10^6≤price≤10^6、0≤quantity≤10^6；负价表示抵扣。最后单独一个 0 结束，最多 100 单、总商品种类≤10000。每单输出一行总金额；仅输入 0 时不输出。',
     _cases, r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
while True:
    n = next(it)
    if n == 0:
        break
    total = 0
    for _ in range(n):
        price, quantity = next(it), next(it)
        total += price * quantity
    print(total)
''',
     ['每单结束后才读取下一单的 n。', '商品数量为 0 不代表输入结束。', '先判断 n，再读取该订单的 2n 个整数。'],
     '每轮消费恰好一条订单，累加每项 price×quantity，符合订单金额定义。易错点是把商品字段中的 0 当成终止符。',
     'O(总商品种类)', 'O(1)', '基础')

_fractions = [
    [(1, 2, 1, 3), (1, 4, -1, 4)], [(3, -4, 1, 2)], [],
    [(0, 5, 0, -7)], [(5, 6, 7, 15)], [(-3, -9, 2, 3)],
    [(10**8, 3, 1, 3)], [(i, i + 1, -i, i + 2) for i in range(1, 9)],
]
_cases = []
for rows in _fractions:
    out = []
    for a, b, c, d in rows:
        numerator, denominator = a * d + b * c, b * d
        factor = gcd(numerator, denominator)
        numerator, denominator = numerator // factor, denominator // factor
        if denominator < 0:
            numerator, denominator = -numerator, -denominator
        out.append(f'{numerator}/{denominator}')
    _cases.append((_text(*rows) if rows else '', '\n'.join(out)))
_add(37, '读到 EOF：精确分数合并',
     'EOF 表示输入流结束，不一定有组数。分数相加用整数交叉相乘，随后约分并统一分母符号，避免浮点误差。',
     'from fractions import Fraction\nvalue = Fraction(a, b) + Fraction(c, d)\nprint(f"{value.numerator}/{value.denominator}")',
     '输入 0～1000 组整数 a b c d，表示 a/b+c/d；每组 4 个 token，可跨行，读到 EOF 结束。各数绝对值≤10^8，b、d 非 0。每组输出一行最简分数 p/q，q>0，零写为 0/1。',
     _cases, r'''
from fractions import Fraction
data = list(map(int, sys.stdin.buffer.read().split()))
for i in range(0, len(data), 4):
    a, b, c, d = data[i:i + 4]
    value = Fraction(a, b) + Fraction(c, d)
    print(f"{value.numerator}/{value.denominator}")
''',
     ['每 4 个 token 构成完整的一组。', 'Fraction 属于标准库，能保持有理数精度。', '不要先把 a/b 转成 float；直接构造 Fraction(a, b)。'],
     'Fraction 对整数分子分母精确约分，和的 numerator、denominator 已满足最简且分母为正。易错点是 float 会丢失精度，且 str(Fraction(0)) 不是要求的 0/1。',
     'O(G log M)，G 为组数、M 为整数运算规模', 'O(1)', '基础')

_logs = [
    [('A', 10, 'WA'), ('A', 30, 'AC'), ('B', 40, 'AC')],
    [('A', 5, 'WA'), ('B', 8, 'WA')], [], [('Z', 0, 'AC')],
    [('A', 1, 'AC'), ('A', 2, 'WA'), ('A', 3, 'AC')],
    [('A', 9, 'WA'), ('A', 9, 'WA'), ('A', 10, 'AC')],
    [('C', 20, 'WA'), ('B', 21, 'AC'), ('C', 100, 'AC')],
    [(chr(65 + i % 5), i * 3, 'AC' if i >= 15 else 'WA') for i in range(20)],
]
_cases = []
for logs in _logs:
    total = solved = 0
    for name in set(x[0] for x in logs):
        entries = [x for x in logs if x[0] == name]
        first = next((i for i, x in enumerate(entries) if x[2] == 'AC'), None)
        if first is not None:
            solved += 1
            total += entries[first][1] + 20 * first
    _cases.append(_case([len(logs), *logs], [solved, total]))
_add(37, 'ACM 计分板：首次通过与罚时',
     '状态模拟要先明确哪些事件仍然有效。每题保存失败次数与是否通过；第一次 AC 结算，之后的提交全部忽略。',
     'wrong = {}\nsolved = set()\nwrong[name] = wrong.get(name, 0) + 1',
     '输入 n（0≤n≤100000），随后 n 行 problem minute verdict。problem 为一个大写字母，0≤minute≤300，verdict 为 AC 或 WA；日志按时间非降序给出，同分钟按输入顺序处理。首次 AC 的罚时为该分钟加此前 WA 次数×20；未通过题不计罚时，已通过题的后续提交不计。输出通过题数和总罚时。',
     _cases, r'''
lines = sys.stdin.buffer.read().split()
n = int(lines[0])
wrong, solved = {}, set()
penalty = 0
for i in range(n):
    name, minute, verdict = lines[1 + 3 * i:4 + 3 * i]
    if name in solved:
        continue
    if verdict == b'WA':
        wrong[name] = wrong.get(name, 0) + 1
    else:
        solved.add(name)
        penalty += int(minute) + 20 * wrong.get(name, 0)
print(len(solved), penalty)
''',
     ['不同题目的状态不能混在一起。', '在处理 verdict 前，先跳过已通过的题。', 'WA 时只记次数，首次 AC 时才把罚时加入总额。'],
     '每题在首次 AC 前积累全部 WA，AC 当时一次性结算；已通过状态阻止重复累计，故恰好计算有效罚时。易错点是把未通过题的 WA 也计入总分。',
     'O(n)', 'O(题目种类数)', '进阶')

_cases = []
for a, qs in [
    ([1, 2, 2, 9], [(2, 2), (0, 5)]), ([-5, 0, 5], [(-4, 4), (7, 10)]),
    ([], [(0, 0)]), ([7], [(7, 7), (-8, 6)]),
    ([3] * 8, [(3, 3), (2, 4)]), (list(range(30)), [(5, 19), (0, 29)]),
    ([10**9, -10**9], [(-10**9, 10**9), (0, 0)]),
    ([_rng.randrange(-20, 21) for _ in range(100)], [(i, i + 7) for i in range(-22, 20, 3)]),
]:
    _cases.append((_text([len(a), len(qs)], a, *qs),
                   _text(*(sum(l <= x <= r for x in a) for l, r in qs))))
_add(37, '批量值域查询：两个二分边界',
     '先排序，把闭区间 [L,R] 的元素数转为两个插入位置的差。bisect_left 找第一个≥L，bisect_right 找第一个>R，重复元素自然一起计数。',
     'from bisect import bisect_left, bisect_right\ncount = bisect_right(a, R) - bisect_left(a, L)',
     '输入 n q（0≤n≤100000，1≤q≤100000），接着 n 个整数，再给 q 对 L R。所有值绝对值≤10^9，L≤R，数组可无序且有重复。每个查询输出数组中落在闭区间 [L,R] 的元素个数。',
     _cases, r'''
from bisect import bisect_left, bisect_right
it = iter(map(int, sys.stdin.buffer.read().split()))
n, q = next(it), next(it)
a = sorted(next(it) for _ in range(n))
for _ in range(q):
    l, r = next(it), next(it)
    print(bisect_right(a, r) - bisect_left(a, l))
''',
     ['先排序一次，再处理所有查询。', '右边界要求包含等于 R 的元素。', '右侧用 bisect_right，左侧用 bisect_left，二者相减。'],
     '排序后，所有合法元素连续地位于第一个≥L与第一个>R之间，因此位置差正好是数量。易错点是两端都用 bisect_left。',
     'O(n log n + q log n)', 'O(n)', '进阶')

_matrices = [[[1, 2], [3, 4]], [[-2, 5, 0]], [[7]], [[0] * 4 for _ in range(3)],
             [[-i - j for j in range(4)] for i in range(3)],
             [[i * 5 + j for j in range(5)] for i in range(4)],
             [[10**9, -10**9], [-10**9, 10**9]],
             [[_rng.randrange(-9, 10) for _ in range(9)] for _ in range(8)]]
_cases = []
for a in _matrices:
    n, m = len(a), len(a[0])
    qs = [(1, 1, n, m), (1, 1, 1, 1), (n, m, n, m), (1, m, n, m)]
    out = [sum(a[i][j] for i in range(x1 - 1, x2) for j in range(y1 - 1, y2))
           for x1, y1, x2, y2 in qs]
    _cases.append((_text([n, m, len(qs)], *a, *qs), _text(*out)))
_add(37, '二维前缀和：矩形总分',
     '二维前缀和 P[i][j] 表示左上角到 (i,j) 的矩形和。两个方向分别做容斥，用额外的第 0 行与第 0 列处理边界。',
     'p = [[0] * (m + 1) for _ in range(n + 1)]\nvalue = p[x2][y2] - p[x1-1][y2] - p[x2][y1-1] + p[x1-1][y1-1]',
     '输入 n m q（1≤n,m≤400，1≤q≤20000），随后 n×m 个绝对值≤10^9 的整数，再给 q 行 x1 y1 x2 y2，均为从 1 开始的合法闭矩形端点。每个查询输出矩形内元素之和。',
     _cases, r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
n, m, q = next(it), next(it), next(it)
p = [[0] * (m + 1) for _ in range(n + 1)]
for i in range(1, n + 1):
    for j in range(1, m + 1):
        p[i][j] = next(it) + p[i - 1][j] + p[i][j - 1] - p[i - 1][j - 1]
for _ in range(q):
    x1, y1, x2, y2 = (next(it) for _ in range(4))
    print(p[x2][y2] - p[x1 - 1][y2] - p[x2][y1 - 1] + p[x1 - 1][y1 - 1])
''',
     ['不要使用 [[0]*m]*n，多行会共享列表。', '建表时减去重复统计的左上矩形。', '查询时减上、减左，再加回左上交集。'],
     '前缀建表和查询都应用容斥，目标格子最终系数为 1，其余为 0。易错点是忘记查询公式末尾的加号。',
     'O(nm + q)', 'O(nm)', '进阶')

_cases = []
for n, m, rects in [
    (3, 3, [(1, 1, 2, 2), (2, 2, 3, 3)]), (2, 4, [(1, 1, 2, 4)]),
    (1, 1, []), (1, 1, [(1, 1, 1, 1)] * 4),
    (4, 4, [(1, 1, 1, 4), (4, 1, 4, 4)]),
    (5, 5, [(i, i, 5, 5) for i in range(1, 6)]),
    (3, 4, [(1, 2, 3, 2), (2, 1, 2, 4)]),
    (12, 13, [(1, i, 12, i + 3) for i in range(1, 11)]),
]:
    cover = [[sum(x1 <= i <= x2 and y1 <= j <= y2 for x1, y1, x2, y2 in rects)
              for j in range(1, m + 1)] for i in range(1, n + 1)]
    best = max(map(max, cover))
    count = sum(x == best for row in cover for x in row)
    _cases.append(_case([[n, m, len(rects)], *rects], [best, count]))
_add(37, '二维差分：叠加矩形涂色',
     '差分把一次矩形更新压缩为四个角的增减。全部更新完成后求二维前缀和，即可恢复每格覆盖次数。',
     'd[x1][y1] += 1\nd[x2+1][y1] -= 1\nd[x1][y2+1] -= 1\nd[x2+1][y2+1] += 1',
     '输入 n m k（1≤n,m≤400，0≤k≤100000），初始 n×m 网格全为 0。随后 k 行 x1 y1 x2 y2，把合法的 1 基闭矩形每格加 1。输出最大覆盖次数，以及达到该次数的格子数。k=0 时最大值为 0、格子数为 nm。',
     _cases, r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
n, m, k = next(it), next(it), next(it)
d = [[0] * (m + 2) for _ in range(n + 2)]
for _ in range(k):
    x1, y1, x2, y2 = (next(it) for _ in range(4))
    d[x1][y1] += 1
    d[x2 + 1][y1] -= 1
    d[x1][y2 + 1] -= 1
    d[x2 + 1][y2 + 1] += 1
best, count = -1, 0
for i in range(1, n + 1):
    for j in range(1, m + 1):
        d[i][j] += d[i - 1][j] + d[i][j - 1] - d[i - 1][j - 1]
        if d[i][j] > best:
            best, count = d[i][j], 1
        elif d[i][j] == best:
            count += 1
print(best, count)
''',
     ['为 x2+1、y2+1 预留空间。', '四个角的符号为 +、-、-、+。', '只统计真实网格，不统计额外边界。'],
     '四角操作经二维前缀累加后，在目标矩形内贡献 1，矩形外相互抵消；线性叠加即可恢复全部更新。易错点是把 r+1 写成 r。',
     'O(nm + k)', 'O(nm)', '进阶')

_cases = []
for intervals in [
    [(1, 4), (2, 5), (4, 6)], [(0, 1), (1, 2)], [], [(9, 10)],
    [(1, 3)] * 5, [(0, 10), (2, 8), (4, 6)],
    [(-10, -2), (-2, 0), (-5, 5)], [(i, i + 7) for i in range(40)],
]:
    expected = max((sum(l <= t < r for l, r in intervals) for t in
                    [x for interval in intervals for x in interval]), default=0)
    _cases.append(_case([len(intervals), *intervals], expected))
_add(37, '扫描线：半开区间的资源峰值',
     '将开始和结束变成事件，排序后扫描。区间为 [start,end)，同一时刻的结束必须先于开始，这样资源可以立即复用。',
     'events.append((start, 1))\nevents.append((end, -1))\nevents.sort()',
     '输入 n（0≤n≤100000），随后 n 行 start end，-10^9≤start<end≤10^9。每项任务在半开区间 [start,end) 占用一份资源。输出任意时刻同时运行的任务数最大值；n=0 输出 0。',
     _cases, r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
events = []
for _ in range(next(it)):
    l, r = next(it), next(it)
    events.extend(((l, 1), (r, -1)))
active = best = 0
for _, delta in sorted(events):
    active += delta
    best = max(best, active)
print(best)
''',
     ['每个任务创建两个事件。', '元组排序会把同刻的 -1 排在 +1 前。', '沿时间更新 active 并维护最大值。'],
     '最大并发只可能在开始事件后出现；结束先处理使首尾相接的任务不重叠。易错点是把半开区间当成闭区间。',
     'O(n log n)', 'O(n)', '进阶')

_cases = []
for n, k in [(5, 2), (7, 3), (1, 1), (4, 1), (6, 6), (9, 13), (20, 2), (35, 97)]:
    alive, index, order = list(range(1, n + 1)), 0, []
    while alive:
        index = (index + k - 1) % len(alive)
        order.append(alive.pop(index))
    _cases.append(_case([[n, k]], order))
_add(37, '循环淘汰：约瑟夫队列',
     '队列旋转可以表示循环报数。每轮把前 k-1 个位置移到末尾，然后弹出当前队首；人数变少后先取模，避免无谓旋转。',
     'from collections import deque\nqueue.rotate(-steps)\nremoved = queue.popleft()',
     '输入 n k（1≤n≤3000，1≤k≤10^9）。编号 1～n 围成环，从 1 开始报数，报到 k 的人出列，下一人重新从 1 报数，直到全部出列。输出一行出列顺序。',
     _cases, r'''
from collections import deque
n, k = map(int, sys.stdin.buffer.read().split())
queue = deque(range(1, n + 1))
answer = []
while queue:
    queue.rotate(-((k - 1) % len(queue)))
    answer.append(queue.popleft())
print(*answer)
''',
     ['数到 k 的位置前有 k-1 个人。', 'rotate 的负数表示向左旋转。', '每轮长度不同，必须重新取模。'],
     '旋转跳过 k-1 个仍在场的人，弹出的队首就是第 k 人，剩余队首正是下一轮起点。易错点是偏移写成 k。本题允许二次复杂度；大规模只求最后幸存者时可另用递推。',
     'O(n²) 最坏情况', 'O(n)', '进阶')

_tasks = [
    [(3, 4), (2, 5), (4, 6)], [(5, 2), (1, 1)], [], [(1, 1)] * 5,
    [(2, 2), (2, 4), (2, 6)], [(10, 10), (3, 11), (3, 12), (3, 13)],
    [(1, 100), (10, 100), (30, 100), (60, 100)],
    [(i % 4 + 1, i + 2) for i in range(10)],
]
_cases = []
for tasks in _tasks:
    best = 0
    for mask in range(1 << len(tasks)):
        chosen = sorted((tasks[i] for i in range(len(tasks)) if mask >> i & 1),
                        key=lambda t: t[1])
        elapsed = 0
        for duration, deadline in chosen:
            elapsed += duration
            if elapsed > deadline:
                break
        else:
            best = max(best, len(chosen))
    _cases.append(_case([len(tasks), *tasks], best))
_add(37, '截止日期：用堆撤回最长任务',
     '按截止日期排序，暂时选入每个任务；一旦超时，撤回当前集合中耗时最长的任务。最大堆在 Python 中可通过存负数实现。',
     'import heapq\nheapq.heappush(heap, -duration)\nelapsed += heapq.heappop(heap)',
     '输入 n（0≤n≤100000），随后 n 行 duration deadline（均为 1～10^9）。单机从时刻 0 开始，任务不可打断，可任意排序或放弃；完成时间≤deadline 才有效。输出最多能完成的任务数。',
     _cases, r'''
import heapq
it = iter(map(int, sys.stdin.buffer.read().split()))
tasks = [(next(it), next(it)) for _ in range(next(it))]
heap, elapsed = [], 0
for duration, deadline in sorted(tasks, key=lambda t: t[1]):
    elapsed += duration
    heapq.heappush(heap, -duration)
    if elapsed > deadline:
        elapsed += heapq.heappop(heap)
print(len(heap))
''',
     ['先按截止日期排序。', '超时时移除最长任务，给后面留下最多时间。', '最小负数对应最大耗时。'],
     '按截止日期排列可检测集合可行性。超时时移除最长任务，在相同数量的方案中尽量减少耗时；交换论证表明不会妨碍未来获得更多任务。易错点是只丢弃当前任务，错过替换更长旧任务的机会。',
     'O(n log n)', 'O(n)')


# Chapter 38: range data structures. Direct list operations are test oracles.
_arrays = [[2, -1, 4, 3], [0, 5], [7], [0] * 7, [-9, -2, -8, -1],
           [10**9, -10**9, 10**9], list(range(15)),
           [_rng.randrange(-100, 101) for _ in range(180)]]


def _operation_cases(kind):
    cases = []
    for original in _arrays:
        n, a = len(original), original[:]
        operations, out = [], []
        for step in range(18):
            l = 1 if step == 0 else _rng.randrange(1, n + 1)
            r = n if step == 0 else _rng.randrange(l, n + 1)
            if step % 3 == 1:
                delta = _rng.randrange(-15, 16)
                if kind in ('point_sum', 'set_max'):
                    operations.append((1, l, delta))
                    a[l - 1] = delta if kind == 'set_max' else a[l - 1] + delta
                else:
                    operations.append((1, l, r, delta))
                    for i in range(l - 1, r):
                        a[i] += delta
            elif kind == 'range_point':
                operations.append((2, l))
                out.append(a[l - 1])
            else:
                operations.append((2, l, r))
                out.append(max(a[l - 1:r]) if kind == 'set_max' else
                           min(a[l - 1:r]) if kind == 'range_min' else sum(a[l - 1:r]))
        cases.append((_text([n, len(operations)], original, *operations), _text(*out)))
    return cases


_BIT = r'''
bit = [0] * (n + 1)
def add(i, value):
    while i <= n:
        bit[i] += value
        i += i & -i
def prefix(i):
    total = 0
    while i > 0:
        total += bit[i]
        i -= i & -i
    return total
'''
_range_input = ('输入 n q（1≤n,q≤100000），再给 n 个绝对值≤10^9 的初始整数。'
                '接着 q 条操作，所有位置均为从 1 开始的合法下标，l≤r，更新量绝对值≤10^9。')
_add(38, '树状数组：单点增加与区间求和',
     'lowbit(i)=i&-i 提取最低的二进制 1。树状数组的 bit[i] 保存以 i 结尾、长度 lowbit(i) 的区间和；更新向父区间走，查询将前缀拆成互不重叠的块。',
     'i += i & -i  # 更新时向上\ni -= i & -i  # 查询时向左',
     _range_input + '操作 1 i delta 表示 a[i]+=delta；操作 2 l r 查询闭区间和。每次查询输出一行。',
     _operation_cases('point_sum'),
     r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
n, q = next(it), next(it)
''' + _BIT + r'''
for i in range(1, n + 1):
    add(i, next(it))
for _ in range(q):
    op, x, y = next(it), next(it), next(it)
    if op == 1:
        add(x, y)
    else:
        print(prefix(y) - prefix(x - 1))
''',
     ['下标必须从 1 开始，0 的 lowbit 也是 0。', '前缀查询每次清除最低位的 1。', '区间和等于 prefix(r)-prefix(l-1)。'],
     '更新遍历所有包含该点的树状区间；查询选出的区间不重不漏覆盖 [1,i]，因此前缀差得到闭区间和。易错点是对下标 0 调用 add，造成死循环。',
     'O((n+q) log n)', 'O(n)', '进阶')

_add(38, '差分树状数组：区间增加与单点查询',
     '将原数组转换为差分 d[i]=a[i]-a[i-1]。闭区间加 delta 只改变 d[l] 和 d[r+1]；a[i] 是差分的前缀和。',
     'add(l, delta)\nadd(r + 1, -delta)\nvalue = prefix(i)',
     _range_input + '操作 1 l r delta 表示闭区间每个数加 delta；操作 2 i 查询 a[i]。每次查询输出一行。',
     _operation_cases('range_point'),
     r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
n, q = next(it), next(it)
''' + _BIT + r'''
previous = 0
for i in range(1, n + 1):
    value = next(it)
    add(i, value - previous)
    previous = value
for _ in range(q):
    op = next(it)
    if op == 1:
        l, r, value = next(it), next(it), next(it)
        add(l, value)
        add(r + 1, -value)
    else:
        print(prefix(next(it)))
''',
     ['先把初始数组变成相邻差。', 'r=n 时，n+1 的更新可直接忽略。', '查询的是差分前缀，不能再做一次前缀差。'],
     '区间左边界开始增加 delta，右边界之后抵消它，前缀累加便只影响目标区间。易错点是只初始化原值而没有先求差分。',
     'O((n+q) log n)', 'O(n)', '进阶')

_add(38, '双树状数组：区间增加与区间求和',
     '设差分为 d，则前 x 项和为 Σ(x-i+1)d[i]=(x+1)Σd[i]-Σi·d[i]。分别维护 d[i] 和 i·d[i] 两棵树，就能同时支持区间更新与区间查询。',
     'prefix_sum = (x + 1) * query(bit1, x) - query(bit2, x)',
     _range_input + '操作 1 l r delta 表示区间加；操作 2 l r 查询区间和。每次查询输出一行。',
     _operation_cases('range_sum'),
     r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
n, q = next(it), next(it)
b1, b2 = [0] * (n + 1), [0] * (n + 1)
def change(i, value):
    weighted = i * value
    while i <= n:
        b1[i] += value
        b2[i] += weighted
        i += i & -i
def total(x):
    i, s1, s2 = x, 0, 0
    while i:
        s1 += b1[i]
        s2 += b2[i]
        i -= i & -i
    return (x + 1) * s1 - s2
previous = 0
for i in range(1, n + 1):
    value = next(it)
    change(i, value - previous)
    previous = value
for _ in range(q):
    op, l, r = next(it), next(it), next(it)
    if op == 1:
        value = next(it)
        change(l, value)
        change(r + 1, -value)
    else:
        print(total(r) - total(l - 1))
''',
     ['画出一个差分项对多少个前缀元素有贡献。', '第二棵树存的是原始位置 i 乘增量。', '更新循环中 i 在变化，weighted 必须提前计算。'],
     '交换求和顺序后每项 d[i] 出现 x-i+1 次，双树公式就是这一恒等式。边界差分更新保持等式有效。易错点是用树状数组循环中的新 i 计算加权增量。',
     'O((n+q) log n)', 'O(n)')

_cases = [_case([len(a), a], sum(a[i] > a[j] for i in range(len(a))
                               for j in range(i + 1, len(a)))) for a in _arrays]
_add(38, '离散化与树状数组：严格逆序对',
     '数值可能很大，只需保留大小关系即可离散化。从左到右扫描，已见元素数减去≤当前值的数量，就是以当前位置为右端点的严格逆序对。',
     'rank = {value: i + 1 for i, value in enumerate(sorted(set(a)))}',
     '输入 n（1≤n≤100000）及 n 个绝对值≤10^9 的整数。输出满足 i<j 且 a[i]>a[j] 的下标对数量。相等元素不算逆序对。',
     _cases, r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
length = next(it)
a = [next(it) for _ in range(length)]
rank = {x: i + 1 for i, x in enumerate(sorted(set(a)))}
n = len(rank)
''' + _BIT + r'''
answer = 0
for seen, value in enumerate(a):
    r = rank[value]
    answer += seen - prefix(r)
    add(r, 1)
print(answer)
''',
     ['相等数值必须映射到同一个排名。', '查询已出现且≤当前值的数量。', '先查询再插入当前值，避免把自己统计进去。'],
     '每对逆序对在右端点被访问时恰好计入一次。离散化保持严格大小关系，prefix(rank) 包含相等项，因此不会误计重复值。易错点是查询 rank-1 后相减，把相等也计入。',
     'O(n log n)', 'O(n)')

_cases = []
for base in [[1, 2, 0, 1], [0, 3], [1], [2] * 6, [0, 0, 5],
             [1, 0, 0, 0, 1], [3, 1, 4, 1, 5], [i % 4 for i in range(80)]]:
    a, ops, out = base[:], [], []
    for step in range(12):
        if step % 3 == 1:
            i, delta = _rng.randrange(len(a)), _rng.randrange(1, 5)
            ops.append((1, i + 1, delta))
            a[i] += delta
        else:
            k = 1 if step == 0 else sum(a) if step == 2 else _rng.randrange(1, sum(a) + 1)
            ops.append((2, k))
            expanded = [i + 1 for i, count in enumerate(a) for _ in range(count)]
            out.append(expanded[k - 1])
    _cases.append((_text([len(base), len(ops)], base, *ops), _text(*out)))
_add(38, '树状数组倍增：寻找第 k 个元素',
     '非负频次的前缀和单调。直接在树状数组中按二进制位试探最大前缀，使其累计数量仍小于 k；答案是该前缀的下一个位置。',
     'step = 1 << (n.bit_length() - 1)\nif candidate <= n and bit[candidate] < k:\n    k -= bit[candidate]\n    index = candidate',
     '输入 n q（1≤n,q≤100000），再给 n 个 0～10^6 的频次，总频次至少 1。操作 1 i delta 将频次增加 delta（1≤delta≤10^6）；操作 2 k 查询按值从小到大排列的多重集合中第 k 个元素的值（即下标）。保证 1≤k≤当前总频次。每次查询输出一行下标。',
     _cases, r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
n, q = next(it), next(it)
''' + _BIT + r'''
for i in range(1, n + 1):
    add(i, next(it))
for _ in range(q):
    op = next(it)
    if op == 1:
        add(next(it), next(it))
    else:
        k, index = next(it), 0
        step = 1 << (n.bit_length() - 1)
        while step:
            candidate = index + step
            if candidate <= n and bit[candidate] < k:
                index = candidate
                k -= bit[candidate]
            step >>= 1
        print(index + 1)
''',
     ['频次非负，才能用前缀单调性。', '寻找的是累计数量严格小于 k 的最长前缀。', '跳过一个块时，k 同时减去该块频次。'],
     '倍增从高位到低位确定可跳过的前缀长度；每次跳过的块总频次小于剩余排名，故第 k 个元素不在该块。结束时下一位置必覆盖剩余排名。易错点是把条件写成≤k。',
     'O((n+q) log n)', 'O(n)')

_add(38, '迭代线段树：单点赋值与区间最大值',
     '线段树叶子存元素，父节点合并两个孩子的最大值。把查询变为半开区间 [l,r)，当端点落在完整右孩子或左孩子边界时取出该块。',
     'while l < r:\n    if l & 1:\n        answer = max(answer, tree[l])\n        l += 1\n    l //= 2\n    r //= 2',
     _range_input + '操作 1 i value 将 a[i] 直接赋值为 value；操作 2 l r 输出闭区间最大值。全负数组也必须正确处理。',
     _operation_cases('set_max'), r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
n, q = next(it), next(it)
size = 1
while size < n:
    size *= 2
tree = [float('-inf')] * (2 * size)
for i in range(n):
    tree[size + i] = next(it)
for i in range(size - 1, 0, -1):
    tree[i] = max(tree[2 * i], tree[2 * i + 1])
for _ in range(q):
    op, x, y = next(it), next(it), next(it)
    if op == 1:
        p = size + x - 1
        tree[p] = y
        p //= 2
        while p:
            tree[p] = max(tree[2 * p], tree[2 * p + 1])
            p //= 2
    else:
        l, r = size + x - 1, size + y
        answer = float('-inf')
        while l < r:
            if l & 1:
                answer = max(answer, tree[l])
                l += 1
            if r & 1:
                r -= 1
                answer = max(answer, tree[r])
            l //= 2
            r //= 2
        print(answer)
''',
     ['补齐叶子使用负无穷，不能用 0。', '赋值后只更新从该叶子到根的路径。', '1 基闭区间 [x,y] 对应叶子半开区间 [size+x-1,size+y)。'],
     '每个父节点始终是其覆盖区间的最大值；查询逐层取出不重叠的完整块，最终覆盖原区间。易错点是用 0 初始化答案，使全负区间出错。',
     'O(n + q log n)', 'O(n)')

_add(38, '懒标记线段树：区间增加与区间最小值',
     '整段统一加 v 会使最小值也加 v。懒标记记录尚未下传的增量；只有继续访问孩子时才下传，避免逐个修改叶子。',
     'minimum[node] += delta\nlazy[node] += delta',
     _range_input + '操作 1 l r delta 表示闭区间加；操作 2 l r 查询闭区间最小值。每次查询输出一行。',
     _operation_cases('range_min'), r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
n, q = next(it), next(it)
a = [next(it) for _ in range(n)]
tree, lazy = [0] * (4 * n), [0] * (4 * n)
def build(p, l, r):
    if l == r:
        tree[p] = a[l - 1]
        return
    m = (l + r) // 2
    build(p * 2, l, m)
    build(p * 2 + 1, m + 1, r)
    tree[p] = min(tree[p * 2], tree[p * 2 + 1])
def push(p):
    for child in (p * 2, p * 2 + 1):
        tree[child] += lazy[p]
        lazy[child] += lazy[p]
    lazy[p] = 0
def update(p, l, r, x, y, v):
    if x <= l and r <= y:
        tree[p] += v
        lazy[p] += v
        return
    push(p)
    m = (l + r) // 2
    if x <= m:
        update(p * 2, l, m, x, y, v)
    if y > m:
        update(p * 2 + 1, m + 1, r, x, y, v)
    tree[p] = min(tree[p * 2], tree[p * 2 + 1])
def query(p, l, r, x, y):
    if x <= l and r <= y:
        return tree[p]
    push(p)
    m, result = (l + r) // 2, float('inf')
    if x <= m:
        result = min(result, query(p * 2, l, m, x, y))
    if y > m:
        result = min(result, query(p * 2 + 1, m + 1, r, x, y))
    return result
build(1, 1, n)
for _ in range(q):
    op, l, r = next(it), next(it), next(it)
    if op == 1:
        update(1, 1, n, l, r, next(it))
    else:
        print(query(1, 1, n, l, r))
''',
     ['节点最小值立即更新，lazy 只表示孩子尚未接收的增量。', '访问部分区间前先下传。', '更新孩子后重新取两个孩子的最小值。'],
     '节点值始终包含其整段已收到的全部更新；标记下传不会改变真实数组，只使孩子与父节点一致。分解查询仍覆盖原区间。易错点是下传后忘记清零父标记，导致重复添加。',
     'O(n + q log n)', 'O(n)')

_cases = []
for a in _arrays:
    a = [abs(x) for x in a]
    n = len(a)
    qs = [(1, n), (1, 1), (n, n)] + [
        (i, min(n, i + 3)) for i in range(1, n + 1, max(1, n // 5))]
    answers = []
    for l, r in qs:
        value = 0
        for x in a[l - 1:r]:
            value = gcd(value, x)
        answers.append(value)
    _cases.append((_text([n, len(qs)], a, *qs), _text(*answers)))
_add(38, '稀疏表：静态区间最大公约数',
     '稀疏表预处理长度为 2 的幂的区间。gcd 是幂等运算，重复覆盖不改变答案，因此任意查询可由两个允许重叠的等长区间合并。',
     'k = (r - l + 1).bit_length() - 1\nanswer = gcd(st[k][l], st[k][r - (1 << k) + 1])',
     '输入 n q（1≤n≤100000，1≤q≤100000），再给 n 个 0～10^9 的整数，随后 q 行合法 1 基闭区间 l r。数组不修改，每次输出区间所有元素的 gcd，gcd(0,0)=0。',
     _cases, r'''
from math import gcd
it = iter(map(int, sys.stdin.buffer.read().split()))
n, q = next(it), next(it)
st = [[next(it) for _ in range(n)]]
power = 1
while 2 * power <= n:
    previous = st[-1]
    st.append([gcd(previous[i], previous[i + power]) for i in range(n - 2 * power + 1)])
    power *= 2
for _ in range(q):
    l, r = next(it) - 1, next(it) - 1
    k = (r - l + 1).bit_length() - 1
    print(gcd(st[k][l], st[k][r - (1 << k) + 1]))
''',
     ['第 k 层保存长度 2^k 的区间。', '长度的 bit_length()-1 就是 floor(log2(length))。', '两个区间可能重叠；gcd 可以重叠，求和则不可以。'],
     '两个最长二次幂区间覆盖整个查询范围，重复元素对 gcd 无影响，故合并结果正确。易错点是把同样的双块方法直接用于区间和。',
     'O(n log n + q)，按单次 gcd 为整数机器运算计', 'O(n log n)')

_cases = []
for a in _arrays:
    n = len(a)
    qs = [(1, n, 0), (1, n, max(a)), (1, 1, a[0] - 1)] + [
        (1, i, a[i - 1]) for i in range(1, n + 1, max(1, n // 5))]
    _cases.append((_text([n, len(qs)], a, *qs),
                   _text(*(sum(x <= k for x in a[l - 1:r]) for l, r, k in qs))))
_add(38, '离线查询：区间内不超过阈值的数量',
     '查询之间没有依赖时，可以调整处理顺序。把元素按值排序、查询按阈值排序；逐步激活值≤k 的位置，用树状数组回答位置区间计数。',
     'queries.sort(key=lambda row: row[2])\nanswer[original_index] = prefix(r) - prefix(l - 1)',
     '输入 n q（1≤n,q≤100000），再给 n 个绝对值≤10^9 的整数，随后 q 行 l r k，1≤l≤r≤n，|k|≤10^9。每行查询区间 [l,r] 中≤k 的元素数，按原查询顺序输出。',
     _cases, r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
n, q = next(it), next(it)
items = sorted((next(it), i) for i in range(1, n + 1))
queries = [(next(it), next(it), next(it), j) for j in range(q)]
''' + _BIT + r'''
answers, pos = [0] * q, 0
for l, r, k, index in sorted(queries, key=lambda row: row[2]):
    while pos < n and items[pos][0] <= k:
        add(items[pos][1], 1)
        pos += 1
    answers[index] = prefix(r) - prefix(l - 1)
print(*answers, sep='\n')
''',
     ['排序元素时保留它在原数组中的位置。', '处理阈值 k 前激活全部≤k 的元素。', '查询也保存原编号，最后恢复输出顺序。'],
     '每次查询时树中恰好标记所有符合阈值条件的位置，区间和即所求数量。阈值单调使每个元素只需激活一次。易错点是用<k而遗漏相等元素。',
     'O((n+q) log(n+q))', 'O(n+q)')

_cases = []
for a in _arrays:
    n = len(a)
    qs = [(1, n), (1, 1), (n, n), (1, n)] + [
        (i, min(n, i + 6)) for i in range(1, n + 1, max(1, n // 6))]
    _cases.append((_text([n, len(qs)], a, *qs),
                   _text(*(len(set(a[l - 1:r])) for l, r in qs))))
_add(38, '莫队算法：区间不同值的个数',
     '莫队维护一个可增删两端的当前区间。左端点按块排序，块内右端点交替升降；移动一步只改变一个数的频次，频次跨过 0 时更新种类数。',
     'block = max(1, isqrt(n))\nqueries.sort(key=lambda q: (q[0] // block, q[1] if q[0] // block % 2 == 0 else -q[1]))',
     '输入 n q（1≤n,q≤20000），再给 n 个绝对值≤10^9 的整数，随后 q 行合法 1 基闭区间 l r。数组不修改。按原顺序输出每个区间内不同整数的数量。',
     _cases, r'''
from math import isqrt
it = iter(map(int, sys.stdin.buffer.read().split()))
n, q = next(it), next(it)
a = [next(it) for _ in range(n)]
queries = [(next(it) - 1, next(it) - 1, i) for i in range(q)]
block = max(1, isqrt(n))
queries.sort(key=lambda row: (row[0] // block, row[1] if row[0] // block % 2 == 0 else -row[1]))
freq, distinct = {}, 0
def change(index, delta):
    nonlocal distinct
    x = a[index]
    before = freq.get(x, 0)
    after = before + delta
    distinct += (after > 0) - (before > 0)
    freq[x] = after
l, r, answers = 0, -1, [0] * q
for x, y, index in queries:
    while l > x:
        l -= 1
        change(l, 1)
    while r < y:
        r += 1
        change(r, 1)
    while l < x:
        change(l, -1)
        l += 1
    while r > y:
        change(r, -1)
        r -= 1
    answers[index] = distinct
print(*answers, sep='\n')
''',
     ['初始空区间可表示为 l=0、r=-1。', '先扩张后收缩，避免短暂删除尚未加入的元素。', 'nonlocal 允许嵌套函数更新 main 的 distinct。'],
     '每次移动都同步调整唯一被增删元素的频次，故计数始终对应当前区间。分块排序只改变处理顺序，不改变结果；排序控制指针总移动量。易错点是频次从 2 降到 1 时错误减少种类数。',
     'O((n+q)√n + q log q)', 'O(n+q)')


# Keep long lessons in focused modules while exposing one complete ACM track.
from .competitive_graph_dp import PROBLEMS as _GRAPH_DP_PROBLEMS
from .competitive_strings_math import PROBLEMS as _STRINGS_MATH_PROBLEMS

PROBLEMS.extend(_GRAPH_DP_PROBLEMS)
PROBLEMS.extend(_STRINGS_MATH_PROBLEMS)
