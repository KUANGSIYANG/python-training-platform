"""ACM chapters 39--40, with independent, deterministic fixture oracles.

The small oracles deliberately enumerate paths, cuts, assignments or partitions;
the reference programs demonstrate the scalable algorithms taught in each lesson.
"""

from functools import lru_cache
from itertools import permutations, product
from math import comb
from textwrap import dedent, indent

from .schema import acm_problem

PROBLEMS = []
_counts = {}


def _text(*rows):
    return '\n'.join(' '.join(map(str, row)) if isinstance(row, (tuple, list))
                     else str(row) for row in rows) + '\n'


def _case(rows, answer):
    return _text(*rows), _text(answer)


def _add(ch, title, teach, syntax, spec, cases, body, hints, proof, time, space,
         difficulty='挑战', skills=None):
    _counts[ch] = _counts.get(ch, 0) + 1
    solution = ('import sys\n\n\ndef main():\n' +
                indent(dedent(body).strip(), '    ') +
                '\n\n\nif __name__ == "__main__":\n    main()\n')
    assert len(cases) >= 9 and len(hints) == 3
    PROBLEMS.append(acm_problem(
        ch, _counts[ch], title,
        teach + '\n\nPython 语法小课：\n```python\n' + syntax + '\n```',
        spec + '\n\n提交完整 Python 程序，从标准输入读取，向标准输出打印答案。输出按空白分隔的 token 比较。',
        cases, solution, hints,
        proof + '\n\n复杂度：时间 ' + time + '，额外空间 ' + space +
        '（不计批量读取的输入文本与最终输出）。',
        difficulty=difficulty, complexity={'time': time, 'space': space},
        prerequisites=[22, 23, 24, 37] if ch == 39 else [24, 33, 37],
        skills=skills or [title.split('：')[0]]))


def _reach(n, edges, start, skip_edge=-1, skip_vertex=-1, directed=False):
    adjacency = [[] for _ in range(n)]
    for i, edge in enumerate(edges):
        u, v = edge[:2]
        if i == skip_edge or u == skip_vertex or v == skip_vertex:
            continue
        adjacency[u].append(v)
        if not directed:
            adjacency[v].append(u)
    seen = {start}
    todo = [start]
    for u in todo:
        for v in adjacency[u]:
            if v not in seen:
                seen.add(v)
                todo.append(v)
    return seen


def _components(n, edges, skip_edge=-1, skip_vertex=-1):
    seen, answer = set(), 0
    for u in range(n):
        if u != skip_vertex and u not in seen:
            answer += 1
            seen |= _reach(n, edges, u, skip_edge, skip_vertex)
    return answer


def _edge_rows(edges):
    return [(u + 1, v + 1, *rest) for u, v, *rest in edges]


# 381: transitive reachability is an independent oracle for Kosaraju.
_directed = [
    (5, [(0, 1), (1, 0), (1, 2), (2, 3), (3, 2), (3, 4)]),
    (4, [(0, 1), (1, 2), (2, 3), (3, 0)]),
    (1, []), (4, []), (1, [(0, 0)]),
    (3, [(0, 1), (0, 1), (1, 2)]),
    (6, [(0, 1), (1, 0), (2, 3), (3, 4), (4, 2), (5, 5)]),
    (6, [(i, i + 1) for i in range(5)]),
    (5, [(u, v) for u in range(5) for v in range(5)]),
]
_cases = []
for n, edges in _directed:
    reach = [_reach(n, edges, s, directed=True) for s in range(n)]
    groups = {tuple(v for v in range(n) if v in reach[u] and u in reach[v])
              for u in range(n)}
    _cases.append(_case([(n, len(edges)), *_edge_rows(edges)],
                        (len(groups), max(map(len, groups)))))
_add(39, '强连通分量：双向可达的通信组',
     '有向图中，互相可达是一种等价关系，每个等价类叫强连通分量。Kosaraju 先在原图记录 DFS 完成顺序，再按完成时间倒序在反图搜索；第二遍每次搜索恰好得到一个分量。显式栈可避免长链触发 Python 递归深度限制。',
     'stack = [(start, 0)]  # 节点与下一条待检查边的位置\norder.append(stack.pop()[0])\nfor u in reversed(order):\n    pass',
     '输入 n m（1≤n≤100000，0≤m≤200000），随后 m 行 u v 表示有向边 u→v，顶点编号 1～n。允许自环、重边和不连通的图。输出两个整数：强连通分量个数、最大分量的顶点数。孤立点单独构成一个分量。',
     _cases, r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
n, m = next(it), next(it)
g = [[] for _ in range(n)]
rg = [[] for _ in range(n)]
for _ in range(m):
    u, v = next(it) - 1, next(it) - 1
    g[u].append(v)
    rg[v].append(u)
seen = [False] * n
order = []
for start in range(n):
    if seen[start]:
        continue
    seen[start] = True
    stack = [(start, 0)]
    while stack:
        u, pos = stack[-1]
        if pos == len(g[u]):
            order.append(u)
            stack.pop()
        else:
            stack[-1] = (u, pos + 1)
            v = g[u][pos]
            if not seen[v]:
                seen[v] = True
                stack.append((v, 0))
seen = [False] * n
count = largest = 0
for start in reversed(order):
    if seen[start]:
        continue
    count += 1
    size = 0
    seen[start] = True
    stack = [start]
    while stack:
        u = stack.pop()
        size += 1
        for v in rg[u]:
            if not seen[v]:
                seen[v] = True
                stack.append(v)
    largest = max(largest, size)
print(count, largest)
''',
     ['先区分“从 u 到 v 可达”和“u、v 相互可达”。', '第一遍要在节点所有出边处理完成后加入 order，不能用入栈顺序。', '反转所有边，按 reversed(order) 执行第二遍 DFS，并统计每次新搜索的大小。'],
     '正确性：将每个强连通分量缩成一点得到 DAG。原图第一遍中，分量之间若有边 C→D，则 C 的最大完成时间大于 D 的最大完成时间。第二遍选取尚未访问且完成时间最大的分量，它在剩余反图中没有通向其他分量的边，而内部仍互相可达，所以恰好取出一个完整分量。重复后得到全部分量。易错点：用 DFS 进入顺序替代完成顺序，或第二遍忘记改用反图。',
     'O(n+m)', 'O(n+m)', skills=['强连通分量', 'Kosaraju', '迭代 DFS'])


# Bridges and articulation points use literal deletion plus connectivity checks.
_undirected = [
    (5, [(0, 1), (1, 2), (2, 0), (1, 3), (3, 4)]),
    (3, [(0, 1), (0, 1), (1, 2), (2, 2)]),
    (1, []), (4, []), (2, [(0, 0), (1, 1)]),
    (6, [(0, 1), (1, 2), (3, 4), (4, 5), (5, 3)]),
    (6, [(0, i) for i in range(1, 6)]),
    (7, [(i, i + 1) for i in range(6)]),
    (5, [(u, v) for u in range(5) for v in range(u + 1, 5)]),
]
_cases = []
for n, edges in _undirected:
    base = _components(n, edges)
    answer = [i + 1 for i in range(len(edges))
              if _components(n, edges, skip_edge=i) > base]
    _cases.append((_text((n, len(edges)), *_edge_rows(edges)),
                   _text(len(answer), answer)))
_add(39, '桥与 low-link：找到不可替代的道路',
     '桥是删除后使无向图连通分量数增加的边。DFS 时间戳 tin[u] 表示首次访问顺序；low[u] 是从 u 的子树经树边向下，再至多用一条返祖边能到达的最小时间戳。树边 u—v 是桥当且仅当 low[v]>tin[u]。重边必须用边编号区分。',
     'for v, edge_id in graph[u]:\n    if edge_id == parent_edge[u]:\n        continue  # 只跳过进入 u 的那一条边',
     '输入 n m（1≤n≤100000，0≤m≤1000），随后 m 行 u v 表示无向边，顶点编号 1～n。边按输入顺序编号 1～m，允许自环、重边和不连通。第一行输出桥的数量，第二行按升序输出所有桥的编号；没有桥时第二行为空。本地训练限制边数以控制答案长度，算法仍适用于更大的图。',
     _cases, r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
n, m = next(it), next(it)
g = [[] for _ in range(n)]
for eid in range(m):
    u, v = next(it) - 1, next(it) - 1
    g[u].append((v, eid))
    g[v].append((u, eid))
tin = [-1] * n
low = [0] * n
parent = [-1] * n
parent_edge = [-1] * n
timer = 0
bridge = [False] * m
for root in range(n):
    if tin[root] != -1:
        continue
    tin[root] = low[root] = timer
    timer += 1
    stack = [(root, 0)]
    while stack:
        u, pos = stack[-1]
        if pos == len(g[u]):
            stack.pop()
            p = parent[u]
            if p != -1:
                low[p] = min(low[p], low[u])
                if low[u] > tin[p]:
                    bridge[parent_edge[u]] = True
            continue
        stack[-1] = (u, pos + 1)
        v, eid = g[u][pos]
        if eid == parent_edge[u]:
            continue
        if tin[v] == -1:
            parent[v], parent_edge[v] = u, eid
            tin[v] = low[v] = timer
            timer += 1
            stack.append((v, 0))
        else:
            low[u] = min(low[u], tin[v])
answer = [eid + 1 for eid in range(m) if bridge[eid]]
print(len(answer))
print(*answer)
''',
     ['删除每条边重算连通性可以验证小图，但正式算法不能重复搜索。', '对子节点回溯时，把 low[child] 合并到 low[parent]。', '若 low[child] 严格大于 tin[parent]，子树没有绕过该边的返回路线。'],
     '正确性：DFS 子树中通向外部祖先的边，都会以返祖边时间戳参与 low 的最小值。low[v]≤tin[u] 表示子树有一条避开树边 u—v 的出口，因此该边在环上；反之该子树与外部只有这条树边相连，删除后必分裂。非树边本就在 DFS 路径形成的环上，不是桥。易错点：跳过所有指向父顶点的边会把两条平行边误判为桥；判定符号是 >。',
     'O(n+m)', 'O(n+m)', skills=['桥', 'low-link', '多重图'])

_cases = []
for n, edges in _undirected:
    base = _components(n, edges)
    answer = [u + 1 for u in range(n)
              if _components(n, edges, skip_vertex=u) > base]
    _cases.append((_text((n, len(edges)), *_edge_rows(edges)),
                   _text(len(answer), answer)))
_add(39, '割点：失效后使网络分裂的节点',
     '割点是删除该顶点及其关联边后，使连通分量数增加的点。非根 u 若存在 DFS 子节点 v 满足 low[v]≥tin[u]，则 v 的子树无法绕过 u 连到上方。DFS 根没有上方，因此必须有至少两个 DFS 子节点才是割点。',
     'children[u] += 1\nis_cut[u] = True\nanswer = [u + 1 for u, flag in enumerate(is_cut) if flag]',
     '输入 n m（1≤n≤1000，0≤m≤200000），随后 m 行无向边 u v，顶点编号 1～n。允许自环、重边、孤立点和多个连通分量。第一行输出割点数量，第二行按编号升序输出割点；没有割点时第二行为空。删除孤立点不会增加连通分量数。本地训练限制顶点数以控制答案长度，算法仍按线性规模扩展。',
     _cases, r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
n, m = next(it), next(it)
g = [[] for _ in range(n)]
for eid in range(m):
    u, v = next(it) - 1, next(it) - 1
    g[u].append((v, eid))
    g[v].append((u, eid))
tin = [-1] * n
low = [0] * n
parent = [-1] * n
parent_edge = [-1] * n
children = [0] * n
cut = [False] * n
timer = 0
for root in range(n):
    if tin[root] != -1:
        continue
    tin[root] = low[root] = timer
    timer += 1
    stack = [(root, 0)]
    while stack:
        u, pos = stack[-1]
        if pos == len(g[u]):
            stack.pop()
            p = parent[u]
            if p == -1:
                cut[u] = children[u] >= 2
            else:
                low[p] = min(low[p], low[u])
                if parent[p] != -1 and low[u] >= tin[p]:
                    cut[p] = True
            continue
        stack[-1] = (u, pos + 1)
        v, eid = g[u][pos]
        if eid == parent_edge[u]:
            continue
        if tin[v] == -1:
            parent[v], parent_edge[v] = u, eid
            children[u] += 1
            tin[v] = low[v] = timer
            timer += 1
            stack.append((v, 0))
        else:
            low[u] = min(low[u], tin[v])
answer = [u + 1 for u in range(n) if cut[u]]
print(len(answer))
print(*answer)
''',
     ['先明确“删除顶点”与“删除一条边”的差别。', '非根使用 low[child]≥tin[u]；等号表示只能回到 u，删除 u 后仍会断开。', '为每棵 DFS 树单独统计根的树孩子数，而不是根的邻接边数。'],
     '正确性：非根 u 的父侧仍存在，若某子树不能抵达 u 的严格祖先，删除 u 后该子树就与父侧分离；若所有子树都有出口，则它们仍与父侧相连。根的不同 DFS 子树之间没有边，否则早被同一次 DFS 访问，因此删除根后剩下的连通部分恰好按树孩子划分。易错点：把桥的严格 > 原封不动用于割点，或把根的度数当作树孩子数。',
     'O(n+m)', 'O(n+m)', skills=['割点', 'low-link', 'DFS 树'])


# 384: distances in fixtures are computed with a separate BFS per query.
_trees = [
    (5, [(0, 1), (0, 2), (1, 3), (1, 4)]),
    (4, [(0, 1), (1, 2), (2, 3)]),
    (1, []), (2, [(0, 1)]),
    (7, [(0, i) for i in range(1, 7)]),
    (9, [(i, i + 1) for i in range(8)]),
    (7, [((i - 1) // 2, i) for i in range(1, 7)]),
    (6, [(0, 4), (4, 2), (2, 5), (5, 1), (1, 3)]),
    (8, [(0, 1), (0, 2), (2, 3), (2, 4), (4, 5), (4, 6), (6, 7)]),
]
def _tree_distances(n, edges):
    g = [[] for _ in range(n)]
    for u, v in edges:
        g[u].append(v)
        g[v].append(u)
    all_dist = []
    for start in range(n):
        d = [-1] * n
        d[start] = 0
        todo = [start]
        for u in todo:
            for v in g[u]:
                if d[v] == -1:
                    d[v] = d[u] + 1
                    todo.append(v)
        all_dist.append(d)
    return all_dist

_cases = []
for n, edges in _trees:
    queries = [(u, v) for u in range(n) for v in range(u, n)]
    distances = _tree_distances(n, edges)
    _cases.append((_text((n, len(queries)), *_edge_rows(edges), *_edge_rows(queries)),
                   _text(*(distances[u][v] for u, v in queries))))
_add(39, '倍增 LCA：批量查询树上距离',
     '树上两点的路径会经过它们的最近公共祖先 LCA。设根深度为 0，则距离为 depth[u]+depth[v]-2·depth[LCA]。倍增表 up[k][u] 保存 u 的 2^k 级祖先，先把较深节点抬到同一层，再从大步到小步同时抬升。',
     'LOG = n.bit_length()\nif difference & (1 << k):\n    u = up[k][u]\nup = [[0] * n for _ in range(LOG)]',
     '输入 n q（1≤n≤100000，1≤q≤1000），随后 n-1 行无向边 u v，再给 q 行查询 u v。顶点编号 1～n，输入保证是一棵连通树，没有自环和重边；每条边长度为 1。对每个查询输出两点之间的边数，每行一个整数。允许 u=v。本地训练限制查询数以控制输出长度，倍增预处理可支持更多查询。',
     _cases, r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
n, q = next(it), next(it)
g = [[] for _ in range(n)]
for _ in range(n - 1):
    u, v = next(it) - 1, next(it) - 1
    g[u].append(v)
    g[v].append(u)
depth = [0] * n
parent = [-1] * n
parent[0] = 0
order = [0]
for u in order:
    for v in g[u]:
        if parent[v] == -1:
            parent[v] = u
            depth[v] = depth[u] + 1
            order.append(v)
up = [parent]
for k in range(1, n.bit_length()):
    prev = up[-1]
    up.append([prev[prev[u]] for u in range(n)])
def lca(u, v):
    if depth[u] < depth[v]:
        u, v = v, u
    delta = depth[u] - depth[v]
    for k in range(len(up)):
        if delta & (1 << k):
            u = up[k][u]
    if u == v:
        return u
    for k in range(len(up) - 1, -1, -1):
        if up[k][u] != up[k][v]:
            u, v = up[k][u], up[k][v]
    return up[0][u]
answer = []
for _ in range(q):
    u, v = next(it) - 1, next(it) - 1
    ancestor = lca(u, v)
    answer.append(str(depth[u] + depth[v] - 2 * depth[ancestor]))
print('\n'.join(answer))
''',
     ['先任选 1 为根，求每个点的父亲与深度。', '把高度差写成二进制，只跳对应的 2^k 级祖先。', '同层后仅在两人的 2^k 级祖先不同时一起跳，最后父亲就是 LCA。'],
     '正确性：倍增递推把两个连续的 2^(k-1) 级跳跃组合成 2^k 级跳跃。对齐深度不会越过 LCA；同步抬升始终保持两点位于 LCA 的不同后代分支，最终停在其两个孩子。根到两点的深度和将根到 LCA 的公共段计算两次，减去即可得到路径长度。易错点：根父亲设为 -1 会触发 Python 负下标；应让根指向自己。',
     'O((n+q) log n)', 'O(n log n)', skills=['LCA', '倍增', '树上距离'])


# 385: enumerate all left-side choices, independently of augmenting paths.
_bipartite = [
    (3, 3, [(0, 0), (0, 1), (1, 0), (2, 1), (2, 2)]),
    (3, 2, [(0, 0), (1, 0), (2, 0)]),
    (1, 1, []), (1, 1, [(0, 0), (0, 0)]),
    (4, 4, [(u, v) for u in range(4) for v in range(4)]),
    (4, 3, [(0, 1), (1, 0), (1, 1), (2, 2)]),
    (4, 4, [(0, 0), (0, 1), (1, 1), (1, 2), (2, 2), (2, 3), (3, 0)]),
    (2, 5, [(0, 4), (1, 4), (1, 3)]),
    (5, 3, [(0, 0), (1, 1), (2, 1), (3, 2), (4, 2)]),
]
_cases = []
for left, right, edges in _bipartite:
    allowed = set(edges)
    best = 0
    for choices in product(range(-1, right), repeat=left):
        chosen = [v for v in choices if v >= 0]
        if len(set(chosen)) == len(chosen) and all(v < 0 or (u, v) in allowed
                                                  for u, v in enumerate(choices)):
            best = max(best, len(chosen))
    _cases.append(_case([(left, right, len(edges)), *_edge_rows(edges)], best))
_add(39, '二分图匹配：用增广路重新分配任务',
     '匹配要求每个左点和右点至多参与一条选中边。贪心遇到已占用的右点时，可以递归尝试为原主人寻找新位置；若最后找到空位，整条交替路径翻转后匹配数增加 1。每轮搜索都重新设置访问标记。',
     'owner = [-1] * right_count\nseen = [False] * right_count\nif owner[v] == -1 or augment(owner[v]):\n    owner[v] = u',
     '输入 L R m（1≤L,R≤150，0≤m≤10000），随后 m 行 u v，表示左侧编号 u（1～L）可与右侧编号 v（1～R）配对。两侧编号属于不同集合，所以 u=v 仍是普通跨侧边；允许重复边和孤立点，没有同侧边。输出最大匹配的边数。',
     _cases, r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
left, right, m = next(it), next(it), next(it)
g = [[] for _ in range(left)]
for _ in range(m):
    u, v = next(it) - 1, next(it) - 1
    g[u].append(v)
owner = [-1] * right
def augment(u):
    for v in g[u]:
        if seen[v]:
            continue
        seen[v] = True
        if owner[v] == -1 or augment(owner[v]):
            owner[v] = u
            return True
    return False
answer = 0
for u in range(left):
    seen = [False] * right
    if augment(u):
        answer += 1
print(answer)
''',
     ['先用 owner[v] 记录右点 v 当前分配给哪个左点。', '右点被占用并不意味着失败；尝试为原主人寻找另一个右点。', '每处理一个新的左点都重置 seen；同一轮中每个右点只访问一次。'],
     '正确性：一次成功的增广搜索以未匹配左点开始、以未匹配右点结束，交替替换沿途匹配后恰好多一条边，仍满足匹配约束。若当前匹配小于某个最优匹配，两者对称差中必有增广路；搜索穷尽所有可行交替延伸，因此找不到增广路时已最优。逐个加入左点保持已处理子图上的最大匹配。易错点：给每个左点都使用永久 visited，会禁止后续重新分配。',
     'O(L·(m+R))', 'O(L+R+m)', skills=['二分图', '增广路', '最大匹配'])


def _simple_path_weights(n, edges, source, target):
    """Enumerate vertex-simple paths; parallel edges remain distinct choices."""
    g = [[] for _ in range(n)]
    for u, v, w in edges:
        g[u].append((v, w))
    answers = []
    def visit(u, seen, total):
        if u == target:
            answers.append(total)
            return
        for v, w in g[u]:
            if v not in seen:
                visit(v, seen | {v}, total + w)
    visit(source, {source}, 0)
    return answers


# 386: exhaustive simple paths provide distances without Floyd or Dijkstra.
_weighted = [
    (4, [(0, 1, 5), (0, 1, 2), (1, 2, 3), (0, 2, 9)]),
    (3, [(0, 1, 0), (1, 2, 4), (2, 0, 1)]),
    (1, []), (1, [(0, 0, 7)]), (4, []),
    (3, [(0, 1, 1000000000), (1, 2, 1000000000)]),
    (5, [(0, 1, 2), (1, 4, 8), (0, 2, 4), (2, 3, 1), (3, 4, 1)]),
    (4, [(0, 1, 3), (1, 0, 2), (2, 3, 0), (3, 2, 0)]),
    (5, [(u, v, abs(u - v)) for u in range(5) for v in range(5)]),
]
_cases = []
for n, edges in _weighted:
    queries = list(product(range(n), repeat=2))
    answer = []
    for u, v in queries:
        paths = _simple_path_weights(n, edges, u, v)
        answer.append(min(paths) if paths else -1)
    _cases.append((_text((n, len(edges), len(queries)), *_edge_rows(edges),
                         *_edge_rows(queries)), _text(*answer)))
_add(39, 'Floyd 动态规划：任意两站的最短路',
     'Floyd 不是枚举路径，而是逐步扩大“允许作为中转点”的集合。处理 k 时，最短路要么不经过 k，要么由 i→k 与 k→j 两段组成，所以更新 d[i][j]=min(d[i][j],d[i][k]+d[k][j])。k 必须是最外层循环。',
     'INF = 10**30\nd = [[INF] * n for _ in range(n)]\nfor i in range(n):\n    d[i][i] = 0\nrow = d[i]  # 缓存行引用，减少三重循环中的下标访问',
     '输入 n m q（1≤n≤180，0≤m≤20000，1≤q≤800），随后 m 行 u v w 表示有向边，0≤w≤10^9，再给 q 行查询 u v。顶点编号 1～n。允许自环、重边与不连通。每个查询单独输出最短距离；不可达输出 -1；点到自身允许走空路径，距离为 0。本地训练限制查询数以控制输出长度。',
     _cases, r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
n, m, q = next(it), next(it), next(it)
INF = 10**30
d = [[INF] * n for _ in range(n)]
for i in range(n):
    d[i][i] = 0
for _ in range(m):
    u, v, w = next(it) - 1, next(it) - 1, next(it)
    d[u][v] = min(d[u][v], w)
for k in range(n):
    middle = d[k]
    for i in range(n):
        row = d[i]
        prefix = row[k]
        if prefix == INF:
            continue
        for j in range(n):
            candidate = prefix + middle[j]
            if candidate < row[j]:
                row[j] = candidate
answer = []
for _ in range(q):
    u, v = next(it) - 1, next(it) - 1
    answer.append(str(-1 if d[u][v] == INF else d[u][v]))
print('\n'.join(answer))
''',
     ['直接边先初始化；重边保留最小权值，对角线保留 0。', '想象只允许编号前 k 个点充当路径内部节点。', '把 k 放在最外层，再枚举起点 i 与终点 j；最终所有中转点都已允许。'],
     '正确性：对允许的中转点数量归纳。初始状态只允许直接边或空路径。引入 k 后，不经过 k 的最优路径已在旧状态中；经过 k 的最优路径可在 k 处分为两段，两段内部只使用之前允许的点。非负权保证去掉环不会变差，因此无需多次经过 k。取两类最小值得到新状态。易错点：重边直接覆盖、对角线漏设 0、把 k 放到内层。',
     'O(n³+m+q)', 'O(n²)', skills=['Floyd', '全源最短路', '动态规划'])


def _has_negative_simple_cycle(n, edges):
    g = [[] for _ in range(n)]
    for u, v, w in edges:
        g[u].append((v, w))
    def search(start, u, seen, total):
        for v, w in g[u]:
            if v == start and total + w < 0:
                return True
            if v not in seen and search(start, v, seen | {v}, total + w):
                return True
        return False
    return any(search(s, s, {s}, 0) for s in range(n))

_negative_graphs = [
    (3, [(0, 1, 2), (1, 2, -5), (2, 0, 1)]),
    (3, [(0, 1, -3), (1, 2, 4), (2, 0, 0)]),
    (1, []), (1, [(0, 0, -1)]), (1, [(0, 0, 0)]),
    (5, [(0, 1, 8), (3, 4, -2), (4, 3, 1)]),
    (4, [(0, 1, -9), (1, 2, -8), (2, 3, -7)]),
    (2, [(0, 1, 5), (0, 1, -4), (1, 0, 3)]),
    (4, [(0, 1, 1), (1, 2, 1), (2, 0, -2), (3, 3, 9)]),
]
_cases = [_case([(n, len(edges)), *_edge_rows(edges)],
                'YES' if _has_negative_simple_cycle(n, edges) else 'NO')
          for n, edges in _negative_graphs]
_add(39, 'Bellman–Ford：检测任意位置的负环',
     '负环是总边权为负的有向环，沿它反复绕行能不断降低路径代价。单源最短路只能发现源点可达的负环；把所有 dist 初始化为 0，等价于添加一个到每个顶点都有零权边的超级源点，就能覆盖所有连通部分。',
     'dist = [0] * n\nchanged = False\nif dist[v] > dist[u] + weight:\n    dist[v] = dist[u] + weight\n    changed = True',
     '输入 n m（1≤n≤300，0≤m≤3000），随后 m 行 u v w 表示有向边，顶点编号 1～n，-10^6≤w≤10^6。允许自环、重边与不连通。若图的任意位置存在总权值严格小于 0 的有向环，输出 YES，否则输出 NO。总权值等于 0 的环不算负环。',
     _cases, r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
n, m = next(it), next(it)
edges = [(next(it) - 1, next(it) - 1, next(it)) for _ in range(m)]
dist = [0] * n
negative = False
for turn in range(n):
    changed = False
    for u, v, w in edges:
        if dist[v] > dist[u] + w:
            dist[v] = dist[u] + w
            changed = True
    if not changed:
        break
    if turn == n - 1:
        negative = True
print('YES' if negative else 'NO')
''',
     ['不能只从顶点 1 出发，负环可能在另一块不连通区域。', '令每个 dist 初值为 0，然后完整扫描所有边 n 轮。', '某轮没有更新就可提前结束；第 n 轮仍有严格下降才说明存在负环。'],
     '正确性：没有负环时，任意最短路线都能删去非负环成为至多 n-1 条边的简单路径，因此 n-1 轮后所有距离已稳定；原地松弛只会更早传播信息。若有负环，假设所有边都无法松弛，沿环累加 dist[v]≤dist[u]+w 会推出 0≤环权，与负权矛盾，所以每一轮仍会更新。易错点：只将一个源点置 0，或把非严格比较写成 >= 而误报零权环。',
     'O(nm+n)', 'O(n+m)', skills=['Bellman–Ford', '负环', '超级源点'])


_dags = [
    (5, 0, [(0, 1, 2), (0, 2, 5), (1, 3, 7), (2, 3, 1), (3, 4, -2)]),
    (4, 1, [(0, 2, 10), (1, 2, -5), (2, 3, -2)]),
    (1, 0, []), (4, 2, []),
    (4, 3, [(3, 1, 2), (1, 0, 3), (0, 2, 4)]),
    (3, 0, [(0, 1, -1), (0, 1, 3), (1, 2, 0)]),
    (5, 0, [(i, i + 1, -10**9) for i in range(4)]),
    (6, 0, [(0, 1, 0), (0, 2, 0), (1, 3, 0), (2, 3, 0), (4, 5, 9)]),
    (6, 0, [(u, v, (u + v) % 5 - 2) for u in range(6) for v in range(u + 1, 6)]),
]
_cases = []
for n, source, edges in _dags:
    answer = []
    for target in range(n):
        paths = _simple_path_weights(n, edges, source, target)
        answer.append(max(paths) if paths else 'UNREACHABLE')
    _cases.append(_case([(n, len(edges), source + 1), *_edge_rows(edges)], answer))
_add(39, 'DAG 最长路：带负收益的项目链',
     '一般图的最长简单路径很难，但 DAG 的拓扑序消除了循环依赖。将源点距离置 0，其他点视为不可达；按拓扑顺序，对每条边更新最大的累计权值。负权边也适用，因为正确性来自无环结构，而不是权值非负。',
     'from collections import deque\nqueue = deque(u for u in range(n) if indegree[u] == 0)\ndistance = [None] * n\nif distance[u] is not None:\n    candidate = distance[u] + weight',
     '输入 n m s（1≤n≤500，0≤m≤200000，1≤s≤n），随后 m 行 u v w，表示有向边 u→v，-10^9≤w≤10^9。保证图无有向环，因此没有自环；允许重边和不连通。按顶点 1～n 的顺序输出 n 个 token：从 s 出发的最大路径权值，不可达则输出 UNREACHABLE。s 到自身空路径权值为 0。本地训练限制顶点数以控制输出长度，拓扑算法仍适用于大型 DAG。',
     _cases, r'''
from collections import deque
it = iter(map(int, sys.stdin.buffer.read().split()))
n, m, source = next(it), next(it), next(it) - 1
g = [[] for _ in range(n)]
indegree = [0] * n
for _ in range(m):
    u, v, w = next(it) - 1, next(it) - 1, next(it)
    g[u].append((v, w))
    indegree[v] += 1
queue = deque(u for u in range(n) if indegree[u] == 0)
dist = [None] * n
dist[source] = 0
while queue:
    u = queue.popleft()
    for v, w in g[u]:
        if dist[u] is not None:
            candidate = dist[u] + w
            if dist[v] is None or candidate > dist[v]:
                dist[v] = candidate
        indegree[v] -= 1
        if indegree[v] == 0:
            queue.append(v)
print(*('UNREACHABLE' if x is None else x for x in dist))
''',
     ['负收益意味着不能把所有点的距离初始化为 0。', '用 Kahn 算法生成拓扑处理顺序；所有入度为 0 的点都要入队。', '不可达点不更新距离，但仍要删除出边、减少后继入度。'],
     '正确性：拓扑序保证处理 v 前，所有可能的最后一条入边 u→v 的起点都已处理。按最后一条边分类，每条 s→v 路径的权值等于某条 s→u 路径权值加边权；对所有可达前驱取最大值，就得到 v 的最优值。源点空路径建立归纳起点。易错点：因为某点不可达就跳过其出边的入度维护，会阻塞本应可达的其他节点。',
     'O(n+m)', 'O(n+m)', skills=['拓扑排序', 'DAG 最长路', '负权'])


_positive = [
    (4, 0, 3, [(0, 1, 1), (0, 2, 1), (1, 3, 2), (2, 3, 2), (0, 3, 3)]),
    (3, 0, 2, [(0, 1, 2), (0, 1, 2), (1, 2, 3), (0, 2, 9)]),
    (1, 0, 0, []), (3, 0, 2, []),
    (2, 0, 1, [(0, 0, 1), (0, 1, 5), (1, 0, 1)]),
    (4, 0, 3, [(0, 1, 10), (0, 2, 1), (2, 1, 1), (1, 3, 1)]),
    (4, 3, 0, [(3, 2, 10**9), (2, 1, 10**9), (1, 0, 10**9)]),
    (5, 0, 4, [(0, 1, 2), (0, 2, 2), (1, 3, 2), (2, 3, 2), (3, 4, 1)]),
    (5, 0, 4, [(u, v, abs(u - v) + 1) for u in range(5) for v in range(5)]),
]
_cases = []
for n, source, target, edges in _positive:
    paths = _simple_path_weights(n, edges, source, target)
    answer = (min(paths), paths.count(min(paths))) if paths else (-1, 0)
    _cases.append(_case([(n, len(edges), source + 1, target + 1), *_edge_rows(edges)], answer))
# Many equal shortest paths: a chain with two distinguishable parallel edges per step.
_cases.append(_case([(41, 80, 1, 41),
                     *((u, u + 1, 1) for u in range(1, 41) for _ in range(2))],
                    (40, pow(2, 40, 1000000007))))
_add(39, 'Dijkstra 计数：最短路线有多少条',
     '在距离之外维护 ways[u]。找到更短路线时，旧的最短路线全部作废，ways[v]=ways[u]；找到相等长度时，把 ways[u] 累加。要求边权严格为正，可保证最短路上的前驱距离更小，v 出堆前所有贡献已经到齐。',
     'from heapq import heappush, heappop\nif candidate < dist[v]:\n    dist[v], ways[v] = candidate, ways[u]\nelif candidate == dist[v]:\n    ways[v] = (ways[v] + ways[u]) % MOD',
     '输入 n m s t（1≤n≤100000，0≤m≤200000，1≤s,t≤n），随后 m 行有向边 u v w，1≤w≤10^9。允许自环、重边和不连通；每条输入边都有独立身份，经过不同平行边算不同路线。输出最短距离和最短路线数，计数模 1000000007；不可达输出 -1 0。s=t 时唯一最短路线为空路径，输出 0 1。',
     _cases, r'''
from heapq import heappush, heappop
it = iter(map(int, sys.stdin.buffer.read().split()))
n, m, source, target = next(it), next(it), next(it) - 1, next(it) - 1
g = [[] for _ in range(n)]
for _ in range(m):
    u, v, w = next(it) - 1, next(it) - 1, next(it)
    g[u].append((v, w))
INF, MOD = 10**30, 1000000007
dist = [INF] * n
ways = [0] * n
dist[source], ways[source] = 0, 1
heap = [(0, source)]
while heap:
    distance, u = heappop(heap)
    if distance != dist[u]:
        continue
    for v, w in g[u]:
        candidate = distance + w
        if candidate < dist[v]:
            dist[v], ways[v] = candidate, ways[u]
            heappush(heap, (candidate, v))
        elif candidate == dist[v]:
            ways[v] = (ways[v] + ways[u]) % MOD
if dist[target] == INF:
    print(-1, 0)
else:
    print(dist[target], ways[target])
''',
     ['距离与方案数是不同的状态；源点距离为 0，方案数为 1。', '更短时覆盖方案数，一样短时累加方案数。', '堆中旧距离必须跳过；相等距离只加计数，不重复压堆扩展。'],
     '正确性：Dijkstra 按非降距离确定最短距离。由于边权严格为正，任何最短路线的最后一个前驱都比终点距离小，因此终点被处理时，每个前驱的最短路线数已完整确定。按最后一条有独立身份的边分类，各类路线互不重叠，累加即得完整计数。易错点：相等距离重复入堆会使同一个节点重复传播方案数；零权边也不能直接套用本计数结论。',
     'O((n+m) log(n+m))', 'O(n+m)', skills=['Dijkstra', '最短路计数', '优先队列'])


# 390: enumerate all s-t cuts rather than running a flow algorithm.
_flows = [
    (4, [(0, 1, 3), (0, 2, 2), (1, 2, 1), (1, 3, 2), (2, 3, 3)]),
    (4, [(0, 1, 7), (2, 3, 8)]),
    (2, []), (2, [(0, 1, 4), (0, 1, 5), (1, 0, 7)]),
    (3, [(0, 0, 99), (0, 1, 0), (1, 2, 5)]),
    (3, [(0, 1, 10**9), (1, 2, 10**9)]),
    (6, [(0, 1, 1), (0, 2, 1), (1, 3, 1), (1, 4, 1),
         (2, 3, 1), (3, 5, 1), (4, 5, 1)]),
    (5, [(0, 1, 4), (1, 2, 3), (2, 1, 8), (2, 4, 2), (0, 3, 3), (3, 4, 2)]),
    (5, [(u, v, (u + 2 * v) % 5) for u in range(5) for v in range(5)]),
]
_cases = []
for n, edges in _flows:
    cuts = []
    for mask in range(1 << (n - 2)):
        side = {0} | {u for u in range(1, n - 1) if mask >> (u - 1) & 1}
        cuts.append(sum(c for u, v, c in edges if u in side and v not in side))
    _cases.append(_case([(n, len(edges)), *_edge_rows(edges)], min(cuts)))
_add(39, '最大流：残量网络与最短增广路',
     '每条容量边限制可运送的流量，除源汇外每个点流入等于流出。残量网络既记录还能增加多少，也用反向边记录能撤回多少。Edmonds–Karp 每次 BFS 找边数最少的增广路，沿路增加最小剩余容量，再重复到没有增广路。',
     'capacity[u][v] += amount  # 平行边合并\ncapacity[u][v] -= pushed\ncapacity[v][u] += pushed  # 允许撤销先前决策',
     '输入 n m（2≤n≤60，0≤m≤400），随后 m 行 u v c 表示有向容量边，顶点编号 1～n，0≤c≤10^9。源点固定为 1，汇点固定为 n。允许自环、平行边、方向相反的边与不连通。平行边容量相加；自环不会增加源汇流量。输出可从源点送到汇点的最大整数流量。',
     _cases, r'''
from collections import deque
it = iter(map(int, sys.stdin.buffer.read().split()))
n, m = next(it), next(it)
cap = [[0] * n for _ in range(n)]
g = [set() for _ in range(n)]
for _ in range(m):
    u, v, c = next(it) - 1, next(it) - 1, next(it)
    cap[u][v] += c
    g[u].add(v)
    g[v].add(u)
answer = 0
while True:
    parent = [-1] * n
    parent[0] = 0
    queue = deque([0])
    while queue and parent[n - 1] == -1:
        u = queue.popleft()
        for v in g[u]:
            if parent[v] == -1 and cap[u][v] > 0:
                parent[v] = u
                queue.append(v)
    if parent[n - 1] == -1:
        break
    pushed = 10**30
    v = n - 1
    while v != 0:
        u = parent[v]
        pushed = min(pushed, cap[u][v])
        v = u
    v = n - 1
    while v != 0:
        u = parent[v]
        cap[u][v] -= pushed
        cap[v][u] += pushed
        v = u
    answer += pushed
print(answer)
''',
     ['把“剩余可用容量”与原始容量区分开，并为反向残量边建立邻接关系。', 'BFS 记录 parent，回溯求整条路线的最小残量。', '每次增加正向流量都同步增加反向残量；没有路径时结束。'],
     '正确性：每次增广只在残量允许范围内修改，沿途内部点流入流出同时改变，所以容量约束和流量守恒始终成立。终止时，取残量图中源点可达点集 S，所有 S 到外部的残量均为 0，当前流量等于该割的容量。任何流量都不能超过任意割容量，因此当前流量最大。BFS 增广距离单调不降，给出 Edmonds–Karp 的多项式界。易错点：没有反向边时无法撤回早先选错的路线。',
     'O(nm²+n²)', 'O(n²+m)', difficulty='高手', skills=['最大流', '残量网络', 'Edmonds–Karp'])


# 391: enumerate chronological adjacent-merge operations, not interval splits.
def _merge_stones_oracle(stones):
    @lru_cache(None)
    def search(state):
        if len(state) == 1:
            return 0
        return min(state[i] + state[i + 1] +
                   search(state[:i] + (state[i] + state[i + 1],) + state[i + 2:])
                   for i in range(len(state) - 1))
    return search(tuple(stones))

_stone_arrays = [[4, 1, 3, 2], [10, 20, 30], [7], [0], [0, 0, 0],
                 [1, 100, 1], [2, 2, 2, 2, 2], [0, 5, 0, 5], [9, 2, 7, 1, 8, 3]]
_cases = [_case([len(a), a], _merge_stones_oracle(a)) for a in _stone_arrays]
_add(40, '区间 DP：相邻石堆的最小合并代价',
     '区间 DP 适合“最后一次操作把区间分成两段”的问题。令 dp[l][r] 为将 l～r 合成一堆的最小代价，最后一步一定把 [l,k] 和 [k+1,r] 两堆合并，新增代价是整个区间的重量和。按区间长度递增计算，所有依赖都已完成。',
     'prefix = [0]\nfor weight in weights:\n    prefix.append(prefix[-1] + weight)\nsegment_sum = prefix[right + 1] - prefix[left]\nfor length in range(2, n + 1):\n    pass',
     '输入 n（1≤n≤150），再输入按一条直线排列的 n 堆石子的重量，0≤a[i]≤10^9。每次只能合并相邻两堆，代价等于两堆重量之和；新堆留在原位置。输出将所有石堆合成一堆的最小总代价。不是环形排列，首尾两堆不相邻；n=1 时为 0。',
     _cases, r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
n = next(it)
a = [next(it) for _ in range(n)]
prefix = [0]
for x in a:
    prefix.append(prefix[-1] + x)
dp = [[0] * n for _ in range(n)]
for length in range(2, n + 1):
    for left in range(n - length + 1):
        right = left + length - 1
        best = 10**30
        for split in range(left, right):
            best = min(best, dp[left][split] + dp[split + 1][right])
        dp[left][right] = best + prefix[right + 1] - prefix[left]
print(dp[0][n - 1])
''',
     ['不能总合并当前最轻的两堆，因为必须相邻且当前选择会改变后续代价。', '考虑整个区间的最后一次合并；它两侧各自必须先合成一堆。', '枚举分界 k，用前缀和 O(1) 求最后一步的区间总重量。'],
     '正确性：单堆无需操作。任何区间的合法最终合并都有唯一左右分界 k，两侧操作互不影响；若某侧不是最优，可替换它得到更低总代价。因此最优答案包含两个最优子区间，加上固定的整段重量。枚举所有 k 不漏掉任何最后一步，按长度归纳得到全局最优。易错点：把线性问题当成环形问题，或漏掉分界 right-1。',
     'O(n³)', 'O(n²)', skills=['区间 DP', '前缀和', '最优子结构'])


def _matrix_chain_oracle(dimensions):
    initial = tuple(zip(dimensions, dimensions[1:]))
    def enumerate_operations(matrices):
        if len(matrices) == 1:
            return [0]
        outcomes = []
        for i in range(len(matrices) - 1):
            rows, inner = matrices[i]
            _, cols = matrices[i + 1]
            reduced = matrices[:i] + ((rows, cols),) + matrices[i + 2:]
            outcomes.extend(rows * inner * cols + x for x in enumerate_operations(reduced))
        return outcomes
    return min(enumerate_operations(initial))

_dimension_sets = [[10, 30, 5, 60], [30, 35, 15, 5, 10, 20, 25], [7, 9],
                   [3, 4, 5], [1, 1, 1, 1, 1], [100, 1, 100, 1],
                   [2, 9, 3, 8, 4], [5, 2, 7, 3, 6], [1000, 1000, 1000]]
_cases = [_case([len(d) - 1, d], _matrix_chain_oracle(d)) for d in _dimension_sets]
_cases.append(_case([60, [10] * 61], 59 * 1000))
_add(40, '矩阵链乘法：选择计算括号的位置',
     '矩阵相乘满足结合律，但运算量不同。a×b 与 b×c 两个矩阵相乘需要 a·b·c 次标量乘法。dp[l][r] 表示连续矩阵 l～r 的最小乘法次数；若最后在 k 处分开，新增代价为 p[l]·p[k+1]·p[r+1]。维度取决于区间边界，不能把矩阵真实乘出来。',
     'for split in range(left, right):\n    extra = p[left] * p[split + 1] * p[right + 1]\n    candidate = dp[left][split] + dp[split + 1][right] + extra',
     '输入矩阵数 n（1≤n≤150），再输入 n+1 个维度 p[0]～p[n]（1≤p[i]≤1000）。第 i 个矩阵的形状为 p[i-1]×p[i]，矩阵顺序固定，只能改变括号。输出计算整个乘积需要的最少标量乘法次数；单个矩阵不需要乘法，输出 0。输入不含矩阵元素。',
     _cases, r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
n = next(it)
p = [next(it) for _ in range(n + 1)]
dp = [[0] * n for _ in range(n)]
for length in range(2, n + 1):
    for left in range(n - length + 1):
        right = left + length - 1
        dp[left][right] = min(
            dp[left][split] + dp[split + 1][right] +
            p[left] * p[split + 1] * p[right + 1]
            for split in range(left, right))
print(dp[0][n - 1])
''',
     ['乘积 A[l]…A[r] 的形状始终是 p[l]×p[r+1]，与括号无关。', '枚举最后一次乘法的分界，分别优化左、右子链。', '新增成本使用三个维度：区间左边界、分界、区间右边界。'],
     '正确性：任意合法括号方案的最外层乘法都对应一个分界 k。左右子链的输出形状固定，所以替换为各自最优方案不会改变最终乘法成本。递推枚举所有分界并加入相应三维乘积，完整覆盖所有方案；按链长归纳成立。易错点：输入有 n+1 个维度，而不是 n 个；不能照搬石子合并题的区间和成本。',
     'O(n³)', 'O(n²)', skills=['矩阵链', '区间 DP', '维度分析'])


_bounded = [
    (10, [(2, 3, 3), (3, 5, 2)]),
    (7, [(3, 4, 1), (2, 3, 2), (5, 10, 0)]),
    (0, [(1, 9, 3)]), (10, []), (4, [(5, 100, 2)]),
    (8, [(2, 0, 4), (3, 5, 2)]),
    (12, [(2, 3, 3), (2, 4, 2), (4, 7, 1)]),
    (15, [(1, 1, 3), (4, 7, 2), (6, 12, 2)]),
    (9, [(3, 5, 1), (3, 5, 1), (3, 5, 1)]),
]
_cases = []
for capacity, items in _bounded:
    best = 0
    for quantities in product(*(range(count + 1) for _, _, count in items)):
        weight = sum(q * w for q, (w, _, _) in zip(quantities, items))
        if weight <= capacity:
            best = max(best, sum(q * v for q, (_, v, _) in zip(quantities, items)))
    _cases.append(_case([(len(items), capacity), *items], best))
_cases.append(_case([(1, 5000), (3, 7, 10**9)], (5000 // 3) * 7))
_add(40, '多重背包：二进制拆分有限库存',
     '每类物品有有限件数，直接枚举拿几件会多一层循环。把 s 件拆成 1、2、4…以及最后余数的若干包，每个包作为只能拿一次的物品。所有 0～s 的件数都能由这些包表示，再使用容量倒序的 0/1 背包即可。先把库存截断到容量最多能容纳的件数。',
     'remaining = min(stock, capacity // weight)\nbundle = 1\nwhile remaining:\n    take = min(bundle, remaining)\n    remaining -= take\n    bundle <<= 1',
     '输入 n W（0≤n≤60，0≤W≤5000），随后 n 行 w v s，表示单件重量、价值、库存；1≤w≤5000，0≤v≤10^9，0≤s≤10^9。物品只能整件选取，总重量不得超过 W，不要求装满。输出最大总价值；空选合法。',
     _cases, r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
n, capacity = next(it), next(it)
dp = [0] * (capacity + 1)
for _ in range(n):
    weight, value, stock = next(it), next(it), next(it)
    remaining = min(stock, capacity // weight)
    bundle = 1
    while remaining:
        take = min(bundle, remaining)
        cost, gain = take * weight, take * value
        for c in range(capacity, cost - 1, -1):
            dp[c] = max(dp[c], dp[c - cost] + gain)
        remaining -= take
        bundle <<= 1
print(dp[capacity])
''',
     ['重量大于容量的物品、库存为 0 的物品可以直接略过。', '库存 13 可拆成 1、2、4、6，任意 0～13 都能选出。', '每个包至多使用一次，所以容量必须倒序遍历。'],
     '正确性：拆分中每个新包的件数不超过此前所有包件数之和加 1，因此可表示件数区间从 [0,t] 无缝扩展到 [0,t+包大小]，最后覆盖 0～s。包的重量价值均线性缩放，所以与原库存选择等价。倒序更新确保每个包的转移只引用尚未使用该包的状态，归纳得到最大价值。易错点：容量正序会重复使用同一个包，把有限库存误写成无限库存。',
     'O(n+W·Σ log(sᵢ′+1))，sᵢ′=min(sᵢ,⌊W/wᵢ⌋)', 'O(W)', skills=['多重背包', '二进制拆分', '滚动数组'])


_digit_ranges = [(0, 30, 3), (98, 123, 2), (0, 0, 1), (11, 11, 2),
                 (10, 10, 1), (1, 99, 7), (100, 500, 5),
                 (990, 1100, 9), (10000, 10300, 13)]
_cases = []
for lower, upper, divisor in _digit_ranges:
    count = sum(sum(map(int, str(x))) % divisor == 0 and
                all(a != b for a, b in zip(str(x), str(x)[1:]))
                for x in range(lower, upper + 1))
    _cases.append(_case([(lower, upper, divisor)], count))
_cases.append(_case([(0, 10**18, 1)], 1 + sum(9**length for length in range(1, 19))))
_add(40, '数位 DP：相邻不同且数位和整除',
     '上界达到 10^18 时不能逐数枚举。把数字从高位到低位构造，状态记录位置、上一位、数位和余数，以及是否仍贴着上界。前导零不属于真实数字，上一位用特殊值 10 表示“尚未开始”；区间答案由 F(R)-F(L-1) 得到。',
     'from functools import lru_cache\n@lru_cache(None)\ndef dfs(pos, previous, remainder, tight):\n    pass\nnext_tight = tight and digit == digits[pos]',
     '输入 L R k（0≤L≤R≤10^18，1≤k≤100）。统计闭区间内满足两项条件的整数：十进制正常写法中相邻数字不相同；所有数位之和能被 k 整除。数字 0 的写法为单个 0，数位和为 0，满足条件。输出精确数量，不取模。',
     _cases, r'''
from functools import lru_cache
lower, upper, divisor = map(int, sys.stdin.buffer.read().split())
def count(bound):
    if bound < 0:
        return 0
    digits = list(map(int, str(bound)))
    @lru_cache(None)
    def dfs(pos, previous, remainder, tight):
        if pos == len(digits):
            return int(remainder == 0)
        limit = digits[pos] if tight else 9
        answer = 0
        for digit in range(limit + 1):
            next_tight = tight and digit == digits[pos]
            if previous == 10 and digit == 0:
                answer += dfs(pos + 1, 10, remainder, next_tight)
            elif digit != previous:
                answer += dfs(pos + 1, digit, (remainder + digit) % divisor, next_tight)
        return answer
    return dfs(0, 10, 0, True)
print(count(upper) - count(lower - 1))
''',
     ['先实现统计 [0,X] 的 F(X)，再用前缀差处理任意闭区间。', '是否贴住上界决定当前位最多选多少；一旦变小，后续每位都可选到 9。', '用特殊 previous=10 跳过前导零；全程没开始的唯一构造代表数字 0。'],
     '正确性：固定长度、允许前导零的构造与 [0,X] 中整数一一对应。tight 精确保证不超过 X，previous 只记录真实数字的前一位，余数在加入每一位后保持等于真实数位和模 k。每个状态枚举全部且互斥的下一位选择，终点仅接受余数 0，故得到 F(X)。前缀相减保留且仅保留区间内整数。易错点：把前导零当相邻数字，会错误排除短数字和 0。',
     'O(D·k·10²)，D 为 R 的位数', 'O(D·k·10)', skills=['数位 DP', '记忆化', '前导零'])


_assignment_matrices = [
    [[9, 2, 7], [6, 4, 3], [5, 8, 1]],
    [[-1, -5], [-4, -2]], [[7]], [[0]],
    [[1, 1, 1], [1, 1, 1], [1, 1, 1]],
    [[0, 100, 100], [100, 0, 100], [100, 100, 0]],
    [[8, 1, 5, 9], [2, 7, 3, 8], [6, 4, 9, 2], [7, 5, 1, 6]],
    [[10**9, -10**9], [-10**9, 10**9]],
    [[(u * 7 + v * 3) % 11 - 4 for v in range(5)] for u in range(5)],
]
_cases = [_case([len(cost), *cost],
                min(sum(cost[u][v] for u, v in enumerate(perm))
                    for perm in permutations(range(len(cost)))))
          for cost in _assignment_matrices]
_add(40, '状态压缩 DP：最低成本的一对一分工',
     'n 项任务是否已分配可压成 n 位二进制 mask。已分配人数就是 mask 中 1 的数量，因此无需额外人数维度。dp[mask] 表示把前 popcount(mask) 个人分配到这些任务的最小成本，枚举一个尚未使用的任务扩展即可。',
     'person = mask.bit_count()\nif not (mask & (1 << job)):\n    next_mask = mask | (1 << job)\n# 括号让位运算与逻辑判断的边界清晰',
     '输入 n（1≤n≤18），随后 n 行各 n 个整数 c[i][j]（-10^9≤c[i][j]≤10^9），表示第 i 个人做第 j 项任务的成本。每个人恰好做一项任务，每项任务恰好分给一个人，所有配对都允许。输出总成本的最小值。成本可以为负。',
     _cases, r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
n = next(it)
cost = [[next(it) for _ in range(n)] for _ in range(n)]
size = 1 << n
INF = 10**30
dp = [INF] * size
dp[0] = 0
for mask in range(size - 1):
    person = mask.bit_count()
    remaining = (size - 1) ^ mask
    while remaining:
        bit = remaining & -remaining
        job = bit.bit_length() - 1
        nxt = mask | bit
        dp[nxt] = min(dp[nxt], dp[mask] + cost[person][job])
        remaining -= bit
print(dp[-1])
''',
     ['逐人安排任务，过去的具体顺序不重要，只需知道哪些任务已用。', 'mask.bit_count() 给出下一个待安排的人的下标。', '从空集合 dp[0]=0 出发，每次设置一个原为 0 的位，并取最小成本。'],
     '正确性：任何前 t 人的分配都对应一个有 t 个置位的任务集合。其最后一人必选择其中某项任务，移除这项选择后得到 dp 的前驱状态；反过来每个转移都产生合法且没有重复任务的分配。按人数归纳，dp[mask] 恰为相应集合的最小成本，满集合即完整分配。易错点：每一层重新任选任意人会重复计算，并丢失“前 t 人”的状态含义。',
     'O(n·2ⁿ)', 'O(n²+2ⁿ)', skills=['状态压缩', '任务分配', '位运算'])


_tour_matrices = [
    [[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]],
    [[0, 1, 9], [9, 0, 2], [3, 9, 0]], [[0]],
    [[0, 5], [8, 0]], [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
    [[0 if u == v else 7 for v in range(5)] for u in range(5)],
    [[0, 1, 20, 20], [20, 0, 1, 20], [20, 20, 0, 1], [50, 20, 20, 0]],
    [[0 if u == v else 10**9 for v in range(3)] for u in range(3)],
    [[0 if u == v else (u * 11 + v * 7) % 17 for v in range(6)] for u in range(6)],
]
_cases = []
for cost in _tour_matrices:
    n = len(cost)
    values = []
    for middle in permutations(range(1, n)):
        route = (0,) + middle + (0,)
        values.append(sum(cost[u][v] for u, v in zip(route, route[1:])))
    _cases.append(_case([n, *cost], min(values)))
_add(40, '旅行商 DP：访问集合与当前终点',
     '旅行商问题还必须记录路线最后停在哪个点，因此状态为 dp[mask][u]：从 1 出发、恰好访问 mask 中的点、最终停在 u 的最小成本。把一个没访问的点接到末尾；所有点访问完后，别忘了最后返回 1 的边。',
     'dp = [[INF] * n for _ in range(1 << n)]\ndp[1][0] = 0  # 只访问编号 1 的城市\nnext_mask = mask | (1 << v)\n# 二维列表需逐行创建，不能使用 [[INF] * n] * size',
     '输入 n（1≤n≤15），随后 n 行各 n 个整数 c[i][j]，0≤c[i][j]≤10^9，且 c[i][i]=0。所有城市间都有有向道路，费用不一定对称。必须从城市 1 出发，将其余每个城市恰好访问一次，再返回城市 1。输出最小总费用；n=1 时允许空旅行，输出 0。',
     _cases, r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
n = next(it)
cost = [[next(it) for _ in range(n)] for _ in range(n)]
size, INF = 1 << n, 10**30
dp = [[INF] * n for _ in range(size)]
dp[1][0] = 0
for mask in range(1, size, 2):
    for u in range(n):
        current = dp[mask][u]
        if current == INF:
            continue
        remaining = (size - 1) ^ mask
        while remaining:
            bit = remaining & -remaining
            v = bit.bit_length() - 1
            nxt = mask | bit
            dp[nxt][v] = min(dp[nxt][v], current + cost[u][v])
            remaining -= bit
print(min(dp[-1][u] + cost[u][0] for u in range(n)))
''',
     ['同一个已访问集合，停在不同城市会影响下一步成本，所以终点不能省略。', '从 dp[1][0]=0 开始，只向 mask 中尚未出现的城市扩展。', '最终答案对所有末尾城市 u 取 dp[full][u]+c[u][0] 的最小值。'],
     '正确性：任何合法前缀路线都由较短前缀加最后一条边得到，移除终点后恰为对应前驱状态。状态保存集合和终点，已包含决定未来可选点和转移成本的全部信息；更昂贵的同状态前缀永远不优。按集合大小归纳得到最小前缀成本，枚举最后终点并补回起点的边得到最优环游。易错点：只输出满集合最小值会漏算回程，也不能假定费用矩阵对称。',
     'O(n²·2ⁿ)', 'O(n·2ⁿ)', difficulty='高手', skills=['旅行商', '状态压缩', '集合与终点'])


# 397: enumerate every nonempty vertex subset and check its connectivity.
_connected_trees = [
    (5, [(0, 1), (0, 2), (1, 3), (1, 4)], [3, -2, 4, 5, -9]),
    (3, [(0, 1), (1, 2)], [-5, -1, -7]),
    (1, [], [8]), (1, [], [-8]), (1, [], [0]),
    (4, [(0, 1), (1, 2), (2, 3)], [5, -2, -2, 6]),
    (5, [(0, i) for i in range(1, 5)], [-10, 4, 4, 4, 4]),
    (6, [((i - 1) // 2, i) for i in range(1, 6)], [0, 2, -5, 4, -1, 20]),
    (8, [(0, 1), (0, 2), (2, 3), (2, 4), (4, 5), (4, 6), (6, 7)],
     [1, -4, 3, -8, 5, 6, -2, 7]),
]
_cases = []
for n, edges, weights in _connected_trees:
    best = -10**30
    for mask in range(1, 1 << n):
        selected = {u for u in range(n) if mask >> u & 1}
        subedges = [(u, v) for u, v in edges if u in selected and v in selected]
        start = next(iter(selected))
        if _reach(n, subedges, start) == selected:
            best = max(best, sum(weights[u] for u in selected))
    _cases.append(_case([n, weights, *_edge_rows(edges)], best))
_cases.append(_case([1200, [-1] * 1200,
                     *((u, u + 1) for u in range(1, 1200))], -1))
_add(40, '树形 DP：最大权值的连通点集',
     '任选根后，dp[u] 表示位于 u 的子树内、必须包含 u 的最大连通点集权值。要连接某个孩子方向的点，必须经过该孩子；因此可独立选择所有正收益子树，dp[u]=w[u]+Σmax(0,dp[v])。全局最优点集可能不含根，答案要对所有 u 取最大值。',
     'for u in reversed(order):\n    for v in children[u]:\n        dp[u] += max(0, dp[v])\nanswer = max(dp)  # 不能先与 0 取最大，点集必须非空',
     '输入 n（1≤n≤100000），再输入 n 个点权 w[i]（-10^9≤w[i]≤10^9），随后 n-1 行无向边 u v。顶点编号 1～n，保证是一棵连通树，无自环、无重边。选择一个非空顶点集合，要求这些顶点在原树中诱导的子图连通。输出所选点权之和的最大值。',
     _cases, r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
n = next(it)
dp = [next(it) for _ in range(n)]
g = [[] for _ in range(n)]
for _ in range(n - 1):
    u, v = next(it) - 1, next(it) - 1
    g[u].append(v)
    g[v].append(u)
parent = [-1] * n
parent[0] = 0
order = [0]
for u in order:
    for v in g[u]:
        if parent[v] == -1:
            parent[v] = u
            order.append(v)
for u in reversed(order[1:]):
    dp[parent[u]] += max(0, dp[u])
print(max(dp))
''',
     ['用“必须包含当前节点”约束子状态，才能保证接上父节点时仍连通。', '每个孩子方向只能整体贡献一个包含孩子的最优连通块；负收益可以不选。', '每个非空连通点集都有唯一最浅节点，因此对所有 dp[u] 取最大值。'],
     '正确性：固定包含 u 的连通点集，它与每个孩子子树的交集要么为空，要么是包含该孩子的连通点集。各孩子方向之间没有额外边，选择互不冲突，所以逐个取正收益最优子状态即为最优。任何非空连通集合有唯一最浅节点，故一定被某个 dp[u] 覆盖。易错点：全负权时答案是最大单点权值，不能输出空集合的 0；迭代后序避免长链递归溢出。',
     'O(n)', 'O(n)', skills=['树形 DP', '连通子树', '迭代后序'])


# 398: all-source BFS is independent of the reroot recurrence.
_cases = []
for n, edges in _trees:
    answer = [sum(row) for row in _tree_distances(n, edges)]
    _cases.append(_case([n, *_edge_rows(edges)], answer))
_add(40, '换根 DP：每个节点到全树的距离和',
     '先固定根求子树大小 size[u] 与根到所有点的距离和。把根从 u 沿一条边移到孩子 v 时，v 子树内 size[v] 个点距离各减 1，其余 n-size[v] 个点距离各加 1。因此 ans[v]=ans[u]+n-2·size[v]，一次向下遍历即可求全部根。',
     'for u in reversed(order[1:]):\n    size[parent[u]] += size[u]\nfor u in order[1:]:\n    answer[u] = answer[parent[u]] + n - 2 * size[u]',
     '输入 n（1≤n≤1000），随后 n-1 行无向边 u v。顶点编号 1～n，保证是一棵连通树，无自环、无重边，每条边长为 1。按顶点编号 1～n 输出 n 个整数，第 i 个值等于顶点 i 到所有 n 个顶点的距离之和；到自身距离为 0。本地训练限制顶点数以控制输出长度，换根算法仍为线性复杂度。',
     _cases, r'''
it = iter(map(int, sys.stdin.buffer.read().split()))
n = next(it)
g = [[] for _ in range(n)]
for _ in range(n - 1):
    u, v = next(it) - 1, next(it) - 1
    g[u].append(v)
    g[v].append(u)
parent = [-1] * n
parent[0] = 0
depth = [0] * n
order = [0]
for u in order:
    for v in g[u]:
        if parent[v] == -1:
            parent[v] = u
            depth[v] = depth[u] + 1
            order.append(v)
size = [1] * n
for u in reversed(order[1:]):
    size[parent[u]] += size[u]
answer = [0] * n
answer[0] = sum(depth)
for u in order[1:]:
    answer[u] = answer[parent[u]] + n - 2 * size[u]
print(*answer)
''',
     ['只对顶点 1 做一次遍历，先求出所有深度与子树大小。', '沿边把根移到孩子后，恰好孩子子树中的点变近，其余点变远。', '后序累计子树大小，前序传播答案；两次遍历方向不同。'],
     '正确性：删去树边 u—v 后图分成两个部分；当 v 为固定根下的孩子时，含 v 的部分恰有 size[v] 个点。根从 u 移到 v 后，这些点的唯一路径少经过该边，其他点多经过该边，故距离和变化为 n-2·size[v]。已知根答案后，按父先子后的顺序应用此精确等式，得到每个点的答案。易错点：换根时无需重新计算 size，它始终是最初固定根下的子树大小。',
     'O(n)', 'O(n)', skills=['换根 DP', '子树大小', '距离和'])


_inversion_queries = [(3, 1), (4, 3), (0, 0), (1, 1), (4, 0),
                      (4, 6), (4, 7), (5, 5), (7, 10)]
_cases = []
for n, k in _inversion_queries:
    answer = 0
    for perm in permutations(range(n)):
        inversions = sum(perm[i] > perm[j] for i in range(n) for j in range(i + 1, n))
        answer += inversions == k
    _cases.append(_case([(n, k)], answer))
# Independent coefficient extraction from product(1-x^j)/(1-x)^n.
_n, _k = 100, 10
_coefficient = 0
for subset in range(1 << _k):
    shift = sum(j + 1 for j in range(_k) if subset >> j & 1)
    if shift <= _k:
        _coefficient += (-1)**subset.bit_count() * comb(_n + _k - shift - 1, _n - 1)
_cases.append(_case([(_n, _k)], _coefficient % 1000000007))
_add(40, '计数 DP 优化：恰有 k 个逆序对的排列',
     '把最大元素 i 插入长度 i-1 的排列，会新增 0～i-1 个逆序对，每种新增数对应唯一插入位置。因此新 dp[j] 是旧 dp[j]、dp[j-1]…dp[j-i+1] 的窗口和。相邻 j 的窗口只增加一项、移除一项，可将三重循环优化为 O(nk)。',
     'window = (window + dp[j]) % MOD\nif j >= length:\n    window = (window - dp[j - length]) % MOD\n# Python 的 % 会把负数规范到 0～MOD-1',
     '输入 n k（0≤n≤500，0≤k≤10000）。统计由 1～n 组成且逆序对数恰为 k 的排列数量，模 1000000007 输出。逆序对指 i<j 且 a[i]>a[j]。n=0 时只有一个空排列，它有 0 个逆序对。k 超出可能范围时输出 0。',
     _cases, r'''
n, k = map(int, sys.stdin.buffer.read().split())
MOD = 1000000007
if k > n * (n - 1) // 2:
    print(0)
    return
dp = [0] * (k + 1)
dp[0] = 1
for length in range(1, n + 1):
    new = [0] * (k + 1)
    window = 0
    for j in range(min(k, length * (length - 1) // 2) + 1):
        window += dp[j]
        if j >= length:
            window -= dp[j - length]
        window %= MOD
        new[j] = window
    dp = new
print(dp[k])
''',
     ['新增最大元素不会改变旧元素之间的逆序关系。', '把最大元素放在末尾新增 0，对应往左移动一步新增 1。', '转移是长度至多 i 的连续窗口和，滚动维护它，不要为每个 j 再枚举新增逆序数。'],
     '正确性：从最终排列删除最大元素可唯一恢复较短排列和最大元素的插入位置，因此各新增逆序数对应的方案互不重叠且覆盖全部排列。递推窗口和准确实现这些方案数之和；窗口向右移动时只需加右端、减左端，值与直接求和相同。空排列初始化为 1，逐层归纳后得到所求计数。易错点：窗口宽度为 i，移除下标是 j-i；不是 j-i+1。',
     'O((n+1)(k+1))', 'O(k+1)', difficulty='高手', skills=['计数 DP', '滑动窗口优化', '逆序对'])


def _domino_oracle(board):
    rows, cols = len(board), len(board[0])
    free = frozenset((r, c) for r in range(rows) for c in range(cols) if board[r][c] == '.')
    def place(cells):
        if not cells:
            return 1
        r, c = min(cells)
        answer = 0
        for other in ((r + 1, c), (r, c + 1)):
            if other in cells:
                answer += place(cells - {(r, c), other})
        return answer
    return place(free)

_boards = [['...', '...'], ['.#.', '...', '.#.'], ['.'], ['#'],
           ['..'], ['.', '.'], ['##', '##'], ['..', '.#'],
           ['....', '.##.', '....'], ['....', '....', '....', '....']]
_cases = [_case([(len(board), len(board[0])), *board], _domino_oracle(board)) for board in _boards]
# A 2-by-h empty board has Fibonacci(h+1) tilings, from a separate first-column proof.
_a, _b = 1, 1
for _ in range(60):
    _a, _b = _b, _a + _b
_cases.append(_case([(60, 2), *(['..'] * 60)], _a % 1000000007))
_add(40, '轮廓线 DP：带障碍棋盘的骨牌铺法',
     '当棋盘很长但很窄时，不必记录整张棋盘，只保留扫描边界上哪些格子已被上一行伸下来的竖骨牌占据。逐行维护二进制 mask，并在当前行填第一个空格：横放覆盖同行下一格，竖放则在下一行 mask 设置一位。障碍格相当于已占据，但不能与传入的竖骨牌重叠。',
     'blocked = sum(1 << c for c, char in enumerate(row) if char == "#")\nif incoming & blocked:\n    continue\nfull = (1 << width) - 1\n# mask 的第 c 位代表第 c 列，不是第 c 行',
     '输入 h w（1≤h≤100，1≤w≤8），随后 h 行长度恰为 w 的字符串，仅含 . 与 #。. 是待铺格，# 是障碍。使用任意数量 1×2 骨牌，可横放或竖放，每个待铺格恰好覆盖一次，障碍不可覆盖，骨牌不可伸出棋盘。输出不同铺法数模 1000000007；全部为障碍时空铺法计 1。',
     _cases, r'''
tokens = sys.stdin.buffer.read().split()
height, width = int(tokens[0]), int(tokens[1])
board = [row.decode() for row in tokens[2:]]
blocked = [sum(1 << c for c, char in enumerate(row) if char == '#') for row in board]
MOD = 1000000007
full = (1 << width) - 1
dp = {0: 1}
for row in range(height):
    next_dp = {}
    for incoming, count in dp.items():
        if incoming & blocked[row]:
            continue
        def fill(occupied, outgoing):
            if occupied == full:
                next_dp[outgoing] = (next_dp.get(outgoing, 0) + count) % MOD
                return
            empty = full ^ occupied
            bit = empty & -empty
            col = bit.bit_length() - 1
            if col + 1 < width and not (occupied & (bit << 1)):
                fill(occupied | bit | (bit << 1), outgoing)
            if row + 1 < height and not (blocked[row + 1] & bit):
                fill(occupied | bit, outgoing | bit)
        fill(incoming | blocked[row], 0)
    dp = next_dp
print(dp.get(0, 0))
''',
     ['处理新的一行时，上一行竖放的骨牌决定了已经被占据的列。', '总是选当前行最左边的空格放骨牌；这样不会因放置顺序不同而重复计数。', '横放要求右邻格为空；竖放要求下一行存在且对应格不是障碍，最后只接受 outgoing=0。'],
     '正确性：扫描到某行时，已完成区域对未来的唯一影响就是跨越边界的竖骨牌列集合，故 mask 足够描述状态。填最左空格时，合法铺法在该格必定横放或竖放，两个分支互斥且完整；递归不会重排已经放置的骨牌，所以不重复计数。完成整行后按相同 outgoing 汇总，逐行归纳得到全部铺法。最终 mask=0 排除越过棋盘底部的骨牌。易错点：忽略 incoming 与障碍重叠，或把全障碍棋盘计为 0。',
     'O(h·w·4ʷ)，每个传入状态至多枚举 2ʷ 种填行分支', 'O(2ʷ+h·w)',
     difficulty='高手', skills=['轮廓线 DP', '状态压缩', '骨牌覆盖'])


assert [p['id'] for p in PROBLEMS] == list(range(381, 401))
