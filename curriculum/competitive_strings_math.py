"""ACM chapters 41--42: strings, number theory and combinatorics.

Fixtures use direct definitions, enumeration or independent identities. None
executes the reference program to manufacture its expected answer.
"""

from math import comb, gcd
from textwrap import dedent, indent

from .schema import acm_problem

PROBLEMS = []
_counts = {}


def _text(*rows):
    return '\n'.join(' '.join(map(str, row)) if isinstance(row, (list, tuple))
                     else str(row) for row in rows) + '\n'


def _case(rows, answer):
    return _text(*rows), _text(answer)


def _add(ch, title, teach, syntax, spec, cases, body, hints, proof, time, space,
         difficulty='挑战', skills=None):
    _counts[ch] = _counts.get(ch, 0) + 1
    assert len(cases) >= 7 and len(hints) == 3
    solution = ('import sys\n\n\ndef main():\n' +
                indent(dedent(body).strip(), '    ') +
                '\n\n\nif __name__ == "__main__":\n    main()\n')
    PROBLEMS.append(acm_problem(
        ch, _counts[ch], title,
        teach + '\n\n语法小课：\n```python\n' + syntax + '\n```',
        spec + '\n\n提交完整 Python 程序，从标准输入读取，用 print 或 sys.stdout.write 输出；输出按空白分隔的 token 比较。',
        cases, solution, hints,
        proof + '\n\n复杂度：时间 ' + time + '，额外空间 ' + space +
        '（不计批量读取的输入文本与最终输出）。',
        difficulty=difficulty, complexity={'time': time, 'space': space},
        prerequisites=[4, 19, 35, 37] if ch == 41 else [12, 19, 35, 37],
        skills=skills or [title.split('：')[0]]))


# 401: brute-force proper-border oracle, with a closed-form long fixture.
def _border_oracle(s):
    return [max((k for k in range(i + 1) if s[:k] == s[i + 1 - k:i + 1]),
                default=0) for i in range(len(s))]


_words = ['ababaca', 'aaaaa', 'a', 'abcdef', 'abacabab', 'abcababcab',
          'aabaaab', 'ababbabbab']
_cases = [_case([s], _border_oracle(s)) for s in _words]
_cases.append(_case(['a' * 1200], list(range(1200))))
_add(41, '前缀函数：最长相等真前后缀',
     '字符串 s 的前缀函数 pi[i]，是 s[0:i+1] 的最长相等真前缀与后缀的长度；“真”表示不能取整段本身。'
     '例如 ababa 的最后一个值是 3，对应 aba。计算下一个位置时，先尝试延长已有边界；失配后，可能的更短边界只能是当前边界自己的边界，因此令 j=pi[j-1] 继续尝试。'
     '这一跳转复用了已经比较过的信息，也是 KMP 匹配的基础。数组中保存的是长度，而不是字符下标。',
     'pi = [0] * len(s)\nj = pi[i - 1]\nwhile j > 0 and s[i] != s[j]:\n    j = pi[j - 1]',
     '输入一行非空小写英文字母串 s，1≤|s|≤1500。输出 |s| 个整数 pi[0] 到 pi[|s|-1]，用空格隔开。空字符串不在输入范围内。',
     _cases, r'''
s = sys.stdin.buffer.readline().decode().strip()
pi = [0] * len(s)
for i in range(1, len(s)):
    j = pi[i - 1]
    while j > 0 and s[i] != s[j]:
        j = pi[j - 1]
    if s[i] == s[j]:
        j += 1
    pi[i] = j
print(*pi)
''',
     ['pi[0] 永远为 0，因为单个字符没有非空真前后缀。',
      '不要逐个枚举所有短前缀；失配时跳到 pi[j-1]。',
      '只有字符相等时才让 j 加 1；当前结果保存到 pi[i]。'],
     '归纳假设前面的 pi 已正确。任一可延长的边界必属于 pi[i-1] 的边界链；依次跳转按长度递减访问全部可能候选，首次可延长者就是最长答案。'
     'j 的增加总次数至多 n，失败跳转使其减小，所以总比较次数为线性。易错点：把“真前缀”误写成整个子串，或在 j=0 时访问 pi[-1]。',
     'O(n)', 'O(n)', difficulty='进阶', skills=['前缀函数', '失配跳转', '摊还分析'])


# 402: straightforward substring comparisons count overlapping matches.
_matches = [('aaaaa', 'aaa'), ('abcxyz', 'zz'), ('', 'a'), ('a', 'a'),
            ('ab', 'abcd'), ('abababab', 'abab'), ('abcabcab', 'abcab'),
            ('mississippi', 'issi'), ('a' * 1800, 'a' * 70)]
_cases = []
for _s, _p in _matches:
    _pos = [i for i in range(len(_s) - len(_p) + 1) if _s[i:i + len(_p)] == _p]
    _cases.append(_case([_s or '-', _p], [len(_pos)] + _pos))
_add(41, 'KMP：保留重叠的全部匹配',
     'KMP 维护 j：已经读过的文本后缀与模式串前缀相等的最大长度。文本游标只向右走，失配时根据模式串的前缀函数调整 j。'
     '找到完整匹配后，不能一律清零，因为新匹配可能与旧匹配重叠；应回退到 pi[m-1]，保留仍然有效的后缀。例如 aaaaa 中 aaa 的起点是 0、1、2。'
     '先预处理模式，再扫描文本，使最坏时间从逐位置比较的 O(nm) 降到 O(n+m)。',
     'for i, ch in enumerate(text):\n    # 完整匹配结束位置 i 对应起点 i - len(pattern) + 1\n    pass\nprint(len(positions), *positions)',
     '第一行给文本 t（0≤|t|≤2000），第二行给非空模式 p（1≤|p|≤2000），字符均为小写英文字母。文本为空时第一行写单独的 -；模式不能为 -。'
     '输出一行：先输出匹配次数，再按升序输出所有匹配起点，起点从 0 编号，允许重叠。没有匹配时只输出 0。',
     _cases, r'''
t = sys.stdin.buffer.readline().decode().strip()
p = sys.stdin.buffer.readline().decode().strip()
if t == '-':
    t = ''
m = len(p)
pi = [0] * m
for i in range(1, m):
    j = pi[i - 1]
    while j and p[i] != p[j]:
        j = pi[j - 1]
    if p[i] == p[j]:
        j += 1
    pi[i] = j
j = 0
positions = []
for i, ch in enumerate(t):
    while j and ch != p[j]:
        j = pi[j - 1]
    if ch == p[j]:
        j += 1
    if j == m:
        positions.append(i - m + 1)
        j = pi[j - 1]
print(len(positions), *positions)
''',
     ['前缀函数只需对模式 p 计算一次。', 'j 表示已匹配长度；文本字符失配时，文本下标不回退。',
      '记录起点 i-m+1 后，令 j=pi[m-1]，这样不会遗漏重叠匹配。'],
     '每次读入字符后，边界跳转保持“j 是文本后缀与模式前缀的最大匹配长度”的不变量。j 达到 m 当且仅当出现一次完整匹配。'
     '记录后保留模式最长真边界，等价于保留所有下一次匹配可能共用的信息，因此每个起点恰好输出一次。易错点：匹配后仍用 j=m 访问 p[j]；把 - 当作文本字符。',
     'O(n+m)', 'O(m+k)，k 为匹配次数', skills=['KMP', '重叠匹配', '标准输入协议'])


# 403: independent enumeration of divisors and repeated blocks.
_words = ['ababab', 'abcab', 'a', 'aaaaaa', 'abcabcabcabc', 'abacaba',
          'xyzxyz', 'aabaabaab', 'abcd' * 1500]
_cases = []
for _s in _words:
    _period = next(k for k in range(1, len(_s) + 1)
                   if len(_s) % k == 0 and _s[:k] * (len(_s) // k) == _s)
    _cases.append(_case([_s], [_period, len(_s) // _period]))
_add(41, '循环节：最短完整重复单元',
     '如果一个串能写成某个非空串重复 k 次，就称该串是完整重复单元，k=1 也允许。前缀函数最后一项 L 表示整串的最长真边界。'
     '将前缀与后缀重叠摆放，可得到候选周期 p=n-L。但“相邻字符按周期一致”不等于“能完整重复”：还必须检查 n 能否被 p 整除。'
     '例如 abcab 的候选周期为 3，却不能由 abc 完整重复得到，因此题目的最短单元长度仍为 5。',
     'candidate = len(s) - pi[-1]\nperiod = candidate if len(s) % candidate == 0 else len(s)\nprint(period, len(s) // period)',
     '输入一行非空小写英文字母串 s，1≤|s|≤100000。输出两个整数：最短完整重复单元的长度、该单元的重复次数。'
     '没有更短单元时输出 |s| 和 1。输入不包含空串。',
     _cases, r'''
s = sys.stdin.buffer.readline().decode().strip()
n = len(s)
pi = [0] * n
for i in range(1, n):
    j = pi[i - 1]
    while j and s[i] != s[j]:
        j = pi[j - 1]
    if s[i] == s[j]:
        j += 1
    pi[i] = j
p = n - pi[-1]
if n % p:
    p = n
print(p, n // p)
''',
     ['先计算整串的前缀函数，而不是枚举所有切分点。', '最长真边界长度为 L 时，最短候选周期是 n-L。',
      '检查 n % p；不整除时只能把整个串作为完整重复单元。'],
     '边界长度 L 等价于位移 n-L 后重叠位置全部相同，所以最长边界给出最短普通周期 p。若 p 整除 n，按 p 切分的各段完全相同。'
     '若存在更短的完整重复单元，其长度必须是最短周期的倍数并整除 n，进而 p 也整除 n；故不整除时没有真重复单元。易错点：漏掉整除检查。',
     'O(n)', 'O(n)', difficulty='进阶', skills=['前缀函数应用', '循环节', '整除条件'])


# 404: definition-based Z oracle.
def _z_oracle(s):
    result = [len(s)]
    for i in range(1, len(s)):
        k = 0
        while i + k < len(s) and s[k] == s[i + k]:
            k += 1
        result.append(k)
    return result


_words = ['aabcaabxaaaz', 'aaaaa', 'a', 'abcdef', 'abacaba', 'abcabcab',
          'baaaabaaa', 'aabaabaax']
_cases = [_case([s], _z_oracle(s)) for s in _words]
_cases.append(_case(['a' * 1200], list(range(1200, 0, -1))))
_add(41, 'Z 函数：复用前缀匹配区间',
     'Z[i] 是后缀 s[i:] 与整个串前缀的最长公共前缀长度，本题约定 Z[0]=n。与前缀函数不同，Z 直接回答“从当前位置能匹配前缀多少字符”。'
     '维护已经发现的、右端点最远的匹配区间 [l,r)。如果 i<r，区间内字符等同于某段前缀，因此可先借用 Z[i-l]，但最多借用 r-i。'
     '然后只比较尚未确认的字符并更新区间。使用半开区间可以让长度始终写作 r-l，降低边界出错概率。',
     'if i < right:\n    z[i] = min(right - i, z[i - left])\n# 区间 [left, right) 不包含 right',
     '输入一行非空小写英文字母串 s，1≤|s|≤1500。输出 n 个整数 Z[0] 至 Z[n-1]。本题特别规定 Z[0]=n；不接受把首项写成 0 的另一种约定。',
     _cases, r'''
s = sys.stdin.buffer.readline().decode().strip()
n = len(s)
z = [0] * n
z[0] = n
left = right = 0
for i in range(1, n):
    if i < right:
        z[i] = min(right - i, z[i - left])
    while i + z[i] < n and s[z[i]] == s[i + z[i]]:
        z[i] += 1
    if i + z[i] > right:
        left, right = i, i + z[i]
print(*z)
''',
     ['Z[0] 按题意直接设为 n，其余位置才需要计算。', '在匹配区间内部，借用镜像位置的信息，但不能越过 right。',
      '从已知长度继续向右比较，只有新区间更远时才更新 left、right。'],
     '区间 [left,right) 与同长度前缀完全相同，因此 min(right-i,Z[i-left]) 是可安全复用的匹配长度；继续逐字符比较后得到精确答案。'
     '区间外成功比较会推进最右边界，最多推进 n 次；每个位置至多额外经历一次失败，故总时间为线性。易错点：混用闭区间和半开区间，或忽略本题首项约定。',
     'O(n)', 'O(n)', skills=['Z 函数', '区间复用', '半开区间'])


# 405: dictionary/multiset oracle independent of the trie implementation.
_opsets = [
    [('I', 'app'), ('I', 'apple'), ('P', 'app'), ('C', 'app'), ('D', 'app'), ('C', 'app'), ('P', 'app')],
    [('I', 'a'), ('I', 'a'), ('C', 'a'), ('D', 'a'), ('C', 'a'), ('D', 'a'), ('D', 'a'), ('P', 'a')],
    [('C', 'x'), ('P', 'x'), ('D', 'x'), ('P', '-')],
    [('I', 'ab'), ('I', 'abc'), ('I', 'b'), ('P', '-'), ('P', 'a'), ('C', 'a'), ('P', 'b')],
    [('I', 'z'), ('D', 'zz'), ('P', 'z'), ('D', 'z'), ('I', 'zz'), ('C', 'z'), ('P', 'z')],
    [('I', 'hello'), ('I', 'helium'), ('I', 'help'), ('P', 'hel'), ('P', 'hello'), ('P', 'hex')],
    [('I', 'abc'), ('D', 'abc'), ('I', 'abc'), ('C', 'abc'), ('P', '-'), ('D', 'a'), ('P', '-')],
    [('I', 'a' * 40)] * 100 + [('P', 'a'), ('C', 'a' * 40)] + [('D', 'a' * 40)] * 99 + [('P', '-')],
]
_cases = []
for _ops in _opsets:
    _bag, _answer = {}, []
    for _op, _s in _ops:
        if _op == 'I':
            _bag[_s] = _bag.get(_s, 0) + 1
        elif _op == 'D':
            _bag[_s] = max(0, _bag.get(_s, 0) - 1)
        elif _op == 'C':
            _answer.append(_bag.get(_s, 0))
        else:
            _answer.append(sum(v for w, v in _bag.items() if w.startswith('' if _s == '-' else _s)))
    _cases.append(_case([len(_ops)] + _ops, _answer))
_add(41, 'Trie：可重复词典的插入删除与前缀计数',
     'Trie 把词的公共前缀合并成一条路径。每个节点保存子节点、经过该节点的词条数 pass_count，以及恰在该节点结束的词条数 end_count。'
     '重复插入必须累计次数，查询完整单词看 end_count，查询前缀看 pass_count，两者不能混用。删除时先确认完整词确实存在，再把路径计数减 1；不需要物理删除节点。'
     '根节点代表空前缀，其计数等于当前词典全部词条的数量。以数组下标代表节点，能避免复杂的类定义和递归。',
     'children = [{}]\nchildren.append({})\nnext_node = children[node].get(ch)\n# None 表示边不存在；节点编号 0 仍然是有效编号',
     '第一行 q（1≤q≤1000），之后 q 行，每行是操作码和字符串。I s 插入一份；D s 删除一份，不存在则忽略；C s 查询完整词的份数；P s 查询以前缀 s 开头的词条份数。'
     'I、D、C 的 s 均为非空小写英文串。P 允许空前缀，用单独的 - 表示。单词长度≤100，所有操作字符串总长度≤20000，至少有一次 C 或 P。每次查询输出一个整数。',
     _cases, r'''
data = sys.stdin.buffer.read().decode().split()
q = int(data[0])
children = [{}]
passed = [0]
ended = [0]
out = []
for i in range(q):
    op, word = data[1 + 2 * i:3 + 2 * i]
    if op == 'P' and word == '-':
        word = ''
    node = 0
    path = [0]
    found = True
    for ch in word:
        nxt = children[node].get(ch)
        if nxt is None:
            if op != 'I':
                found = False
                break
            nxt = len(children)
            children[node][ch] = nxt
            children.append({})
            passed.append(0)
            ended.append(0)
        node = nxt
        path.append(node)
    if op == 'I':
        for u in path:
            passed[u] += 1
        ended[node] += 1
    elif op == 'D':
        if found and ended[node] > 0:
            for u in path:
                passed[u] -= 1
            ended[node] -= 1
    elif op == 'C':
        out.append(str(ended[node] if found else 0))
    else:
        out.append(str(passed[node] if found else 0))
print('\n'.join(out))
''',
     ['为每个节点分别维护经过次数和结束次数。', '先完整走完删除路径，并检查结束次数大于 0，才能修改计数。',
      '把根节点也放进插入和删除路径，空前缀查询就能直接使用根计数。'],
     '每个词条恰好经过对应前缀的节点，因此插入或删除一份时沿路径增减 1，保持经过次数等于前缀匹配份数。终点计数只随完整词条更新，故完整查询也正确。'
     '不存在的删除完全不修改数据，计数不会变成负数。易错点：把重复词当集合、删除仅为前缀的词、忽略根的总数。',
     'O(L)，L 为所有操作字符串总长度（另有 O(q) 操作开销）', 'O(L)', skills=['Trie', '多重集合', '计数不变量'])


# 406: all rotations oracle; long repetitive case has a known answer.
_words = ['baca', 'abab', 'a', 'aaaa', 'cba', 'baabaa', 'cabca', 'zxyzzxy', 'cabbage']
_cases = []
for _s in _words:
    _rot, _idx = min((_s[i:] + _s[:i], i) for i in range(len(_s)))
    _cases.append(_case([_s], [_idx, _rot]))
_cases.append(_case(['b' + 'a' * 3500], [1, 'a' * 3500 + 'b']))
_add(41, '最小表示法：字典序最小的循环旋转',
     '在环形字符串中，不同起点会产生不同旋转；最小表示法寻找其中字典序最小者。直接构造 n 个旋转会产生平方级工作。'
     'Booth 算法把串复制成 s+s，维护两个候选起点 i、j 和共同匹配长度 k。如果它们在第 k 个字符第一次不同，较大一方不仅当前起点失败，随后 k 个起点也不可能最优，可以整段跳过。'
     '每次淘汰至少一个候选区间，并把 k 清零；若连续匹配了 n 个字符，则两者对应同一个旋转，取更小下标。',
     'doubled = s + s\nrotation = doubled[start:start + len(s)]\n# 字符之间可直接用 <、> 按字典序比较',
     '输入非空小写英文串 s，1≤n=|s|≤5000。把起点 i 的旋转定义为 s[i:]+s[:i]（0≤i<n）。输出一行两个项目：字典序最小旋转的最小起点下标、该旋转字符串。'
     '多个起点产生相同最小字符串时必须取最小下标。',
     _cases, r'''
s = sys.stdin.buffer.readline().decode().strip()
n = len(s)
t = s + s
i, j, k = 0, 1, 0
while i < n and j < n and k < n:
    a, b = t[i + k], t[j + k]
    if a == b:
        k += 1
        continue
    if a > b:
        i += k + 1
        if i <= j:
            i = j + 1
    else:
        j += k + 1
        if j <= i:
            j = i + 1
    k = 0
start = min(i, j)
print(start, t[start:start + n])
''',
     ['用 s+s 访问跨越末尾的旋转字符，无需反复取模。', '首次失配在偏移 k 时，较大候选起点向前跳 k+1。',
      '保持两个候选不同；最后输出 min(i,j)，这也处理了周期串的并列起点。'],
     '假设 i 方在偏移 k 处较大。前 k 个字符对应相等，所以对每个 0≤d≤k，从 i+d 开始的旋转都被从 j+d 开始的旋转击败；淘汰这段不会删掉最小答案。'
     '候选只增不减，失配时跳过已匹配长度，累计比较次数为 O(n)。相同旋转从未互相淘汰，最终较小候选就是最早起点。易错点：只跳 1、漏清零 k、输出起点从 1 编号。',
     'O(n)', 'O(n)', skills=['Booth 算法', '字典序', '候选区间淘汰'])


# 407: enumerate all substrings; the long single-letter fixture is algebraic.
def _palindrome_oracle(s):
    count, best, start = 0, 0, -1
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            t = s[i:j]
            if t == t[::-1]:
                count += 1
                if len(t) > best or (len(t) == best and i < start):
                    best, start = len(t), i
    return [count, best, start]


_words = ['abba', 'babad', '', 'a', 'abcdef', 'aaaaa', 'abacaba', 'aabbaa', 'abbaxyzyx']
_cases = [_case([s or '-'], _palindrome_oracle(s)) for s in _words]
_cases.append(_case(['a' * 12000], [12000 * 12001 // 2, 12000, 0]))
_add(41, 'Manacher：统计回文并定位最长回文',
     '回文可以按中心分成奇数长度与偶数长度。d1[i] 表示以字符 i 为中心的奇回文半径，包含中心本身；d2[i] 表示以 i-1 与 i 之间为中心的偶回文半径。'
     '半径为 k 的中心贡献 k 个不同区间，所以总回文数为 sum(d1)+sum(d2)。Manacher 维护最右回文区间，利用对称中心已有的半径作为初值，然后只向边界外扩展。'
     '同一内容出现在不同位置要分别计数；最长回文有多个时需要显式比较起点。本题分开处理奇偶，避免插入分隔符造成下标换算混乱。',
     'odd_length = 2 * d1[i] - 1\nodd_start = i - d1[i] + 1\neven_length = 2 * d2[i]\neven_start = i - d2[i]',
     '输入一行小写英文串 s，0≤n≤100000；空串用单独的 - 表示。输出三个整数：非空回文子串的区间数量、最长回文长度、最长回文最小起点下标（从 0 开始）。'
     '不同区间独立计数，即使内容相同。空串规定输出 0 0 -1。',
     _cases, r'''
s = sys.stdin.buffer.readline().decode().strip()
if s == '-':
    s = ''
n = len(s)
d1, d2 = [0] * n, [0] * n
left, right = 0, -1
for i in range(n):
    k = 1 if i > right else min(d1[left + right - i], right - i + 1)
    while i - k >= 0 and i + k < n and s[i - k] == s[i + k]:
        k += 1
    d1[i] = k
    if i + k - 1 > right:
        left, right = i - k + 1, i + k - 1
left, right = 0, -1
for i in range(n):
    k = 0 if i > right else min(d2[left + right - i + 1], right - i + 1)
    while i - k - 1 >= 0 and i + k < n and s[i - k - 1] == s[i + k]:
        k += 1
    d2[i] = k
    if i + k - 1 > right:
        left, right = i - k, i + k - 1
best, start = 0, -1
for i in range(n):
    for length, pos in ((2 * d1[i] - 1, i - d1[i] + 1), (2 * d2[i], i - d2[i])):
        if length > best or (length == best and length > 0 and pos < start):
            best, start = length, pos
print(sum(d1) + sum(d2), best, start)
''',
     ['先掌握 d1、d2 的半径定义，再写左右端点公式。', '镜像半径可能超出最右回文区间，要截断到 right-i+1 再扩展。',
      '每个中心贡献半径个回文；最长答案同时比较长度和起点。'],
     '最右回文内部关于中心对称，因此镜像中心的已知回文在公共范围内仍是回文；越过已知范围后逐字符验证，得到真实最大半径。'
     '每个非空回文有唯一中心和半径，求和无遗漏且无重复。每次额外成功扩展都会推进最右边界，所以奇偶两轮均为线性。易错点：偶回文镜像下标缺少 +1、把子串内容去重、遗漏空串约定。',
     'O(n)', 'O(n)', skills=['Manacher', '奇偶回文半径', '回文计数'])


# 408: each pattern is independently checked against every text position.
_acsets = [('ahishers', ['he', 'she', 'his', 'hers']), ('aaaaa', ['a', 'aa', 'aaa', 'a']),
           ('', ['a', 'abc']), ('abc', ['abcd', 'bc', 'c']),
           ('abababa', ['aba', 'ba', 'ababa', 'b']), ('mississippi', ['iss', 'ssi', 'i', 'ppi']),
           ('xyzxyz', ['zxy', 'xyz', 'zz']), ('abcabcab', ['ab', 'cab', 'bcab', 'abcabcab']),
           ('a' * 10000, ['a', 'aa', 'a' * 100, 'b'])]
_cases = []
for _s, _patterns in _acsets:
    _answer = [sum(_s[i:i + len(p)] == p for i in range(len(_s) - len(p) + 1)) for p in _patterns]
    _cases.append(_case([len(_patterns), *_patterns, _s or '-'], _answer))
_add(41, 'AC 自动机：一次扫描统计多个模式',
     '多个模式分别运行 KMP 会重复扫描文本。AC 自动机先把所有模式放入 Trie，再为每个节点建立 fail 指针，指向其路径串的最长可用真后缀状态。'
     '按 BFS 顺序补齐 26 种字符转移后，每个文本字符只需一次状态跳转。扫描时只给当前状态的访问次数加 1，随后逆 BFS 顺序把计数累加到 fail 父亲。'
     '这是因为某状态代表的长串出现时，其 fail 链上的所有模式后缀也同时出现。把累加留到最后，避免在 a、aa、aaa 这类嵌套模式上逐次枚举输出链。',
     'from collections import deque\nqueue = deque([0])\nu = queue.popleft()\nletter = ord(ch) - ord("a")\n# reversed(order) 保证先处理 fail 树的深层节点',
     '第一行模式数量 p（1≤p≤500），随后 p 行各给一个非空小写英文模式，再下一行给文本 t。模式总长度≤10000，0≤|t|≤100000，空文本写单独的 -。'
     '模式可重复，匹配允许重叠。按输入顺序输出 p 个整数，分别表示各模式出现次数；重复模式也分别输出相同的次数。',
     _cases, r'''
from collections import deque
data = sys.stdin.buffer.read().decode().split()
p = int(data[0])
patterns = data[1:p + 1]
text = data[p + 1]
if text == '-':
    text = ''
go = [[0] * 26]
fail = [0]
visits = [0]
terminal = []
for word in patterns:
    u = 0
    for ch in word:
        c = ord(ch) - 97
        if go[u][c] == 0:
            go[u][c] = len(go)
            go.append([0] * 26)
            fail.append(0)
            visits.append(0)
        u = go[u][c]
    terminal.append(u)
queue = deque(v for v in go[0] if v)
order = []
while queue:
    u = queue.popleft()
    order.append(u)
    for c in range(26):
        v = go[u][c]
        if v:
            fail[v] = go[fail[u]][c]
            queue.append(v)
        else:
            go[u][c] = go[fail[u]][c]
u = 0
for ch in text:
    u = go[u][ord(ch) - 97]
    visits[u] += 1
for u in reversed(order):
    visits[fail[u]] += visits[u]
print(*(visits[u] for u in terminal))
''',
     ['每个输入模式都记录一个终止节点；重复模式无需重复建节点。', 'BFS 时，fail 父亲的完整转移表已经准备好，可以直接继承。',
      '扫描只统计当前状态，再按逆 BFS 顺序把次数传播到 fail 父亲。'],
     '补齐的转移始终指向“已扫描文本的最长 Trie 前缀后缀”，这是 fail 定义与 BFS 层次顺序共同保证的。某模式在当前位置结束，等价于其终点在当前状态的 fail 祖先链上。'
     '逆序传播把每次访问恰好计入这些祖先，因此每个模式得到全部出现次数。易错点：只统计当前终点而漏掉后缀模式、正序传播、合并输出中的重复模式。',
     'O(26L+n+p)，L 为模式总长度', 'O(26L+p)', skills=['AC 自动机', '失败指针', '逆序计数传播'])


# 409: sorting literal suffixes is deliberately different from rank doubling.
_words = ['banana', 'aaaa', 'a', 'abcdef', 'fedcba', 'mississippi', 'abababa', 'cabca']
_cases = [_case([s], sorted(range(len(s)), key=lambda i, s=s: s[i:])) for s in _words]
_cases.append(_case(['a' * 1500], list(range(1499, -1, -1))))
_add(41, '后缀数组：倍增排序全部后缀',
     '后缀数组 sa 按字典序排列所有非空后缀的起点，例如 banana 的最小后缀是 a。直接把 s[i:] 作为排序键会复制平方级字符。'
     '倍增法先给单个字符排名，再用一对排名 (rank[i],rank[i+k]) 表示长 2k 的片段。第二段越界时记作 -1，使短且已结束的后缀排在较长相同前缀之前。'
     '每轮排序后重新编号相同键，令 k 翻倍；当每个后缀排名都不同就可以停止。这里使用 Python 内置比较排序，必须诚实计入每轮 O(n log n) 的代价。',
     'sa.sort(key=lambda i: (rank[i], rank[i + width] if i + width < n else -1))\n# key 返回元组：先比较第一项，再比较第二项',
     '输入一行非空小写英文串 s，1≤n≤2000。输出 n 个整数，表示所有非空后缀按字典序从小到大排列后的起点下标，下标从 0 开始。'
     '空后缀不参与排序；一个后缀是另一个的前缀时，更短者在前。',
     _cases, r'''
s = sys.stdin.buffer.readline().decode().strip()
n = len(s)
sa = list(range(n))
rank = [ord(c) for c in s]
width = 1
while width < n:
    sa.sort(key=lambda i: (rank[i], rank[i + width] if i + width < n else -1))
    new = [0] * n
    for j in range(1, n):
        a, b = sa[j - 1], sa[j]
        first = (rank[a], rank[a + width] if a + width < n else -1)
        second = (rank[b], rank[b + width] if b + width < n else -1)
        new[b] = new[a] + (first != second)
    rank = new
    if rank[sa[-1]] == n - 1:
        break
    width *= 2
print(*sa)
''',
     ['初始排名可以直接使用字符的 ord 值。', '长度 2k 的比较由前后两个长度 k 的排名组成；越界段的排名为 -1。',
      '新排名要按排好序的 sa 顺序赋值；相同键必须得到相同排名。'],
     '归纳地，rank 的大小关系等价于长度 k 前缀的字典序。两段排名组成的键因此准确比较长度 2k 前缀；相同键重新编号后，归纳条件继续成立。'
     '当 2k 覆盖全串或所有排名互异时，排序就是完整后缀字典序。共有 O(log n) 轮。易错点：原地覆盖旧排名、越界排名使用 0 与合法排名混淆、错误宣称本实现为 O(n log n)。',
     'O(n log²n)', 'O(n)', skills=['后缀数组', '倍增', '元组排序'])


# 410: literal substring set oracle; larger repetitive fixtures use identities.
_words = ['ababa', 'aaaa', '', 'a', 'abcde', 'banana', 'mississippi', 'abacaba']
_cases = [_case([s or '-'], len({s[i:j] for i in range(len(s)) for j in range(i + 1, len(s) + 1)})) for s in _words]
_cases += [_case(['a' * 5000], 5000), _case(['ab' * 2500], 9999)]
_add(41, '后缀数组与 LCP：不同子串数量',
     '长度 n 的串有 n(n+1)/2 个非空子串区间，但内容可能重复。按后缀字典序考虑：每个后缀贡献自身所有非空前缀，其中与前一个后缀相同的前缀已经出现，数量正好等于相邻最长公共前缀 LCP。'
     '因此不同子串数为 n(n+1)/2 减去全部相邻 LCP。Kasai 算法按原串起点顺序计算 LCP：从 i 移到 i+1 时，已知匹配长度最多先减少 1，再继续扩展。'
     '后缀数组负责把可能重复的前缀排到一起，LCP 则量化必须去掉的重复贡献。',
     'position = [0] * n\nfor order, start in enumerate(sa):\n    position[start] = order\n# position 是 sa 的逆排列',
     '输入一行小写英文串 s，0≤n≤20000，空串写单独的 -。输出一个整数，表示按内容去重后的非空连续子串数量。'
     '相同内容即使出现在不同区间也只计一次；空子串不计入。',
     _cases, r'''
s = sys.stdin.buffer.readline().decode().strip()
if s == '-':
    s = ''
n = len(s)
if n == 0:
    print(0)
    return
sa = list(range(n))
rank = [ord(c) for c in s]
width = 1
while width < n:
    sa.sort(key=lambda i: (rank[i], rank[i + width] if i + width < n else -1))
    new = [0] * n
    for r in range(1, n):
        a, b = sa[r - 1], sa[r]
        ka = (rank[a], rank[a + width] if a + width < n else -1)
        kb = (rank[b], rank[b + width] if b + width < n else -1)
        new[b] = new[a] + (ka != kb)
    rank = new
    if rank[sa[-1]] == n - 1:
        break
    width *= 2
position = [0] * n
for r, start in enumerate(sa):
    position[start] = r
common, duplicated = 0, 0
for i in range(n):
    r = position[i]
    if r == 0:
        common = 0
        continue
    j = sa[r - 1]
    while i + common < n and j + common < n and s[i + common] == s[j + common]:
        common += 1
    duplicated += common
    if common:
        common -= 1
print(n * (n + 1) // 2 - duplicated)
''',
     ['所有子串都能看成某个后缀的前缀。', '排序后，一个后缀与此前后缀重复的前缀长度，由它与相邻前驱的 LCP 决定。',
      '建立后缀排名的逆排列，按原串起点遍历并复用 common-1。'],
     '字典序中共享同一前缀的后缀必连续排列，所以当前后缀已出现的前缀恰为它与前驱的共同前缀，共 LCP 个。逐后缀去掉这些贡献，每种子串恰好保留一次。'
     'Kasai 在起点前进后保留 common-1 个已知相等字符，总扩展为线性；总复杂度由倍增排序主导。易错点：把区间数当内容数、把空串也计入、最小后缀处忘记重置 common。',
     'O(n log²n)', 'O(n)', skills=['后缀数组', 'Kasai 算法', '不同子串计数'])


# 411: trial division oracle for primality (not another sieve).
def _is_prime_trial(n):
    return n >= 2 and all(n % d for d in range(2, int(n ** 0.5) + 1))


_querysets = [[1, 2, 3, 10, 20], [0, 1, 4, 9], [2], [25, 29, 30, 31],
              [49, 50, 97, 100], [1000, 7, 1000, 0], [121, 127, 128], [4999, 5000]]
_cases = [_case([len(qs), qs], [sum(_is_prime_trial(x) for x in range(n + 1)) for n in qs]) for qs in _querysets]
_cases.append(_case([3, [100000, 200000, 10]], [9592, 17984, 4]))
_add(42, '埃氏筛：多次查询素数个数',
     '素数是大于 1 且只有 1 与自身两个正因子的整数。多次查询“有多少素数不超过 n”时，逐个试除会重复工作。埃氏筛先假设所有数为素数，再让每个尚未被划掉的 p 标记其倍数。'
     '可以从 p² 开始标记，因为更小的 p 的倍数已有较小质因子，会在此前被处理。筛到最大查询值后建立前缀计数，任一查询都能 O(1) 回答。'
     '0 和 1 不是素数；最大查询为 0 时也要保证初始化下标合法。',
     'from math import isqrt\nflags = bytearray(b"\\x01") * (limit + 1)\nfor p in range(2, isqrt(limit) + 1):\n    pass',
     '输入首个整数 q（1≤q≤1000），随后 q 个整数 n，均满足 0≤n≤200000，换行位置任意。对每个查询输出一个整数：区间 [0,n] 内的素数数量。',
     _cases, r'''
from math import isqrt
data = list(map(int, sys.stdin.buffer.read().split()))
q = data[0]
queries = data[1:1 + q]
limit = max(queries)
prime = bytearray(b'\x01') * (limit + 1)
prime[0] = 0
if limit >= 1:
    prime[1] = 0
for p in range(2, isqrt(limit) + 1):
    if prime[p]:
        for multiple in range(p * p, limit + 1, p):
            prime[multiple] = 0
prefix = [0] * (limit + 1)
for x in range(1, limit + 1):
    prefix[x] = prefix[x - 1] + prime[x]
print(*(prefix[n] for n in queries))
''',
     ['先读完查询，筛到最大的 n 即可。', '只有 prime[p] 仍为真时才需要标记，起点是 p*p。',
      '再做一次前缀累加，把每次查询从扫描区间变成查数组。'],
     '任一合数都有不超过其平方根的质因子，因此会被某个素数的倍数标记；素数不会被其他素数整除，所以保留下来。前缀和随后准确累计不超过各下标的素数数目。'
     '标记工作量为 M/2+M/3+M/5+…，得到 O(M log log M)。易错点：把 1 当素数、漏掉平方数、只输出最大查询的结果。',
     'O(M log log(M+2)+q)，M 为最大查询', 'O(M+q)', difficulty='进阶', skills=['埃氏筛', '前缀计数', '离线预处理'])


# 412: gcd enumeration for small values; factorizations give large answers.
_querysets = [[1, 9, 10, 12], [2, 3, 5, 7], [4, 8, 16, 32], [6, 18, 36],
              [25, 49, 121], [60, 72, 90, 100], [97, 101, 210]]
_cases = [_case([len(qs), qs], [sum(gcd(k, n) == 1 for k in range(1, n + 1)) for n in qs]) for qs in _querysets]
_cases.append(_case([5, [1000000000, 999999937, 99980001, 536870912, 387420489]],
                    [400000000, 999999936, 59994000, 268435456, 258280326]))
_add(42, '欧拉函数：互质整数的数量',
     '欧拉函数 φ(n) 表示 1 到 n 中与 n 互质的整数个数，约定 φ(1)=1。若 n 的不同质因子为 p，则 φ(n)=n∏(1-1/p)。'
     '原因是互质数必须排除所有这些质因子的倍数，乘积恰好实现容斥。计算时令 answer=n；每发现一个新质因子 p，执行 answer-=answer//p，再把 n 中所有 p 因子除尽。'
     '同一个质因子无论指数多大都只处理一次。试除结束后剩余的大于 1 的数本身是质数，也必须纳入。',
     'while remaining % p == 0:\n    remaining //= p\nanswer -= answer // p\n# // 是整数除法，避免把整数公式写成浮点数',
     '输入 q（1≤q≤30），随后 q 个整数 n（1≤n≤10^9）。对每个 n 输出 φ(n)，即区间 [1,n] 中与 n 最大公约数为 1 的整数个数。',
     _cases, r'''
data = list(map(int, sys.stdin.buffer.read().split()))
out = []
for n in data[1:1 + data[0]]:
    remaining, answer = n, n
    p = 2
    while p * p <= remaining:
        if remaining % p == 0:
            answer -= answer // p
            while remaining % p == 0:
                remaining //= p
        p += 1
    if remaining > 1:
        answer -= answer // remaining
    out.append(str(answer))
print('\n'.join(out))
''',
     ['互质只与不同质因子有关，不需要枚举每个候选整数。', '发现质因子后，更新答案一次，并除尽它的所有幂。',
      '循环条件使用 remaining；循环后 remaining>1 时仍有一个质因子。'],
     '对每个质因子 p 排除其倍数，容斥展开即 n∏(1-1/p)。试除过程恰好访问每个不同质因子一次，逐次整数更新与乘积完全相同。'
     '剩余数若仍为合数，其较小因子不会超过其平方根，与循环退出条件矛盾，所以最后剩余者可直接处理。易错点：质因子重复更新、漏掉末尾大质因子、把 φ(1) 设成 0。',
     'O(q√M)，M 为最大 n', 'O(q) 保存查询；单次计算 O(1)', difficulty='进阶', skills=['质因数分解', '欧拉函数', '容斥'])


# 413: enumerate all residue classes for the small fixtures.
_equations = [(3, 4, 7), (6, 5, 9), (6, 3, 9), (0, 0, 5), (0, 3, 5),
              (-3, 2, 7), (14, -6, 20), (8, 0, 12), (5, 8, 13)]
_cases = []
for _a, _b, _m in _equations:
    _solutions = [x for x in range(_m) if (_a * x - _b) % _m == 0]
    _cases.append(_case([[_a, _b, _m]], [_solutions[0], len(_solutions)] if _solutions else -1))
_cases += [_case([[1, -1, 10**18]], [10**18 - 1, 1]),
           _case([[10**18, 0, 10**18]], [0, 10**18])]
_add(42, '扩展欧几里得：求解线性同余',
     '线性同余 ax≡b (mod m) 意味着 ax-b 能被 m 整除。设 g=gcd(a,m)，仅当 g 整除 b 时有解；约去 g 后，a/g 与 m/g 互质，才能使用乘法逆元。'
     '扩展欧几里得不仅计算最大公约数，还维护系数 x、y，使 ax+my=g。于是 x 是约分后系数的逆元，乘 b/g 得到一组解。'
     '解在模 m/g 意义下唯一，在 [0,m) 内恰有 g 个，最小非负解可用 % (m/g) 归一化。这也统一处理 a=0 和负数。',
     'quotient = old_r // r\nold_r, r = r, old_r - quotient * r\n# 同时赋值右侧全部使用更新前的状态\n# a % m 在 m>0 时得到 [0,m) 范围内的余数',
     '输入三个整数 a、b、m，|a|、|b|≤10^18，2≤m≤10^18。求 ax≡b (mod m)。无解只输出 -1；有解输出最小非负整数解 x0，以及区间 [0,m) 中的解的数量。'
     '不保证 a 与 m 互质。a=0 也是合法输入。',
     _cases, r'''
a, b, m = map(int, sys.stdin.buffer.read().split())
a %= m
old_r, r = a, m
old_x, x = 1, 0
while r:
    quotient = old_r // r
    old_r, r = r, old_r - quotient * r
    old_x, x = x, old_x - quotient * x
g = old_r
if b % g:
    print(-1)
else:
    modulus = m // g
    smallest = (old_x * (b // g)) % modulus
    print(smallest, g)
''',
     ['先判断 gcd(a,m) 是否整除 b；不互质并不总是无解。', '在欧几里得每次余数更新时，同步更新 a 的系数。',
      '最小解应对 m/g 取模，解的份数是 g；模数为 1 时最小解仍为 0。'],
     '等式 ax+my=g 的系数随欧几里得线性组合保持不变。若 g 不整除 b，则左侧永远是 g 的倍数而不可能等于 b；若整除，乘 b/g 得到特解。'
     '约分后的 a/g 与 m/g 互质，所以全部解为 x0+k(m/g)，在 [0,m) 内恰有 g 个。易错点：对原模数归一化后直接当最小解、对合数模数盲用费马逆元、遗漏 a=0。',
     'O(log m)', 'O(1)', skills=['扩展欧几里得', '线性同余', '逆元存在条件'])


# 414: direct search over one common period for small CRT systems.
_systems = [[(2, 3), (3, 5)], [(1, 2), (0, 4)], [(2, 4), (6, 8)], [(5, 7)],
            [(-1, 3), (3, 4)], [(0, 1), (4, 6)], [(1, 2), (1, 3), (1, 5)],
            [(0, 4), (0, 6), (0, 9)], [(3, 5), (3, 5)]]
_cases = []
for _system in _systems:
    _period = 1
    for _r, _m in _system:
        _period = _period // gcd(_period, _m) * _m
    _x = next((x for x in range(_period) if all((x - r) % m == 0 for r, m in _system)), None)
    _cases.append(_case([len(_system), *_system], -1 if _x is None else [_x, _period]))
_cases.append(_case([3, [999999, 1000000], [999982, 999983], [999978, 999979]],
                    [1000000 * 999983 * 999979 - 1, 1000000 * 999983 * 999979]))
_add(42, '广义中国剩余定理：合并非互质模数',
     '经典 CRT 常要求模数两两互质，广义 CRT 则允许共享因子。维护已经合并的 x≡r (mod M)，准备加入 x≡a (mod m)。写成 x=r+Mt 后，需要解 Mt≡a-r (mod m)。'
     '设 g=gcd(M,m)，当且仅当 g 整除 a-r 时可合并。约去 g 后用扩展欧几里得求 t，再把答案对 lcm(M,m) 归一化。'
     '逐条合并把复杂方程组化为同一个两方程步骤；任何一步冲突都意味着原系统无解。余数可以为负，先归一化即可。',
     'g = gcd(modulus, m)\nnew_modulus = modulus // g * m\nnew_remainder = (remainder + modulus * t) % new_modulus',
     '第一行 k（1≤k≤50），随后 k 行给 ri、mi，表示 x≡ri (mod mi)。|ri|≤10^18，1≤mi≤10^6，所有模数的最小公倍数保证≤10^18。'
     '模数不保证互质。无解输出 -1；否则输出最小非负解 x0 和全部解的最小正周期 M，即模数的最小公倍数。',
     _cases, r'''
data = list(map(int, sys.stdin.buffer.read().split()))
k = data[0]
remainder, modulus = 0, 1
for i in range(k):
    a, m = data[1 + 2 * i:3 + 2 * i]
    a %= m
    old_r, r = modulus, m
    old_x, x = 1, 0
    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_x, x = x, old_x - q * x
    g = old_r
    difference = a - remainder
    if difference % g:
        print(-1)
        return
    reduced = m // g
    t = (difference // g * old_x) % reduced
    new_modulus = modulus * reduced
    remainder = (remainder + modulus * t) % new_modulus
    modulus = new_modulus
print(remainder, modulus)
''',
     ['把前面所有方程压缩成一个余数 remainder 和一个周期 modulus。', '加入新方程时，转换成 modulus*t≡a-remainder (mod m)。',
      '判定整除条件后求 t，对 lcm 取模；新周期不是简单的 modulus*m。'],
     '根据归纳假设，旧系统全部解恰为 remainder+modulus*t。新方程约束 t 的线性同余；无解时原系统也无解，有解时 t 的周期为 m/g。'
     '代回后 x 的周期就是 modulus*m/g，归一化余数得到全部公共解中的最小非负者。易错点：套用互质 CRT、忘记检查冲突、把负余数当无解、模数 1 时除零。',
     'O(k log(M+1))，M 为最终公倍数（整数算术模型）', 'O(k) 保存方程；合并状态 O(1)', skills=['广义 CRT', '线性同余合并', '最小公倍数'])


# 415: Python's exact binomial coefficients provide independent expectations.
_MOD = 1000000007
_combsets = [[(5, 2), (5, 0), (3, 5)], [(0, 0), (0, 1)], [(10, 3), (10, 7)],
             [(1, 0), (1, 1), (1, 2)], [(100, 50), (100, 99)],
             [(20, 10), (30, 15), (50, 25)], [(1000, 500), (999, 2)],
             [(200000, 0), (200000, 1), (200000, 2), (200000, 200000)]]
_cases = [_case([len(qs), *qs], [comb(n, k) % _MOD if k <= n else 0 for n, k in qs]) for qs in _combsets]
_add(42, '组合数预处理：阶乘与逆阶乘',
     '组合数 C(n,k) 统计从 n 个不同元素中无序选择 k 个的方案数。公式 n!/(k!(n-k)!) 中的除法在取模后不能直接使用 //，而要乘分母的模逆元。'
     '本题固定素数 P=1000000007，且 n<P，所以所有需要的阶乘都非零并存在逆元。根据费马小定理，a 的逆元为 pow(a,P-2,P)。'
     '先预处理阶乘，只求一次最大阶乘的逆元，再从后往前递推 invfact[i-1]=invfact[i]*i，即可把每次组合数查询降到 O(1)。',
     'inverse = pow(value, MOD - 2, MOD)\nanswer = fact[n] * invfact[k] % MOD * invfact[n - k] % MOD\n# 三参数 pow 在每次乘法时取模',
     '输入 q（1≤q≤1000），随后 q 行各给 n、k（0≤n,k≤200000）。对每组输出 C(n,k) 对固定素数 1000000007 取模的结果。'
     '约定 k>n 时答案为 0，C(0,0)=1。所有 n 均小于模数，这一条件保证逆阶乘存在。',
     _cases, r'''
data = list(map(int, sys.stdin.buffer.read().split()))
q = data[0]
queries = [(data[1 + 2 * i], data[2 + 2 * i]) for i in range(q)]
MOD = 1000000007
limit = max(n for n, k in queries)
fact = [1] * (limit + 1)
for i in range(1, limit + 1):
    fact[i] = fact[i - 1] * i % MOD
invfact = [1] * (limit + 1)
invfact[limit] = pow(fact[limit], MOD - 2, MOD)
for i in range(limit, 0, -1):
    invfact[i - 1] = invfact[i] * i % MOD
out = []
for n, k in queries:
    value = 0 if k > n else fact[n] * invfact[k] % MOD * invfact[n - k] % MOD
    out.append(str(value))
print('\n'.join(out))
''',
     ['先读所有查询，确定阶乘预处理的最大 n。', '只对 fact[limit] 调用一次快速幂，然后倒序求出全部逆阶乘。',
      'k>n 必须先返回 0，否则 n-k 为负数会在 Python 中产生合法但错误的下标。'],
     '费马小定理在素数模数与非零分母条件下保证逆元公式正确。倒序递推来自 (i-1)! 的逆元等于 i 乘 i! 的逆元，因此所有 invfact 都正确。'
     '将阶乘公式中的除法替换成模逆元乘法，所得结果与整数 C(n,k) 的余数一致。易错点：使用 //、忘记 n<P 前提、对每个查询都重新计算阶乘。',
     'O(N+q+log P)，N 为最大 n', 'O(N+q)', skills=['组合数', '费马逆元', '阶乘预处理'])


# 416: exact comb for ordinary inputs, small-k integer formulas for huge n.
_lucassets = [(7, [(8, 1), (8, 2), (10, 3)]), (2, [(5, 1), (5, 2), (7, 3), (0, 0)]),
              (3, [(9, 3), (8, 4), (4, 7)]), (5, [(25, 5), (24, 12), (25, 0)]),
              (11, [(120, 60), (121, 11), (11, 1)]), (13, [(50, 20), (100, 99)]),
              (1999, [(2000, 1000), (3998, 1999)]),
              (97, [(10**18, 0), (10**18, 1), (10**18, 2), (10**18, 10**18), (3, 10**18)])]
_cases = [_case([[p, len(qs)], *qs], [comb(n, k) % p if k <= n else 0 for n, k in qs]) for p, qs in _lucassets]
_add(42, 'Lucas 定理：大 n、小素数模数的组合数',
     '当 n≥p 时，n! 在模 p 下为 0，直接使用阶乘逆元公式会失效。Lucas 定理把 n、k 按素数 p 进制展开，令各位为 ni、ki，则 C(n,k)≡∏C(ni,ki) (mod p)。'
     '每一位都小于 p，可以使用普通阶乘与逆阶乘；某位 ki>ni 时，该位组合数为 0，整个答案也为 0。'
     '因此即使 n 达到 10^18，只需要处理 O(log_p n) 个数位。p 为素数是定理和逆元计算共同依赖的前提，不能直接替换成任意合数。',
     'digit_n, digit_k = n % p, k % p\nn //= p\nk //= p\n# 每次取出最低 p 进制数位',
     '第一行给素数 p 和查询数 q，2≤p≤2000，1≤q≤100。随后 q 行各给 n、k，0≤n,k≤10^18。输出每组 C(n,k) mod p；k>n 时输出 0，C(0,0)=1。'
     '输入保证 p 为素数，无需自行验证素性。',
     _cases, r'''
data = list(map(int, sys.stdin.buffer.read().split()))
p, q = data[:2]
fact = [1] * p
for i in range(1, p):
    fact[i] = fact[i - 1] * i % p
invfact = [1] * p
invfact[p - 1] = pow(fact[p - 1], p - 2, p)
for i in range(p - 1, 0, -1):
    invfact[i - 1] = invfact[i] * i % p
out = []
for i in range(q):
    n, k = data[2 + 2 * i:4 + 2 * i]
    answer = 1
    while n or k:
        a, b = n % p, k % p
        if b > a:
            answer = 0
            break
        answer = answer * fact[a] % p * invfact[b] % p * invfact[a - b] % p
        n //= p
        k //= p
    out.append(str(answer))
print('\n'.join(out))
''',
     ['只预处理 0 到 p-1 的阶乘，不要尝试为 10^18 建数组。', '反复使用 %p 与 //p 同时取出 n、k 的最低位。',
      '只要某一位 k 的数字大于 n 的数字，就立即得到 0。'],
     '模素数 p 时，二项式中间系数可被 p 整除，所以 (1+x)^p≡1+x^p。把 n 按 p 进制分解，比较展开式中 x^k 的系数，得到 Lucas 的逐位乘积公式。'
     '每位小于 p，阶乘均可逆，程序因此正确计算每个因子并累乘。易错点：使用合数模数、循环只检查 n 而遗漏 k 的高位、把 (0,0) 输出为 0。',
     'O(p+q(1+log_p(N+1))+log p)，N 为最大输入数', 'O(p+q)', skills=['Lucas 定理', '进制分解', '组合数模素数'])


# 417: dynamic-programming balanced-prefix oracle for small sizes.
def _balanced_oracle(n):
    ways = {0: 1}
    for _ in range(2 * n):
        nxt = {}
        for balance, count in ways.items():
            nxt[balance + 1] = nxt.get(balance + 1, 0) + count
            if balance:
                nxt[balance - 1] = nxt.get(balance - 1, 0) + count
        ways = nxt
    return ways.get(0, 0)


_querysets = [[0, 1, 2, 3], [4, 5], [6], [7, 8], [9, 10], [12, 15], [20, 25]]
_cases = [_case([len(qs), qs], [_balanced_oracle(n) % _MOD for n in qs]) for qs in _querysets]
_cases.append(_case([3, [1000, 5000, 200000]],
                    [comb(2 * n, n) // (n + 1) % _MOD for n in [1000, 5000, 200000]]))
_add(42, 'Catalan 数：合法括号序列的计数',
     '一个合法括号序列必须左右括号总数相等，且任何前缀中左括号不少于右括号。把左括号看作 +1、右括号看作 -1，就得到从 0 出发、不跌到负数并回到 0 的路径。'
     '所有含 n 个左括号和 n 个右括号的排列有 C(2n,n) 个。对首次跌到 -1 的路径进行前缀反射，可与另一类路径一一对应，坏路径数为 C(2n,n-1)。'
     '由对称性 C(2n,n-1)=C(2n,n+1)，答案是两项组合数之差，即第 n 个 Catalan 数。空序列也是一种合法方案。',
     'answer = (choose(2 * n, n) - choose(2 * n, n + 1)) % MOD\n# 取模差值也要再 % MOD，输出非负余数',
     '输入 q（1≤q≤1000），随后 q 个整数 n（0≤n≤200000）。对每个 n 输出长度恰为 2n、包含 n 对括号的合法括号序列数量，结果对素数 1000000007 取模。'
     '空序列计为 1；只区分括号排列，不给括号额外编号。保证 2n 小于模数。',
     _cases, r'''
data = list(map(int, sys.stdin.buffer.read().split()))
queries = data[1:1 + data[0]]
MOD = 1000000007
limit = 2 * max(queries)
fact = [1] * (limit + 1)
for i in range(1, limit + 1):
    fact[i] = fact[i - 1] * i % MOD
invfact = [1] * (limit + 1)
invfact[limit] = pow(fact[limit], MOD - 2, MOD)
for i in range(limit, 0, -1):
    invfact[i - 1] = invfact[i] * i % MOD
def choose(n, k):
    if k < 0 or k > n:
        return 0
    return fact[n] * invfact[k] % MOD * invfact[n - k] % MOD
out = [(choose(2 * n, n) - choose(2 * n, n + 1)) % MOD for n in queries]
print(*out)
''',
     ['合法性不仅要求左右数量相等，还要求每个前缀余额非负。', '先数所有排列，再用反射原理减去首次越过负数边界的坏排列。',
      '预处理到 2*max(n)，使用组合数差公式；n=0 时第二项为 0。'],
     '对坏序列截至首次余额 -1 的前缀交换左右括号，可逆地映射到左括号 n+1 个、右括号 n-1 个的排列，因此坏序列恰有 C(2n,n+1) 个。'
     '从全部 C(2n,n) 个排列中相减即得合法序列数。2n<P 保证阶乘逆元存在。易错点：只检查总括号数、把 n 对括号误当长度 n、忽略空序列、未规范化减法余数。',
     'O(N+q+log P)，N 为最大 n', 'O(N+q)', skills=['Catalan 数', '反射原理', '组合计数'])


# 418: elementary linear recurrence oracle; huge fixtures are fixed recurrences.
def _recurrence_oracle(a, b, f0, f1, n, mod):
    if n == 0:
        return f0 % mod
    previous, current = f0 % mod, f1 % mod
    for _ in range(2, n + 1):
        previous, current = current, (a * current + b * previous) % mod
    return current


_recsets = [[(1, 1, 0, 1, 10, 1000), (1, 1, 0, 1, 0, 1000)],
            [(2, 3, 4, 5, 1, 7), (2, 3, 4, 5, 2, 100)],
            [(0, 1, 3, 7, 9, 100), (0, 1, 3, 7, 10, 100)],
            [(0, 0, 9, 8, 2, 13), (0, 0, 9, 8, 0, 2)],
            [(1, 1, 0, 1, 100, 1000000007)], [(5, 7, 11, 13, 40, 1000)],
            [(1000000000, 999999999, 1000000000, 999999999, 50, 999999937)]]
_cases = [_case([len(qs), *qs], [_recurrence_oracle(*row) for row in qs]) for qs in _recsets]
_cases.append(_case([3, [1, 0, 3, 8, 10**18, 1000], [0, 1, 3, 8, 10**18, 1000],
                     [0, 1, 3, 8, 10**18 - 1, 1000]], [8, 3, 8]))
_add(42, '矩阵快速幂：计算超大下标递推',
     '二阶递推 F(n)=aF(n-1)+bF(n-2) 可以用状态向量 [F(n),F(n-1)] 表示；每前进一步，左乘转移矩阵 [[a,b],[1,0]]。'
     '所以 n≥1 时，只需计算该矩阵的 n-1 次幂，再乘初始向量 [F1,F0]。二进制快速幂把指数拆成二进制位：当前位为 1 就把底数乘进答案，每轮将底数平方。'
     '矩阵乘法通常不满足交换律，必须保持乘法方向；但满足结合律，因此快速幂仍然成立。这里模数可以为合数，因为完全不需要除法或逆元。',
     '# 2×2 矩阵用行优先四元组 (a00,a01,a10,a11) 保存\nidentity = (1, 0, 0, 1)\nwhile exponent:\n    exponent //= 2',
     '第一行 T（1≤T≤100），随后 T 行各给 a b F0 F1 n m。定义 F(0)=F0、F(1)=F1、F(i)=aF(i-1)+bF(i-2)（i≥2）。'
     '0≤a,b,F0,F1≤10^9，0≤n≤10^18，2≤m≤10^9，m 不必为素数。每组输出 F(n) mod m。',
     _cases, r'''
data = list(map(int, sys.stdin.buffer.read().split()))
out = []
for case in range(data[0]):
    a, b, f0, f1, n, mod = data[1 + 6 * case:7 + 6 * case]
    if n == 0:
        out.append(str(f0 % mod))
        continue
    def multiply(x, y):
        return ((x[0] * y[0] + x[1] * y[2]) % mod,
                (x[0] * y[1] + x[1] * y[3]) % mod,
                (x[2] * y[0] + x[3] * y[2]) % mod,
                (x[2] * y[1] + x[3] * y[3]) % mod)
    result = (1, 0, 0, 1)
    base = (a % mod, b % mod, 1, 0)
    exponent = n - 1
    while exponent:
        if exponent & 1:
            result = multiply(result, base)
        base = multiply(base, base)
        exponent >>= 1
    out.append(str((result[0] * f1 + result[1] * f0) % mod))
print('\n'.join(out))
''',
     ['状态需要同时保存连续两项，转移矩阵第二行是 [1,0]。', 'n=0 单独返回；n≥1 使用指数 n-1。',
      '幂的初值是单位矩阵，矩阵每次乘法后都对 m 取模。'],
     '转移矩阵乘状态向量的第一行恰为递推式，第二行把旧 F(n) 移到下一状态，因此归纳可得 n-1 次转移得到所需项。'
     '快速幂维护 result*base^exponent 等于目标幂；按指数奇偶更新保持该不变量，指数归零时 result 即目标矩阵。易错点：指数用 n、把单位矩阵写成全 1、对 n=0 执行负指数循环。',
     'O(T(1+log(N+1)))，N 为最大下标', 'O(T) 保存测试组；矩阵状态 O(1)', skills=['矩阵快速幂', '线性递推', '单位矩阵'])


# 419: divisor enumeration and a simple harmonic sum are independent oracles.
_numbers = [1, 2, 6, 10, 16, 37, 100, 10000, 100000]
_cases = [_case([n], sum(n // d for d in range(1, n + 1))) for n in _numbers]
# Hyperbola symmetry counts lattice points below xy=n independently of blocks.
_large_n, _root_n = 10**12, 10**6
_cases.append(_case([_large_n], 2 * sum(_large_n // d for d in range(1, _root_n + 1)) - _root_n**2))
_add(42, '整除分块：所有整数的约数个数之和',
     '记 τ(x) 为正整数 x 的正约数数量，本题求 Στ(x)。交换计数顺序：固定约数 d，它能整除不超过 n 的 floor(n/d) 个数，因此答案为 Σ floor(n/d)。'
     '逐个 d 累加仍需 O(n)。观察商 q=floor(n/l) 在一整段下标中保持不变，该段最远右端点是 r=floor(n/q)，这段贡献为 q*(r-l+1)。'
     '每次把 l 跳到 r+1，就能按商相等的区间分块。不同商只有 O(√n) 种：小下标不超过 √n，大下标对应的商不超过 √n。',
     'quotient = n // left\nright = n // quotient\ncontribution = quotient * (right - left + 1)\nleft = right + 1',
     '输入一个整数 n（1≤n≤10^12）。输出精确整数 Σ_{x=1}^n τ(x)，其中 τ(x) 为 x 的正约数个数。答案不取模，Python 整数能够保存结果。',
     _cases, r'''
n = int(sys.stdin.buffer.read())
answer = 0
left = 1
while left <= n:
    quotient = n // left
    right = n // quotient
    answer += quotient * (right - left + 1)
    left = right + 1
print(answer)
''',
     ['先交换“枚举被除数”和“枚举约数”的顺序，得到 Σ(n//d)。', '如果当前商为 q，那么保持该商的最后一个下标是 n//q。',
      '一次累加整段长度乘 q，然后直接跳到下一个区间。'],
     '每一对满足 d|x 的正整数 (d,x) 在两种求和顺序中各出现一次，故约数和等于 Σfloor(n/d)。'
     '当 q=floor(n/l) 时，对所有 l≤d≤floor(n/q)，商都等于 q；下一位置商变小，因此分块互不重叠且恰好覆盖 [1,n]。易错点：区间长度漏加 1、下一块仍从 right 开始、用浮点除法影响大数端点。',
     'O(√n)', 'O(1)', skills=['整除分块', '交换求和', '约数函数'])


# 420: gcd enumeration for small n, totient sieve identity for the larger case.
_numbers = [1, 2, 3, 5, 10, 20, 37, 60]
_cases = [_case([n], sum(gcd(a, b) == 1 for a in range(1, n + 1) for b in range(1, n + 1))) for n in _numbers]
_limit = 20000
_phi = list(range(_limit + 1))
for _p in range(2, _limit + 1):
    if _phi[_p] == _p:
        for _multiple in range(_p, _limit + 1, _p):
            _phi[_multiple] -= _phi[_multiple] // _p
_cases.append(_case([_limit], 2 * sum(_phi[1:]) - 1))
_add(42, 'Möbius 反演：统计有序互质数对',
     'Möbius 函数 μ(1)=1；若 n 含平方质因子则 μ(n)=0；否则有 k 个不同质因子时 μ(n)=(-1)^k。关键恒等式是 Σ_{d|g}μ(d) 在 g=1 时等于 1，其余情况等于 0。'
     '用它表示“gcd(a,b)=1”的指示值，再交换求和，得到互质有序数对数量 Σ μ(d)*floor(n/d)^2。'
     '本题用线性筛同时生成素数与 μ：新素数 μ=-1；若 p 已整除 i，μ(ip)=0 并停止；否则 μ(ip)=-μ(i)。这把容斥中正负符号与平方因子的消除统一进一张数组。',
     'mu[1] = 1\nif i % p == 0:\n    mu[i * p] = 0\n    break\nmu[i * p] = -mu[i]',
     '输入一个整数 n（1≤n≤1000000）。输出满足 1≤a,b≤n 且 gcd(a,b)=1 的有序整数对 (a,b) 数量，答案不取模。'
     '(a,b) 与 (b,a) 在 a≠b 时算不同数对；(1,1) 计入。',
     _cases, r'''
n = int(sys.stdin.buffer.read())
mu = [0] * (n + 1)
mu[1] = 1
composite = bytearray(n + 1)
primes = []
for i in range(2, n + 1):
    if not composite[i]:
        primes.append(i)
        mu[i] = -1
    for p in primes:
        value = i * p
        if value > n:
            break
        composite[value] = 1
        if i % p == 0:
            mu[value] = 0
            break
        mu[value] = -mu[i]
answer = 0
for d in range(1, n + 1):
    quotient = n // d
    answer += mu[d] * quotient * quotient
print(answer)
''',
     ['用 Σ_{d|gcd(a,b)}μ(d) 表示互质条件，而不是枚举每一对做 gcd。', '固定 d，同时能被 d 整除的 a、b 各有 n//d 种选择。',
      '线性筛遇到 i%p==0 时令 μ(ip)=0 并 break；这个停止条件保证每个合数只被其最小质因子生成。'],
     '若 g 有 k>0 个不同质因子，非零 μ 项对应这些质因子的所有子集，其和为 (1-1)^k=0；g=1 时仅有 μ(1)=1。因此上述除数和正是互质指示值。'
     '交换有限求和后，每个 d 贡献 μ(d)*floor(n/d)^2。线性筛的两种更新分别对应重复质因子与新增质因子，正确生成 μ。易错点：将有序对除以 2、漏掉 μ(1)、含平方因子时仅变号。',
     'O(n)', 'O(n)', skills=['Möbius 函数', '线性筛', '数论反演'])


assert [item['id'] for item in PROBLEMS] == list(range(401, 421))
