"""Chapters 19–24: exam-style input, data structures, and algorithms."""

from .schema import problem

PROBLEMS = []
_counts = {}


def add(chapter, title, lesson, syntax, task, params, tests, body, hints, why,
        difficulty='进阶'):
    _counts[chapter] = _counts.get(chapter, 0) + 1
    names = ', '.join(p[0] for p in params)
    code = 'def solve(' + names + '):\n' + '\n'.join(
        '    ' + line if line else '' for line in body.strip().splitlines())
    PROBLEMS.append(problem(
        chapter, _counts[chapter], title,
        lesson + '\n\n```python\n' + syntax + '\n```', task, params,
        tests, code, hints, why, difficulty=difficulty))


# 19 — Input formats and cost models, before more involved algorithms.
add(19, '读到 EOF：多组两数之和',
    '机考常用 sys.stdin.read() 一次读取全部标准输入。本平台把同样的文本作为 text 参数传入，练习解析逻辑即可。split() 会把连续空格、换行和制表符统一视为分隔符；int 把字符串转成整数。将多行答案先放入列表，再用换行符连接。',
    'tokens = text.split()\nnumbers = list(map(int, tokens))\noutput = "\\n".join(["3", "7"])',
    'text 含 0～200 个整数，每连续两个整数是一组，保证总数为偶数。逐组求和，返回每组答案各占一行的字符串，末尾不加换行。允许负数和任意空白；空输入返回空字符串。不要调用 input()，不要用 print 代替 return。',
    [('text', 'str', '模拟整个标准输入')],
    [(['1 2\n3 4\n'], '3\n7'), (['-3 8\n0 0'], '5\n0'), ([''], ''),
     ([' \n\t '], ''), ([' 10\t-10\n2  5\n'], '0\n7')],
    '''nums = list(map(int, text.split()))
answers = []
for i in range(0, len(nums), 2):
    answers.append(str(nums[i] + nums[i + 1]))
return "\\n".join(answers)''',
    ['先把文本转成整数列表，不要假设每行恰好有两个数。', 'range(0, len(nums), 2) 每次指向一组的第一个数。', '将每组之和转成 str，最后用 "\\n".join(answers) 返回。'],
    '按两个一组扫描全部整数。join 只在相邻答案间添加换行，因此不会产生尾随换行。设输入长度为 L，时间 O(L)，空间 O(L)。', '基础')

add(19, '先读 T：变长数组求和',
    '带组数的输入通常先给 T，之后每组先给 n，再给 n 个数据。维护游标 pos，始终指向下一个还没读取的 token；切片 nums[pos:pos+n] 不包含右端点。',
    'n = nums[pos]\npos += 1\nvalues = nums[pos:pos + n]\npos += n',
    'text 的第一个整数是组数 T（0～30）；每组依次包含 n 和 n 个整数，0≤n≤100。返回 T 行数组元素和，空数组和为 0，末尾无换行。保证 token 数量与声明一致，换行位置任意。T=0 返回空字符串。',
    [('text', 'str', '含组数和各组长度的合法输入')],
    [(['2\n3 1 2 3\n2 -4 9'], '6\n5'), (['3\n0\n1 7\n2 0 0'], '0\n7\n0'),
     (['0'], ''), (['1 1 -8'], '-8'), (['2 2 -1 -2 3 5 5 5'], '-3\n15')],
    '''nums = list(map(int, text.split()))
pos = 1
answers = []
for _ in range(nums[0]):
    n = nums[pos]
    pos += 1
    answers.append(str(sum(nums[pos:pos + n])))
    pos += n
return "\\n".join(answers)''',
    ['第一个数是 T，不是第一组的数组长度。', '每组先消耗一个长度 token，再消耗 n 个数据 token。', '将 pos 初始设为 1；处理一组后游标推进到下一组的 n。'],
    '游标把变长记录串联起来，n=0 时切片为空但长度 token 仍然被消耗。输入总长度 L，时间 O(L)，空间 O(L)。', '基础')

add(19, '遇到 0 0：终止符输入',
    'break 只结束最近的一层循环。哨兵输入把某个特殊记录作为结束标志，它自身不产生答案。条件 a == 0 and b == 0 要求两个数同时为零。',
    'if a == 0 and b == 0:\n    break\nanswers.append(str(a + b))',
    'text 含偶数个整数，每两个一组。返回各组之和，每行一个；遇到第一组 0 0 时停止，该组及之后数据忽略。没有终止符则处理到末尾。单独一个数为 0 不终止。空输入返回空字符串，末尾不加换行；最多 100 组。',
    [('text', 'str', '由整数对组成的文本')],
    [(['1 2\n0 0\n8 9'], '3'), (['0 5\n4 0\n0 0'], '5\n4'),
     (['0 0'], ''), ([''], ''), (['-2 -3\n1 -1'], '-5\n0')],
    '''nums = list(map(int, text.split()))
answers = []
for i in range(0, len(nums), 2):
    a, b = nums[i:i + 2]
    if a == 0 and b == 0:
        break
    answers.append(str(a + b))
return "\\n".join(answers)''',
    ['在记录答案之前判断终止符。', '应使用 and，不能写成只要任意一个数为 0 就停止。', '循环步长设为 2；遇到 (0, 0) 执行 break，循环后统一 join。'],
    '先识别控制记录，再处理普通数据。因为 read/split 已读取全部文本，设完整输入长度为 L，总时间和空间仍为 O(L)，即使终止符较早出现。', '基础')

add(19, '矩阵输入：逐行求和',
    '矩阵可以按行存入一维 token 列表。若头部占两个 token，第 r 行从 2 + r * cols 开始。行号从 0 开始；零列矩阵的每一行都是空行，其和为 0。',
    'start = 2 + r * cols\nrow = numbers[start:start + cols]',
    'text 先给 rows 和 cols（均为 0～20），随后给 rows*cols 个整数，按行排列。返回 rows 行行和，末尾无换行。rows=0 返回空字符串；cols=0 时每行结果为 0。保证输入合法，不能依赖实际换行分行。',
    [('text', 'str', '行列数及矩阵元素')],
    [(['2 3\n1 2 3\n4 5 6'], '6\n15'), (['3 0'], '0\n0\n0'),
     (['0 4'], ''), (['1 3 -2 0 7'], '5'), (['2 1 9 -9'], '9\n-9')],
    '''nums = list(map(int, text.split()))
rows, cols = nums[:2]
answers = []
for r in range(rows):
    start = 2 + r * cols
    answers.append(str(sum(nums[start:start + cols])))
return "\\n".join(answers)''',
    ['先读行列数，后面的整数才属于矩阵。', '第 r 行有 cols 个元素，起点是 2 + r*cols。', '即使 cols 为 0，也要为每个 r 添加字符串 "0"。'],
    '行起点公式把二维下标映射到一维位置。按整数个数计，时间和空间为 O(rows*cols + rows + 1)；字符串解析另外与输入字符数成正比。', '基础')

add(19, '前缀和：批量区间查询',
    'prefix[i] 表示前 i 个元素的和，prefix[0]=0。这样原数组闭区间 [l,r]（从 1 编号）的和是 prefix[r]-prefix[l-1]。一次预处理后，每个查询只做一次减法。',
    'prefix = [0]\nfor x in values:\n    prefix.append(prefix[-1] + x)\nanswer = prefix[r] - prefix[l - 1]',
    'text 依次给 n、q、n 个整数及 q 对 l r。每对表示从 1 开始的闭区间，满足 1≤l≤r≤n。返回 q 行区间和，无末尾换行。0≤n,q≤200；n=0 时保证 q=0。要求预处理 O(n)、每次查询 O(1)。',
    [('text', 'str', '数组和区间查询的完整输入')],
    [(['5 3\n1 2 3 4 5\n1 3\n2 5\n4 4'], '6\n14\n4'),
     (['3 2 -2 0 7 1 3 2 2'], '5\n0'), (['0 0'], ''),
     (['1 2 9 1 1 1 1'], '9\n9'), (['2 0 3 4'], '')],
    '''nums = list(map(int, text.split()))
n, q = nums[:2]
prefix = [0]
for x in nums[2:2 + n]:
    prefix.append(prefix[-1] + x)
answers = []
pos = 2 + n
for _ in range(q):
    left, right = nums[pos:pos + 2]
    answers.append(str(prefix[right] - prefix[left - 1]))
    pos += 2
return "\\n".join(answers)''',
    ['额外保留 prefix[0]=0，避免左边界为 1 时单独分类。', '先累加 n 个数组值，再用游标读取 q 对查询。', '每次答案是 prefix[right]-prefix[left-1]，不要对每个区间重复 sum。'],
    '两个前缀相减，正好消去区间左侧的数据。在整数运算视为 O(1) 的模型下，时间 O(n+q)，空间 O(n+q)；真实文本解析还与字符总数成正比。')

add(19, '读懂嵌套循环：三角形计数',
    '嵌套循环不能只看层数，还要看每层次数。for i in range(n) 内再执行 for j in range(i)，总次数是 0+1+…+(n-1)。识别等差数列可以把模拟转换成公式。',
    'count = 0\nfor i in range(n):\n    for j in range(i):\n        count += 1\n# 总次数可直接用 n * (n - 1) // 2 计算',
    '返回示例双重循环中 count 最终的整数值。0≤n≤10^9，请用公式完成，不能实际执行平方级循环。n 为 0 或 1 时返回 0。',
    [('n', 'int', '外层循环次数')],
    [([4], 6), ([0], 0), ([1], 0), ([10], 45), ([1000000000], 499999999500000000)],
    'return n * (n - 1) // 2',
    ['固定 i 时，内层执行 i 次。', '求和 0+1+…+(n-1)，首尾配对。', '使用 n*(n-1)//2，整数除法保持整数答案。'],
    '模拟需要 Θ(n²) 次计数；等差数列公式在固定宽度整数运算模型下只需 O(1) 时间、O(1) 空间。Python 大整数运算成本与位数有关，本题无需逐次模拟。', '基础')

add(19, '每次翻倍：对数级循环',
    '变量每次乘以 2 时，经过 k 步会从 1 变成 2**k。while 循环次数因此随 n 的对数增长。边界判断是严格小于 n：一旦达到或超过 n 就停止。',
    'value = 1\nsteps = 0\nwhile value < n:\n    value *= 2\n    steps += 1',
    '从 value=1 开始，每次 value*=2，直到 value≥n，返回翻倍次数。1≤n≤10^18。n=1 返回 0；n 是 2 的整数次幂时不要多算一步。',
    [('n', 'int', '希望达到的阈值')],
    [([9], 4), ([8], 3), ([1], 0), ([2], 1), ([1000000000000000000], 60)],
    '''value = 1
steps = 0
while value < n:
    value *= 2
    steps += 1
return steps''',
    ['初始 1 已经满足 n=1，所以计数从 0 开始。', '循环条件写 value < n，每轮同时更新数值和计数。', '9 的变化是 1→2→4→8→16，因此答案为 4。'],
    '返回最小的 k，使 2**k≥n。整数比较避免浮点对数在整幂边界的舍入问题。时间 O(log n)，辅助空间 O(1)（按整数运算模型）。', '基础')

add(19, '辗转相除求最大公约数',
    '欧几里得算法利用 gcd(a,b)=gcd(b,a%b)。当 b=0 时答案为 a。Python 同时赋值会先算右边，a,b=b,a%b 可以安全地交换并更新。',
    'a, b = abs(a), abs(b)\nwhile b:\n    a, b = b, a % b',
    '给定两个整数 a、b（绝对值≤10^9），用辗转相除法返回非负最大公约数。约定 gcd(0,0)=0；一方为 0 时结果是另一方绝对值。不要调用 math.gcd。',
    [('a', 'int', '第一个整数'), ('b', 'int', '第二个整数')],
    [([48, 18], 6), ([-12, 8], 4), ([0, 0], 0), ([0, -7], 7), ([17, 13], 1), ([9, 9], 9)],
    '''a, b = abs(a), abs(b)
while b:
    a, b = b, a % b
return a''',
    ['先用 abs 统一负数情况。', '只要 b 非零，就把数对换成 (b, a%b)。', '循环结束时 b 为 0，a 就是答案，包括 (0,0)。'],
    '取余不会改变共同约数，而第二个数持续减小。固定宽度整数模型下时间 O(log(max(|a|,|b|)+1))，辅助空间 O(1)。', '基础')

add(19, '双指针：有序数组两数之和',
    '双指针把 left 放在最小元素、right 放在最大元素。和偏小时增大 left，和偏大时减小 right。这个方向选择依赖数组已经有序；left<right 保证使用两个不同位置。',
    'left, right = 0, len(nums) - 1\nwhile left < right:\n    total = nums[left] + nums[right]',
    'nums 是非递减整数数组，长度 0～1000，元素绝对值≤10^6。判断是否存在两个不同下标的元素之和等于 target，返回 bool。允许重复值，单个元素不能使用两次。要求 O(n) 时间、O(1) 辅助空间。',
    [('nums', 'list[int]', '已经按升序排列的数组'), ('target', 'int', '目标和')],
    [([[1, 2, 4, 7], 9], True), ([[1, 2, 4], 8], False), ([[], 0], False),
     ([[3], 6], False), ([[3, 3], 6], True), ([[-5, -2, 0, 7], 2], True)],
    '''left, right = 0, len(nums) - 1
while left < right:
    total = nums[left] + nums[right]
    if total == target:
        return True
    if total < target:
        left += 1
    else:
        right -= 1
return False''',
    ['从数组两端开始，避免枚举所有数对。', '总和太小就移动左指针，太大就移动右指针。', '循环必须用 left < right；相遇后已经没有两个不同位置可选。'],
    '和太小时，当前左端点与任何更小右端点都不可能得到目标，因此可以排除左端点；偏大时同理排除右端点。每步缩短区间，时间 O(n)，空间 O(1)。')

add(19, '滑动窗口：固定长度最大和',
    '相邻的长度 k 窗口只差两个元素：去掉旧窗口左端，加上新窗口右端。维护 window_sum 可将每次更新从 O(k) 降到 O(1)。全负数情况下，最大和也可能是负数，不能把答案初始设为 0。',
    'window_sum = sum(nums[:k])\nwindow_sum += nums[i] - nums[i - k]',
    '返回 nums 中连续 k 个元素的最大和。长度 n 为 0～1000，0≤k≤n，整数绝对值≤10^6。约定 k=0 返回 0。要求 O(n) 时间；不能只挑不连续的大元素。',
    [('nums', 'list[int]', '整数数组'), ('k', 'int', '窗口长度')],
    [([[1, 3, -2, 5, 4], 2], 9), ([[-4, -2, -7], 2], -6),
     ([[], 0], 0), ([[3, 1], 0], 0), ([[2, -1, 4], 3], 5), ([[7, 2, 8], 1], 8)],
    '''if k == 0:
    return 0
window_sum = sum(nums[:k])
best = window_sum
for i in range(k, len(nums)):
    window_sum += nums[i] - nums[i - k]
    best = max(best, window_sum)
return best''',
    ['先处理 k=0，再计算第一个实际窗口。', '用第一个窗口和初始化 best，保证全负数正确。', 'i 从 k 开始，加入 nums[i] 并减去 nums[i-k]，每次更新最大值。'],
    '每次窗口右移一格，其和由旧和加减两个元素得到。时间 O(n)；参考代码 nums[:k] 的临时切片占 O(k) 空间，改用索引求初始和可降为 O(1) 辅助空间。')


# 20 — Sorting gives order; binary search exploits that order.
add(20, '冒泡排序：原地交换相邻逆序对',
    '冒泡排序每一趟比较相邻元素。若左边大于右边，就用多重赋值交换它们；一趟结束后，当前未排序部分的最大值已经到达右端。提前一趟没有发生交换，说明整个数组已有序。',
    'for j in range(0, end):\n    if values[j] > values[j + 1]:\n        values[j], values[j + 1] = values[j + 1], values[j]',
    '返回 nums 的升序新列表。nums 长度为 0 到 200，元素为整数；保留重复值和负数，不能修改调用者传入的 nums。空列表和单元素列表直接返回对应的新列表。',
    [('nums', 'list[int]', '待排序的整数列表')],
    [([[3, 1, 2]], [1, 2, 3]), ([[-2, 0, -2]], [-2, -2, 0]),
     ([[]], []), ([[5]], [5]), ([[5, 4, 3, 2, 1]], [1, 2, 3, 4, 5])],
    '''values = nums[:]
for end in range(len(values) - 1, 0, -1):
    swapped = False
    for j in range(end):
        if values[j] > values[j + 1]:
            values[j], values[j + 1] = values[j + 1], values[j]
            swapped = True
    if not swapped:
        break
return values''',
    ['先复制 nums，避免直接改动参数。', '外层从最后一个下标向左缩小，内层只比较到 end。', '记录 swapped；一整趟都没交换时立刻结束。'],
    '每次交换都会把较大的相邻元素向右推进；因此完成一趟后右端元素可不再参与后续比较。最坏和平均时间复杂度为 O(n²)，已排序输入配合提前结束为 O(n)，额外空间 O(n) 用于复制。')

add(20, '归并两个有序数组',
    '两个数组都已升序时，用 i、j 分别指向尚未取出的最小元素。比较 nums1[i] 与 nums2[j]，把较小者追加到结果；某一边耗尽后，另一边剩余元素可整体追加。',
    'while i < len(nums1) and j < len(nums2):\n    if nums1[i] <= nums2[j]:\n        result.append(nums1[i]); i += 1',
    'nums1 和 nums2 均为非递减整数列表，长度各不超过 500。返回包含两者全部元素的非递减新列表；允许空列表、负数和重复值。相等时先取 nums1 的元素，以保持稳定的合并顺序。',
    [('nums1', 'list[int]', '第一条已升序列表'), ('nums2', 'list[int]', '第二条已升序列表')],
    [([[1, 3, 5], [2, 4, 6]], [1, 2, 3, 4, 5, 6]), ([[-2, 2], [-2, 0]], [-2, -2, 0, 2]),
     ([[], []], []), ([[1, 1], [1]], [1, 1, 1]), ([[], [0, 7]], [0, 7])],
    '''i = 0
j = 0
result = []
while i < len(nums1) and j < len(nums2):
    if nums1[i] <= nums2[j]:
        result.append(nums1[i])
        i += 1
    else:
        result.append(nums2[j])
        j += 1
result.extend(nums1[i:])
result.extend(nums2[j:])
return result''',
    ['两个指针都从下标 0 开始。', '每次只移动刚刚放入结果的那一侧指针。', '主循环结束后用 extend 追加尚未耗尽的一侧。'],
    '两个指针只会向右移动，每个输入元素恰好被追加一次。时间复杂度 O(m+n)，结果列表占 O(m+n) 空间；不会重排任一输入列表。')

add(20, '多关键字排序：成绩优先、姓名破同分',
    'sorted(iterable, key=...) 返回新列表。key 可以返回元组，Python 按元组从左到右比较；负的 score 可把“分数高在前”转换为普通升序，姓名保持字典序升序。',
    'ordered = sorted(records, key=lambda row: (-row[1], row[0]))',
    'records 的每项均为 [name, score]：name 是字符串，score 是整数，长度 0 到 200。返回按 score 降序、同分按 name 升序排列的新二维列表；不得修改原 records，也不得把同名同分记录去重。',
    [('records', 'list[list]', '每项为 [姓名, 分数] 的记录列表')],
    [([[['张三', 90], ['李四', 95], ['王五', 90]]], [['李四', 95], ['张三', 90], ['王五', 90]]),
     ([[['b', 1], ['a', 1]]], [['a', 1], ['b', 1]]),
     ([[]], []), ([[['A', -1], ['B', 0]]], [['B', 0], ['A', -1]]),
     ([[['同', 3], ['同', 3], ['甲', 3]]], [['同', 3], ['同', 3], ['甲', 3]])],
    '''return [row[:] for row in sorted(records, key=lambda row: (-row[1], row[0]))]''',
    ['排序键先放分数，再放姓名。', '想让数字降序，可在键中使用负号。', '用 row[:] 复制每一项，结果与输入不共享内部列表。'],
    '键元组先比较 -score，再比较 name，所以规则与题意一致。Python 排序时间复杂度 O(n log n)，复制输出占 O(n) 空间；稳定排序会保留完全同键记录的相对次序。')

add(20, '二分查找：第一个目标下标',
    '二分查找维护一个仍可能含答案的闭区间 [left, right]。命中 target 后不要立即返回，而是记录位置并继续向左缩小，才能得到重复值中的第一个下标。',
    'mid = (left + right) // 2\nif nums[mid] >= target:\n    right = mid - 1\nelse:\n    left = mid + 1',
    'nums 为非递减整数列表，长度 0 到 100000；返回 target 第一次出现的 0 起始下标，若不存在返回 -1。允许重复值、负数和空列表，要求 O(log n) 时间。',
    [('nums', 'list[int]', '非递减整数列表'), ('target', 'int', '要查找的值')],
    [([[1, 2, 2, 2, 5], 2], 1), ([[1, 3, 5], 4], -1),
     ([[], 1], -1), ([[7], 7], 0), ([[-3, -3, 0], -3], 0)],
    '''left = 0
right = len(nums) - 1
answer = -1
while left <= right:
    mid = (left + right) // 2
    if nums[mid] >= target:
        if nums[mid] == target:
            answer = mid
        right = mid - 1
    else:
        left = mid + 1
return answer''',
    ['使用闭区间时，循环条件是 left <= right。', '遇到 target 先保存 mid，但仍要向左找。', 'nums[mid] 小于 target 才能安全地令 left = mid + 1。'],
    '当中点值大于等于目标时，第一个目标只能在中点或左侧；记录命中后继续排除右侧。搜索区间每轮至少减半，时间复杂度 O(log n)，额外空间 O(1)。')

add(20, '下界：保持有序的插入位置',
    '下界 lower bound 是第一个“大于或等于 target”的位置。采用左闭右开区间 [left, right)，right 可以等于 len(nums)，因此结果也允许是列表末尾。',
    'left, right = 0, len(nums)\nwhile left < right:\n    mid = (left + right) // 2',
    'nums 为非递减整数列表，长度 0 到 100000。返回将 target 插入后仍保持非递减顺序的最小下标，也就是 target 已存在时最左一次出现的位置；空列表返回 0。',
    [('nums', 'list[int]', '非递减整数列表'), ('target', 'int', '待插入的整数')],
    [([[1, 3, 5], 4], 2), ([[1, 2, 2, 4], 2], 1),
     ([[], 9], 0), ([[2, 3], 1], 0), ([[2, 3], 9], 2)],
    '''left = 0
right = len(nums)
while left < right:
    mid = (left + right) // 2
    if nums[mid] < target:
        left = mid + 1
    else:
        right = mid
return left''',
    ['右边界初值是 len(nums)，不是最后一个下标。', '只有严格小于 target 的中点可以被排除到左边。', '循环结束时 left 与 right 相等，left 就是插入点。'],
    '区间始终保存可能的插入位置；小于目标的元素不可能是答案，其他元素保留在右半区。时间复杂度 O(log n)，额外空间 O(1)。')

add(20, '二分答案：整数平方根',
    '当答案单调时也能二分。对非负 x，若 mid * mid <= x，则 mid 及其左侧都可行；继续寻找更大的可行值。Python 整数没有溢出，但在固定宽度语言里通常比较 mid <= x // mid。',
    'if mid * mid <= x:\n    answer = mid\n    left = mid + 1',
    '给定 0 到 10^12 的整数 x，返回最大的非负整数 r，使 r*r <= x；也就是 x 的平方根向下取整。x 为 0 或 1 时直接得到自身，不能调用 math.sqrt。',
    [('x', 'int', '非负整数')],
    [([8], 2), ([16], 4), ([0], 0), ([1], 1), ([1000000000000], 1000000)],
    '''left = 0
right = x
answer = 0
while left <= right:
    mid = (left + right) // 2
    if mid * mid <= x:
        answer = mid
        left = mid + 1
    else:
        right = mid - 1
return answer''',
    ['答案范围从 0 到 x；x=0 也有效。', '可行的 mid 先记为 answer，再向右继续搜索。', '平方过大时缩小 right，循环结束后返回最后可行的 answer。'],
    '“平方不超过 x”随候选数增大只会从真变假，满足二分条件。每轮将候选区间减半，时间复杂度 O(log x)，额外空间 O(1)。')

add(20, '二分答案：切绳的最大整数长度',
    '长度 L 可行，表示所有绳子切出的长度为 L 的段数至少为 k。更小的长度也一定可行，这种单调性让“最大可行 L”可以二分；长度 0 不参与二分。',
    'pieces = sum(length // mid for length in lengths)\nif pieces >= k:\n    left = mid + 1',
    'lengths 为正整数绳长列表，长度 0 到 1000，每根不超过 10^9；k 为正整数。每段必须是相同的正整数长度，允许丢弃余料。返回能够切出至少 k 段的最大长度；若总绳长不足以切出 k 段长度 1，返回 0。',
    [('lengths', 'list[int]', '每根绳子的正整数长度'), ('k', 'int', '至少需要的段数')],
    [([[8, 7, 5], 5], 3), ([[1, 1], 3], 0),
     ([[], 1], 0), ([[5], 5], 1), ([[10, 10], 3], 5)],
    '''if not lengths:
    return 0
left = 1
right = max(lengths)
answer = 0
while left <= right:
    mid = (left + right) // 2
    pieces = sum(length // mid for length in lengths)
    if pieces >= k:
        answer = mid
        left = mid + 1
    else:
        right = mid - 1
return answer''',
    ['空列表没有任何可切长度，先返回 0。', '用每根 length // mid 累加段数。', '段数够时记录 mid 并往更长处找；不够时缩短长度。'],
    '固定候选长度时可在线性时间统计段数；可行性对长度单调。设 n 为绳子数、M 为最大绳长，时间复杂度 O(n log M)，额外空间 O(1)。')

add(20, '归并排序：统计逆序对',
    '逆序对是 i<j 且 nums[i]>nums[j] 的一对下标。归并两个已排序半段时，如果右半段元素先被取走，它比左半段当前元素小，因此与左侧所有剩余元素都构成逆序对。',
    'if left[i] <= right[j]:\n    merged.append(left[i])\nelse:\n    merged.append(right[j])\n    count += len(left) - i',
    'nums 是长度 0 到 2000 的整数列表，返回其中逆序对总数。相等元素不算逆序对；空列表和单元素列表返回 0，输入不能被修改。',
    [('nums', 'list[int]', '待统计的整数列表')],
    [([[2, 4, 1, 3, 5]], 3), ([[3, 2, 1]], 3),
     ([[]], 0), ([[1, 1]], 0), ([[-1, -3, 2]], 1)],
    '''def sort_count(values):
    if len(values) <= 1:
        return values[:], 0
    middle = len(values) // 2
    left, left_count = sort_count(values[:middle])
    right, right_count = sort_count(values[middle:])
    i = 0
    j = 0
    merged = []
    count = left_count + right_count
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            count += len(left) - i
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged, count
return sort_count(nums)[1]''',
    ['把函数的返回值设计为“排好序的列表和该列表的逆序对数”。', '左右半段内部的数量先递归得到。', '右元素小于左元素时，一次增加 len(left)-i，而不是只加 1。'],
    '归并阶段一次线性扫描，同时统计跨越两半的逆序对；递归层数为 O(log n)。时间复杂度 O(n log n)，归并列表与递归切片占 O(n log n) 的实现级临时空间（可用索引优化到 O(n)）。')

add(20, '排序后合并重叠区间',
    '把区间按起点排序后，只需和当前已合并结果的最后一个区间比较。若下一个 start 小于等于最后一个 end，两个闭区间相交或相接，应把 end 扩到两者较大值。',
    'ordered = sorted(intervals, key=lambda item: item[0])\nif start <= merged[-1][1]:\n    merged[-1][1] = max(merged[-1][1], end)',
    'intervals 的每项是 [start, end] 且 start<=end，元素为整数，长度 0 到 500。把重叠或端点相接的闭区间合并，返回按起点升序的全新二维列表；空输入返回 []，不能修改内部区间。',
    [('intervals', 'list[list[int]]', '闭区间列表 [起点, 终点]')],
    [([[[1, 3], [2, 6], [8, 10], [15, 18]]], [[1, 6], [8, 10], [15, 18]]),
     ([[[1, 4], [4, 5]]], [[1, 5]]),
     ([[]], []), ([[[-3, -1], [-2, 2]]], [[-3, 2]]),
     ([[[5, 7], [1, 2], [2, 3]]], [[1, 3], [5, 7]])],
    '''if not intervals:
    return []
ordered = sorted(intervals, key=lambda item: item[0])
merged = [[ordered[0][0], ordered[0][1]]]
for start, end in ordered[1:]:
    if start <= merged[-1][1]:
        merged[-1][1] = max(merged[-1][1], end)
    else:
        merged.append([start, end])
return merged''',
    ['先单独处理空列表，后面才能读取 ordered[0]。', '排序后创建第一个独立的 [start, end] 副本。', '判断使用 <=，因为 [1,4] 与 [4,5] 在端点相接。'],
    '排序保证未来区间的起点不会回退，所以每个区间只需与最后一个合并结果比较一次。排序主导时间复杂度 O(n log n)，输出及排序副本使用 O(n) 空间。')

add(20, '荷兰国旗：三色原地分区',
    '当数组元素只可能是 0、1、2 时，用 low、scan、high 分别划分已放好的 0 区、正在扫描区和已放好的 2 区。遇到 2 与 high 交换后，不要前进 scan，因为换来的值尚未检查。',
    'if values[scan] == 0:\n    values[low], values[scan] = values[scan], values[low]\nelif values[scan] == 2:\n    values[scan], values[high] = values[high], values[scan]',
    'nums 只含整数 0、1、2，长度 0 到 100000。返回按 0、1、2 分区后的新列表，不调用 sorted，不修改 nums。空列表允许。',
    [('nums', 'list[int]', '仅由 0、1、2 组成的列表')],
    [([[2, 0, 2, 1, 1, 0]], [0, 0, 1, 1, 2, 2]), ([[1, 1, 0]], [0, 1, 1]),
     ([[]], []), ([[2, 2]], [2, 2]), ([[0, 1, 2]], [0, 1, 2])],
    '''values = nums[:]
low = 0
scan = 0
high = len(values) - 1
while scan <= high:
    if values[scan] == 0:
        values[low], values[scan] = values[scan], values[low]
        low += 1
        scan += 1
    elif values[scan] == 2:
        values[scan], values[high] = values[high], values[scan]
        high -= 1
    else:
        scan += 1
return values''',
    ['复制 nums 后再交换，避免修改调用者的数据。', '0 交换后 low 和 scan 都右移；1 只右移 scan。', '2 交换后只左移 high，scan 留在原处重新检查。'],
    '每个元素至多被 scan 检查一次或由 high 换入一次，指针单调靠拢。时间复杂度 O(n)，算法本身辅助空间 O(1)，本题为返回新列表额外使用 O(n) 复制空间。')


# 21 — Linear data structures make order and “the next item” explicit.
add(21, '栈匹配：有效括号序列',
    '栈遵循后进先出。扫描到左括号就压栈；扫描到右括号时，必须与栈顶左括号配对并弹出。扫描结束后栈也必须为空，才没有遗留的左括号。',
    'pairs = {")": "(", "]": "[", "}": "{"}\nif not stack or stack[-1] != pairs[ch]:\n    return False',
    's 仅由 ()[]{} 六种字符组成，长度 0 到 100000。判断括号是否全部正确配对且嵌套顺序合法，返回 bool；空字符串是有效序列，不能只比较三种括号的总数量。',
    [('s', 'str', '括号组成的字符串')],
    [(['()[]{}'], True), (['([)]'], False), ([''], True), (['((('], False), (['{[()]}'], True)],
    '''pairs = {')': '(', ']': '[', '}': '{'}
stack = []
for ch in s:
    if ch in '([{':
        stack.append(ch)
    else:
        if not stack or stack[-1] != pairs[ch]:
            return False
        stack.pop()
return not stack''',
    ['左括号压入列表，列表末尾就是栈顶。', '遇到右括号前先判断栈是否为空。', '右括号匹配后 pop；最后返回 not stack。'],
    '每个字符最多压栈、弹栈各一次，栈顶保证嵌套次序正确。时间复杂度 O(n)，最坏情况下所有字符都是左括号，辅助空间 O(n)。')

add(21, '栈计算：逆波兰表达式',
    '逆波兰表达式把运算符放在两个操作数之后。读到数字压栈；读到运算符时，先弹出右操作数 b，再弹出左操作数 a，计算 a 运算 b 后压回，顺序不能颠倒。',
    'b = stack.pop()\na = stack.pop()\nstack.append(a - b)',
    'tokens 是一条合法的逆波兰表达式，元素为十进制整数字符串或 +、-、*、/；至少含一个数字。除法结果向 0 截断，保证不会除以 0，最终结果在 [-10^9,10^9]。返回整数结果。',
    [('tokens', 'list[str]', '逆波兰表达式的 token 列表')],
    [([['2', '1', '+', '3', '*']], 9), ([['4', '13', '5', '/', '+']], 6),
     ([['-7']], -7), ([['5', '-2', '/']], -2), ([['3', '4', '-', '2', '*']], -2)],
    '''stack = []
for token in tokens:
    if token not in {'+', '-', '*', '/'}:
        stack.append(int(token))
        continue
    b = stack.pop()
    a = stack.pop()
    if token == '+':
        stack.append(a + b)
    elif token == '-':
        stack.append(a - b)
    elif token == '*':
        stack.append(a * b)
    else:
        quotient = abs(a) // abs(b)
        stack.append(quotient if (a >= 0) == (b >= 0) else -quotient)
return stack[-1]''',
    ['数字 token 可以直接 int 后压栈。', '弹出顺序是 b 再 a，所以减法和除法要计算 a-b、a/b。', '用绝对值整除再恢复符号，明确实现向 0 截断。'],
    '合法表达式保证每个运算符前都有两个数。每个 token 只进栈或出栈常数次，时间复杂度 O(n)，栈的最坏空间复杂度 O(n)。')

add(21, '栈化简：绝对 Unix 路径',
    '把绝对路径按 / 分割后，空段和 . 表示“留在当前目录”；.. 表示返回上一级，因此从栈尾弹出一个目录。普通目录名压栈，最后再用 / 连接。',
    'for part in path.split("/"):\n    if part == "..":\n        if stack:\n            stack.pop()',
    'path 是以 / 开头的 Unix 风格绝对路径，长度不超过 10000，路径段只可能是小写字母、. 或 ..，可含连续斜杠。返回规范路径：根目录为 /，无重复斜杠、无尾部斜杠；在根目录继续 .. 仍留在根目录。',
    [('path', 'str', '绝对 Unix 路径')],
    [(['/a//b/./c/../'], '/a/b'), (['/../'], '/'),
     (['/'], '/'), (['/home/../../x'], '/x'), (['/a/./b/../../c/'], '/c')],
    '''stack = []
for part in path.split('/'):
    if not part or part == '.':
        continue
    if part == '..':
        if stack:
            stack.pop()
    else:
        stack.append(part)
return '/' + '/'.join(stack)''',
    ['split("/") 后会出现空字符串，直接跳过。', '.. 只有在栈非空时才 pop。', '普通目录压栈，最后用 "/" + "/".join(stack) 生成结果。'],
    '栈中始终保存从根到当前位置的目录。每个路径段只处理一次，时间复杂度 O(n)，栈和输出使用 O(n) 空间。')

add(21, '循环队列：模拟有限缓冲区',
    '循环队列用 head 指向队首、tail 指向下一个写入位置，tail 每次通过 (tail+1) % capacity 回绕。size 区分“空”和“满”：同一组 head、tail 在没有 size 时会产生歧义。',
    'queue[tail] = value\ntail = (tail + 1) % capacity\nsize += 1',
    'capacity 是 0 到 100 的整数。operations 的操作为 ["push", value] 或 ["pop"]，最多 500 项：队满时 push 被忽略，队空时 pop 被忽略。返回所有成功 pop 出的值，顺序与出队顺序一致；不返回被忽略操作的标记。',
    [('capacity', 'int', '队列最多容纳的元素数'), ('operations', 'list[list]', '入队或出队操作序列')],
    [([2, [['push', 1], ['push', 2], ['pop'], ['push', 3], ['pop'], ['pop']]], [1, 2, 3]),
     ([1, [['pop'], ['push', 7], ['push', 8], ['pop']]], [7]),
     ([0, [['push', 1], ['pop']]], []),
     ([3, []], []),
     ([2, [['push', -1], ['push', 0], ['pop'], ['pop']]], [-1, 0])],
    '''if capacity == 0:
    return []
queue = [None] * capacity
head = 0
tail = 0
size = 0
removed = []
for operation in operations:
    if operation[0] == 'push':
        if size < capacity:
            queue[tail] = operation[1]
            tail = (tail + 1) % capacity
            size += 1
    elif size:
        removed.append(queue[head])
        head = (head + 1) % capacity
        size -= 1
return removed''',
    ['capacity 为 0 时不能做模运算，先返回空结果。', '入队前检查 size < capacity，出队前检查 size 是否非零。', '成功出队后移动 head、减少 size，并把值追加到 removed。'],
    '每个操作都只进行常数次读写。时间复杂度 O(q)，其中 q 是操作数；队列数组占 O(capacity) 空间，输出另占 O(q)。')

add(21, '两个栈实现先进先出的队列',
    '一个输入栈负责接收 push，一个输出栈负责 pop/peek。当输出栈为空时，把输入栈逐个弹出并压入输出栈，顺序便被反转，最早进入的元素来到输出栈顶。',
    'if not out_stack:\n    while in_stack:\n        out_stack.append(in_stack.pop())',
    'operations 的操作为 ["push", value]、["pop"] 或 ["peek"]，最多 1000 项。按顺序模拟队列：pop 和 peek 若队空都产生 null；每次 pop 或 peek 的结果依次放入返回列表，push 不产生输出。',
    [('operations', 'list[list]', '队列操作序列')],
    [([[['push', 1], ['push', 2], ['peek'], ['pop'], ['pop']]], [1, 1, 2]),
     ([[['pop'], ['peek']]], [None, None]),
     ([[['push', -3], ['peek'], ['pop']]], [-3, -3]),
     ([[]], []),
     ([[['push', 1], ['pop'], ['push', 2], ['peek']]], [1, 2])],
    '''in_stack = []
out_stack = []
answers = []
def move_if_needed():
    if not out_stack:
        while in_stack:
            out_stack.append(in_stack.pop())
for operation in operations:
    kind = operation[0]
    if kind == 'push':
        in_stack.append(operation[1])
    else:
        move_if_needed()
        if kind == 'pop':
            answers.append(out_stack.pop() if out_stack else None)
        else:
            answers.append(out_stack[-1] if out_stack else None)
return answers''',
    ['push 一律压入 in_stack。', '在 pop 或 peek 前，若 out_stack 为空才转移元素。', '空队列用 None 表示；不要把 None 当成“没有输出”而漏掉它。'],
    '每个元素最多从输入栈移到输出栈一次，再从输出栈弹出一次，因此 q 次操作的总时间为 O(q)，均摊每次 O(1)，空间复杂度 O(q)。')

add(21, '单链表反转：用内部节点模拟',
    '链表节点只保存 value 和 next。反转时维护 prev、current：先保存 current.next，再让 current.next 指向 prev，最后共同前移；千万不要在保存 next 前覆盖它。',
    'following = current.next\ncurrent.next = previous\nprevious = current\ncurrent = following',
    'values 按链表从头到尾的顺序给出，长度 0 到 1000。请在 solve 内构造内部单链表并反转，再以列表返回反转后的值；空链表返回 []，不得调用 reversed 或直接返回 values[::-1]。',
    [('values', 'list[int]', '按头到尾顺序编码的链表值')],
    [([[1, 2, 3]], [3, 2, 1]), ([[]], []),
     ([[7]], [7]), ([[-1, 0]], [0, -1]), ([[1, 1, 2]], [2, 1, 1])],
    '''class Node:
    def __init__(self, value, next_node=None):
        self.value = value
        self.next = next_node
head = None
for value in reversed(values):
    head = Node(value, head)
previous = None
current = head
while current is not None:
    following = current.next
    current.next = previous
    previous = current
    current = following
result = []
while previous is not None:
    result.append(previous.value)
    previous = previous.next
return result''',
    ['先用 Node(value, head) 从后向前建出原链表。', '每轮先保存 following，再改 current.next。', '反转结束后的 previous 是新头，从它遍历收集结果。'],
    '反转阶段让每个节点的 next 恰好改写一次。建表、反转和收集各为 O(n)，总时间 O(n)，内部节点和结果列表占 O(n) 空间。')

add(21, '快慢指针：单链表的中间节点',
    'slow 每轮走一步，fast 每轮走两步；当 fast 到达尾部时，slow 正好在中部。对偶数个节点，循环条件允许 fast 走完最后一步，因此返回第二个中间节点。',
    'while fast is not None and fast.next is not None:\n    slow = slow.next\n    fast = fast.next.next',
    'values 按单链表顺序给出，长度 0 到 1000。请在 solve 内构造内部节点后返回中间节点的值；空链表返回 null。长度为偶数时返回两个中间节点中靠右的一个。',
    [('values', 'list[int]', '按头到尾顺序编码的链表值')],
    [([[1, 2, 3, 4, 5]], 3), ([[1, 2, 3, 4]], 3),
     ([[]], None), ([[9]], 9), ([[-1, 0]], 0)],
    '''class Node:
    def __init__(self, value, next_node=None):
        self.value = value
        self.next = next_node
head = None
tail = None
for value in values:
    node = Node(value)
    if head is None:
        head = node
    else:
        tail.next = node
    tail = node
slow = head
fast = head
while fast is not None and fast.next is not None:
    slow = slow.next
    fast = fast.next.next
return None if slow is None else slow.value''',
    ['建链表时保留 tail，才能把新节点接到末尾。', 'slow 和 fast 都从 head 开始。', '先检查 fast 与 fast.next，才能安全访问 fast.next.next。'],
    '快指针速度是慢指针的两倍，所以快指针到尾部时慢指针走了约一半节点。建表和扫描时间复杂度 O(n)，节点空间 O(n)，快慢指针本身只占 O(1)。')

add(21, '合并两条有序单链表',
    '给两个已排序链表各放一个指针，每次把较小节点接到 dummy 哨兵节点后。dummy 自身不属于答案，但能统一“第一个节点”与后续节点的连接逻辑。',
    'if left.value <= right.value:\n    tail.next = left\n    left = left.next\nelse:\n    tail.next = right',
    'left_values、right_values 都是非递减整数列表，长度各不超过 500。请在 solve 内构造两条内部单链表、合并它们并返回值列表；允许空列表和重复值，相等时优先取左链表节点。',
    [('left_values', 'list[int]', '第一条已排序链表的值'), ('right_values', 'list[int]', '第二条已排序链表的值')],
    [([[1, 2, 4], [1, 3, 4]], [1, 1, 2, 3, 4, 4]), ([[], [0]], [0]),
     ([[], []], []), ([[-3, 2], [-2, 2]], [-3, -2, 2, 2]), ([[5], []], [5])],
    '''class Node:
    def __init__(self, value, next_node=None):
        self.value = value
        self.next = next_node
def build(values):
    head = None
    tail = None
    for value in values:
        node = Node(value)
        if head is None:
            head = node
        else:
            tail.next = node
        tail = node
    return head
left = build(left_values)
right = build(right_values)
dummy = Node(0)
tail = dummy
while left is not None and right is not None:
    if left.value <= right.value:
        tail.next = left
        left = left.next
    else:
        tail.next = right
        right = right.next
    tail = tail.next
tail.next = left if left is not None else right
result = []
node = dummy.next
while node is not None:
    result.append(node.value)
    node = node.next
return result''',
    ['用 build 分别构造两条链表。', 'dummy 和 tail 让第一次连接不需要特殊分支。', '一条链表耗尽后，把另一条的剩余部分直接接到 tail。'],
    '合并时每个节点只被比较和接入一次。设两条长度为 m、n，建表、合并和收集总时间 O(m+n)，内部节点与输出使用 O(m+n) 空间。')

add(21, '单调队列：滑动窗口最大值',
    '双端队列存放“可能成为最大值”的下标，且对应数值从队首到队尾单调递减。新元素到来时，从队尾删除不大于它的旧下标；窗口左界外的下标从队首删除。',
    'while queue and nums[queue[-1]] <= value:\n    queue.pop()\nqueue.append(i)',
    'nums 是长度 0 到 100000 的整数列表，0<=k<=len(nums)。返回每个连续长度 k 窗口的最大值列表；k=0 返回 []，负数和重复值都允许，要求 O(n) 时间。',
    [('nums', 'list[int]', '整数列表'), ('k', 'int', '窗口长度')],
    [([[1, 3, -1, -3, 5, 3, 6, 7], 3], [3, 3, 5, 5, 6, 7]), ([[-1, -1], 1], [-1, -1]),
     ([[], 0], []), ([[2, 1], 2], [2]), ([[9, 9, 9], 2], [9, 9])],
    '''from collections import deque
if k == 0:
    return []
queue = deque()
answer = []
for i, value in enumerate(nums):
    while queue and queue[0] <= i - k:
        queue.popleft()
    while queue and nums[queue[-1]] <= value:
        queue.pop()
    queue.append(i)
    if i >= k - 1:
        answer.append(nums[queue[0]])
return answer''',
    ['队列存下标而非值，才能判断元素是否已滑出窗口。', '先清理过期队首，再从队尾清理不可能成为最大值的下标。', '当 i>=k-1 时，队首对应当前窗口最大值。'],
    '每个下标最多进入队列一次、从两端删除一次，因此总操作数线性。时间复杂度 O(n)，双端队列最多保存 k 个下标，辅助空间 O(k)，结果空间 O(n)。')

add(21, '快慢指针：数组表示的链表是否有环',
    'nexts[i] 记录节点 i 的下一个节点下标，-1 表示空指针。慢指针每轮走一步、快指针走两步；若链表有环，快指针最终会在环内追上慢指针。',
    'while fast != -1 and nexts[fast] != -1:\n    slow = nexts[slow]\n    fast = nexts[nexts[fast]]',
    'nexts 长度为 0 到 1000，每项为 -1 或合法下标；head 为 -1 或合法下标。按 nexts 从 head 走，判断是否会进入环，返回 bool。空链表无环，所有输入索引均有效。',
    [('nexts', 'list[int]', '数组表示的 next 指针'), ('head', 'int', '头节点下标，-1 表示空')],
    [([[1, 2, -1], 0], False), ([[1, 2, 0], 0], True),
     ([[], -1], False), ([[-1], 0], False), ([[2, -1, 0], 0], True)],
    '''if head == -1:
    return False
slow = head
fast = head
while fast != -1 and nexts[fast] != -1:
    slow = nexts[slow]
    fast = nexts[nexts[fast]]
    if slow == fast:
        return True
return False''',
    ['head 为 -1 时没有节点，直接返回 False。', '循环条件先保证 fast 及其下一跳都存在。', '每轮更新后比较 slow 与 fast；相遇就说明进入了环。'],
    '无环时快指针会先遇到 -1；有环时相对速度为每轮一步，有限环中必然相遇。时间复杂度 O(n)，两个指针占 O(1) 辅助空间。')


# 22 — Trees organize hierarchy; heaps and union-find maintain useful invariants.
add(22, '二叉树层序遍历：按层收集节点',
    '本题用完全二叉树数组表示树：下标 i 的左右孩子是 2*i+1、2*i+2，None 表示缺失节点。广度优先搜索把当前层所有下标取出，再把有效孩子加入下一层。',
    'left = 2 * index + 1\nright = 2 * index + 2\nif left < len(values) and values[left] is not None:\n    next_level.append(left)',
    'values 用完全二叉树数组编码，元素为整数或 null，长度 0 到 1000；null 节点没有非 null 后代。返回从根到叶的每层值列表。空数组或根为 null 返回 []；每层保持从左到右顺序。',
    [('values', 'list', '完全二叉树数组，null 表示缺失节点')],
    [([[3, 9, 20, None, None, 15, 7]], [[3], [9, 20], [15, 7]]), ([[1]], [[1]]),
     ([[]], []), ([[None]], []), ([[1, 2, 3, 4, 5]], [[1], [2, 3], [4, 5]])],
    '''if not values or values[0] is None:
    return []
current = [0]
answer = []
while current:
    answer.append([values[index] for index in current])
    next_level = []
    for index in current:
        left = 2 * index + 1
        right = left + 1
        if left < len(values) and values[left] is not None:
            next_level.append(left)
        if right < len(values) and values[right] is not None:
            next_level.append(right)
    current = next_level
return answer''',
    ['根不存在时没有任何层，先返回 []。', 'current 保存当前层的数组下标，而不是值。', '遍历当前层后再整体替换为 next_level。'],
    '每个非空节点只进入一层并检查两个孩子一次。时间复杂度 O(n)，当前层和答案使用 O(n) 空间，其中队列式层列表最坏可达 O(n)。')

add(22, '二叉树最大深度',
    '树的深度可以递归定义：空树深度为 0，非空树深度为左右子树深度的较大者加 1。数组表示下递归参数是节点下标，越界或 None 都对应空子树。',
    'def depth(index):\n    if index >= len(values) or values[index] is None:\n        return 0\n    return 1 + max(depth(2*index+1), depth(2*index+2))',
    'values 的编码规则同上一题，长度 0 到 1000。返回根到最深叶子的节点数量；空树和根为 null 的深度为 0，单节点树深度为 1。',
    [('values', 'list', '完全二叉树数组，null 表示缺失节点')],
    [([[3, 9, 20, None, None, 15, 7]], 3), ([[1, 2, None, 3]], 3),
     ([[]], 0), ([[None]], 0), ([[8]], 1)],
    '''def depth(index):
    if index >= len(values) or values[index] is None:
        return 0
    return 1 + max(depth(2 * index + 1), depth(2 * index + 2))
return depth(0)''',
    ['把越界下标和 None 都当成空树。', '左右孩子下标分别是 2*i+1、2*i+2。', '当前非空节点的答案是 1 + 两个子树深度的较大值。'],
    '递归恰好访问每个有效节点一次。时间复杂度 O(n)，递归调用栈的空间复杂度 O(h)，h 是树高；极端偏斜树时 h 可为 O(n)。')

add(22, '验证二叉搜索树：上下界约束',
    '二叉搜索树不只要求节点与直接孩子比较。递归向左子树传入更小的上界，向右子树传入更大的下界；这样后代也会受到全部祖先的约束。',
    'if not (low < value < high):\n    return False\nreturn check(left, low, value) and check(right, value, high)',
    'values 用完全二叉树数组编码，元素为整数或 null，null 节点没有非 null 后代，长度 0 到 1000。判断它是否为严格二叉搜索树，返回 bool；空树为 True，重复值不合法，左子树值必须严格小于祖先，右子树值必须严格大于祖先。',
    [('values', 'list', '完全二叉树数组，整数值互不相同')],
    [([[2, 1, 3]], True), ([[5, 1, 4, None, None, 3, 6]], False),
     ([[]], True), ([[1, None, 2]], True), ([[2, 2, 3]], False)],
    '''def check(index, low, high):
    if index >= len(values) or values[index] is None:
        return True
    value = values[index]
    if not (low < value < high):
        return False
    return (check(2 * index + 1, low, value) and
            check(2 * index + 2, value, high))
return check(0, float('-inf'), float('inf'))''',
    ['空节点天然满足约束。', '不要只比较父节点；把 low、high 一起向下传递。', '左孩子继承 low 并把 high 设为当前值；右孩子相反。'],
    '上下界覆盖了每个祖先的限制，因此能发现“右子树里的值小于根”等局部比较遗漏的问题。时间复杂度 O(n)，递归栈空间 O(h)。')

add(22, '二叉树最近公共祖先：数组父下标',
    '完全二叉树数组中，非根节点 i 的父下标是 (i-1)//2。先把 p 的所有祖先下标放入集合，再从 q 向上走，第一个命中的下标就是两者离 q 最近的公共祖先。',
    'parent = (index - 1) // 2\nancestors.add(index)\nwhile index not in ancestors:\n    index = (index - 1) // 2',
    'values 用完全二叉树数组编码，非 null 值唯一且 null 节点没有非 null 后代。p、q 是待查询的节点值，可能有一个不存在。两者都存在时返回其最近公共祖先的值；任一不存在、空树时返回 null，p 与 q 相同则返回该节点。',
    [('values', 'list', '完全二叉树数组，非空值唯一'), ('p', 'int', '第一个节点值'), ('q', 'int', '第二个节点值')],
    [([[3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], 5, 1], 3),
     ([[3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], 5, 4], 5),
     ([[], 1, 2], None), ([[1, 2, 3], 2, 9], None), ([[1, 2, 3], 2, 2], 2)],
    '''if not values:
    return None
positions = {value: index for index, value in enumerate(values) if value is not None}
if p not in positions or q not in positions:
    return None
ancestors = set()
index = positions[p]
while True:
    ancestors.add(index)
    if index == 0:
        break
    index = (index - 1) // 2
index = positions[q]
while index not in ancestors:
    index = (index - 1) // 2
return values[index]''',
    ['先建值到下标的映射，同时自然跳过 None。', 'p 不存在或 q 不存在时必须先返回 None。', '从 q 向根走，第一次落在 p 祖先集合的位置就是答案。'],
    '两条祖先链长度都不超过树高 h。建立位置映射需 O(n) 时间和空间，向上查找为 O(h)；额外的祖先集合空间 O(h)。')

add(22, '最小堆：第 k 个最大元素',
    '大小为 k 的最小堆把当前最大的 k 个元素保留下来，堆顶始终是其中最小的一个。加入新值后若堆超过 k，就弹出堆顶；扫描结束后的堆顶即第 k 大。',
    'heappush(heap, value)\nif len(heap) > k:\n    heappop(heap)',
    'nums 是长度 1 到 100000 的整数列表，1<=k<=len(nums)。按数值从大到小计数（重复元素也占位置），返回第 k 个最大元素；允许负数和重复值，不能直接对 nums 调用 sort。',
    [('nums', 'list[int]', '整数列表'), ('k', 'int', '从大到小的名次')],
    [([[3, 2, 1, 5, 6, 4], 2], 5), ([[3, 2, 3, 1, 2, 4, 5, 5, 6], 4], 4),
     ([[-1], 1], -1), ([[2, 2], 2], 2), ([[-5, -2, -9], 1], -2)],
    '''from heapq import heappush, heappop
heap = []
for value in nums:
    heappush(heap, value)
    if len(heap) > k:
        heappop(heap)
return heap[0]''',
    ['导入 heappush 和 heappop，Python 的 heapq 是最小堆。', '每读一个值后都保证堆大小不超过 k。', '扫描结束时堆里正好保留最大的 k 个值，heap[0] 是第 k 大。'],
    '堆最多保存 k 个元素，每次入堆或出堆为 O(log k)。总时间复杂度 O(n log k)，辅助空间 O(k)。')

add(22, '堆选前 K 高频元素',
    '先用字典统计频次，再把 [值, 次数] 看作候选项。heapq.nsmallest 可以按照自定义 key 取最小的 k 项；键设为 (-次数, 值) 后，就实现“频次降序、值升序”的确定规则。',
    'counts[value] = counts.get(value, 0) + 1\nbest = nsmallest(k, counts.items(), key=lambda item: (-item[1], item[0]))',
    'nums 是长度 0 到 100000 的整数列表，0<=k<=不同值数量。返回频次最高的 k 个值，按频次降序；频次相同按数值升序。k=0 或 nums 为空时返回 []，结果中每个不同值至多出现一次。',
    [('nums', 'list[int]', '整数列表'), ('k', 'int', '需要返回的不同值数')],
    [([[1, 1, 1, 2, 2, 3], 2], [1, 2]), ([[4, 4, 1, 1, 2], 2], [1, 4]),
     ([[], 0], []), ([[5], 1], [5]), ([[-1, -1, 0, 0, 0], 2], [0, -1])],
    '''from heapq import nsmallest
counts = {}
for value in nums:
    counts[value] = counts.get(value, 0) + 1
best = nsmallest(k, counts.items(), key=lambda item: (-item[1], item[0]))
return [value for value, _ in best]''',
    ['先建立值到次数的字典。', '排序键的第一项用 -次数，第二项用原数值。', 'nsmallest 返回的是 (值, 次数) 项，最后只取值。'],
    '统计扫描为 O(n)。设 d 为不同值数，nsmallest 的堆选择时间为 O(d log k)，字典和候选堆使用 O(d) 空间；并列规则使输出可重复验证。')

add(22, '并查集：无向图连通分量数',
    '并查集把每个节点所在集合的代表元保存在 parent 中。find 通过路径压缩让节点直接连向根；union 只在两根不同的时候合并，此时连通分量数量减一。',
    'def find(x):\n    if parent[x] != x:\n        parent[x] = find(parent[x])\n    return parent[x]',
    'n 是 0 到 1000，节点编号为 0 到 n-1；edges 为无向边列表，边端点合法，可重复或自环。返回图的连通分量数；n=0 返回 0。重复边和自环不应额外减少分量数。',
    [('n', 'int', '节点总数'), ('edges', 'list[list[int]]', '无向边 [u, v] 列表')],
    [([5, [[0, 1], [1, 2], [3, 4]]], 2), ([3, [[0, 1], [1, 2], [0, 2]]], 1),
     ([0, []], 0), ([4, []], 4), ([2, [[0, 0], [0, 1]]], 1)],
    '''parent = list(range(n))
rank = [0] * n
def find(x):
    if parent[x] != x:
        parent[x] = find(parent[x])
    return parent[x]
components = n
for u, v in edges:
    root_u = find(u)
    root_v = find(v)
    if root_u != root_v:
        if rank[root_u] < rank[root_v]:
            root_u, root_v = root_v, root_u
        parent[root_v] = root_u
        if rank[root_u] == rank[root_v]:
            rank[root_u] += 1
        components -= 1
return components''',
    ['初始时 n 个节点各自是一个分量。', '只有两个根不同，union 才真的合并并减少计数。', '路径压缩写在 find 的递归返回前，按秩合并避免树过高。'],
    '每条边调用常数次 find/union；路径压缩与按秩合并后，摊还时间为 O((n+e) α(n))，α 极慢增长。parent、rank 使用 O(n) 空间。')

add(22, '并查集：找出第一条成环边',
    '在无向图中，若一条新边的两个端点已经属于同一集合，再加入它就会形成环。按给定顺序处理边，第一次发生这种情况的边就是答案。',
    'if find(u) == find(v):\n    return [u, v]\nparent[find(u)] = find(v)',
    'edges 是无向边 [u,v] 列表，节点编号为正整数，最多 1000 条边。按输入顺序返回第一条会形成环的边；若没有环或 edges 为空，返回 []。允许节点编号不连续，边端点均为整数。',
    [('edges', 'list[list[int]]', '按顺序给出的无向边')],
    [([[[1, 2], [1, 3], [2, 3]]], [2, 3]), ([[[1, 2], [2, 3], [3, 4]]], []),
     ([[]], []), ([[[5, 5]]], [5, 5]), ([[[1, 2], [2, 3], [3, 1], [3, 4]]], [3, 1])],
    '''parent = {}
def find(x):
    parent.setdefault(x, x)
    if parent[x] != x:
        parent[x] = find(parent[x])
    return parent[x]
for u, v in edges:
    root_u = find(u)
    root_v = find(v)
    if root_u == root_v:
        return [u, v]
    parent[root_u] = root_v
return []''',
    ['find 中用 setdefault 处理第一次见到的编号。', '先比较两个根；相同根时立即返回当前输入边。', '根不同才把一个根接到另一个根，不必真的维护整张图。'],
    '并查集维护已处理边产生的连通关系，端点已连通等价于添加该边形成环。设 e 为边数，摊还时间 O(e α(e))，parent 字典空间 O(v)。')

add(22, 'Kruskal：最小生成树总权重',
    'Kruskal 按边权从小到大考察边；只有连接两个不同分量的边才能加入，否则会成环。并查集负责快速判断是否应加入，已选 n-1 条边时生成树完成。',
    'for u, v, weight in sorted(edges, key=lambda edge: edge[2]):\n    if find(u) != find(v):\n        parent[find(u)] = find(v)',
    'n 是 0 到 200，节点为 0 到 n-1；edges 的每项为 [u,v,weight]，weight 可为负数，端点合法。返回无向图的最小生成树总权重；n 为 0 或 1 返回 0，图不连通时返回 -1，允许平行边和自环。',
    [('n', 'int', '节点数'), ('edges', 'list[list[int]]', '无向带权边 [u, v, weight]')],
    [([3, [[0, 1, 1], [1, 2, 2], [0, 2, 3]]], 3), ([4, [[0, 1, 1], [2, 3, 1]]], -1),
     ([1, []], 0), ([0, []], 0), ([3, [[0, 1, -2], [1, 2, 3], [0, 2, 5]]], 1)],
    '''if n <= 1:
    return 0
parent = list(range(n))
rank = [0] * n
def find(x):
    if parent[x] != x:
        parent[x] = find(parent[x])
    return parent[x]
total = 0
used = 0
for u, v, weight in sorted(edges, key=lambda edge: edge[2]):
    root_u = find(u)
    root_v = find(v)
    if root_u != root_v:
        if rank[root_u] < rank[root_v]:
            root_u, root_v = root_v, root_u
        parent[root_v] = root_u
        if rank[root_u] == rank[root_v]:
            rank[root_u] += 1
        total += weight
        used += 1
        if used == n - 1:
            return total
return -1''',
    ['n<=1 时没有需要连接的边，答案为 0。', '先按第三项 weight 排序，再逐条判断两端根是否不同。', '每成功合并一条边就累加权重；选到 n-1 条即可返回。'],
    'Kruskal 的贪心安全性来自“当前最轻的跨分量边”可加入某棵最优生成树。排序时间 O(e log e)，并查集操作近似线性，空间 O(n)。')

add(22, '最小堆：操作序列模拟',
    'Python 的 heapq 维护最小堆，heap[0] 始终是最小值。heappush 保持堆性质，heappop 删除并返回最小值；空堆 pop 不能调用 heappop，应按题意返回 null。',
    'heappush(heap, value)\nanswer.append(heappop(heap) if heap else None)',
    'operations 的操作为 ["push", value] 或 ["pop"]，最多 1000 项。模拟一座初始为空的最小堆，返回每个 pop 的结果；空堆 pop 返回 null 并仍在结果中保留一个位置，允许重复值和负数。',
    [('operations', 'list[list]', '堆的插入和删除最小值操作')],
    [([[['push', 3], ['push', 1], ['pop'], ['push', 2], ['pop'], ['pop']]], [1, 2, 3]),
     ([[['pop'], ['push', -1], ['pop']]], [None, -1]),
     ([[]], []), ([[['push', 2], ['push', 2], ['pop'], ['pop']]], [2, 2]),
     ([[['push', 0], ['push', -3], ['pop']]], [-3])],
    '''from heapq import heappush, heappop
heap = []
answer = []
for operation in operations:
    if operation[0] == 'push':
        heappush(heap, operation[1])
    else:
        answer.append(heappop(heap) if heap else None)
return answer''',
    ['导入 heapq 的 heappush、heappop。', 'push 把第二项压入堆；pop 前先判断 heap 是否非空。', '每一次 pop，无论成功与否，都向 answer 追加一个结果。'],
    '堆大小为 h 时插入和删除最小值均为 O(log h)，处理 q 项操作最坏 O(q log q)。堆和 pop 结果各使用 O(q) 空间。')


# 23 — Graph algorithms make the frontier, visited state, and edge direction explicit.
add(23, '广度优先搜索：无权图最短步数',
    '在每条边代价相同的图中，BFS 用队列按距离从近到远扩展。节点第一次出队或入队时得到的距离就是最短步数；visited 防止环使同一节点被反复加入。',
    'queue = deque([(start, 0)])\nfor neighbor in graph[node]:\n    if neighbor not in visited:\n        visited.add(neighbor)\n        queue.append((neighbor, distance + 1))',
    'n 为 1 到 1000，节点编号 0 到 n-1；edges 是有向边 [from,to] 列表，可为空，端点合法。返回从 start 到 target 的最少边数，无法到达返回 -1；start==target 返回 0，重复边不影响结果。',
    [('n', 'int', '节点总数'), ('edges', 'list[list[int]]', '有向边 [起点, 终点]'), ('start', 'int', '起点编号'), ('target', 'int', '终点编号')],
    [([5, [[0, 1], [0, 2], [1, 3], [2, 3], [3, 4]], 0, 4], 3),
     ([3, [[0, 1]], 1, 0], -1),
     ([1, [], 0, 0], 0), ([4, [[0, 1], [1, 2]], 0, 3], -1),
     ([3, [[0, 1], [1, 2], [0, 2]], 0, 2], 1)],
    '''from collections import deque
graph = [[] for _ in range(n)]
for u, v in edges:
    graph[u].append(v)
queue = deque([(start, 0)])
visited = {start}
while queue:
    node, distance = queue.popleft()
    if node == target:
        return distance
    for neighbor in graph[node]:
        if neighbor not in visited:
            visited.add(neighbor)
            queue.append((neighbor, distance + 1))
return -1''',
    ['先建立邻接表，graph[u] 保存 u 的出边终点。', '起点入队时同时放入 visited，避免其他边重复入队。', '从队首取出 target 时，当前 distance 已是最短步数。'],
    '队列按层推进：距离 d 的节点全部处理完才会处理距离 d+1。建图和搜索各线性，时间复杂度 O(n+e)，邻接表、队列与 visited 的空间复杂度 O(n+e)。')

add(23, '深度优先搜索：有向图可达性',
    'DFS 沿一条路径尽可能深入，再回退尝试其他分支。显式栈避免递归深度限制；将节点标记为 visited 后再压入栈，可防止有向环导致无限搜索。',
    'stack = [start]\nwhile stack:\n    node = stack.pop()\n    for neighbor in graph[node]:\n        if neighbor not in visited:\n            visited.add(neighbor)\n            stack.append(neighbor)',
    'n 为 1 到 1000，节点编号 0 到 n-1；edges 是有向边 [from,to] 列表，端点合法。判断 target 是否可从 start 沿边到达，返回 bool；start==target 为 True，图可有环和重复边。',
    [('n', 'int', '节点总数'), ('edges', 'list[list[int]]', '有向边列表'), ('start', 'int', '起点编号'), ('target', 'int', '目标节点编号')],
    [([4, [[0, 1], [1, 2], [2, 1], [2, 3]], 0, 3], True),
     ([3, [[0, 1]], 1, 0], False),
     ([1, [], 0, 0], True), ([3, [[0, 1], [1, 2]], 0, 2], True),
     ([3, [[0, 1], [0, 1]], 2, 1], False)],
    '''graph = [[] for _ in range(n)]
for u, v in edges:
    graph[u].append(v)
stack = [start]
visited = {start}
while stack:
    node = stack.pop()
    if node == target:
        return True
    for neighbor in graph[node]:
        if neighbor not in visited:
            visited.add(neighbor)
            stack.append(neighbor)
return False''',
    ['有向边只加入 graph[u]，不要同时加入反向边。', '把 start 放进栈也放入 visited。', '每发现一个未访问邻居就先标记再压栈，找到 target 即可返回 True。'],
    'DFS 的访问顺序可能不同，但只要访问到 target 就证明存在路径。每个节点和边最多处理常数次，时间 O(n+e)，邻接表、栈和集合空间 O(n+e)。')

add(23, '网格 DFS：岛屿数量',
    '把每个陆地格子看成图节点，上下左右相邻的陆地之间有边。扫描到一个未访问陆地时，进行一次 DFS 并标记它整个连通块；这样的启动次数就是岛屿数。',
    'for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):\n    nr, nc = row + dr, col + dc\n    if 0 <= nr < rows and 0 <= nc < cols:',
    'grid 是由字符串 "0"、"1" 组成的矩形列表，行列均不超过 50；"1" 为陆地、"0" 为水，只按上下左右相连。返回岛屿数量；空 grid 或零列 grid 返回 0，不修改 grid。',
    [('grid', 'list[str]', '由 0 和 1 组成的矩形网格')],
    [([['11000', '11000', '00100', '00011']], 3), ([['111', '111']], 1),
     ([[]], 0), ([['000', '000']], 0), ([['10101']], 3)],
    '''if not grid or not grid[0]:
    return 0
rows = len(grid)
cols = len(grid[0])
visited = set()
count = 0
for row in range(rows):
    for col in range(cols):
        if grid[row][col] != '1' or (row, col) in visited:
            continue
        count += 1
        stack = [(row, col)]
        visited.add((row, col))
        while stack:
            r, c = stack.pop()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if (0 <= nr < rows and 0 <= nc < cols and
                        grid[nr][nc] == '1' and (nr, nc) not in visited):
                    visited.add((nr, nc))
                    stack.append((nr, nc))
return count''',
    ['先处理空网格和空行，避免读取 grid[0] 失败。', '只对未访问的 "1" 启动一次 DFS，并立刻计数。', '把邻居压栈前立刻加入 visited，避免多个方向重复加入。'],
    '每个格子至多被访问一次，每次检查四个方向。设网格大小为 R×C，时间复杂度 O(RC)，visited 与最坏 DFS 栈空间 O(RC)。')

add(23, 'BFS 迷宫：最短移动次数',
    '迷宫每走到上下左右相邻格算一步，边权相同所以 BFS 最先到达 E 的步数最短。墙 # 不可进入，S、E 和 . 都可进入；访问集合同时防止绕圈。',
    'queue.append((start_row, start_col, 0))\nfor dr, dc in directions:\n    nr, nc = row + dr, col + dc\n    queue.append((nr, nc, steps + 1))',
    'grid 是只含 S、E、.、# 的非空矩形字符串列表，最多 50×50，恰有一个 S 和一个 E。返回从 S 到 E 的最少上下左右移动次数，不能穿过 #；若无法到达返回 -1。',
    [('grid', 'list[str]', '迷宫字符网格')],
    [([['S..', '.#.', '..E']], 4), ([['S#E']], -1),
     ([['SE']], 1), ([['S..', '###', '..E']], -1), ([['S.E']], 2)],
    '''from collections import deque
rows = len(grid)
cols = len(grid[0])
start = None
for r in range(rows):
    for c in range(cols):
        if grid[r][c] == 'S':
            start = (r, c)
queue = deque([(start[0], start[1], 0)])
visited = {start}
while queue:
    row, col, steps = queue.popleft()
    if grid[row][col] == 'E':
        return steps
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nr, nc = row + dr, col + dc
        if (0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != '#' and
                (nr, nc) not in visited):
            visited.add((nr, nc))
            queue.append((nr, nc, steps + 1))
return -1''',
    ['先扫描网格找到 S 的行、列。', '坐标越界、墙和已访问格子都不能加入队列。', '出队后若当前位置是 E，立刻返回携带的 steps。'],
    'BFS 按移动次数分层，因此首次取到 E 就是最短路径。设格子数为 R×C，时间复杂度 O(RC)，队列和 visited 的最坏空间复杂度 O(RC)。')

add(23, 'Dijkstra：有向非负权最短路',
    'Dijkstra 用最小堆每次取出当前距离最小的候选节点。若经当前节点到邻居的距离更短，就更新 dist 并把新候选压堆；堆中旧的较大候选取出时跳过。',
    'distance, node = heappop(heap)\nif distance != dist[node]:\n    continue\nif distance + weight < dist[neighbor]:\n    dist[neighbor] = distance + weight',
    'n 为 1 到 500，节点编号 0 到 n-1；edges 为有向边 [from,to,weight]，weight 是 0 到 10^6 的整数，端点合法。返回从 start 到所有节点的最短距离列表，不可达节点填 -1；允许平行边，start 自身距离为 0。',
    [('n', 'int', '节点总数'), ('edges', 'list[list[int]]', '有向非负权边 [起点, 终点, 权重]'), ('start', 'int', '源节点编号')],
    [([4, [[0, 1, 1], [0, 2, 4], [1, 2, 2], [1, 3, 6], [2, 3, 3]], 0], [0, 1, 3, 6]),
     ([3, [[0, 1, 5]], 0], [0, 5, -1]),
     ([1, [], 0], [0]), ([3, [[0, 1, 10], [0, 1, 2], [1, 2, 1]], 0], [0, 2, 3]),
     ([3, [[1, 2, 1]], 1], [-1, 0, 1])],
    '''from heapq import heappush, heappop
graph = [[] for _ in range(n)]
for u, v, weight in edges:
    graph[u].append((v, weight))
dist = [float('inf')] * n
dist[start] = 0
heap = [(0, start)]
while heap:
    distance, node = heappop(heap)
    if distance != dist[node]:
        continue
    for neighbor, weight in graph[node]:
        candidate = distance + weight
        if candidate < dist[neighbor]:
            dist[neighbor] = candidate
            heappush(heap, (candidate, neighbor))
return [value if value != float('inf') else -1 for value in dist]''',
    ['邻接表项同时保存邻居和边权。', 'dist 初始化为无穷大，只有 start 设为 0。', '堆顶距离若不是当前 dist[node]，说明它是旧候选，应跳过。'],
    '非负权保证先从堆中取出的最短候选可安全扩展。使用二叉堆时，时间复杂度 O((n+e) log n)，邻接表、距离表和堆的空间复杂度 O(n+e)。')

add(23, '拓扑排序：字典序最小的任务顺序',
    '有向无环图的拓扑序要求每条 u→v 边中 u 在 v 前。Kahn 算法反复取入度为 0 的节点；最小堆让同时可选的节点总是按编号最小者先输出。',
    'if indegree[neighbor] == 0:\n    heappush(available, neighbor)\nif len(order) != n:\n    return []',
    'n 为 0 到 1000，节点编号 0 到 n-1；edges 为有向边 [u,v]，端点合法且无重复边。返回字典序最小的拓扑序；存在环时返回 []，n=0 也返回 []。',
    [('n', 'int', '任务总数'), ('edges', 'list[list[int]]', '先后约束边 [前置任务, 后续任务]')],
    [([4, [[0, 1], [0, 2], [1, 3], [2, 3]]], [0, 1, 2, 3]),
     ([2, [[0, 1], [1, 0]]], []),
     ([0, []], []), ([3, []], [0, 1, 2]), ([3, [[1, 2]]], [0, 1, 2])],
    '''from heapq import heappush, heappop
graph = [[] for _ in range(n)]
indegree = [0] * n
for u, v in edges:
    graph[u].append(v)
    indegree[v] += 1
available = []
for node in range(n):
    if indegree[node] == 0:
        heappush(available, node)
order = []
while available:
    node = heappop(available)
    order.append(node)
    for neighbor in graph[node]:
        indegree[neighbor] -= 1
        if indegree[neighbor] == 0:
            heappush(available, neighbor)
return order if len(order) == n else []''',
    ['先统计每个节点的入度。', '所有入度为 0 的节点压入最小堆，而不是普通列表。', '若最后输出数小于 n，剩余节点互相依赖，存在环。'],
    '每条边只使入度减一次，每个节点最多进出堆一次。时间复杂度 O((n+e) log n)，图、入度表、堆和结果使用 O(n+e) 空间。')

add(23, '课程安排：检测前置依赖环',
    '把 prerequisite→course 看作有向边，入度表示一门课还缺多少前置课。能不断取出入度为 0 的课程就能完成全部课程；若剩下一批课程入度都非零，依赖关系中存在环。',
    'graph[prerequisite].append(course)\nindegree[course] += 1\nreturn completed == num_courses',
    'num_courses 为 0 到 1000，课程编号 0 到 num_courses-1；prerequisites 每项是 [course, prerequisite]，端点合法且无重复对。判断能否完成所有课程，返回 bool；无课程时为 True，自依赖必为 False。',
    [('num_courses', 'int', '课程总数'), ('prerequisites', 'list[list[int]]', '依赖对 [课程, 前置课程]')],
    [([2, [[1, 0]]], True), ([2, [[1, 0], [0, 1]]], False),
     ([0, []], True), ([1, [[0, 0]]], False), ([3, [[1, 0], [2, 1]]], True)],
    '''from collections import deque
graph = [[] for _ in range(num_courses)]
indegree = [0] * num_courses
for course, prerequisite in prerequisites:
    graph[prerequisite].append(course)
    indegree[course] += 1
queue = deque(node for node in range(num_courses) if indegree[node] == 0)
completed = 0
while queue:
    node = queue.popleft()
    completed += 1
    for neighbor in graph[node]:
        indegree[neighbor] -= 1
        if indegree[neighbor] == 0:
            queue.append(neighbor)
return completed == num_courses''',
    ['边方向是“前置课指向后续课”，不要反过来。', '初始将所有入度 0 课程加入队列。', '最后比较已处理课程数与总数，不能只看队列是否为空。'],
    'Kahn 算法会删除所有不依赖环的课程，环内课程永远无法把入度降到 0。时间复杂度 O(V+E)，邻接表、入度表和队列空间 O(V+E)。')

add(23, 'BFS 泛洪填充：替换连通区域',
    '从起点开始，只向上下左右相邻且颜色等于旧颜色的格子扩展。为避免原图修改影响调用者，先复制每一行；如果 old_color 已等于 color，复制后直接返回即可。',
    'result = [row[:] for row in image]\nqueue = deque([(sr, sc)])\nresult[sr][sc] = color',
    'image 是非空矩形整数矩阵，行列不超过 50，sr、sc 是合法坐标。把与 image[sr][sc] 上下左右连通且颜色相同的像素改成 color，返回新矩阵；不得修改 image，斜对角不连通。',
    [('image', 'list[list[int]]', '整数颜色矩阵'), ('sr', 'int', '起始行'), ('sc', 'int', '起始列'), ('color', 'int', '替换后的颜色')],
    [([[[1, 1, 1], [1, 1, 0], [1, 0, 1]], 1, 1, 2], [[2, 2, 2], [2, 2, 0], [2, 0, 1]]),
     ([[[0, 0, 0], [0, 0, 0]], 0, 0, 0], [[0, 0, 0], [0, 0, 0]]),
     ([[[1]], 0, 0, 9], [[9]]), ([[[1, 2], [2, 2]], 0, 0, 3], [[3, 2], [2, 2]]),
     ([[[1, 1], [1, 2]], 0, 0, 2], [[2, 2], [2, 2]])],
    '''from collections import deque
result = [row[:] for row in image]
old_color = image[sr][sc]
if old_color == color:
    return result
rows = len(image)
cols = len(image[0])
queue = deque([(sr, sc)])
result[sr][sc] = color
while queue:
    row, col = queue.popleft()
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nr, nc = row + dr, col + dc
        if (0 <= nr < rows and 0 <= nc < cols and
                result[nr][nc] == old_color):
            result[nr][nc] = color
            queue.append((nr, nc))
return result''',
    ['用行切片复制二维列表，不能只写 image[:]。', 'old_color 与 color 相等时直接返回复制结果，避免重复入队。', '把邻居改色后再入队，相当于立刻标记为已访问。'],
    '每个匹配颜色的格子只会入队一次，四邻居检查为常数。时间复杂度 O(RC)，复制后的矩阵和队列最坏使用 O(RC) 空间。')

add(23, '多源 BFS：腐烂橘子所需分钟',
    '所有初始腐烂橘子在第 0 分钟同时作为 BFS 源入队。每一层表示一分钟内新腐烂的橘子；最后若仍有新鲜橘子，说明它被空格或边界隔开。',
    'queue = deque((r, c, 0) for ... if grid[r][c] == 2)\nif board[nr][nc] == 1:\n    board[nr][nc] = 2\n    queue.append((nr, nc, minute + 1))',
    'grid 是由 0（空）、1（新鲜）、2（腐烂）组成的矩形整数矩阵，行列均不超过 50，可为空。每分钟腐烂橘子会使上下左右相邻的新鲜橘子腐烂。返回全部腐烂所需最少分钟；没有新鲜橘子返回 0，无法全部腐烂返回 -1，不修改 grid。',
    [('grid', 'list[list[int]]', '橘子状态矩阵')],
    [([[[2, 1, 1], [1, 1, 0], [0, 1, 1]]], 4), ([[[2, 1, 1], [0, 1, 1], [1, 0, 1]]], -1),
     ([[[0, 2]]], 0), ([[]], 0), ([[[1]]], -1)],
    '''from collections import deque
if not grid or not grid[0]:
    return 0
board = [row[:] for row in grid]
rows = len(board)
cols = len(board[0])
queue = deque()
fresh = 0
for r in range(rows):
    for c in range(cols):
        if board[r][c] == 2:
            queue.append((r, c, 0))
        elif board[r][c] == 1:
            fresh += 1
minutes = 0
while queue:
    row, col, minute = queue.popleft()
    minutes = max(minutes, minute)
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nr, nc = row + dr, col + dc
        if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] == 1:
            board[nr][nc] = 2
            fresh -= 1
            queue.append((nr, nc, minute + 1))
return minutes if fresh == 0 else -1''',
    ['空网格或零列网格没有新鲜橘子，返回 0。', '把所有初始 2 都以分钟 0 入队，并单独统计 fresh。', '每感染一个 1 立刻改为 2、fresh 减一并携带 minute+1 入队。'],
    '多源 BFS 让多个腐烂源并行扩展，首次感染一个格子的时间就是最短时间。时间复杂度 O(RC)，复制矩阵、队列和输入规模均为 O(RC)。')

add(23, '二分图判定：BFS 染色',
    '二分图可以把每个连通分量的节点染成两种颜色，使每条边两端颜色不同。从未染色节点启动 BFS；若发现一条边连接同色节点，立即判定失败。',
    'colors[start] = 0\nif colors[neighbor] == -1:\n    colors[neighbor] = 1 - colors[node]\nelif colors[neighbor] == colors[node]:\n    return False',
    'n 为 0 到 1000，节点编号 0 到 n-1；edges 是无向边 [u,v]，端点合法，可有重复边或自环。判断图是否为二分图，返回 bool；不连通图的每个分量都要检查，空图为 True，自环为 False。',
    [('n', 'int', '节点总数'), ('edges', 'list[list[int]]', '无向边列表')],
    [([4, [[0, 1], [1, 2], [2, 3], [3, 0]]], True), ([3, [[0, 1], [1, 2], [2, 0]]], False),
     ([0, []], True), ([2, [[0, 0]]], False), ([4, [[0, 1], [2, 3]]], True)],
    '''from collections import deque
graph = [[] for _ in range(n)]
for u, v in edges:
    graph[u].append(v)
    graph[v].append(u)
colors = [-1] * n
for start in range(n):
    if colors[start] != -1:
        continue
    colors[start] = 0
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if colors[neighbor] == -1:
                colors[neighbor] = 1 - colors[node]
                queue.append(neighbor)
            elif colors[neighbor] == colors[node]:
                return False
return True''',
    ['无向边要同时加入 u 的邻接表和 v 的邻接表。', 'colors 用 -1 表示未染色，遍历每个节点以覆盖不连通分量。', '已染色邻居若与当前节点同色，直接返回 False。'],
    '每条边至多从两端检查一次，每个节点最多入队一次。时间复杂度 O(n+e)，邻接表、颜色表和 BFS 队列占 O(n+e) 空间。')


# 24 — Recursion defines smaller subproblems; greedy and DP record the right choice or state.
add(24, '递归：阶乘的终止条件',
    '递归函数必须有能直接返回的基例。n! 可定义为 0!=1，n! = n*(n-1)!；每次调用把 n 减一，最终一定到达 0，因此不会无限递归。',
    'def factorial(value):\n    if value == 0:\n        return 1\n    return value * factorial(value - 1)',
    '给定整数 n，0<=n<=12，使用递归返回 n 的阶乘。0 的阶乘定义为 1；结果保证在普通整数范围内，不能调用 math.factorial。',
    [('n', 'int', '非负整数')],
    [([5], 120), ([0], 1), ([1], 1), ([10], 3628800), ([12], 479001600)],
    '''def factorial(value):
    if value == 0:
        return 1
    return value * factorial(value - 1)
return factorial(n)''',
    ['先写出最小问题 0! 的答案。', '递归调用的参数必须更接近 0，这里是 value-1。', '递归函数定义在 solve 内，最后 return factorial(n)。'],
    '每层递归只做一次乘法，调用链从 n 降到 0。时间复杂度 O(n)，递归调用栈空间 O(n)。')

add(24, '回溯：生成所有子集',
    '回溯用 path 保存当前选择，并用 start 限制下一次可选位置，避免同一组合因顺序不同重复出现。每到一个递归节点，当前 path 本身就是一个合法子集，要复制后加入结果。',
    'result.append(path[:])\nfor index in range(start, len(nums)):\n    path.append(nums[index])\n    backtrack(index + 1)\n    path.pop()',
    'nums 是元素互不相同的整数列表，长度 0 到 10。返回全部子集：每个子集保持 nums 中的相对顺序，结果按深度优先的“先记录当前 path、再依次扩展”顺序；空列表的结果是 [[]]。',
    [('nums', 'list[int]', '元素互不相同的整数列表')],
    [([[1, 2]], [[], [1], [1, 2], [2]]), ([[0]], [[], [0]]),
     ([[]], [[]]), ([[-1, 3]], [[], [-1], [-1, 3], [3]]), ([[1, 2, 3]], [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]])],
    '''result = []
path = []
def backtrack(start):
    result.append(path[:])
    for index in range(start, len(nums)):
        path.append(nums[index])
        backtrack(index + 1)
        path.pop()
backtrack(0)
return result''',
    ['初始 path 为空，但它也要作为第一个子集记录。', '递归后必须 pop，恢复到进入本层之前的选择。', '递归下层从 index+1 开始，因此一个元素不会重复使用。'],
    '每个子集对应一条选择路径，共有 2^n 个子集；复制各路径后输出规模为 O(n·2^n)。时间复杂度 O(n·2^n)，递归栈和 path 为 O(n)，结果空间为 O(n·2^n)。')

add(24, '回溯：生成全排列',
    '排列要求每个位置选一个尚未使用的元素。used[index] 记录 nums[index] 是否已放入 path；当 path 长度等于 n 时，复制 path 得到一条完整排列，然后回退继续尝试。',
    'if not used[index]:\n    used[index] = True\n    path.append(nums[index])\n    backtrack()\n    path.pop()\n    used[index] = False',
    'nums 是元素互不相同的整数列表，长度 0 到 8。返回全部排列，每条排列按选择时的 nums 下标顺序生成；结果采用深度优先顺序。空列表有一个排列 [[]]，不得修改 nums。',
    [('nums', 'list[int]', '元素互不相同的整数列表')],
    [([[1, 2, 3]], [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]),
     ([[7]], [[7]]), ([[]], [[]]), ([[-1, 0]], [[-1, 0], [0, -1]]),
     ([[2, 1]], [[2, 1], [1, 2]])],
    '''result = []
path = []
used = [False] * len(nums)
def backtrack():
    if len(path) == len(nums):
        result.append(path[:])
        return
    for index in range(len(nums)):
        if not used[index]:
            used[index] = True
            path.append(nums[index])
            backtrack()
            path.pop()
            used[index] = False
backtrack()
return result''',
    ['用 used 记录位置，不要只依据值判断是否已选。', 'path 长度等于 len(nums) 时复制并 return。', '递归回来后同时 pop path 和把 used[index] 改回 False。'],
    '第一个位置有 n 种选择、第二个 n-1 种，最终有 n! 条排列。时间复杂度 O(n·n!)（含复制输出），递归栈、path、used 为 O(n)，结果空间 O(n·n!)。')

add(24, '回溯：N 皇后方案数量',
    '按行放置皇后时，每行只需尝试一个列。集合 cols、diag1(row-col)、diag2(row+col) 记录已被攻击的列与两类对角线；选择后加入集合，递归返回后必须移除。',
    'if col not in cols and row - col not in diag1 and row + col not in diag2:\n    cols.add(col)\n    backtrack(row + 1)\n    cols.remove(col)',
    '给定 n，0<=n<=8，在 n×n 棋盘放置 n 个皇后，使任意两皇后不同行、列或对角线攻击，返回方案总数。n=0 视为一个空摆放方案，返回 1；n=1 返回 1。',
    [('n', 'int', '棋盘边长与皇后数量')],
    [([4], 2), ([1], 1), ([2], 0), ([3], 0), ([0], 1)],
    '''cols = set()
diag1 = set()
diag2 = set()
count = 0
def backtrack(row):
    nonlocal count
    if row == n:
        count += 1
        return
    for col in range(n):
        if col in cols or row - col in diag1 or row + col in diag2:
            continue
        cols.add(col)
        diag1.add(row - col)
        diag2.add(row + col)
        backtrack(row + 1)
        cols.remove(col)
        diag1.remove(row - col)
        diag2.remove(row + col)
backtrack(0)
return count''',
    ['逐行放置，所以不必单独检查“是否同一行”。', '两个对角线键分别用 row-col 与 row+col。', '成功递归后把三个集合中的选择都移除，才能尝试下一列。'],
    '回溯会剪去所有已冲突的位置，最坏搜索量仍呈指数级，常用上界为 O(n!)。cols 和两条对角线集合以及递归栈使用 O(n) 空间。')

add(24, '贪心：最多参加多少个不重叠活动',
    '区间调度的贪心规则是总选结束时间最早的活动。它为后续留下最多时间；按结束时间升序扫描，只要当前活动的 start 不早于已选活动的 end 就能加入。',
    'for start, end in sorted(intervals, key=lambda item: (item[1], item[0])):\n    if start >= last_end:\n        count += 1\n        last_end = end',
    'intervals 的每项为 [start,end] 且 start<end，长度 0 到 1000，时间为整数。一个活动结束时刻等于下一个开始时刻可以连续参加。返回最多可参加活动数；空列表返回 0，不能修改 intervals。',
    [('intervals', 'list[list[int]]', '活动区间 [开始, 结束] 列表')],
    [([[[1, 3], [2, 4], [3, 5], [0, 6], [5, 7], [8, 9]]], 4),
     ([[[1, 2], [2, 3], [3, 4]]], 3),
     ([[]], 0), ([[[5, 7], [1, 4], [4, 5]]], 3),
     ([[[-3, -1], [-2, 2], [2, 3]]], 2)],
    '''last_end = None
count = 0
for start, end in sorted(intervals, key=lambda item: (item[1], item[0])):
    if last_end is None or start >= last_end:
        count += 1
        last_end = end
return count''',
    ['先按结束时间排序，不是按开始时间排序。', '第一项没有 last_end，可直接选择。', '后续活动用 start >= last_end 判断，端点相接允许连续参加。'],
    '最早结束的可选活动不会减少任何最优解可容纳的后续活动数量，交换论证可证明贪心正确。排序时间 O(n log n)，扫描 O(n)，额外空间取决于排序副本，为 O(n)。')

add(24, '贪心：固定面额找零',
    '面额为 100、50、20、10、5、1 时，每次优先取不超过剩余金额的最大面额。divmod(remaining, denomination) 同时给出该面额张数和新的剩余金额，结果顺序固定。',
    'count, remaining = divmod(remaining, denomination)\ncounts.append(count)',
    'amount 是 0 到 10^9 的整数。使用固定面额 [100,50,20,10,5,1] 找零，返回对应张数列表 [c100,c50,c20,c10,c5,c1]；amount=0 返回六个 0。本题指定该面额体系并要求按从大到小的贪心规则。',
    [('amount', 'int', '需要找零的非负金额')],
    [([186], [1, 1, 1, 1, 1, 1]), ([0], [0, 0, 0, 0, 0, 0]),
     ([99], [0, 1, 2, 0, 1, 4]), ([250], [2, 1, 0, 0, 0, 0]), ([6], [0, 0, 0, 0, 1, 1])],
    '''remaining = amount
counts = []
for denomination in (100, 50, 20, 10, 5, 1):
    count, remaining = divmod(remaining, denomination)
    counts.append(count)
return counts''',
    ['从 100 开始依次处理到 1，不能跳过 1。', 'divmod 的第一个返回值是张数，第二个是余数。', '每个面额只处理一次，把张数按固定顺序追加。'],
    '指定的面额和顺序使每一步都尽量消去更多金额；1 元保证最终余数为 0。面额种类固定为 6，时间复杂度 O(1)，除返回列表外辅助空间 O(1)。')

add(24, '贪心：最少跳跃次数',
    '从当前可达范围 [0,end] 扫描时，farthest 记录这一层任一位置能到达的最远下标。扫描到 end 就必须再跳一次进入下一层；若 farthest 没有前进，末尾不可达。',
    'farthest = max(farthest, index + nums[index])\nif index == end:\n    jumps += 1\n    end = farthest',
    'nums 是长度 0 到 100000 的非负整数列表，nums[i] 表示从 i 最多可向右跳的步数。返回从下标 0 到最后下标的最少跳数；空列表或不可达时返回 -1，单元素列表返回 0。',
    [('nums', 'list[int]', '每个位置的最大跳跃长度')],
    [([[2, 3, 1, 1, 4]], 2), ([[3, 2, 1, 0, 4]], -1),
     ([[]], -1), ([[0]], 0), ([[1, 0, 1]], -1)],
    '''if not nums:
    return -1
if len(nums) == 1:
    return 0
jumps = 0
end = 0
farthest = 0
for index in range(len(nums) - 1):
    farthest = max(farthest, index + nums[index])
    if index == end:
        if farthest == end:
            return -1
        jumps += 1
        end = farthest
        if end >= len(nums) - 1:
            return jumps
return -1''',
    ['空列表与单元素列表分别单独处理。', '扫描当前范围内每个位置，持续更新 farthest。', '到达本层边界 end 时若 farthest 没前进就不可达，否则跳数加一并扩展边界。'],
    '每个下标只扫描一次，farthest 概括了同一跳数下所有选择，因此不需枚举路径。时间复杂度 O(n)，只用常数个变量，辅助空间 O(1)。')

add(24, '动态规划：0/1 背包最大价值',
    'dp[c] 表示容量不超过 c 时的最大价值。处理一个物品时容量必须从大到小更新，这样 dp[c-weight] 仍是“没用当前物品”的上一轮状态，才能保证每件物品最多选一次。',
    'for capacity_now in range(capacity, weight - 1, -1):\n    dp[capacity_now] = max(dp[capacity_now], dp[capacity_now - weight] + value)',
    'weights、values 等长，长度 0 到 100；weights 为正整数，values 为非负整数，capacity 为 0 到 1000。每件物品最多选一次，返回总重量不超过 capacity 的最大总价值；空物品或容量 0 返回 0。',
    [('weights', 'list[int]', '每件物品重量'), ('values', 'list[int]', '每件物品价值'), ('capacity', 'int', '背包容量')],
    [([[1, 3, 4], [15, 20, 30], 4], 35), ([[2, 3, 4], [4, 5, 10], 6], 14),
     ([[], [], 5], 0), ([[1, 2], [10, 20], 0], 0), ([[5], [9], 4], 0)],
    '''dp = [0] * (capacity + 1)
for weight, value in zip(weights, values):
    for capacity_now in range(capacity, weight - 1, -1):
        dp[capacity_now] = max(dp[capacity_now], dp[capacity_now - weight] + value)
return dp[capacity]''',
    ['dp 长度是 capacity+1，dp[0] 表示容量 0。', '逐件遍历 weights、values，再从 capacity 向下遍历容量。', '若容量装得下当前物品，比较“不选”和“选后加 value”。'],
    '逆序容量循环使一个物品不能在同一轮反复使用。设物品数为 n、容量为 C，时间复杂度 O(nC)，一维 dp 使用 O(C) 空间。')

add(24, '动态规划：最长公共子序列长度',
    '子序列可以删除字符但不能改变剩余字符顺序。令 dp[i][j] 表示 a 前 i 个字符与 b 前 j 个字符的 LCS 长度：末字符相等就接在 dp[i-1][j-1] 后，否则取删去其中一个末字符的较大值。',
    'if char_a == char_b:\n    current.append(previous[j - 1] + 1)\nelse:\n    current.append(max(previous[j], current[j - 1]))',
    'a、b 是长度各不超过 200 的字符串，字符可重复且可为空。返回最长公共子序列的长度；子序列不要求连续，空串与任何字符串的答案为 0。',
    [('a', 'str', '第一个字符串'), ('b', 'str', '第二个字符串')],
    [(['abcde', 'ace'], 3), (['abc', 'abc'], 3),
     (['abc', 'def'], 0), (['', 'abc'], 0), (['aab', 'azab'], 3)],
    '''previous = [0] * (len(b) + 1)
for char_a in a:
    current = [0]
    for j, char_b in enumerate(b, start=1):
        if char_a == char_b:
            current.append(previous[j - 1] + 1)
        else:
            current.append(max(previous[j], current[j - 1]))
    previous = current
return previous[-1]''',
    ['空前缀的 LCS 长度都是 0，所以 previous 初始全为 0。', '每处理 a 的一个字符都新建 current，并从 b 的第 1 列开始。', '相等看左上 previous[j-1]；不等取上 previous[j] 与左 current[j-1] 的较大值。'],
    '状态转移覆盖了两串末字符相等和不等的全部情况。完整二维表时间与空间均为 O(mn)；此处只保留前一行，时间 O(mn)、辅助空间 O(n)。')

add(24, '动态规划：凑零钱的最少硬币数',
    'dp[value] 表示凑出 value 的最少硬币数，初始 dp[0]=0，其余设为一个不可能的较大值。对每种硬币从 coin 向上更新，让 dp[value-coin] 已代表可以重复使用该硬币的最优值。',
    'dp = [amount + 1] * (amount + 1)\ndp[0] = 0\nfor coin in coins:\n    for value in range(coin, amount + 1):\n        dp[value] = min(dp[value], dp[value - coin] + 1)',
    'coins 是互不相同的正整数面额列表，长度 0 到 100；amount 为 0 到 1000。每种硬币可无限使用，返回凑出 amount 的最少硬币数；amount=0 返回 0，无法凑出返回 -1。',
    [('coins', 'list[int]', '可无限使用的正整数面额'), ('amount', 'int', '目标金额')],
    [([[1, 2, 5], 11], 3), ([[2], 3], -1),
     ([[], 0], 0), ([[1], 0], 0), ([[2, 5, 10, 1], 27], 4)],
    '''dp = [amount + 1] * (amount + 1)
dp[0] = 0
for coin in coins:
    for value in range(coin, amount + 1):
        dp[value] = min(dp[value], dp[value - coin] + 1)
return dp[amount] if dp[amount] <= amount else -1''',
    ['dp[0] 必须是 0，其他状态先设成 amount+1。', '每枚硬币从 coin 向上枚举 value，才允许重复使用该面额。', '最后若 dp[amount] 仍大于 amount，说明没有任何组合到达目标。'],
    '每个状态尝试每一种面额一次，且最优子结构来自最后放入的一枚硬币。设面额数为 n，时间复杂度 O(n·amount)，dp 数组空间 O(amount)。')
