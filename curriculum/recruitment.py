"""Chapters 31–36: interview patterns, invariants, and engineering simulations.

The small cases are deliberately hand-auditable. Scale cases have closed-form
answers rather than answers produced by the reference implementations.
"""

from .schema import problem

PROBLEMS = []
_counts = {}


def add(chapter, title, lesson, syntax, task, params, tests, body, hints,
        proof, time, space, pitfall, skills, prerequisites, difficulty='进阶'):
    _counts[chapter] = _counts.get(chapter, 0) + 1
    names = ', '.join(p[0] for p in params)
    solution = 'def solve(' + names + '):\n' + '\n'.join(
        '    ' + line if line else '' for line in body.strip().splitlines())
    p = problem(chapter, _counts[chapter], title,
                lesson + '\n\nPython 语法小课：\n```python\n' + syntax + '\n```',
                task, params, tests, solution, hints,
                proof + '\n复杂度：时间 ' + time + '；辅助空间 ' + space + '。\n易错点：' + pitfall,
                difficulty=difficulty)
    p.update(track='recruitment', learning_goal=skills[0] + '：' + title,
             prerequisites=prerequisites, skills=skills,
             complexity={'time': time, 'space': space})
    PROBLEMS.append(p)


# 31: prefix states, frequency windows, and monotone structures.
add(31, '前缀状态：和为目标值的子数组数量',
    '前缀和相减得到区间和。遇到当前前缀 s 时，之前出现过多少次 s-target，就有多少个以当前位置结尾的答案。字典保存频次而不是位置；空前缀的和为0，必须预先计数一次。这个方法允许负数，而普通伸缩窗口不允许。',
    'freq = {0: 1}\ncount = freq.get(prefix - target, 0)\nfreq[prefix] = freq.get(prefix, 0) + 1',
    '给定长度0～20000的整数列表 nums，元素绝对值≤10^6，target 为绝对值≤10^12的整数。返回和恰为 target 的非空连续子数组数量。相同数值但下标不同的区间分别计数；空数组返回0。',
    [('nums','list[int]','允许负数和零'),('target','int','目标和')],
    [([[1,1,1],2],2), ([[1,-1,0],0],3), ([[],0],0), ([[0],0],1),
     ([[0,0,0],0],6), ([[3,-2,4],5],1), ([[2,2],1],0), ([[0]*10000,0],50005000)],
    '''freq = {0: 1}
prefix = answer = 0
for x in nums:
    prefix += x
    answer += freq.get(prefix - target, 0)
    freq[prefix] = freq.get(prefix, 0) + 1
return answer''',
    ['先写出区间和等于两个前缀和之差。','当前前缀是 s，需要查找的旧前缀是 s-target。','先查询再增加当前前缀的频次，避免把空区间算进去。'],
    '处理每个右端点之前，字典恰好保存它左侧所有前缀。每个合法区间有唯一右端点和对应旧前缀，因此会被计入且只计入一次。',
    'O(n) 平均','O(n)','如果先更新频次，target=0 时会多算空区间。',
    ['前缀和计数','哈希表','负数边界'],[6,19])

add(31, '双向累积：除自身外的数组乘积',
    '把自身左边与右边的乘积分别计算，再相乘。输出列表可以暂存左侧乘积，反向遍历时用一个变量维护右侧乘积。乘法单位元为1，因此边界不用特殊分支。无需除法，也能自然处理一个或多个零。',
    'for i in range(len(nums) - 1, -1, -1):\n    answer[i] *= right\n    right *= nums[i]',
    'nums 长度0～500，元素为-9～9的整数。返回等长列表，第i项为所有其他位置元素的乘积。请尝试不使用除法；单元素列表返回[1]，空列表返回[]。Python整数无溢出，复杂度按整数运算次数计。',
    [('nums','list[int]','整数列表')],
    [([[1,2,3,4]],[24,12,8,6]), ([[0,2,3]],[6,0,0]), ([[]],[]),
     ([[3]],[1]), ([[0,0,2]],[0,0,0]), ([[-1,2,-3]],[-6,3,-2]), ([[1,1]],[1,1])],
    '''answer = [1] * len(nums)
left = 1
for i, x in enumerate(nums):
    answer[i] = left
    left *= x
right = 1
for i in range(len(nums) - 1, -1, -1):
    answer[i] *= right
    right *= nums[i]
return answer''',
    ['每个答案拆成左乘积乘右乘积。','第一遍写入不含自身的左乘积，然后才把自身乘入累积量。','第二遍从右向左，用同样的更新顺序补上右乘积。'],
    '第一遍结束时answer[i]包含所有j<i的因子，第二遍乘入所有j>i的因子；两部分不重不漏且均不含i。',
    'O(n) 次整数运算','O(1)，不计返回列表','累积量更新放错顺序会把自身也乘入；多个零不需要分支。',
    ['前后缀分解','逆序循环','零值边界'],[5,19])

add(31, '集合去重：最长连续整数段',
    '连续指整数值连续，不要求在原列表中相邻。把数据放进集合，只有x-1不存在时才把x当作一段的起点。这样每个数至多被其所属段扫描一次，避免从每个数开始重复延伸。',
    'values = set(nums)\nif x - 1 not in values:\n    end = x\n    while end in values:\n        end += 1',
    'nums 长度0～20000，整数绝对值≤10^9。返回由列表中的不同整数构成的最长连续段长度。重复数字不增加长度；空列表返回0。目标平均O(n)时间，不排序。',
    [('nums','list[int]','无序整数列表')],
    [([[100,4,200,1,3,2]],4), ([[0,-1,1,1]],3), ([[]],0), ([[5]],1),
     ([[2,2,2]],1), ([[1,3,5]],1), ([[-4,-3,-2,8,9]],3)],
    '''values = set(nums)
best = 0
for x in values:
    if x - 1 not in values:
        end = x
        while end in values:
            end += 1
        best = max(best, end - x)
return best''',
    ['先去掉重复数字。','一段连续数的最小值有什么特征？它的前一个整数不在集合中。','只从这些最小值向上延伸，记录end-x的最大值。'],
    '每段恰有一个没有前驱的起点。所有延伸循环扫描的集合元素互不重叠，因此虽然代码有嵌套循环，总扫描数仍为n。',
    'O(n) 平均','O(n)','不要对集合中的每个值都向后扫描，否则连续输入会退化到平方级。',
    ['集合起点判定','摊还分析'],[6,19])

add(31, '计数转化：恰好 K 种不同值的子数组',
    '“恰好”条件不好直接维护，可以用“至多K种”的数量减去“至多K-1种”的数量。固定右端点时，若最小合法左端点为left，则所有left到right之间的起点都合法，共right-left+1个。',
    'freq[x] = freq.get(x, 0) + 1\nif freq[y] == 0:\n    del freq[y]',
    'nums 长度0～20000，元素为整数且绝对值≤10^9；0≤k≤20000。返回恰好包含k种不同值的非空连续子数组数量。k=0或空列表返回0。',
    [('nums','list[int]','整数列表'),('k','int','不同值的精确数量')],
    [([[1,2,1,2,3],2],7), ([[1,2,1,3,4],3],3), ([[],1],0),
     ([[1,1,1],1],6), ([[1,2],0],0), ([[1,2],3],0), ([[1,2,3],2],2)],
    '''def at_most(limit):
    if limit < 0:
        return 0
    freq = {}
    left = total = 0
    for right, x in enumerate(nums):
        freq[x] = freq.get(x, 0) + 1
        while len(freq) > limit:
            y = nums[left]
            freq[y] -= 1
            if freq[y] == 0:
                del freq[y]
            left += 1
        total += right - left + 1
    return total
return at_most(k) - at_most(k - 1)''',
    ['先解决“至多k种”。','每个右端点收缩到合法后，一次增加窗口长度，而不是只增加1。','做两次窗口统计，相减去掉不足k种的区间。'],
    '至多k种的集合包含至多k-1种的集合，差集恰好是k种。窗口左侧更早起点均不合法，窗口内所有起点均合法，故长度就是当前右端点的贡献。',
    'O(n) 平均','O(n)','频次归零必须删除键，否则len(freq)不再代表不同值数量。',
    ['滑动窗口','差分计数','频次字典'],[6,19])

add(31, '覆盖窗口：最短包含目标字符的片段',
    '目标可能含重复字符，集合无法表达所需次数。用缺额字典记录还缺多少，每加入一个确实缺少的字符，总缺额减一。总缺额为零后尽量收缩左端点，再记录最短窗口。切片放到最后，避免循环内反复复制长字符串。',
    'from collections import Counter\nneed = Counter(target)\ntext[start:start + length]',
    'text、target 只含英文字母，长度分别0～20000、0～2000。返回包含target全部字符及其重复次数的最短连续片段；长度并列取起点最早者。target为空或无解返回空串，区分大小写。',
    [('text','str','搜索范围'),('target','str','需覆盖的多重集合')],
    [(['ADOBECODEBANC','ABC'],'BANC'), (['aaab','aab'],'aab'), (['','a'],''),
     (['abc',''],''), (['a','aa'],''), (['bbaa','ba'],'ba'), (['abxxab','ab'],'ab')],
    '''from collections import Counter
if not target:
    return ''
need = Counter(target)
missing = len(target)
left = start = 0
length = len(text) + 1
for right, char in enumerate(text):
    if need[char] > 0:
        missing -= 1
    need[char] -= 1
    while missing == 0:
        if right - left + 1 < length:
            start, length = left, right - left + 1
        old = text[left]
        need[old] += 1
        if need[old] > 0:
            missing += 1
        left += 1
return '' if length > len(text) else text[start:start + length]''',
    ['统计target中每种字符的次数，不只记录是否出现。','维护尚缺字符总数；负频次表示当前有多余字符。','缺额为0时反复移除左边字符；只有严格更短才更新答案以保留最早起点。'],
    '缺额为零恰好表示覆盖成立。每个右端点都尝试删除全部可删前缀，因此不会遗漏以它结束的最短合法窗口。严格变短时更新满足并列规则。',
    'O(n+m)','O(1)，字母表固定','target为空要提前返回，否则收缩循环没有自然停止条件。',
    ['覆盖型滑动窗口','多重集合'],[4,6,11,19],'挑战')

add(31, '正数窗口：达到阈值的最短区间',
    '元素全为正数时，扩大窗口只会增加和，缩小窗口只会减少和。这种单调性允许左右指针各向右移动一次。请把该前提与下一类含负数题对比，理解算法为什么成立。',
    'while total >= target:\n    best = min(best, right - left + 1)\n    total -= nums[left]\n    left += 1',
    'nums 长度0～20000，每个元素1～10^6；1≤target≤10^12。返回和至少target的最短非空连续子数组长度，无解返回0。',
    [('nums','list[int]','严格正数列表'),('target','int','正数阈值')],
    [([[2,3,1,2,4,3],7],2), ([[1,4,4],4],1), ([[],1],0),
     ([[1,1,1],4],0), ([[2],2],1), ([[1,2,3],6],3), ([[5,1,1],6],2)],
    '''left = total = 0
best = len(nums) + 1
for right, x in enumerate(nums):
    total += x
    while total >= target:
        best = min(best, right - left + 1)
        total -= nums[left]
        left += 1
return 0 if best > len(nums) else best''',
    ['先固定右端点，看当前和是否足够。','足够时记录长度并尝试移除最左元素。','不足时才继续扩大右端点；用n+1作为无解哨兵。'],
    '对于每个右端点，循环检查其所有仍满足阈值的左端点；正数保证一旦不足，再缩短也不可能恢复合法。左右指针不回退，所以总操作数线性。',
    'O(n)','O(1)','该算法依赖严格正数，不能直接用于有负数的数组。',
    ['窗口单调性','最短区间'],[5,19])

add(31, '同余前缀：和可被 K 整除的区间',
    '两个前缀和的差可被k整除，当且仅当它们除以k的余数相同。Python对正除数的取模结果总在0到k-1之间，因此负数也能直接归类。保存余数出现次数，能一次统计所有匹配左端点。',
    'remainder = (remainder + x) % k\n# 在 Python 中，-1 % 5 等于 4',
    'nums 长度0～20000，元素绝对值≤10^9；1≤k≤10^9。返回元素和能被k整除的非空连续子数组数量。允许负数、零；空数组返回0。',
    [('nums','list[int]','整数列表'),('k','int','正除数')],
    [([[4,5,0,-2,-3,1],5],7), ([[-1,2,9],2],2), ([[],3],0),
     ([[1,2,3],1],6), ([[0,0],7],3), ([[1],2],0), ([[-5],5],1)],
    '''freq = {0: 1}
remainder = answer = 0
for x in nums:
    remainder = (remainder + x) % k
    answer += freq.get(remainder, 0)
    freq[remainder] = freq.get(remainder, 0) + 1
return answer''',
    ['把整除条件写成两个前缀和同余。','无需保存完整前缀和，只需要余数。','字典从{0:1}开始，当前余数已有多少次就增加多少个区间。'],
    '同余关系与区间和整除完全等价。每个新前缀与所有相同余数的旧前缀配对，恰好枚举以当前位置为右端点的合法区间。',
    'O(n) 平均','O(min(n,k))','不要把k当作数组长度直接分配，k可能很大；字典只保存实际出现的余数。',
    ['模运算','前缀状态'],[6,12,19])

add(31, '状态最早位置：零一数量相等的最长区间',
    '把0视为-1、1视为+1，零一数量相等就变成区间和为0。求最长长度时，应保存某个前缀状态第一次出现的位置，而不是频次或最近位置。下标-1代表还没有读取元素的空前缀。',
    'first = {0: -1}\nif balance not in first:\n    first[balance] = i',
    'bits 长度0～20000，元素仅为0或1。返回含相同数量0和1的最长连续子数组长度，无解返回0。',
    [('bits','list[int]','零一列表')],
    [([[0,1]],2), ([[0,1,0]],2), ([[]],0), ([[1,1,1]],0),
     ([[0,0,1,1]],4), ([[0,1,1,0,1,0]],6), ([[0,0,0,1,1]],4)],
    '''first = {0: -1}
balance = best = 0
for i, bit in enumerate(bits):
    balance += 1 if bit == 1 else -1
    if balance in first:
        best = max(best, i - first[balance])
    else:
        first[balance] = i
return best''',
    ['把两种元素映射为相反的增量。','前缀状态相同意味着中间的增量和为0。','保留最早下标，后续同状态尽量与它配对。'],
    '两个相同balance之间的1与0数量相等。固定右端点，最早同状态前缀给出最大长度，保留它足以得到全局最优。',
    'O(n) 平均','O(n)','覆盖最早位置会丢失较长答案；空前缀位置是-1而不是0。',
    ['状态映射','前缀最早位置'],[6,19])

add(31, '排序双指针：去重的三数之和',
    '先固定最小值，再在右侧用双指针寻找另外两个数。排序后，和太小就增大左指针，和太大就减小右指针。题目按数值组合去重，因此固定值和命中后的两端值都要跳过重复。',
    'a = sorted(nums)\nwhile left < right and a[left] == previous:\n    left += 1',
    'nums 长度0～200，元素绝对值≤10^6。返回所有和为0的不同三元组。必须使用三个不同下标；每个三元组升序，整体按字典序升序；相同数值组合只返回一次。无解返回[]。',
    [('nums','list[int]','允许重复的整数列表')],
    [([[-1,0,1,2,-1,-4]],[[-1,-1,2],[-1,0,1]]), ([[0,0,0,0]],[[0,0,0]]),
     ([[]],[]), ([[1,2]],[]), ([[1,2,3]],[]), ([[-2,0,1,1,2]],[[-2,0,2],[-2,1,1]]),
     ([[-1,-1,2,2]],[[-1,-1,2]])],
    '''a = sorted(nums)
answer = []
for i in range(len(a) - 2):
    if i and a[i] == a[i - 1]:
        continue
    left, right = i + 1, len(a) - 1
    while left < right:
        total = a[i] + a[left] + a[right]
        if total < 0:
            left += 1
        elif total > 0:
            right -= 1
        else:
            answer.append([a[i], a[left], a[right]])
            x, y = a[left], a[right]
            while left < right and a[left] == x:
                left += 1
            while left < right and a[right] == y:
                right -= 1
return answer''',
    ['先排序，把三重枚举中的后两重变为双指针。','和太小时左移右指针无益，应该把左指针向右移动。','固定数相同则跳过；命中后跳过两个端点的重复值。'],
    '排序的单调性保证每次丢弃的端点不可能再参与尚未找到的目标组合。按固定值、第二值递增地产生结果，去重后天然满足字典序要求。',
    'O(n²)','O(n)，不计返回结果','三个下标必须不同，左指针从i+1开始，而不是从0开始。',
    ['排序双指针','组合去重'],[5,20])

add(31, '含负数的最短区间：单调前缀队列',
    '存在负数时，扩大窗口可能让和减少，普通窗口失效。改为维护前缀和候选下标：队首检查是否达到阈值，队尾删除前缀和更大且位置更早的劣势候选。deque支持两端O(1)弹出。',
    'from collections import deque\ncandidates = deque()\ncandidates.popleft()\ncandidates.pop()',
    'nums 长度0～20000，元素绝对值≤10^6；1≤target≤10^12。返回和至少target的最短非空连续子数组长度，无解返回-1。允许负数。要求O(n)时间。',
    [('nums','list[int]','可含负数'),('target','int','正阈值')],
    [([[2,-1,2],3],3), ([[84,-37,32,40,95],167],3), ([[],1],-1),
     ([[1],1],1), ([[1,2],4],-1), ([[3,-5,4],4],1), ([[-2,-1],1],-1)],
    '''from collections import deque
prefix = [0]
for x in nums:
    prefix.append(prefix[-1] + x)
candidates = deque()
best = len(nums) + 1
for i, value in enumerate(prefix):
    while candidates and value - prefix[candidates[0]] >= target:
        best = min(best, i - candidates.popleft())
    while candidates and prefix[candidates[-1]] >= value:
        candidates.pop()
    candidates.append(i)
return -1 if best > len(nums) else best''',
    ['对每个右前缀i，需要旧前缀j满足prefix[i]-prefix[j]≥target。','新前缀更小且更靠右时，旧的大前缀永远不如它。','队首满足阈值就记录并弹出；队尾维持前缀和严格递增。'],
    '删除队尾时，新下标更晚且前缀不大，任何未来区间都能取得不少的和与更短的长度。队首一旦形成合法区间，未来与它配对只会更长，故可删除。每个下标只进出队列一次。',
    'O(n)','O(n)','答案长度是前缀下标之差，不加1；无解的返回值与上一题不同。',
    ['单调队列','前缀和','支配关系'],[19,21],'挑战')

# 32: monotone feasibility and exchange arguments.
add(32, '二分运力：按顺序在 D 天内运完包裹',
    '二分的对象不一定是数组下标，也可以是答案。容量增大时所需天数不会增加，形成先不可行、后可行的单调判定。固定容量后，每天尽量装入下一个包裹即可得到最少使用天数。',
    'while low < high:\n    mid = (low + high) // 2\n    if feasible(mid):\n        high = mid\n    else:\n        low = mid + 1',
    'weights 长度1～20000，包裹重量1～10^6；1≤days≤20000。每天运送原顺序的一段连续包裹，不可拆分，可以提前结束。返回在最多days天内运完的最小整数容量。',
    [('weights','list[int]','按运输顺序的正重量'),('days','int','最多天数')],
    [([[1,2,3,4,5,6,7,8,9,10],5],15), ([[3,2,2,4,1,4],3],6),
     ([[5],1],5), ([[1,2,3],1],6), ([[1,2,3],9],3), ([[2,2,2],2],4),
     ([[1]*10000,100],100)],
    '''low, high = max(weights), sum(weights)
while low < high:
    capacity = (low + high) // 2
    used, load = 1, 0
    for weight in weights:
        if load + weight > capacity:
            used += 1
            load = 0
        load += weight
    if used <= days:
        high = capacity
    else:
        low = capacity + 1
return low''',
    ['容量下界是最重包裹，上界是所有包裹总和。','写出固定容量时需要几天的顺序模拟。','可行时收缩右边界到mid，寻找第一个可行值。'],
    '固定容量下，每天尽量向后装不会让后续天数变多，因而模拟得到最少天数。可行容量向上封闭，二分保留包含最小可行值的区间直到收敛。',
    'O(n log S)，S为总重量','O(1)','超过容量时先开始新的一天，再放入当前包裹。',
    ['二分答案','单调可行性'],[20,24])

add(32, '向上取整判定：最小处理速度',
    '一次只能处理一个任务，最后不足一小时也占一小时，因此任务耗时是向上取整。整数公式(a+b-1)//b避免浮点误差。速度越高，总耗时越少，适合二分最小可行速度。',
    'hours = (amount + speed - 1) // speed\n# 等价于数学上的 ceil(amount / speed)',
    'piles 长度1～10000，每项1～10^9，表示独立任务工作量。每小时只能处理一个任务，最多处理speed单位；剩余小时不能转给其他任务。1≤hours≤10^12。返回能按时完成的最小正整数speed；若hours小于任务数则返回-1。',
    [('piles','list[int]','各任务工作量'),('hours','int','允许总小时')],
    [([[3,6,7,11],8],4), ([[30,11,23,4,20],5],30), ([[4,4],1],-1),
     ([[1],1],1), ([[9],2],5), ([[2,2],10],1), ([[10,10,10],6],5)],
    '''if hours < len(piles):
    return -1
low, high = 1, max(piles)
while low < high:
    speed = (low + high) // 2
    used = sum((x + speed - 1) // speed for x in piles)
    if used <= hours:
        high = speed
    else:
        low = speed + 1
return low''',
    ['至少每个任务都要一小时，先识别无解。','每个任务单独向上取整，不能先加总工作量再除速度。','在1到最大工作量之间找第一个耗时不超过hours的速度。'],
    '判定精确相加每个不可共享小时的任务耗时。该总和随速度增加不增，因此标准下界二分返回最小可行速度。',
    'O(n log M)，M为最大工作量','O(1)','sum(ceil(x/s))与ceil(sum(x)/s)不是同一个量。',
    ['整数向上取整','二分答案'],[1,20])

add(32, '最大化最小值：放置设备的最远间隔',
    '最大化最小距离，可以转为“至少相隔d能否放下k个”。按位置从左到右，每次放在第一个合法位置，给后续设备留下最多空间。可行性随d增大从真变假，二分时要使用上取整中点。',
    'mid = (low + high + 1) // 2\nif possible(mid):\n    low = mid\nelse:\n    high = mid - 1',
    'positions 为2～20000个互不相同的整数坐标，绝对值≤10^9，输入无序；2≤k≤len(positions)。选择k个位置，使相邻已选位置的最小距离最大，返回该最大整数距离。',
    [('positions','list[int]','互异坐标'),('k','int','设备数量')],
    [([[1,2,8,4,9],3],3), ([[0,10],2],10), ([[0,1,2],3],1),
     ([[-5,0,5],2],10), ([[1,3,7,10],3],3), ([[0,4,8,12],3],4), ([[9,1,5],2],8)],
    '''a = sorted(positions)
low, high = 0, a[-1] - a[0]
while low < high:
    distance = (low + high + 1) // 2
    count, previous = 1, a[0]
    for x in a[1:]:
        if x - previous >= distance:
            count += 1
            previous = x
    if count >= k:
        low = distance
    else:
        high = distance - 1
return low''',
    ['先排序，把目标改为检查一个候选间隔。','最左设备放最左位置，之后总选最早的合法位置。','寻找最后一个可行的距离，用上取整中点避免两端相邻时停滞。'],
    '把任意可行方案的第一个位置换成更早位置不损害后续间隔；逐个交换可知贪心可放数量最大。距离越小越容易可行，故二分找最大可行值。',
    'O(n log n+n log D)，D为坐标跨度','O(n)','这里寻找最后一个真，与最小可行值的二分更新方向不同。',
    ['二分答案','贪心判定','交换论证'],[20,24])

add(32, '隐式有序集合：乘法表第 K 小值',
    '不用生成整个乘法表。第i行是i、2i、3i……，不大于x的元素有min(cols,x//i)个。对值域二分，寻找累计数量第一次达到k的位置；重复数值也各占一个排名。',
    'count = sum(min(cols, value // row)\n            for row in range(1, rows + 1))',
    '1≤rows,cols≤1000，表格第i行第j列为i*j，行列从1开始；1≤k≤rows*cols。返回全部单元格值按非降序排列后的第k小值，重复值重复计数。',
    [('rows','int','行数'),('cols','int','列数'),('k','int','从1开始的排名')],
    [([3,3,5],3), ([2,3,6],6), ([1,1,1],1), ([1,7,4],4),
     ([2,2,3],2), ([3,4,1],1), ([4,3,12],12)],
    '''rows, cols = min(rows, cols), max(rows, cols)
low, high = 1, rows * cols
while low < high:
    mid = (low + high) // 2
    count = sum(min(cols, mid // i) for i in range(1, rows + 1))
    if count >= k:
        high = mid
    else:
        low = mid + 1
return low''',
    ['先回答有多少个单元格的值≤x。','一行的满足数量可直接整除得到，再与列数取最小值。','数量≥k时向左找，不能只找数量恰好等于k。'],
    '计数函数是精确的秩函数且单调不减。最小的计数至少为k的整数，恰好是第k小单元格的值，即使存在重复也成立。',
    'O(min(rows,cols) log(rows*cols))','O(1)','忘记按列数截断会统计表外元素。',
    ['隐式排名','值域二分'],[19,20],'挑战')

add(32, '闭区间贪心：最少刺穿点数',
    '一个点可以同时覆盖所有包含它的闭区间。按右端点排序，在最早结束且尚未覆盖的区间右端点放一个点，这个选择尽量向右，给后面的区间更多机会复用。注意闭区间端点相等时可以共用。',
    'ordered = sorted(intervals, key=lambda item: item[1])\nif point is None or left > point:\n    point = right',
    'intervals 为0～20000个闭区间[left,right]，整数端点绝对值≤10^9且left≤right。返回使每个区间至少包含一个所选点的最少点数。允许零长度区间和重复区间。',
    [('intervals','list[list[int]]','闭区间列表')],
    [([[[10,16],[2,8],[1,6],[7,12]]],2), ([[[1,2],[2,3]]],1), ([[]],0),
     ([[[1,1]]],1), ([[[1,2],[3,4],[5,6]]],3), ([[[0,9],[2,3],[3,4]]],1),
     ([[[-3,-1],[-1,0],[1,1]]],2)],
    '''point = None
answer = 0
for left, right in sorted(intervals, key=lambda item: item[1]):
    if point is None or left > point:
        point = right
        answer += 1
return answer''',
    ['最早结束的区间必须被某个点覆盖。','把覆盖它的点移动到它的右端点，不会损失任何后续区间的覆盖。','只在下一个区间左端点严格大于当前点时新增点。'],
    '对最早结束区间，任意最优解在其中必有一点；把该点移到右端点，对所有右端点更晚且原被覆盖的区间仍有效。反复应用此交换得到贪心解。',
    'O(n log n)','O(n)','闭区间用left>point判断不相交，不能写成>=。',
    ['区间贪心','闭区间端点'],[20,24])

add(32, '扫描线：会议室最少数量',
    '每个会议开始使占用数加一，结束使占用数减一。同一时刻应先结束再开始，因为时间区间采用左闭右开。把变化事件排序并累加，最大同时占用量就是需要的房间数。',
    'events.append((start, 1))\nevents.append((end, -1))\n# 元组排序在同一时间先处理 -1',
    'meetings 含0～20000个[start,end]，0≤start<end≤10^9，表示半开时间区间[start,end)。会议不能中断，可重复。返回最少会议室数；结束时间等于另一个开始时间时可以复用房间。',
    [('meetings','list[list[int]]','半开会议时间区间')],
    [([[[0,30],[5,10],[15,20]]],2), ([[[1,2],[2,3]]],1), ([[]],0),
     ([[[1,3]]],1), ([[[1,3],[1,3],[1,3]]],3), ([[[1,10],[2,9],[3,8]]],3),
     ([[[0,1],[0,2],[1,2]]],2)],
    '''events = []
for start, end in meetings:
    events.append((start, 1))
    events.append((end, -1))
active = best = 0
for _, delta in sorted(events):
    active += delta
    best = max(best, active)
return best''',
    ['把每个区间拆成两个占用变化事件。','同一时刻结束与开始如何排序取决于半开区间语义。','维护事件前缀和，取最大值。'],
    '任意时刻重叠的会议必须使用不同房间，峰值是下界。结束即释放的安排可在每次开始时分配空房，最多使用峰值间数，故该下界可达。',
    'O(n log n)','O(n)','同一时刻先处理开始会误把可复用的两个会议算作重叠。',
    ['扫描线','事件排序','半开区间'],[20,24])

add(32, '局部失败排除：环形加油站起点',
    '记录每站获得燃料减去行驶消耗。若从候选起点到i的累计量首次为负，这段内任何站都不能作成功起点，可以整体跳过。总差为负时必定无解；否则最后保留的候选能完成一圈。',
    'if tank < 0:\n    candidate = i + 1\n    tank = 0',
    'gas与cost等长，长度1～20000，每项0～10^6。到站i先获得gas[i]，再消耗cost[i]驶向下一站；从空油箱出发，油箱无限大。若存在多个可行起点，返回最小下标；无解返回-1。',
    [('gas','list[int]','每站加油量'),('cost','list[int]','驶向下一站耗油量')],
    [([[1,2,3,4,5],[3,4,5,1,2]],3), ([[2,3,4],[3,4,3]],-1),
     ([[0],[0]],0), ([[1],[2]],-1), ([[2,2],[1,1]],0), ([[0,1,1],[1,0,1]],1),
     ([[1,0,1],[1,1,0]],2)],
    '''total = tank = candidate = 0
for i, (gain, expense) in enumerate(zip(gas, cost)):
    difference = gain - expense
    total += difference
    tank += difference
    if tank < 0:
        candidate = i + 1
        tank = 0
return candidate if total >= 0 else -1''',
    ['先判断总燃料是否足以覆盖总消耗。','候选到i首次失败时，候选到中间站的前缀油量都非负，从中间出发只会更差。','一次扫描维护总差、当前段差与候选下标。'],
    '每次失败会证明此前所有尚未排除的起点均失败，故最终候选是最小可能起点。它位于首次全局最小前缀之后；总和非负保证从它到末尾再绕回的所有累计量都非负。',
    'O(n)','O(1)','累计量等于0不能判失败；用<0才能保留最小可行下标。',
    ['贪心排除','前缀最小值'],[19,24])

add(32, '频次瓶颈：带冷却时间的最短任务日程',
    '最频繁任务把时间轴分成若干间隔。若其频次为f，有c种任务并列最高，则至少需要(f-1)*(cooldown+1)+c个时隙；其他任务足够多时，时隙数又不能小于总任务数。',
    'from collections import Counter\nfrequency = Counter(tasks)\npeak = max(frequency.values(), default=0)',
    'tasks为0～20000个大写字母的列表，每项任务耗时1；同字母任务之间必须间隔至少cooldown个时隙，可空闲、可任意重排。0≤cooldown≤10000。返回完成全部任务的最少时隙数，空任务返回0。',
    [('tasks','list[str]','可重复的A～Z任务'),('cooldown','int','相同任务之间最少间隔')],
    [([list('AAABBB'),2],8), ([list('AAABBB'),0],6), ([[],3],0),
     ([['A'],100],1), ([list('AAAA'),2],10), ([list('ABC'),5],3), ([list('AAABBC'),1],6)],
    '''from collections import Counter
if not tasks:
    return 0
frequency = Counter(tasks)
peak = max(frequency.values())
tied = sum(count == peak for count in frequency.values())
return max(len(tasks), (peak - 1) * (cooldown + 1) + tied)''',
    ['先画出出现最多的任务，强制留出冷却间隔。','若多种任务都出现最多次，最后一组需要容纳它们全部。','其他任务可填空位；最终答案取频次下界与任务总量的最大值。'],
    '最高频任务的前f-1次之间都必须容纳完整冷却块，最后一轮有c项，给出频次下界。其余任务填入这些块，若仍有剩余可扩展各块而无需新增空闲，因而两个下界的最大值可以实现。',
    'O(n)','O(1)，至多26种任务','公式中的末项是最高频任务种数，不一定是1。',
    ['频次贪心','下界构造'],[6,11,24],'挑战')

add(32, '反悔贪心：到达目的地的最少加油次数',
    '先尽量向前行驶；当燃料不足时，再从已经经过的站里选择可加燃料最多的一站。这是“延后决定”的贪心，用最大堆实现。Python的heapq是最小堆，存负数即可优先取最大值。',
    'import heapq\nheapq.heappush(heap, -fuel)\nreach += -heapq.heappop(heap)',
    'target为1～10^9，start_fuel为0～10^9，每单位燃料行驶1距离。stations为0～2000个[position,fuel]，严格按互异position升序，0<position<target且1≤fuel≤10^9。油箱无限。每站只能加一次且获得全部fuel。返回最少加油次数，无解-1；到站时燃料为0也可加油。',
    [('target','int','目的地距离'),('start_fuel','int','初始燃料'),('stations','list[list[int]]','站点和可加燃料')],
    [([100,10,[[10,60],[20,30],[30,30],[60,40]]],2), ([100,1,[[10,100]]],-1),
     ([1,1,[]],0), ([10,0,[]],-1), ([10,5,[[5,5]]],1),
     ([30,10,[[5,5],[10,20],[20,5]]],1), ([25,5,[[5,5],[10,5],[15,10]]],3)],
    '''import heapq
heap = []
reach, index, stops = start_fuel, 0, 0
while reach < target:
    while index < len(stations) and stations[index][0] <= reach:
        heapq.heappush(heap, -stations[index][1])
        index += 1
    if not heap:
        return -1
    reach -= heapq.heappop(heap)
    stops += 1
return stops''',
    ['用reach表示当前燃料策略能到达的最远坐标。','把所有position≤reach的站加入可选堆。','无法直接到终点时，选过去站点中燃料最多的，增加一次停靠。'],
    '需要额外一次停靠时，所有已可达站点都能被选择，选最大燃料使可达范围至少不小于任意其他单次选择。交换最优方案的这次停靠不会变差，重复得到最少次数。',
    'O(n log n)','O(n)','可到达站点判断用<=；堆中负数弹出后应减去它来增加reach。',
    ['最大堆','反悔贪心'],[22,24],'挑战')

add(32, '截止日期排程：最多完成多少门课程',
    '按截止日期考虑课程，先尝试加入。当总时长超出当前截止日期时，移除已选课程里耗时最长的一门，这会为之后的课程保留最多时间。最大堆允许撤销较早的选择。',
    'selected = []\nheapq.heappush(selected, -duration)\nif elapsed > deadline:\n    elapsed += heapq.heappop(selected)',
    'courses为0～10000个[duration,deadline]，两个值均为1～10^9。从时间0开始，同一时刻只能修一门，课程不可中断，完成时刻≤deadline才有效。可选择和重排课程，返回最多完成数量。',
    [('courses','list[list[int]]','时长与完成截止时间')],
    [([[[100,200],[200,1300],[1000,1250],[2000,3200]]],3), ([[[5,4],[2,3]]],1),
     ([[]],0), ([[[1,1]]],1), ([[[3,2]]],0), ([[[5,5],[2,6],[2,6]]],2),
     ([[[2,2],[2,4],[2,6]]],3)],
    '''import heapq
selected = []
elapsed = 0
for duration, deadline in sorted(courses, key=lambda item: item[1]):
    elapsed += duration
    heapq.heappush(selected, -duration)
    if elapsed > deadline:
        elapsed += heapq.heappop(selected)
return len(selected)''',
    ['先按截止时间排序，使当前约束成为最紧的最新约束。','加入一门后超时，需要放弃一门；放弃最长的最有利。','用负时长堆维护已选课程，最终堆长度就是答案。'],
    '处理每个前缀时，已选集合在达到最大数量的同时保留最小总耗时。新课程能放下就增加数量，不能放下则删除最长者，在数量不变的候选中最节省时间；删除不会破坏之前的截止要求。',
    'O(n log n)','O(n)','删除的可能是当前课程，也可能是之前课程，不能只丢弃最新课程。',
    ['截止日期排序','反悔贪心','堆'],[20,22,24],'挑战')

# 33: state definitions before transitions; compressed DP with explicit order.
add(33, '最小结尾状态：严格递增子序列长度',
    '子序列可以跳过元素但保留顺序。tails[i]保存长度i+1的递增子序列能达到的最小结尾，结尾越小越有利于接入未来元素。bisect_left找第一个≥x的位置，所以相等元素会替换而不会增加长度。',
    'from bisect import bisect_left\ni = bisect_left(tails, x)\nif i == len(tails):\n    tails.append(x)',
    'nums 长度0～20000，整数绝对值≤10^9。返回严格递增子序列的最大长度，空列表返回0；相等元素不能彼此延长。要求O(n log n)时间。',
    [('nums','list[int]','原始顺序的整数列表')],
    [([[10,9,2,5,3,7,101,18]],4), ([[0,1,0,3,2,3]],4), ([[]],0),
     ([[2,2,2]],1), ([[5,4,3,2]],1), ([[-3,-2,-1]],3), ([[1,3,2,4]],3),
     ([list(range(10000))],10000)],
    '''from bisect import bisect_left
tails = []
for x in nums:
    i = bisect_left(tails, x)
    if i == len(tails):
        tails.append(x)
    else:
        tails[i] = x
return len(tails)''',
    ['先理解O(n²)定义：以某元素结尾的最长长度。','同长度方案只需保留结尾最小的那个。','用bisect_left找到替换位置，位于末尾时才扩展长度。'],
    '较小的结尾能接入原结尾能接入的所有未来数，所以替换不会损失最优长度。tails递增，二分定位正确，最后存在的最长状态长度就是答案。',
    'O(n log n)','O(n)','tails本身未必是原序列的一条有效子序列，它保存不同长度的最小结尾。',
    ['状态压缩','二分优化动态规划'],[20,24])

add(33, '编辑距离：两段文本的最少修改次数',
    'dp[i][j]表示把a的前i个字符变为b的前j个字符的最少操作数。最后一次操作只有删除、插入、替换三类；末字符相等时可以直接继承左上角。只保存上一行和当前行即可压缩空间。',
    'previous = list(range(len(b) + 1))\ncurrent = [i] + [0] * len(b)\nprevious, current = current, previous',
    'a、b为长度0～500的小写字母字符串。每次可插入、删除或替换一个字符，代价均为1；返回把a变为b的最小总代价。',
    [('a','str','原字符串'),('b','str','目标字符串')],
    [(['horse','ros'],3), (['intention','execution'],5), (['','abc'],3),
     (['abc',''],3), (['same','same'],0), (['a','b'],1), (['ab','ba'],2)],
    '''if len(a) < len(b):
    a, b = b, a
previous = list(range(len(b) + 1))
for i, x in enumerate(a, 1):
    current = [i] + [0] * len(b)
    for j, y in enumerate(b, 1):
        current[j] = min(previous[j] + 1, current[j - 1] + 1,
                         previous[j - 1] + (x != y))
    previous = current
return previous[-1]''',
    ['先考虑一个字符串为空时，需要多少次插入或删除。','最后一步分类：来自上方、左方或左上方。','当前行依赖上一行和本行左侧，因此从左到右计算。'],
    '任意最优编辑方案的最后一步属于列举的三类，删掉该步后必为相应前缀子问题的最优解，否则可替换以降低成本。取三类最小值覆盖全部方案。',
    'O(nm)','O(min(n,m))','交换两个字符不是本题允许的一次操作，ab到ba需要2步。',
    ['二维动态规划','滚动数组'],[4,24])

add(33, '完全背包计数：无序零钱组合',
    '求组合数量与求最少硬币使用不同状态。dp[s]为当前已处理面额组成s的方案数。外层枚举面额，内层金额递增，可重复使用当前面额；每个组合只在其最大已处理面额这一轮形成。',
    'dp = [0] * (amount + 1)\ndp[0] = 1\nfor coin in coins:\n    for value in range(coin, amount + 1):\n        dp[value] += dp[value - coin]',
    'coins为0～30种互不相同的正整数面额，每个面额1～10^9，每种无限枚；0≤amount≤1000。返回组成amount的组合数量，顺序不同视为同一组合。amount=0有一种空组合；结果不取模。复杂度按整数运算次数计。',
    [('coins','list[int]','互异正整数面额，最大1000'),('amount','int','目标金额')],
    [([[1,2,5],5],4), ([[2],3],0), ([[],0],1), ([[],4],0),
     ([[3],9],1), ([[2,1],4],3), ([[2,3,5],10],4)],
    '''dp = [0] * (amount + 1)
dp[0] = 1
for coin in coins:
    for value in range(coin, amount + 1):
        dp[value] += dp[value - coin]
return dp[amount]''',
    ['把最优值状态改为方案数，dp[0]初始化为1。','先枚举币种确保不会把1+2与2+1重复计数。','金额递增让本轮刚更新的状态继续使用同一币种。'],
    '每轮更新把不含当前币种的旧方案与至少含一枚当前币种的方案相加；后者与金额减去一个coin的方案一一对应。按币种构建使无序组合只被计数一次。',
    'O(c*amount)','O(amount)','把金额放外层、币种放内层通常会变成有序排列计数。',
    ['完全背包','组合计数','循环顺序'],[24])

add(33, '带障碍网格：一维状态计算路径数',
    '只能向右或向下时，一个格子的路径数等于上方加左方。压成一维后，更新前dp[c]是上方，已更新的dp[c-1]是左方；遇到障碍必须把dp[c]清零，防止旧路径穿过墙。',
    'if grid[r][c] == 1:\n    dp[c] = 0\nelif c > 0:\n    dp[c] += dp[c - 1]',
    'grid为1～50行、1～50列的矩形，0表示可走，1表示障碍。返回从左上角到右下角、每次只向右或向下移动一格的路径数量。起点或终点为障碍则0；单个可走格有1条不移动的路径。结果不取模。',
    [('grid','list[list[int]]','零一矩形网格')],
    [([[[0,0,0],[0,1,0],[0,0,0]]],2), ([[[0,1],[0,0]]],1), ([[[0]]],1),
     ([[[1]]],0), ([[[0,0,1]]],0), ([[[0],[0],[0]]],1), ([[[0,0],[0,1]]],0)],
    '''cols = len(grid[0])
dp = [0] * cols
dp[0] = 1
for row in grid:
    for c, cell in enumerate(row):
        if cell == 1:
            dp[c] = 0
        elif c:
            dp[c] += dp[c - 1]
return dp[-1]''',
    ['先写二维状态：走到当前格子的路径数。','按行扫描时只依赖上一行同列和本行前一列。','障碍清零；在扫描起点前用dp[0]=1表示一种初始方式。'],
    '每条到达可走格的路径最后一步来自上方或左方，两类互斥且穷尽。障碍没有到达方式。滚动数组在更新顺序下保留这两个正确子状态。',
    'O(rows*cols) 次整数运算','O(cols)','不能用continue跳过障碍而不清零，否则上一行的路径会穿越障碍。',
    ['网格动态规划','空间压缩'],[5,24])

add(33, '双状态：最大乘积连续子数组',
    '负数会把最大乘积变成最小、把最小变成最大，所以每个位置同时保存以它结尾的最大与最小乘积。下一状态从单独取当前数、接在旧最大后、接在旧最小后三种方式选择。',
    'high, low = max(x, high*x, low*x), min(x, high*x, low*x)\n# 右侧先整体求值，再同时赋值',
    'nums长度1～200，元素为-10～10的整数。返回非空连续子数组的最大乘积。允许零；结果不取模，按整数运算次数分析复杂度。',
    [('nums','list[int]','非空整数列表')],
    [([[2,3,-2,4]],6), ([[-2,0,-1]],0), ([[-2]],-2), ([[0]],0),
     ([[-2,3,-4]],24), ([[-1,-1,-1]],1), ([[0,-2,-3,0,4]],6)],
    '''high = low = best = nums[0]
for x in nums[1:]:
    high, low = max(x, high * x, low * x), min(x, high * x, low * x)
    best = max(best, high)
return best''',
    ['最大乘积遇到负数会变小，只记最大值不够。','同时维护以当前位置结尾的最小乘积。','使用同时赋值或临时变量，确保两个新状态都来自旧状态。'],
    '任何以当前元素结尾的非空区间，要么仅含当前元素，要么由前一位置的区间延长。乘上正数时极值来自同方向极值，负数时来自反方向极值，所以两个状态足够。',
    'O(n) 次整数运算','O(1) 个整数','初始化为0会在全负的单元素列表上错误地选择空子数组。',
    ['极值双状态','同时赋值'],[1,24])

add(33, '环形约束拆解：不取相邻位置的最大收益',
    '环形使第一个与最后一个位置相邻，不能同时选。任意合法解至少排除其中之一，因此分别求去掉末尾与去掉开头的线性问题，再取最大。线性状态只需保存前两个位置的最优值。',
    'skip, best = best, max(best, skip + value)',
    'values长度0～20000，每项0～10^9。选择若干位置，使任意两个被选位置在环上不相邻，返回最大收益；允许一个都不选。长度1时可选唯一位置，长度2时最多选一个。',
    [('values','list[int]','环形各位置收益')],
    [([[2,3,2]],3), ([[1,2,3,1]],4), ([[]],0), ([[7]],7),
     ([[5,8]],8), ([[0,0,0]],0), ([[5,1,1,5]],6)],
    '''if len(values) <= 1:
    return sum(values)
def linear(start, end):
    previous = best = 0
    for i in range(start, end):
        previous, best = best, max(best, previous + values[i])
    return best
return max(linear(0, len(values) - 1), linear(1, len(values)))''',
    ['先写直线上的不相邻选取状态。','环的额外冲突只发生在首尾之间。','分别排除首、尾求两次，单元素要单独处理。'],
    '所有环形可行解都属于“未选首”或“未选尾”至少一种，两类线性最优值的最大值覆盖全体。线性递推按最后一个位置选或不选分类。',
    'O(n)','O(1)','直接对整圈运行线性递推可能同时选首尾。',
    ['环形动态规划','分类讨论'],[24])

add(33, '交易状态机：卖出后冷却一天',
    '用状态表达交易规则：hold为持股、sold为今天刚卖出、rest为不持股且可买入。买入只能来自昨天rest；昨天sold只能进入今天rest，所以禁止卖出后第二天立刻买入。每一步都从旧状态同时转移。',
    'hold, sold, rest = max(hold, rest - price), hold + price, max(rest, sold)',
    'prices长度0～20000，每项0～10^6。每天可买一股、卖出持有的一股或不操作；最多持一股，卖出后的下一天不能买入。可多次交易，初始无持股，返回最终不持股的最大利润。无手续费。',
    [('prices','list[int]','每日股价')],
    [([[1,2,3,0,2]],3), ([[1]],0), ([[]],0), ([[5,4,3]],0),
     ([[1,2]],1), ([[1,2,0,3]],3), ([[0,0,0]],0)],
    '''hold = sold = float('-inf')
rest = 0
for price in prices:
    hold, sold, rest = max(hold, rest - price), hold + price, max(rest, sold)
return max(rest, sold)''',
    ['按是否持股和是否刚卖出区分状态。','买入只能从rest来；卖出只能从hold来。','同时更新三个状态，最终答案只从不持股状态中选。'],
    '三个状态穷尽每一天合法结束情形。转移分别枚举保持、买入、卖出和冷却结束，且只允许规则要求的来源，因此既不遗漏合法策略也不引入非法交易。',
    'O(n)','O(1)','先更新rest再用它更新hold会让昨日刚卖出的资金立即买入，破坏冷却期。',
    ['状态机动态规划','冷却约束'],[24],'挑战')

add(33, '零一背包判定：分成两个等和集合',
    '总和为偶数时，只需判断能否选一部分元素凑出总和一半。每个元素只能用一次，所以一维布尔背包必须倒序更新。正序更新会让同一个元素在本轮被多次使用。',
    'for value in nums:\n    for total in range(target, value - 1, -1):\n        possible[total] |= possible[total - value]',
    'nums长度0～200，每项0～100，按下标区分元素。判断能否分成两个不相交且覆盖所有下标的组，使两组元素和相同；组可以为空，因此空列表返回True。返回bool。',
    [('nums','list[int]','非负整数列表')],
    [([[1,5,11,5]],True), ([[1,2,3,5]],False), ([[]],True), ([[0]],True),
     ([[2]],False), ([[1,2,5]],False), ([[3,3,3,3]],True)],
    '''total = sum(nums)
if total % 2:
    return False
target = total // 2
possible = [False] * (target + 1)
possible[0] = True
for value in nums:
    for current in range(target, value - 1, -1):
        possible[current] |= possible[current - value]
return possible[target]''',
    ['如果总和是奇数，直接失败。','用possible[s]表示当前已处理元素能否凑出s。','金额倒序扫描，保证来源还没有使用当前元素。'],
    '每个元素有选与不选两种情况，更新取两者逻辑或。倒序使选取来源保持在上一轮，从而每个下标最多使用一次。凑到一半后剩余下标自动构成另一半。',
    'O(nS)，S为总和一半','O(S)','元素为0时状态应保持正确；不要把空组误判为非法。',
    ['零一背包','布尔状态','倒序更新'],[24])

add(33, '回文分割：最少切割次数',
    '先预处理每个区间是否回文，再求前缀的最少切割。若text[start:end+1]是回文，则可以接在start之前的最优分割后；start=0表示整段无需切割。二维回文状态由更短的内部区间决定。',
    'pal[left][right] = (text[left] == text[right] and\n                       (right - left < 2 or pal[left + 1][right - 1]))',
    'text为长度0～500的小写字符串。将它切成若干非空回文片段，返回最少切割次数。整串是回文或空串时返回0；切成k段需要k-1次切割。',
    [('text','str','待分割字符串')],
    [(['aab'],1), (['abccbc'],2), ([''],0), (['a'],0), (['abba'],0),
     (['abc'],2), (['banana'],1)],
    '''n = len(text)
if n == 0:
    return 0
pal = [[False] * n for _ in range(n)]
cuts = [0] * n
for right in range(n):
    cuts[right] = right
    for left in range(right + 1):
        if text[left] == text[right] and (right - left < 2 or pal[left + 1][right - 1]):
            pal[left][right] = True
            cuts[right] = min(cuts[right], 0 if left == 0 else cuts[left - 1] + 1)
return cuts[-1]''',
    ['预处理回文，避免每次用切片反转重复检查。','固定最后一段的左端点，前面的部分交给前缀最优值。','left=0时不需要新增切割，其他情况增加1。'],
    '回文递推检查两端相等且内部回文。任何最优分割都有唯一最后一段，枚举其起点并加上前缀最优切割可覆盖全部方案。',
    'O(n²)','O(n²)','切割次数比片段数少1；空串必须提前处理。',
    ['区间预处理','前缀动态规划'],[4,24],'挑战')

add(33, '倒序字符串计数：组成目标的子序列数量',
    'dp[j]表示从已扫描源字符串中选出目标前j个字符的方法数。当前字符等于target[j-1]时，可以追加到旧dp[j-1]的每个方案。j必须倒序，避免源中的一个字符被同一轮使用多次。',
    'dp[0] = 1\nfor char in source:\n    for j in range(len(target), 0, -1):\n        if char == target[j - 1]:\n            dp[j] += dp[j - 1]',
    'source、target为长度0～500的小写字符串。选择source中严格递增的下标使对应字符恰为target，返回选择方案数；下标不同视为不同方案。空target有1种空选择；结果不取模。',
    [('source','str','源字符串'),('target','str','目标字符串')],
    [(['rabbbit','rabbit'],3), (['babgbag','bag'],5), (['',''],1),
     (['','a'],0), (['abc',''],1), (['aaa','aa'],3), (['abc','abcd'],0)],
    '''dp = [0] * (len(target) + 1)
dp[0] = 1
for char in source:
    for j in range(len(target), 0, -1):
        if char == target[j - 1]:
            dp[j] += dp[j - 1]
return dp[-1]''',
    ['区分跳过当前源字符与选取它两类方案。','只有字符相等时才能从较短目标状态转移。','倒序更新目标长度，保持每个源下标最多用一次。'],
    '不选当前源字符保留旧计数；选择时与较短目标的旧方案一一对应，两类按是否包含当前下标互斥。倒序保证读取旧状态。',
    'O(nm) 次整数运算','O(m)','空目标的计数是1不是0，它是所有非空方案的递推起点。',
    ['子序列计数','倒序压缩'],[24],'挑战')

# 34: graph state design, tree DP, and constrained shortest paths.
add(34, '两次搜索：无权树的直径',
    '树中任意两点只有一条简单路径。从任意点找到最远点a，再从a找最远点，其距离就是直径。使用显式队列避免深链触发Python递归深度限制；距离按边数计。',
    'from collections import deque\nqueue = deque([start])\nwhile queue:\n    node = queue.popleft()',
    '1≤n≤20000，节点为0～n-1；edges含n-1条无向边，保证构成树。返回树中任意两点最短路径的最大边数。单节点树返回0。',
    [('n','int','节点数'),('edges','list[list[int]]','树的无向边')],
    [([4,[[0,1],[1,2],[1,3]]],2), ([5,[[0,1],[1,2],[2,3],[3,4]]],4),
     ([1,[]],0), ([2,[[0,1]]],1), ([4,[[0,1],[0,2],[0,3]]],2),
     ([6,[[0,1],[1,2],[2,3],[1,4],[4,5]]],4),
     ([10000,[[i,i+1] for i in range(9999)]],9999)],
    '''from collections import deque
graph = [[] for _ in range(n)]
for u, v in edges:
    graph[u].append(v)
    graph[v].append(u)
def farthest(start):
    distance = [-1] * n
    distance[start] = 0
    queue = deque([start])
    last = start
    while queue:
        last = queue.popleft()
        for neighbor in graph[last]:
            if distance[neighbor] < 0:
                distance[neighbor] = distance[last] + 1
                queue.append(neighbor)
    return last, distance[last]
endpoint, _ = farthest(0)
return farthest(endpoint)[1]''',
    ['树的直径端点通常出现在某次最远点搜索的结果中。','先从0搜索最远点，再以该点作为新起点。','邻接表加BFS距离数组即可；无需对每个节点都搜索一次。'],
    '树的唯一路径性质保证从任意起点取得的最远点是某条直径的端点：若不在直径端点，可沿分叉路径延长并与最远性矛盾。从该端点取最大距离便得到直径。',
    'O(n)','O(n)','此两次搜索结论依赖树结构，不能原样用于一般有环图。',
    ['树直径','迭代搜索'],[22,23])

add(34, '树形动态规划：不相邻节点的最大权重',
    '给树定根后，节点只与父子冲突。take[u]表示选u的子树最优值，此时孩子都不能选；skip[u]表示不选u，每个孩子可以自由选更优状态。先生成遍历顺序，再反向处理，保证孩子早于父亲完成。',
    'for node in reversed(order):\n    take[node] += skip[child]\n    skip[node] += max(take[child], skip[child])',
    'weights长度1～20000，各项绝对值≤10^6；节点0～n-1，edges构成无向树。选择一组互不相邻节点使权重和最大，允许空集。返回最大和；负权节点可以不选。',
    [('weights','list[int]','各节点可正可负的权重'),('edges','list[list[int]]','树边')],
    [([[3,2,3],[[0,1],[1,2]]],6), ([[5,4,4],[[0,1],[0,2]]],8),
     ([[-2],[]],0), ([[7],[]],7), ([[1,2],[[0,1]]],2),
     ([[0,0,0],[[0,1],[1,2]]],0), ([[10,-1,5,5],[[0,1],[1,2],[1,3]]],20)],
    '''n = len(weights)
graph = [[] for _ in range(n)]
for u, v in edges:
    graph[u].append(v)
    graph[v].append(u)
parent = [-1] * n
order = [0]
for u in order:
    for v in graph[u]:
        if v != parent[u]:
            parent[v] = u
            order.append(v)
take = weights[:]
skip = [0] * n
for u in reversed(order):
    for v in graph[u]:
        if parent[v] == u:
            take[u] += skip[v]
            skip[u] += max(take[v], skip[v])
return max(take[0], skip[0])''',
    ['把是否选择当前节点作为两个状态。','选父节点就只能使用每个孩子的skip；不选则取孩子两状态最大值。','反转一次父先于子的遍历顺序，即可迭代完成后序计算。'],
    '树的不同子树之间没有边，因此在固定当前节点是否被选后，子树可独立优化。两种状态穷尽当前节点选择，合并孩子最优值即为全子树最优。',
    'O(n)','O(n)','只按节点权重贪心选最大的会忽略它阻止多个邻居的代价。',
    ['树形动态规划','后序遍历'],[22,23,24],'挑战')

add(34, '隐式图 BFS：单词接龙最短长度',
    '把字典中的单词视为节点，一次只改一个字符就是一条边。无需显式构建所有两两关系，取出单词时枚举每个位置的26种替换。BFS首次访问终点即得到最短转换链。',
    'candidate = word[:i] + letter + word[i + 1:]\nif candidate in remaining:\n    remaining.remove(candidate)',
    'begin、end与words中的单词均为相同长度1～8的小写词，words最多2000个，可重复。每次改一个字符，改变后的词必须在words中。返回最短链的单词数量（包含首尾），无解0；begin==end时返回1，不要求它在words中。',
    [('begin','str','起始单词'),('end','str','目标单词'),('words','list[str]','允许中间词和终点的词表')],
    [(['hit','cog',['hot','dot','dog','lot','log','cog']],5),
     (['hit','cog',['hot','dot','dog']],0), (['a','a',[]],1),
     (['a','c',['b','c']],2), (['ab','cd',['cd']],0),
     (['ab','ac',['ac','ac']],2), (['aa','bb',['ab','bb']],3)],
    '''from collections import deque
if begin == end:
    return 1
remaining = set(words)
if end not in remaining:
    return 0
remaining.discard(begin)
queue = deque([(begin, 1)])
while queue:
    word, length = queue.popleft()
    for i in range(len(word)):
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            candidate = word[:i] + letter + word[i + 1:]
            if candidate in remaining:
                if candidate == end:
                    return length + 1
                remaining.remove(candidate)
                queue.append((candidate, length + 1))
return 0''',
    ['一条转换边的代价相同，使用BFS。','枚举修改位置和新字母，比扫描整个字典找邻居更直接。','入队时就从未访问集合删除，避免重复入队。'],
    '枚举得到且仅得到字典中与当前词相差一个字符的邻居。BFS按转换次数逐层扩展，首次到达终点具有最少边数，加1得到链中单词数量。',
    'O(26*N*L²)，含字符串切片与哈希','O(NL)','答案数单词而不是改动次数；起终点相同需单独处理。',
    ['隐式图','广度优先搜索'],[4,6,23])

add(34, '逆向泛洪：捕获被包围的区域',
    '直接检查每块是否被包围不如先找不会被捕获的格子：所有与边界O连通的O都安全。从全部边界O开始搜索，剩下的O才需要翻成X。这里用字符串输入、字符列表临时编辑、最后join恢复字符串。',
    'board = [list(row) for row in grid]\nreturn ["".join(row) for row in board]',
    'grid为0～100行的字符串列表；非空时各行等长、长度1～100且仅含O和X，组成矩形。上下左右连通，与任何边界O连通的O保持不变，其余O改为X。返回新字符串列表；空输入返回[]。',
    [('grid','list[str]','由O和X组成的矩形')],
    [([['XXXX','XOOX','XXOX','XOXX']],['XXXX','XXXX','XXXX','XOXX']),
     ([['OO','OO']],['OO','OO']), ([[]],[]), ([['O']],['O']),
     ([['XXX','XOX','XXX']],['XXX','XXX','XXX']),
     ([['XOX','XOX','XXX']],['XOX','XOX','XXX']), ([['XXX']],['XXX'])],
    '''if not grid:
    return []
rows, cols = len(grid), len(grid[0])
safe = set()
stack = []
for r in range(rows):
    for c in range(cols):
        if (r in (0, rows - 1) or c in (0, cols - 1)) and grid[r][c] == 'O':
            safe.add((r, c))
            stack.append((r, c))
while stack:
    r, c = stack.pop()
    for nr, nc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 'O' and (nr,nc) not in safe:
            safe.add((nr,nc))
            stack.append((nr,nc))
return [''.join('O' if (r,c) in safe else 'X' for c in range(cols)) for r in range(rows)]''',
    ['被包围等价于无法到达边界。','从边界上的所有O开始标记安全区域。','输出时只保留已标记的O，其余位置全部为X。'],
    '泛洪恰好标记与边界O处于同一连通分量的格子，这些区域均不封闭。未标记O不与边界相连，按定义全部被包围，翻转正确。',
    'O(rows*cols)','O(rows*cols)','对角线接触不表示连通，只能走上下左右。',
    ['逆向思考','多源泛洪'],[5,23])

add(34, '零一 BFS：最少移除障碍数',
    '边权只有0和1时，可以用双端队列替代堆。经过空格不增加代价，把新状态放队首；经过障碍增加1，放队尾。距离数组允许松弛，不能像普通无权BFS那样仅用第一次发现标记。',
    'if weight == 0:\n    queue.appendleft((nr, nc))\nelse:\n    queue.append((nr, nc))',
    'grid为1～100行、1～100列的零一矩形，起点左上角和终点右下角均保证为0。可上下左右移动，进入1格需要移除该障碍。返回连接起终点最少要移除的障碍数量；单格返回0。',
    [('grid','list[list[int]]','0为空地，1为障碍')],
    [([[[0,1,1],[1,1,0],[1,1,0]]],2), ([[[0,0],[1,0]]],0), ([[[0]]],0),
     ([[[0,1,0]]],1), ([[[0],[1],[1],[0]]],2),
     ([[[0,1,0],[0,1,0],[0,0,0]]],0), ([[[0,1],[1,0]]],1)],
    '''from collections import deque
rows, cols = len(grid), len(grid[0])
distance = [[float('inf')] * cols for _ in range(rows)]
distance[0][0] = 0
queue = deque([(0,0,0)])
while queue:
    cost, r, c = queue.popleft()
    if cost != distance[r][c]:
        continue
    for nr, nc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
        if 0 <= nr < rows and 0 <= nc < cols:
            new_cost = cost + grid[nr][nc]
            if new_cost < distance[nr][nc]:
                distance[nr][nc] = new_cost
                state = (new_cost,nr,nc)
                if grid[nr][nc] == 0:
                    queue.appendleft(state)
                else:
                    queue.append(state)
return distance[-1][-1]''',
    ['把进入空格看成权重0的边，进入障碍看成权重1。','队首优先处理不增加代价的转移。','仅在新距离更小时入队，并忽略已被更短距离替代的旧状态。'],
    '双端队列按当前最短代价的相邻两层维护候选，零权转移留在本层，一权转移进入下一层。其松弛顺序满足最短路贪心性质，每格最终得到最小障碍代价。',
    'O(rows*cols)','O(rows*cols)','普通BFS最小化的是步数，本题要最小化进入障碍的次数。',
    ['零一BFS','最短路松弛'],[21,23],'挑战')

add(34, '层次拓扑：全部课程最少学期数',
    '没有先修依赖的课程可以同一学期并行。每一轮固定当前队列长度，只处理这一批；本轮释放的课程必须等下一学期。若处理数量小于课程总数，说明剩余部分存在环。',
    'for _ in range(len(queue)):\n    course = queue.popleft()\n    # 新解锁的课程留到下一轮',
    '0≤n≤20000，课程编号0～n-1。relations最多50000条互不重复的[u,v]，表示修完u后的下个学期才能修v；允许自环。每学期可并行任意多课程，每课恰耗1学期。返回完成全部课程最小学期数，有环返回-1，n=0返回0。',
    [('n','int','课程数'),('relations','list[list[int]]','有向先修关系')],
    [([3,[[0,2],[1,2]]],2), ([3,[[0,1],[1,2],[2,0]]],-1), ([0,[]],0),
     ([4,[]],1), ([1,[[0,0]]],-1), ([4,[[0,1],[1,2],[2,3]]],4),
     ([5,[[0,2],[1,2],[2,3]]],3)],
    '''from collections import deque
graph = [[] for _ in range(n)]
indegree = [0] * n
for u, v in relations:
    graph[u].append(v)
    indegree[v] += 1
queue = deque(i for i in range(n) if indegree[i] == 0)
semesters = done = 0
while queue:
    semesters += 1
    for _ in range(len(queue)):
        u = queue.popleft()
        done += 1
        for v in graph[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                queue.append(v)
return semesters if done == n else -1''',
    ['无先修课程可以在第一学期一起学。','将拓扑排序改为逐层处理队列。','记录已修课程数量，用它区分完成全部和陷入依赖环。'],
    '每课只能在全部前驱完成后的下一学期开始，分层拓扑恰好在这个最早学期安排它。所有课都按最早可行时间安排，所以总学期最少；未处理节点对应环阻塞。',
    'O(n+m)','O(n+m)','不能在同一学期继续处理本轮刚解锁的课程。',
    ['拓扑分层','并行依赖'],[23])

add(34, '边数受限最短路：最多 K 次中转',
    '最便宜但用掉太多中转的路径，未必能作为后续路径的最佳前缀。按允许边数进行动态规划：第t轮只使用上一轮距离来松弛边。复制数组保留使用更少边的方案，并防止一轮内连走多条边。',
    'updated = distance[:]\nfor u, v, price in flights:\n    updated[v] = min(updated[v], distance[u] + price)',
    '1≤n≤100，flights最多1000条有向[u,v,price]，price为1～10^6，允许重边；0≤src,dst<n，0≤k≤100。返回从src到dst最多k个中间停靠点（最多k+1条边）的最小总价，无解-1；src==dst可不乘机，返回0。',
    [('n','int','城市数'),('flights','list[list[int]]','有向航线与价格'),('src','int','起点'),('dst','int','终点'),('k','int','最多中转次数')],
    [([3,[[0,1,100],[1,2,100],[0,2,500]],0,2,1],200),
     ([3,[[0,1,100],[1,2,100],[0,2,500]],0,2,0],500),
     ([2,[],0,1,2],-1), ([1,[],0,0,0],0),
     ([3,[[0,1,1],[1,2,1]],0,2,0],-1),
     ([2,[[0,1,7],[0,1,3]],0,1,0],3),
     ([4,[[0,1,1],[1,2,1],[2,3,1],[0,3,10]],0,3,1],10)],
    '''distance = [float('inf')] * n
distance[src] = 0
for _ in range(k + 1):
    updated = distance[:]
    for u, v, price in flights:
        updated[v] = min(updated[v], distance[u] + price)
    distance = updated
return -1 if distance[dst] == float('inf') else distance[dst]''',
    ['最多k次中转意味着最多k+1条边。','状态增加允许边数这一层；每轮从上一轮转移。','使用新数组更新，结束一轮后整体替换。'],
    '归纳地，第t轮距离保存最多t条边的最小费用。任何最多t+1条边路径或者已经在旧状态中，或者由最多t条边路径加最后一条边组成，因此一次全边松弛得到下一层。',
    'O((k+1)(n+m))','O(n)','原地松弛会在一轮内沿多条边传播，从而违反中转次数限制。',
    ['Bellman-Ford分层','约束最短路'],[23,24],'挑战')

add(34, '函数图：最长有向环长度',
    '每个节点最多一条出边的图，可沿唯一后继不断走。用全局访问时间戳避免重复处理，再记录当前这条路径的开始时间。若走到时间戳不小于本轮起点的节点，就回到了当前路径，形成一个环。',
    'start_time = clock\nstamp[node] = clock\nclock += 1\n# stamp[node] >= start_time 表示属于当前这轮路径',
    'next_nodes长度0～20000，第i项为-1或合法节点下标；-1表示无出边，允许自环。返回图中最长有向环的节点数量，无环返回-1。',
    [('next_nodes','list[int]','每个节点的唯一后继或-1')],
    [([[3,3,4,2,3]],3), ([[2,-1,3,1]],-1), ([[]],-1), ([[0]],1),
     ([[-1]],-1), ([[1,0,3,2]],2), ([[1,2,3,1]],3)],
    '''stamp = [0] * len(next_nodes)
clock = 1
best = -1
for start in range(len(next_nodes)):
    if stamp[start]:
        continue
    beginning = clock
    node = start
    while node != -1 and stamp[node] == 0:
        stamp[node] = clock
        clock += 1
        node = next_nodes[node]
    if node != -1 and stamp[node] >= beginning:
        best = max(best, clock - stamp[node])
return best''',
    ['沿后继走到终点、旧路径或当前路径中的点。','全局访问标记用于保证每个节点只处理一次。','用本轮起始时间区分旧路径与当前路径，环长是时间戳差。'],
    '唯一后继使每条遍历在首次重复时就确定进入哪个环。只有回到当前遍历的节点才产生新环，时间戳差精确数出环节点数；旧路径的环早已处理。',
    'O(n)','O(n)','遇到已访问节点不一定发现新环，它可能属于另一条早先处理的路径。',
    ['函数图','时间戳访问'],[21,23])

add(34, '状态扩展 BFS：拿齐钥匙的最短步数',
    '同一个格子拿着不同钥匙时，可走的门不同，因此访问状态必须是(行,列,钥匙集合)。最多6种钥匙可用整数的6个位表示；OR加入钥匙，AND检查门是否可开。BFS在扩展状态图上仍求最少步数。',
    'mask |= 1 << (ord(char) - ord("a"))\ncan_open = bool(mask & (1 << (ord(door) - ord("A"))))',
    'grid为1～20行、1～20列字符串矩形，恰有一个@起点；.为空地，#为墙，a～f为钥匙，A～F为门，每种钥匙至多一枚。允许有无对应钥匙的门（永远不可通行）。上下左右移动，拿到钥匙可重复开对应门且不消耗。返回拿齐所有现有钥匙的最短步数，无解-1；无钥匙0。',
    [('grid','list[str]','带钥匙与门的网格')],
    [([['@.a..','###.#','b.A.B']],8), ([['@..aA','..B#.','....b']],6),
     ([['@']],0), ([['@Aa']],-1), ([['@a']],1), ([['@..f']],3), ([['@#a']],-1)],
    '''from collections import deque
rows, cols = len(grid), len(grid[0])
goal = 0
for r, row in enumerate(grid):
    for c, char in enumerate(row):
        if char == '@':
            start = (r,c)
        elif 'a' <= char <= 'f':
            goal |= 1 << (ord(char) - ord('a'))
queue = deque([(start[0],start[1],0,0)])
seen = {(start[0],start[1],0)}
while queue:
    r,c,mask,steps = queue.popleft()
    if mask == goal:
        return steps
    for nr,nc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
        if not (0 <= nr < rows and 0 <= nc < cols):
            continue
        char = grid[nr][nc]
        if char == '#' or ('A' <= char <= 'F' and not mask & (1 << (ord(char)-ord('A')))):
            continue
        new_mask = mask
        if 'a' <= char <= 'f':
            new_mask |= 1 << (ord(char)-ord('a'))
        state = (nr,nc,new_mask)
        if state not in seen:
            seen.add(state)
            queue.append((nr,nc,new_mask,steps+1))
return -1''',
    ['仅记录坐标会误剪掉拿到钥匙后返回同一格的必要路径。','把钥匙集合编码为位掩码，构成三维访问状态。','目标掩码来自实际出现的钥匙，不要假设字母连续。'],
    '扩展状态完整记录影响未来动作的钥匙信息，每个合法移动对应一条单位权边。BFS首次达到目标钥匙掩码的状态即为最少步数。',
    'O(rows*cols*2^K)，K≤6','O(rows*cols*2^K)','钥匙可能只有f而没有a，目标掩码不能简单写成(1<<钥匙数)-1。',
    ['状态压缩搜索','位掩码','BFS'],[23,24],'挑战')

add(34, '并查集扩展：增量岛屿数量',
    '陆地逐个出现时，反复全图搜索很浪费。每次新陆地先增加一个连通分量，再与已有相邻陆地合并；每次成功合并减少一个分量。重复添加同一格不改变数量。',
    'if find(a) != find(b):\n    parent[find(a)] = find(b)\n    components -= 1',
    '1≤rows,cols≤200，初始全为水；positions最多20000个合法[r,c]，依次将该格设为陆地，允许重复。上下左右相邻陆地属于一个岛。返回每次操作后的岛屿数量列表。',
    [('rows','int','行数'),('cols','int','列数'),('positions','list[list[int]]','添加陆地的顺序')],
    [([3,3,[[0,0],[0,1],[1,2],[2,1],[1,1]]],[1,1,2,3,1]),
     ([1,1,[[0,0],[0,0]]],[1,1]), ([2,2,[]],[]),
     ([2,2,[[0,0],[1,1]]],[1,2]), ([1,3,[[0,0],[0,2],[0,1]]],[1,2,1]),
     ([2,2,[[0,0],[0,1],[1,0],[1,1]]],[1,1,1,1]),
     ([3,1,[[0,0],[2,0],[1,0],[1,0]]],[1,2,1,1])],
    '''parent = {}
size = {}
answer = []
count = 0
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x
for r,c in positions:
    cell = (r,c)
    if cell not in parent:
        parent[cell] = cell
        size[cell] = 1
        count += 1
        for neighbor in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
            if neighbor in parent:
                a,b = find(cell),find(neighbor)
                if a != b:
                    if size[a] < size[b]:
                        a,b = b,a
                    parent[b] = a
                    size[a] += size[b]
                    count -= 1
    answer.append(count)
return answer''',
    ['把当前岛屿数维护为变量，不必每次重新数。','新格子先是独立分量，与每个已经存在的邻居尝试union。','只在两个根不同且真正合并时减1；重复添加只追加原计数。'],
    '新陆地唯一可能新增的连接是与四个邻居的边。先建立单点分量再合并这些边，得到的分量恰为新图的连通分量；成功合并一次恰减少一个岛。',
    'O(q α(q)) 平均，α为反阿克曼函数','O(q)','相邻的多个格子可能属于同一岛，不能每遇到一个邻居就减少计数。',
    ['动态连通性','并查集'],[22,23],'挑战')


# 35: string structure, bit representations, and exact arithmetic.
add(35, 'KMP 入门：找出所有重叠匹配',
    '暴力匹配失败后会重新比较已经相等的字符。KMP先为模式串建立前缀函数pi：pi[i]是模式串前i+1个字符中，既是前缀又是后缀的最长真子串长度。失配时把已匹配长度j退到pi[j-1]，保留仍然可能匹配的边界。完整匹配后也退回边界，因而不会漏掉重叠出现。',
    'while j and text_char != pattern[j]:\n    j = pi[j - 1]\nif text_char == pattern[j]:\n    j += 1',
    'text和pattern只含小写英文字母，长度分别为0～10000、1～10000。返回pattern在text中全部出现的起始下标，按升序排列，允许重叠；无匹配返回[]。目标时间O(len(text)+len(pattern))，请自行构造前缀函数。',
    [('text','str','被搜索文本'),('pattern','str','非空模式串')],
    [(['aaaaa','aaa'],[0,1,2]), (['ababcabcabababd','ababd'],[10]),
     (['','a'],[]), (['abc','abcd'],[]), (['abc','x'],[]),
     (['ababab','ab'],[0,2,4]), (['a','a'],[0]), (['ababa','aba'],[0,2])],
    '''pi = [0] * len(pattern)
j = 0
for i in range(1, len(pattern)):
    while j and pattern[i] != pattern[j]:
        j = pi[j - 1]
    if pattern[i] == pattern[j]:
        j += 1
    pi[i] = j
answer = []
j = 0
for i, char in enumerate(text):
    while j and char != pattern[j]:
        j = pi[j - 1]
    if char == pattern[j]:
        j += 1
    if j == len(pattern):
        answer.append(i - len(pattern) + 1)
        j = pi[j - 1]
return answer''',
    ['先想清楚失配时，已匹配部分的哪些后缀还能成为下一次匹配的前缀。','用pi记录最长边界，失配沿pi[j-1]逐级回退。','找到完整匹配后记录起点，并回退到pi[j-1]以保留重叠部分。'],
    '扫描文本时，j始终是当前文本后缀与模式前缀相等的最长长度；前缀函数列举所有可能保留的较短边界，回退不会跳过候选。j到达模式长度恰表示一次匹配。j每次增加至多1，总回退次数受总增加次数约束。',
    'O(n+m)','O(m)，不计输出','完整匹配后若直接清零，会漏掉aaaaa中重叠的aaa。',
    ['前缀函数','字符串匹配','摊还分析'],[4,19],'挑战')

add(35, '前缀树：重复词条的前缀计数',
    '前缀树把共同前缀共享为一条路径。每经过一个节点，就增加该节点的通过次数；重复词也重复计数。根表示空前缀，因此所有词都经过根。查询只走前缀长度的路径，不必扫描全部词。节点可以用children和count两个字典字段表示。',
    'node = {"children": {}, "count": 0}\nchild = node["children"].setdefault(char, {"children": {}, "count": 0})',
    'words和prefixes各最多3000个字符串，只含小写英文字母；单串长度0～100，各列表字符总数≤100000。words允许空串和重复串。对每个prefixes元素，返回words中以它开头的词条数量，重复词条分别计数；空前缀匹配所有词。',
    [('words','list[str]','允许重复的词条'),('prefixes','list[str]','按给定顺序查询的前缀')],
    [([['app','apple','app','bat'],['app','ap','b','']], [3,3,1,4]),
     ([['','a'],['','a','aa']], [2,1,0]), ([[],['','x']], [0,0]),
     ([['abc'],[]],[]), ([['a','a'],['a','b']],[2,0]),
     ([['abc','abd','b'],['ab','abc','abcd']],[2,1,0]), ([[''],['','a']],[1,0])],
    '''root = {'children': {}, 'count': 0}
for word in words:
    node = root
    node['count'] += 1
    for char in word:
        node = node['children'].setdefault(char, {'children': {}, 'count': 0})
        node['count'] += 1
answer = []
for prefix in prefixes:
    node = root
    for char in prefix:
        node = node['children'].get(char)
        if node is None:
            break
    answer.append(0 if node is None else node['count'])
return answer''',
    ['把每个不同前缀看作一个节点，空前缀对应根。','插入时累加沿途节点的通过次数，而不只是词尾次数。','查询沿字符逐步下降，缺少任意一条边就返回0。'],
    '每个词条对它的每个前缀节点恰贡献一次计数，因此节点计数正是匹配该前缀的词条数量；不存在的路径对应没有出现过的前缀。',
    'O(S+Q)，S和Q为词条、查询的字符总数，另加词条数与查询数','O(S+1)，不计输出','不能先把words变成集合，否则重复词条的次数会丢失。',
    ['前缀树','嵌套字典','重复计数'],[4,6,22])

add(35, '括号边界：最长有效括号子串',
    '有效括号串要求每个前缀左括号不少于右括号，且最终数量相等。栈保存尚未匹配的左括号下标；栈底保存最近一个不可能越过的边界，初始为-1。右括号消去一个栈项后，若栈非空，当前位置减去新栈顶就是以当前位置结束的最长有效长度。',
    'stack = [-1]\nstack.pop()\nif not stack:\n    stack.append(index)\nelse:\n    best = max(best, index - stack[-1])',
    's只含(和)，长度0～100000。返回最长连续有效括号子串的长度；可以选择空串，所以没有有效非空子串时返回0。要求O(n)时间。',
    [('s','str','括号字符串')],
    [(['(()'],2), ([')()())'],4), ([''],0), (['(((('],0),
     (['))))'],0), (['()(())'],6), (['())(())'],4), (['(()())'],6)],
    '''stack = [-1]
best = 0
for i, char in enumerate(s):
    if char == '(':
        stack.append(i)
    else:
        stack.pop()
        if not stack:
            stack.append(i)
        else:
            best = max(best, i - stack[-1])
return best''',
    ['除了未匹配左括号，还需要记住最近的无效右括号位置。','用-1作为初始边界，让从下标0开始的有效串也能用同一公式。','匹配一个右括号后，新的栈顶决定当前有效串不能跨越的位置。'],
    '栈中未匹配左括号和最后一个无效右括号是有效后缀不可跨越的边界。每次成功消去左括号后，新栈顶之后到当前位置正好有效，且再向左就会跨越边界。枚举所有右端点取最大值即得答案。',
    'O(n)','O(n)','用栈长度不能得到有效子串长度，必须存下标，并更新空栈时的边界。',
    ['栈边界','下标差','字符串不变量'],[21])

add(35, '嵌套解码：带重复次数的字符串',
    '把进入中括号看作暂停外层工作：栈保存外层已解码片段和重复次数，内层从空片段开始。遇到右括号时，将完整内层重复并交还外层。用列表积累片段，关闭一层时join，避免每读取一个字母都复制整个字符串。',
    'stack.append((pieces, repeat))\npieces = []\ninner = "".join(pieces)\nouter, repeat = stack.pop()',
    'encoded是合法表达式，只含小写英文字母、数字及[]；语法是若干字母或k[表达式]的串联，1≤k≤100，多位次数无前导零，数字仅作为重复次数，括号内允许空串。编码长度≤10000、嵌套深度≤50，解码结果长度≤100000。空输入返回空串；返回完整解码字符串。',
    [('encoded','str','保证合法的嵌套编码')],
    [(['3[a2[c]]'],'accaccacc'), (['2[ab]x3[c]'],'ababxccc'),
     ([''],''), (['abc'],'abc'), (['10[a]'],'aaaaaaaaaa'),
     (['2[]x'],'x'), (['1[2[a]b]'],'aab'), (['2[a]2[b]'],'aabb')],
    '''stack = []
pieces = []
number = 0
for char in encoded:
    if char.isdigit():
        number = number * 10 + int(char)
    elif char == '[':
        stack.append((pieces, number))
        pieces = []
        number = 0
    elif char == ']':
        inner = ''.join(pieces)
        pieces, repeat = stack.pop()
        pieces.append(inner * repeat)
    else:
        pieces.append(char)
return ''.join(pieces)''',
    ['遇到左括号时，外层的已解码内容和次数都要保存。','遇到右括号时，先完成当前层，再恢复上一层。','连续数字用number*10+新数字读取，不能把10当成两个次数。'],
    '每层pieces始终是该层已经读取部分的正确解码。字母直接追加；完整内层返回时，按次数复制恰符合语法定义。栈按括号嵌套顺序恢复外层，因此最终根层结果正确。',
    'O(n+dL)，n为编码长度，d为最大深度，L为解码长度','O(n+L+d)','嵌套结构可能多次复制相同结果，不能笼统声称所有解码实现都是O(n+L)。',
    ['栈式解析','多位数读取','输出敏感复杂度'],[4,5,21])

add(35, '异或分组：找出两个只出现一次的数',
    '异或满足x^x=0、x^0=x，且交换顺序不影响结果。全部异或后只剩两个不同数a^b。其任意一个置1位说明a与b在该位不同；按这一位把所有数分组，成对数仍落在同组并抵消。x & -x可以取出最低的置1位。',
    'different = a ^ b\nlowbit = different & -different\nif value & lowbit:\n    group ^= value',
    'nums长度为2～100000，所有数为0～2^31-1的整数；保证恰有两个不同数各出现一次，其余不同数都恰出现两次。返回这两个单次出现的数，按升序排列。要求O(n)时间、O(1)辅助空间。',
    [('nums','list[int]','满足两单次其余成对的列表')],
    [([[1,2,1,3,2,5]],[3,5]), ([[0,7]],[0,7]),
     ([[4,9,4,2]],[2,9]), ([[1,1,0,2,3,3]],[0,2]),
     ([[2147483647,0]],[0,2147483647]), ([[6,6,8,12,8,9]],[9,12]),
     ([[5,4,3,4,3,2]],[2,5])],
    '''different = 0
for value in nums:
    different ^= value
lowbit = different & -different
a = b = 0
for value in nums:
    if value & lowbit:
        a ^= value
    else:
        b ^= value
return sorted([a, b])''',
    ['先异或全部数，成对项会消失。','剩下的异或值非零，找出一个a、b必然不同的二进制位。','按该位分组并分别异或，最后固定返回顺序。'],
    'a≠b保证a^b至少一位置1。分组位使a、b分离，而相同数总进入同组；每组抵消全部成对数后恰剩一个单次数。',
    'O(n)','O(1)','不能直接从a^b恢复两个数，必须利用原列表做第二次分组扫描。',
    ['异或抵消','lowbit','常数空间'],[1,3,19])

add(35, '字母位掩码：互不共享字母的最大长度积',
    '小写字母表只有26种，集合可编码为26位整数。单词包含字符c时，将第ord(c)-ord("a")位置1；两词无共同字母等价于两个掩码按位与为0。同一个掩码只保留最长单词，因为较短词不会带来更好的乘积。',
    'mask |= 1 << (ord(char) - ord("a"))\nindependent = (first_mask & second_mask) == 0',
    'words最多1000个非空小写英文单词，每词长度≤100，允许重复。选两个不同下标且没有共同字母的单词，返回长度乘积最大值；不存在合法二元组时返回0。目标O(S+u^2)，S为字符总数，u为不同字母集合数。',
    [('words','list[str]','非空小写单词列表')],
    [([['abcw','baz','foo','bar','xtfn','abcdef']],16),
     ([['a','ab','abc','d','cd','bcd','abcd']],4), ([[]],0),
     ([['a']],0), ([['aa','aaa','b']],3), ([['ab','ba','abc']],0),
     ([['a','b','c']],1), ([['abcd','ef','ghij']],16)],
    '''longest = {}
for word in words:
    mask = 0
    for char in word:
        mask |= 1 << (ord(char) - ord('a'))
    longest[mask] = max(longest.get(mask, 0), len(word))
items = list(longest.items())
best = 0
for i in range(len(items)):
    for j in range(i):
        if items[i][0] & items[j][0] == 0:
            best = max(best, items[i][1] * items[j][1])
return best''',
    ['把字符是否出现与出现次数分开：本题只关心是否出现。','用26位整数表示集合，按位与检测交集。','同一掩码只保留最大长度，再枚举不同掩码对。'],
    '掩码准确记录字母集合，按位与为0当且仅当交集为空。相同掩码的非空词彼此不能配对，替换为该掩码最长词不会破坏合法性且不会降低乘积，所以压缩后枚举仍包含最优解。',
    'O(S+u^2)','O(u)','长度要取原单词长度，不是掩码中置1位的数量；重复字母仍贡献长度。',
    ['集合位编码','状态压缩','等价状态合并'],[4,6,19])

add(35, '奇偶前缀：元音均出现偶数次的最长子串',
    '只关心五种元音出现次数的奇偶性，故32种状态足够。每读到一个元音，用异或翻转对应位。两个前缀状态相同，表示中间子串对每一位的翻转次数均为偶数。求最长距离时，每个状态只保存第一次出现的位置。',
    'mask ^= 1 << vowel_index\nfirst = {0: -1}\nlength = current_index - first[mask]',
    's只含小写英文字母，长度0～100000。返回最长连续子串长度，要求a、e、i、o、u在子串中各出现偶数次（0次也满足）。其他字母无限制。没有非空合法子串时返回0。',
    [('s','str','小写文本')],
    [(['eleetminicoworoep'],13), (['leetcodeisgreat'],5),
     (['bcbcbc'],6), ([''],0), (['a'],0), (['aa'],2),
     (['aeiouaeiou'],10), (['abca'],4)],
    '''bits = {char: 1 << i for i, char in enumerate('aeiou')}
first = {0: -1}
mask = best = 0
for i, char in enumerate(s):
    mask ^= bits.get(char, 0)
    if mask in first:
        best = max(best, i - first[mask])
    else:
        first[mask] = i
return best''',
    ['把每种元音计数压缩为奇数或偶数两个状态。','一个整数的五个位即可同时保存五种奇偶性。','相同前缀状态之间合法；为最大化长度只保留最早下标。'],
    '两前缀掩码异或等于其间子串的奇偶掩码，结果为0恰表示全部元音计数为偶数。每个右端点配同状态最早前缀，得到该右端点的最大合法长度。',
    'O(n)','O(1)，最多32种状态','空前缀需要放在下标-1；遇到旧状态不能更新其最早位置。',
    ['前缀奇偶状态','位掩码','最长区间'],[6,19,31])

add(35, '二进制快速幂：巨大指数下取模',
    '把指数写成二进制：a^13=a^8*a^4*a。循环维护当前底数、尚未处理的指数和累计答案；指数最低位是1才把当前底数乘入答案，每轮底数平方、指数右移一位。乘法后立即取模，使中间数保持很小。',
    'if exponent & 1:\n    result = result * base % modulus\nbase = base * base % modulus\nexponent >>= 1',
    'base为绝对值≤10^18的整数，0≤exponent≤10^18，1≤modulus≤10^9。返回base的exponent次方除以modulus的非负余数；约定0^0=1，因此modulus=1时任何答案均为0。请实现快速幂，不调用pow，也不先计算完整幂。复杂度按整数运算次数计。',
    [('base','int','允许负数的底数'),('exponent','int','非负指数'),('modulus','int','正模数')],
    [([2,10,1000],24), ([-2,5,13],7), ([0,0,7],1),
     ([9,0,1],0), ([0,8,3],0), ([3,4,5],1),
     ([2,1000000000000000000,3],1), ([100,1,7],2)],
    '''result = 1 % modulus
base %= modulus
while exponent:
    if exponent & 1:
        result = result * base % modulus
    base = base * base % modulus
    exponent >>= 1
return result''',
    ['试着把指数13拆成8+4+1，分别对应三个二进制置1位。','循环不变量可以写成result * base^exponent与原始答案模modulus同余。','初始化答案也要取模，处理exponent=0且modulus=1。'],
    '若指数为偶数，底数平方且指数减半不改变待计算乘积；若为奇数，先把一份底数乘入result后再同样处理。每轮保持乘积同余，指数为0时result就是所求余数。',
    'O(log(exponent+1)) 次整数运算','O(1) 个整数','负底数可先使用Python的%正规化；不能使用浮点幂再取模。',
    ['快速幂','循环不变量','模运算'],[1,3,12,19])

add(35, '长除法状态：分数转循环小数',
    '十进制长除法的下一位只由当前余数决定：余数乘10后除以分母，商是新数字，余数成为下一状态。余数为0表示终止；同一个余数再次出现，后续数字必然重复。记录余数第一次出现时的数字下标，即可准确放置循环节括号。',
    'digit, remainder = divmod(remainder * 10, denominator)\nseen[remainder] = len(digits)\ncycle = "(" + "".join(digits[start:]) + ")"',
    'numerator为绝对值≤10^9的整数，denominator是非零整数且绝对值≤10000。返回最简十进制表示：整数不带小数点，有限小数不补尾零，无限小数用括号括住最短循环节，如1/6返回"0.1(6)"；负号只出现一次，0返回"0"。不得使用浮点数近似。',
    [('numerator','int','分子'),('denominator','int','非零分母')],
    [([1,6],'0.1(6)'), ([1,3],'0.(3)'), ([1,2],'0.5'),
     ([-50,8],'-6.25'), ([0,-7],'0'), ([7,-7],'-1'),
     ([1,90],'0.0(1)'), ([22,7],'3.(142857)'), ([-1,-2],'0.5')],
    '''if numerator == 0:
    return '0'
sign = '-' if (numerator < 0) != (denominator < 0) else ''
whole, remainder = divmod(abs(numerator), abs(denominator))
prefix = sign + str(whole)
if remainder == 0:
    return prefix
denominator = abs(denominator)
digits = []
seen = {}
while remainder and remainder not in seen:
    seen[remainder] = len(digits)
    digit, remainder = divmod(remainder * 10, denominator)
    digits.append(str(digit))
if remainder:
    start = seen[remainder]
    return prefix + '.' + ''.join(digits[:start]) + '(' + ''.join(digits[start:]) + ')'
return prefix + '.' + ''.join(digits)''',
    ['先单独处理符号和整数部分，剩下只做正整数长除法。','记录的状态应是余数，而不是刚刚生成的小数数字。','在生成下一位之前保存余数的位置，重复位置就是循环节起点。'],
    '相同余数产生完全相同的后续商位序列；首次重复前没有同余数状态，因此括住的正是最短循环节。非零余数仅有|denominator|-1种，过程必然终止或进入循环。',
    'O(|denominator|) 次整数运算','O(|denominator|)','数字重复不代表进入循环；例如1/90的小数前导0属于非循环部分。',
    ['余数状态','环检测','精确算术'],[6,12,19])

add(35, '质因数估值：任意进制的阶乘尾零',
    '一个b进制尾零意味着能再提出一个因子b。若b分解为若干p^e，则n!中可用的每种质因子数量除以需求e，最短缺的一种决定能提出多少个b。n!中p的总指数为floor(n/p)+floor(n/p^2)+…，用反复整除求和，无需计算阶乘。',
    'count = 0\nremaining = n\nwhile remaining:\n    remaining //= prime\n    count += remaining',
    '0≤n≤10^12，2≤base≤10^9。返回n!在base进制表示末尾连续0的数量；0!=1，因此n=0时返回0。请分解base并统计质因子指数，不构造n!或实际进制字符串。复杂度按整数运算次数计。',
    [('n','int','阶乘参数'),('base','int','进制')],
    [([10,10],2), ([10,12],4), ([0,2],0), ([5,16],0),
     ([8,16],1), ([25,10],6), ([6,9],1), ([10,7],1),
     ([1000000000000,10],249999999997)],
    '''remaining = base
factors = []
prime = 2
while prime * prime <= remaining:
    if remaining % prime == 0:
        exponent = 0
        while remaining % prime == 0:
            remaining //= prime
            exponent += 1
        factors.append((prime, exponent))
    prime += 1
if remaining > 1:
    factors.append((remaining, 1))
answer = None
for prime, exponent in factors:
    value = n
    count = 0
    while value:
        value //= prime
        count += value
    zeros = count // exponent
    answer = zeros if answer is None else min(answer, zeros)
return answer''',
    ['先用十进制想：一个0需要一对2和5；其他进制需要哪些因子？','n!中p的倍数贡献至少一个p，p²的倍数额外贡献一个，以此类推。','把每种质因子总量除以base中该因子的指数，再取最小值。'],
    '逐层统计p的倍数等价于对1～n每个数的p因子个数求和。b^k整除n!当且仅当所有质因子都有至少k倍所需数量，因此可行k的最大值是各商的最小值。',
    'O(sqrt(base)+log(base)*log(n+1)) 次整数运算','O(log(base))','base=12需要2²和3，不能只比较2和3的原始数量；质因子的需求指数不可遗漏。',
    ['试除分解','阶乘质因子指数','瓶颈约束'],[12,19],'挑战')


# 36: deterministic, pure-function models of engineering state machines.
add(36, 'LRU 缓存：读写都会刷新最近使用顺序',
    'LRU淘汰最久没有被使用的键。哈希表负责按键查找，双向顺序负责把刚用过的键移动到末尾。Python的OrderedDict同时提供这两种操作：move_to_end刷新顺序，popitem(last=False)移除最旧项。命中读取与写入更新都算使用，读取不存在的键不改变顺序。',
    'from collections import OrderedDict\ncache.move_to_end(key)\ncache.popitem(last=False)',
    '0≤capacity≤10000；operations最多20000项，每项为["put",key,value]或["get",key]。key为长度1～30的英文字符串，value为0～10^9整数。缓存初始为空；put插入或更新并设为最近使用，超容量淘汰最久未使用的键；get命中返回值并刷新顺序，未命中返回-1。容量0不保存任何键。只返回所有get操作的结果列表。',
    [('capacity','int','最多保存的键数'),('operations','list[list]','按序执行的缓存操作')],
    [([2,[['put','a',1],['put','b',2],['get','a'],['put','c',3],['get','b'],['get','c']]],[1,-1,3]),
     ([1,[['put','a',1],['put','a',9],['get','a']]],[9]),
     ([0,[['put','a',1],['get','a']]],[-1]), ([3,[]],[]),
     ([1,[['get','x'],['put','x',0],['get','x']]],[-1,0]),
     ([2,[['put','a',1],['put','b',2],['put','a',7],['put','c',3],['get','b'],['get','a']]],[-1,7]),
     ([2,[['put','a',1],['put','b',2],['get','x'],['put','c',3],['get','a']]],[-1,-1])],
    '''from collections import OrderedDict
cache = OrderedDict()
answer = []
for operation in operations:
    action, key = operation[:2]
    if action == 'get':
        if key in cache:
            answer.append(cache[key])
            cache.move_to_end(key)
        else:
            answer.append(-1)
    else:
        cache[key] = operation[2]
        cache.move_to_end(key)
        if len(cache) > capacity:
            cache.popitem(last=False)
return answer''',
    ['字典保存值，但还需要一个可以快速更新的最近使用顺序。','把最近使用的键统一放在末尾；最旧键位于开头。','更新已有键也要刷新顺序，未命中get则不创建键。'],
    '每次操作后，OrderedDict从头到尾恰按最后成功使用时间排列。命中读写把对应键移到末尾保持不变量；超容量移除首项恰为LRU淘汰规则。',
    'O(q) 平均','O(capacity)，不计输出','普通字典对已有键赋值不会自动刷新插入顺序；不能把更新当成无需调整的操作。',
    ['LRU','有序字典','状态机'],[6,11,21])

add(36, '滑动时间窗限流：只统计已接受请求',
    '为每个用户保存已接受请求的时间队列。当前时刻t，只保留(t-window,t]内的记录，因此时间≤t-window的记录先弹出。若剩余数量小于limit就接受并入队，否则拒绝且不入队。时间非递减让每条记录最多进入和离开队列各一次。',
    'while queue and queue[0] <= time - window:\n    queue.popleft()\naccepted = len(queue) < limit',
    'requests最多20000项，每项[t,user]，t为0～10^9整数，整体按t非递减给出，同一时刻按输入顺序处理；user为长度1～30的非空字符串。1≤window≤10^9，0≤limit≤10000。每个用户在任意窗口(t-window,t]内最多接受limit个请求，拒绝的请求不计数。初始无请求记录，按输入顺序返回布尔列表。',
    [('requests','list[list]','按时刻有序的请求'),('window','int','窗口长度'),('limit','int','每用户窗口配额')],
    [([[[0,'a'],[1,'a'],[2,'a'],[10,'a']],10,2],[True,True,False,True]),
     ([[[0,'a'],[0,'b'],[0,'a']],5,1],[True,True,False]),
     ([[],5,2],[]), ([[[0,'a'],[100,'a']],5,0],[False,False]),
     ([[[0,'a'],[5,'a']],5,1],[True,True]),
     ([[[0,'a'],[1,'a'],[2,'a'],[5,'a']],5,1],[True,False,False,True]),
     ([[[7,'a'],[7,'a'],[7,'a']],1,2],[True,True,False])],
    '''from collections import defaultdict, deque
history = defaultdict(deque)
answer = []
for time, user in requests:
    queue = history[user]
    while queue and queue[0] <= time - window:
        queue.popleft()
    accepted = len(queue) < limit
    answer.append(accepted)
    if accepted:
        queue.append(time)
return answer''',
    ['每个用户拥有独立配额，不能共用一个队列。','先清理过期的已接受请求，再判断还有没有名额。','题目的左端点是开区间，恰好相差window的请求应移出。'],
    '每次判断前队列恰含该用户窗口内已接受的请求，因此长度直接表示已用配额。只在接受时追加当前时间，保持此不变量；不同用户的字典项互不影响。',
    'O(q) 平均','O(q)','拒绝请求不能入队，否则连续失败会错误地延长封锁时间。',
    ['按键滑动窗口','队列','开闭边界'],[6,11,31])

add(36, '令牌桶：可积累但有上限的请求配额',
    '滑动窗口限制近期数量，令牌桶则把空闲时间转为可积累的令牌。两次事件之间增加(时间差×速率)个令牌，但最多到capacity。请求只有在令牌足够时才消费cost，否则一个也不消费。把时间作为输入，便可测试限流逻辑而不真正等待。',
    'tokens = min(capacity, tokens + (time - previous) * rate)\nif tokens >= cost:\n    tokens -= cost',
    '0≤capacity≤10^9，0≤rate≤10^9；桶在时刻0初始满载，之后每单位时间补充rate个令牌，上限capacity。requests最多20000项[t,cost]，t为0～10^9整数且非递减，1≤cost≤10^9。同一时刻按输入顺序处理；先补充再判断，足够则接受并扣除cost，不足则拒绝且不扣令牌。返回每次请求是否接受的布尔列表。',
    [('capacity','int','桶容量'),('rate','int','每单位时间增加的令牌数'),('requests','list[list[int]]','有序请求时间与成本')],
    [([5,1,[[0,4],[0,2],[1,2],[5,5]]] ,[True,False,True,False]),
     ([3,2,[[0,3],[10,3],[10,1]]] ,[True,True,False]),
     ([0,5,[[0,1],[10,1]]],[False,False]), ([4,0,[]],[]),
     ([4,0,[[0,3],[100,2],[100,1]]] ,[True,False,True]),
     ([2,1,[[0,3],[0,2],[2,2]]] ,[False,True,True]),
     ([5,2,[[0,5],[2,4],[3,2]]] ,[True,True,True])],
    '''tokens = capacity
previous = 0
answer = []
for time, cost in requests:
    tokens = min(capacity, tokens + (time - previous) * rate)
    previous = time
    accepted = tokens >= cost
    answer.append(accepted)
    if accepted:
        tokens -= cost
return answer''',
    ['记录上次处理时刻和当前令牌余额即可，不必逐单位时间模拟。','先按时间差补充，再用min裁剪到容量。','即使请求拒绝，也要更新上次处理时刻，避免重复计算补充量。'],
    '相邻事件间没有消费，按时间差累加并截断恰等价于连续补充。随后只有可支付的请求扣费，因此每一步余额与定义一致，接受判断正确。',
    'O(q)','O(1)，不计输出','拒绝请求后不能把previous留在旧时刻，否则下次会重复领取已经补过的令牌。',
    ['令牌桶','事件时间模拟','容量约束'],[1,3,19])

add(36, 'TTL 缓存：过期堆与覆盖写入',
    '只有get时检查目标键，无法高效回答size。可额外用最小堆安排过期事件，每次操作前弹出到期事件。覆盖写入会让旧事件失效，因此每次set分配唯一版本号，堆中同时保存该版本；弹出时只有仍与当前版本相同才删除。',
    'heapq.heappush(expirations, (expires_at, version, key))\nif key in cache and cache[key][2] == version:\n    del cache[key]',
    'operations最多20000项，形式为["set",t,key,value,ttl]、["get",t,key]、["size",t]，t为0～10^9且非递减，同时间按输入顺序处理。key为非空字符串长度≤30，0≤value≤10^9，0≤ttl≤10^9。初始空缓存；每项操作前移除过期时间≤t的项。set覆盖旧值且新过期时间为t+ttl，ttl=0立即删除该键；get返回值或-1，size返回当前键数。只返回get和size的结果。',
    [('operations','list[list]','包含虚拟时刻的操作')],
    [([[['set',0,'a',5,2],['get',1,'a'],['get',2,'a'],['size',2]]],[5,-1,0]),
     ([[['set',0,'a',1,2],['set',1,'a',9,10],['size',2],['get',2,'a']]],[1,9]),
     ([[]],[]), ([[['get',0,'x'],['size',0]]],[-1,0]),
     ([[['set',0,'a',1,10],['set',1,'a',2,0],['get',1,'a'],['size',1]]],[-1,0]),
     ([[['set',0,'a',1,3],['set',0,'b',2,3],['size',2],['size',3]]],[2,0]),
     ([[['set',0,'a',1,3],['set',1,'a',2,2],['get',2,'a'],['get',3,'a']]],[2,-1]),
     ([[['set',0,'a',0,1],['get',0,'a'],['set',1,'b',2,1],['size',1]]],[0,1])],
    '''import heapq
cache = {}
expirations = []
answer = []
for version, operation in enumerate(operations):
    action, time = operation[:2]
    while expirations and expirations[0][0] <= time:
        _, old_version, key = heapq.heappop(expirations)
        if key in cache and cache[key][2] == old_version:
            del cache[key]
    if action == 'set':
        _, _, key, value, ttl = operation
        if ttl == 0:
            cache.pop(key, None)
        else:
            expires_at = time + ttl
            cache[key] = (value, expires_at, version)
            heapq.heappush(expirations, (expires_at, version, key))
    elif action == 'get':
        item = cache.get(operation[2])
        answer.append(-1 if item is None else item[0])
    else:
        answer.append(len(cache))
return answer''',
    ['size要求所有过期键都及时清除，可按过期时间用堆取最早事件。','覆盖写入后，堆里的旧事件可能仍在，不能看到键名相同就删除。','每次写入分配新版本，让过期事件只删除自己创建的那一版。'],
    '操作前弹出所有到期事件，当前版本对应的事件会删除过期项，旧版本事件不会影响新值。剩余缓存恰为仍未到期的最新写入；零TTL立即移除保持相同不变量，因此get与size均正确。',
    'O(q log(q+1))','O(q)，旧版本堆项可能暂时保留','只比较键名会让旧TTL误删新值；即使过期时间相同，版本身份也能明确区分写入。',
    ['过期缓存','最小堆','惰性失效','版本号'],[6,22],'挑战')

add(36, '依赖构建：并行任务的最早完成时刻',
    '依赖构成有向图，边u→v表示v必须等u完成。若机器数量无限，v只需等所有前驱中的最晚完成时刻，然后执行自己的duration[v]。按拓扑顺序传播最大完成时间；不能处理全部节点则有环，没有合法构建计划。',
    'finish[v] = max(finish[v], finish[u] + durations[v])\nindegree[v] -= 1\nif indegree[v] == 0:\n    queue.append(v)',
    'durations长度n为0～10000，第i项是任务i所需时间，范围1～10^9。dependencies最多20000对[u,v]，合法节点下标，表示u完成后v才能开始；允许重复依赖和自环。时间从0开始，可无限并行，无其他资源限制。返回各任务最早完成时刻，按任务编号排列；有环返回[-1]；n=0返回[]。重复边应视为同一个约束。',
    [('durations','list[int]','每项任务的正耗时'),('dependencies','list[list[int]]','有向依赖u到v')],
    [([[3,2,4],[[0,2],[1,2]]],[3,2,7]),
     ([[2,3,1],[[0,1],[1,2]]],[2,5,6]), ([[],[]],[]),
     ([[5,1],[]],[5,1]), ([[1,1],[[0,1],[1,0]]],[-1]),
     ([[7],[[0,0]]],[-1]), ([[2,4],[[0,1],[0,1]]],[2,6]),
     ([[3,8,2,1],[[0,2],[1,2],[2,3]]],[3,8,10,11])],
    '''from collections import deque
n = len(durations)
graph = [[] for _ in range(n)]
indegree = [0] * n
for u, v in set(map(tuple, dependencies)):
    graph[u].append(v)
    indegree[v] += 1
finish = list(durations)
queue = deque(i for i in range(n) if indegree[i] == 0)
processed = 0
while queue:
    u = queue.popleft()
    processed += 1
    for v in graph[u]:
        finish[v] = max(finish[v], finish[u] + durations[v])
        indegree[v] -= 1
        if indegree[v] == 0:
            queue.append(v)
return finish if processed == n else [-1]''',
    ['先完成所有前驱，意味着取前驱完成时刻的最大值而不是总和。','按拓扑序处理，节点入队时所有前驱都已贡献过答案。','处理节点数不足n表示有环；不要返回部分构建结果。'],
    '拓扑顺序保证计算任务v时所有前驱完成时刻已确定。任何可行计划中v都不能早于最晚前驱完成后开始；无限并行使此下界可以达到，递推得到最早完成时刻。拓扑无法移除的节点形成或依赖于环。',
    'O(n+m) 平均','O(n+m)','有多个前驱不代表必须串行执行它们；求和会高估时间。',
    ['关键路径','拓扑动态规划','并行依赖'],[23,24,34])

add(36, '稳定游标分页：时间相同也不漏记录',
    '只用时间作为翻页条件，会漏掉同一时间的其他记录。用(created_at,id)形成唯一排序键，下一页选择严格大于游标的记录。游标不必对应仍存在的记录，只代表一个排序边界。多看一条记录可以判断是否确实还有下一页。',
    'from bisect import bisect_right\nstart = bisect_right(sorted_keys, tuple(cursor))\npage = sorted_keys[start:start + limit]',
    'records最多10000项[created_at,id]，两者为0～10^9整数，id在records中唯一，输入未必有序。cursor为[]表示从头开始，或合法二元整数列表[t,id]表示排除所有排序键≤该游标的记录，游标无需实际存在。1≤limit≤1000。按时间升序、id升序返回{"items":当前页记录,"next":下一页游标}；仅当当前页之后还有记录时next为本页最后一条记录，否则为[]。',
    [('records','list[list[int]]','未排序记录'),('cursor','list[int]','空列表或上页最后的排序键'),('limit','int','页大小')],
    [([[[2,8],[1,3],[1,2],[3,1]],[],2],{'items':[[1,2],[1,3]],'next':[1,3]}),
     ([[[1,2],[1,3],[2,8]],[1,2],2],{'items':[[1,3],[2,8]],'next':[]}),
     ([[],[],3],{'items':[],'next':[]}),
     ([[[1,1]],[2,0],1],{'items':[],'next':[]}),
     ([[[1,1],[3,3]],[2,2],1],{'items':[[3,3]],'next':[]}),
     ([[[1,2],[1,4],[1,6]],[1,3],1],{'items':[[1,4]],'next':[1,4]}),
     ([[[0,0]],[],1],{'items':[[0,0]],'next':[]})],
    '''from bisect import bisect_right
keys = sorted(map(tuple, records))
start = bisect_right(keys, tuple(cursor)) if cursor else 0
page = keys[start:start + limit]
has_more = start + len(page) < len(keys)
return {'items': [list(key) for key in page],
        'next': list(page[-1]) if page and has_more else []}''',
    ['先把时间和唯一id组合成二元排序键。','游标是排他边界，应找第一个严格大于它的键。','恰好装满一页不一定还有下一页，要检查后面是否还存在记录。'],
    '唯一二元键给所有记录确定总顺序。bisect_right得到第一个大于游标的位置，截取limit条恰是下一页；下一游标指向本页末项，使后续页既不重复也不跳过同时间记录。',
    'O(n log(n+1)+limit)','O(n+limit)','不能只用created_at排序或过滤；同一时间的多条记录需要id作为稳定决胜键。',
    ['游标分页','多关键字排序','二分边界'],[20,26,30])

add(36, '幂等扣款：成功记录、重试与冲突',
    '同一业务请求可能被发送多次，不能每次都扣款。以幂等键记录成功扣款的金额：同键同金额再次到达只返回replay，同键不同金额返回conflict。余额不足的失败不落成功记录，因此稍后用该键提交不同金额仍可成功。先查幂等记录，再判断余额。',
    'if key in completed:\n    status = "replay" if completed[key] == amount else "conflict"\nelif balance >= amount:\n    balance -= amount\n    completed[key] = amount',
    '0≤balance≤10^12；requests最多20000项[key,amount]，key为长度1～30的非空字符串，1≤amount≤10^9。依次执行：已成功的key且金额相同返回"replay"，金额不同返回"conflict"；未成功的key在余额足够时扣款、记录并返回"ok"，否则返回"insufficient"且不记录。只有ok改变余额。返回{"balance":最终余额,"statuses":各请求状态列表}。',
    [('balance','int','初始余额'),('requests','list[list]','幂等键与扣款金额')],
    [([10,[['a',6],['a',6],['b',5]]],{'balance':4,'statuses':['ok','replay','insufficient']}),
     ([10,[['a',3],['a',4],['b',7]]],{'balance':0,'statuses':['ok','conflict','ok']}),
     ([0,[]],{'balance':0,'statuses':[]}),
     ([0,[['x',1],['x',1]]],{'balance':0,'statuses':['insufficient','insufficient']}),
     ([5,[['x',6],['x',5]]],{'balance':0,'statuses':['insufficient','ok']}),
     ([2,[['a',2],['a',2],['a',1]]],{'balance':0,'statuses':['ok','replay','conflict']}),
     ([7,[['a',2],['b',2],['c',2],['d',2]]],{'balance':1,'statuses':['ok','ok','ok','insufficient']})],
    '''completed = {}
statuses = []
for key, amount in requests:
    if key in completed:
        status = 'replay' if completed[key] == amount else 'conflict'
    elif balance >= amount:
        balance -= amount
        completed[key] = amount
        status = 'ok'
    else:
        status = 'insufficient'
    statuses.append(status)
return {'balance': balance, 'statuses': statuses}''',
    ['只记录成功请求，记录中同时保存金额以识别冲突。','已成功的重试不应再检查余额，否则扣到0后的重试会被误报余额不足。','把状态判断和唯一扣款分支放在同一轮处理里。'],
    'completed始终恰保存所有成功请求及其金额。已有键进入不扣款分支，保证至多扣一次；新键仅在余额足够时成功并写入记录。按此不变量逐项执行得到准确余额和状态。',
    'O(q) 平均','O(q)','先判断余额再查幂等记录会把成功后的合法重试错误地拒绝。本题只模拟顺序处理，不声称提供数据库并发事务。',
    ['幂等性','状态转移','失败语义'],[6,26,30])

add(36, '重试计划：指数退避与服务端等待时间',
    '重试控制要把是否重试与何时重试分开。暂时失败可以重试，但成功或不可重试错误应立即结束。第k次失败后使用base_delay×2^(k-1)，上限cap；服务端若给出更长retry_after，就至少等待该时长。这里生成虚拟时刻，不发请求也不sleep。',
    'delay = max(backoff, retry_after)\ntime += delay\nbackoff = min(cap, backoff * 2)',
    'responses最多50项[code,retry_after]，code为100～599整数，retry_after为-1或0～10^9整数，-1表示未指定。0≤max_attempts≤50，1≤base_delay≤cap≤10^9。第一次尝试在时刻0，每次依次消耗一个response；200～299成功后停止，只有429或500～599可重试，其余停止。第k次尝试失败后的等待为max(min(base_delay*2^(k-1),cap),retry_after)。达到尝试上限或无后续响应则停止，不安排不存在的尝试。返回{"times":实际尝试时刻,"status":最后状态码}，未尝试时status=0。',
    [('responses','list[list[int]]','按尝试顺序给出的响应'),('max_attempts','int','尝试次数上限'),('base_delay','int','初始退避'),('cap','int','指数退避上限')],
    [([[[500,-1],[503,-1],[200,-1]],5,2,10],{'times':[0,2,6],'status':200}),
     ([[[429,9],[200,-1]],3,2,5],{'times':[0,9],'status':200}),
     ([[],3,1,8],{'times':[],'status':0}),
     ([[[200,-1]],0,1,8],{'times':[],'status':0}),
     ([[[404,-1],[200,-1]],3,1,8],{'times':[0],'status':404}),
     ([[[500,-1],[500,-1],[500,-1],[200,-1]],4,2,3],{'times':[0,2,5,8],'status':200}),
     ([[[500,-1],[200,-1]],1,1,4],{'times':[0],'status':500}),
     ([[[503,0]],8,1,4],{'times':[0],'status':503})],
    '''times = []
time = status = 0
backoff = base_delay
attempts = min(max_attempts, len(responses))
for i in range(attempts):
    status, retry_after = responses[i]
    times.append(time)
    retryable = status == 429 or 500 <= status <= 599
    if not retryable or i + 1 == attempts:
        break
    time += max(backoff, retry_after)
    backoff = min(cap, backoff * 2)
return {'times': times, 'status': status}''',
    ['用for循环控制最多尝试次数，避免把重试次数和总尝试次数混淆。','先记录本次响应，再判断是否需要安排下一次。','cap只截断指数退避，服务端retry_after可以大于cap。'],
    '循环第i次恰消耗第i个响应并记录其实际时刻。只有当前失败可重试且存在下一次配额与响应时才累加等待；backoff逐轮倍增并截断，恰符合给定公式。',
    'O(min(max_attempts,n))','O(1)，不计输出','不要把max_attempts解释成额外重试次数；成功后的响应即使还在输入中也不得继续消耗。',
    ['重试策略','指数退避','可测试时间模型'],[3,19,27])

add(36, '单机任务调度：到达、优先级与非抢占执行',
    '有两种顺序：未来任务按到达时间排序，已到达任务按优先级进入堆。机器空闲时从堆选任务；堆为空则直接把时间跳到下一个到达时刻。任务执行期间新来的任务只能等待，任务完成时再统一加入候选集合，避免把非抢占误写成抢占。',
    'while next_index < n and arrivals[next_index][0] <= time:\n    heapq.heappush(ready, (priority, original_index))\npriority, index = heapq.heappop(ready)',
    'jobs最多10000项[arrival,duration,priority]，三者均为整数，0≤arrival,priority≤10^9，1≤duration≤10^9，输入下标是任务编号。单台机器在时刻0空闲；每次空闲时，在arrival≤当前时刻且未执行的任务中选priority最小者，同优先级选编号最小者。任务不可中断，到完成时才重新选；没有可选任务时等待最早到达。返回{"order":执行编号顺序,"finished":按原编号的完成时刻}。',
    [('jobs','list[list[int]]','到达、耗时、优先级')],
    [([[[0,4,2],[1,1,0],[0,2,1]]],{'order':[2,1,0],'finished':[7,3,2]}),
     ([[[0,5,9],[1,1,0]]],{'order':[0,1],'finished':[5,6]}),
     ([[]],{'order':[],'finished':[]}),
     ([[[7,3,0]]],{'order':[0],'finished':[10]}),
     ([[[0,2,1],[0,1,1],[0,1,1]]],{'order':[0,1,2],'finished':[2,3,4]}),
     ([[[10,1,1],[0,1,2],[5,2,3]]],{'order':[1,2,0],'finished':[11,1,7]}),
     ([[[0,2,5],[2,1,2],[1,1,3]]],{'order':[0,1,2],'finished':[2,3,4]})],
    '''import heapq
arrivals = sorted((job[0], i) for i, job in enumerate(jobs))
ready = []
order = []
finished = [0] * len(jobs)
next_index = time = 0
while next_index < len(jobs) or ready:
    if not ready:
        time = max(time, arrivals[next_index][0])
    while next_index < len(jobs) and arrivals[next_index][0] <= time:
        _, index = arrivals[next_index]
        heapq.heappush(ready, (jobs[index][2], index))
        next_index += 1
    _, index = heapq.heappop(ready)
    time += jobs[index][1]
    finished[index] = time
    order.append(index)
return {'order': order, 'finished': finished}''',
    ['未来事件与已经就绪的任务需要两种排序，不能只对jobs整体排序一次。','每次选任务前，把到当前时刻为止到达的所有任务入堆。','用(priority,index)作堆键固定同优先级顺序；执行时一次跳到完成时刻。'],
    '每次弹堆前，所有且仅有已到达未执行任务在堆中，因此堆顶恰为规则要求的任务。一次增加完整耗时实现非抢占；空堆直接跳到下一到达时刻不会遗漏任何可执行任务。',
    'O(n log(n+1))','O(n)','arrival恰等于完成时刻的任务已可参与下一次选择，入堆条件应为≤。',
    ['事件驱动模拟','优先队列','确定性决胜规则'],[20,22,32],'挑战')

add(36, '多路日志归并：稳定合并有序数据流',
    '每个来源内部已按时间排序，故全局下一条只能是某个来源当前最前面的未输出记录。堆只保留每个非空来源的一条候选；弹出一条后，补入该来源的下一条。用(time,source,index)作为堆键，让时间相同的日志也拥有确定顺序。',
    'heapq.heappush(heap, (time, source, index))\ntime, source, index = heapq.heappop(heap)\nnext_index = index + 1',
    'streams为0～1000个来源列表，总记录数N≤3000。每条记录为[time,event]，time为0～10^9整数，event为长度0～100的小写英文字母字符串，全部event总长度≤20000；每个来源内部time非递减，允许空来源和重复时间。合并后返回[time,source,event]列表，按time升序、来源下标source升序排序，同一来源同一时间保留原顺序。目标O(k+N log(k+1))时间、O(k)辅助空间，不计输出，k为来源数。',
    [('streams','list[list[list]]','各自按时间排序的日志来源')],
    [([[[[1,'a'],[3,'b']],[[2,'c'],[3,'d']]]],[[1,0,'a'],[2,1,'c'],[3,0,'b'],[3,1,'d']]),
     ([[],],[]), ([ [[],[]] ],[]),
     ([ [[ [2,'x'],[2,'y'] ]] ],[[2,0,'x'],[2,0,'y']]),
     ([ [[],[[0,'z']]] ],[[0,1,'z']]),
     ([ [[[1,'a'],[1,'b']],[[1,'c']]] ],[[1,0,'a'],[1,0,'b'],[1,1,'c']]),
     ([ [[[9,'late']],[[0,'early'],[10,'last']]] ],[[0,1,'early'],[9,0,'late'],[10,1,'last']]),
     ([ [[[0,'']]] ],[[0,0,'']])],
    '''import heapq
heap = [(stream[0][0], source, 0)
        for source, stream in enumerate(streams) if stream]
heapq.heapify(heap)
answer = []
while heap:
    time, source, index = heapq.heappop(heap)
    answer.append([time, source, streams[source][index][1]])
    index += 1
    if index < len(streams[source]):
        heapq.heappush(heap, (streams[source][index][0], source, index))
return answer''',
    ['每个来源只需暴露当前最前面的一条未输出记录。','在这些候选中用堆选择最小(time,source,index)。','弹出来源s的一条记录后，仅补入s的下一条，堆最多保存k条。'],
    '每个来源的后续记录在规定排序下均不早于当前候选，因此全局最小未输出项必在候选集合中。堆顶选择它，补入同源下一项后不变量继续成立；三元键保证跨源及同源稳定顺序。',
    'O(k+N log(k+1))','O(k)，不计输出','event文本不能参与决胜排序，否则相同时间的原始顺序可能被字典序打乱。',
    ['多路归并','堆','稳定排序','流式处理'],[20,22],'挑战')
