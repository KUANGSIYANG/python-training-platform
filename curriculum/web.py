"""Chapters 25–30: executable SQL, Python services, HTTP and frontend basics."""
from textwrap import dedent
from .schema import problem

PROBLEMS = []


def add(chapter, number, title, concept, description, parameters, tests,
        solution, hints, explanation, language="python", setup_sql=None):
    names = ", ".join(p[0] for p in parameters)
    options = {"language": language}
    if language == "javascript":
        options.update(requires=["node"], starter=f"function solve({names}) {{\n  // 编写代码，并 return 结果\n}}\n")
    elif language == "sql":
        options.update(setup_sql=setup_sql, starter="-- 编写一条 SELECT 或 WITH 查询\nSELECT * FROM " + setup_sql.split()[2].split("(")[0] + ";\n")
        concept += "\n\n本题表结构（已创建，每次测试重新填入数据）：\n```sql\n" + setup_sql + "\n```\n输入对象中每个表的二维数组按列定义顺序填入；只提交查询，结果按行转换为数组。"
    PROBLEMS.append(problem(chapter, number, title, dedent(concept).strip(), description,
                            parameters, tests, dedent(solution).strip(), hints, explanation,
                            difficulty="进阶" if chapter == 30 or number >= 7 else "基础", **options))


DB = [("tables", "object", "表名映射到行数组，列顺序见表结构")]
STUDENTS = "CREATE TABLE students(id INTEGER PRIMARY KEY, name TEXT, score INTEGER);"

add(25, 1, "SELECT 选择列并排序",
    "SELECT 列名 FROM 表名 选择结果列；ORDER BY id ASC 按编号升序。数据库不保证没有 ORDER BY 的查询顺序。",
    "返回所有学生的 [id, name]，按 id 升序；空表返回 []。输入行的先后顺序不代表结果顺序。", DB,
    [([{"students": [[2,"小林",90],[1,"小明",80]]}], [[1,"小明"],[2,"小林"]]),
     ([{"students": []}], []), ([{"students": [[7,"A",0]]}], [[7,"A"]]),
     ([{"students": [[3,"同名",10],[1,"同名",20]]}], [[1,"同名"],[3,"同名"]]),
     ([{"students": [[10,"",None],[-1,"B",100],[0,"C",50]]}], [[-1,"B"],[0,"C"],[10,""]])],
    "SELECT id, name FROM students ORDER BY id ASC;",
    ["先选择题目需要的两列。", "FROM 后写 students。", "使用 ORDER BY id ASC 保证排序。"],
    "SELECT 不改变原表，只投影 id 和 name。ORDER BY 对最终结果排序，空表自然产生零行。", "sql", STUDENTS)

add(25, 2, "WHERE 筛选及格学生",
    "WHERE score >= 60 过滤记录；AND / OR 可以组合条件。NULL 表示未知，NULL >= 60 不为真，因此不会被选中。",
    "选择 score 大于等于 60 的学生，返回 [name, score]，按 score 降序，同分按 id 升序；NULL 分数排除。", DB,
    [([{"students": [[1,"甲",60],[2,"乙",59],[3,"丙",90]]}], [["丙",90],["甲",60]]),
     ([{"students": [[2,"B",70],[1,"A",70],[3,"C",None]]}], [["A",70],["B",70]]),
     ([{"students": []}], []), ([{"students": [[1,"X",0]]}], []),
     ([{"students": [[1,"满分",100],[2,"边界",60]]}], [["满分",100],["边界",60]])],
    "SELECT name, score FROM students WHERE score >= 60 ORDER BY score DESC, id ASC;",
    ["先用 WHERE 去掉不及格和未知分数。", "排序可以有多个键。", "ORDER BY score DESC, id ASC。"],
    "WHERE 在排序前筛选；DESC 让高分优先，第二个排序键确保同分结果稳定。", "sql", STUDENTS)

add(25, 3, "LIMIT 获取价格前三",
    "ORDER BY price DESC, id ASC 可按多个键排序；LIMIT 3 最多保留三行。LIMIT 是排序后的截取，不是随机抽样。",
    "商品价格为非负整数，返回最贵的至多三个商品 [id, name, price]，同价按 id 升序。", DB,
    [([{"products": [[1,"笔",3],[2,"书",30],[3,"包",100],[4,"杯",20]]}], [[3,"包",100],[2,"书",30],[4,"杯",20]]),
     ([{"products": []}], []), ([{"products": [[8,"单品",0]]}], [[8,"单品",0]]),
     ([{"products": [[4,"D",5],[2,"B",5],[1,"A",5],[3,"C",5]]}], [[1,"A",5],[2,"B",5],[3,"C",5]]),
     ([{"products": [[2,"B",1],[1,"A",2]]}], [[1,"A",2],[2,"B",1]])],
    "SELECT id, name, price FROM products ORDER BY price DESC, id ASC LIMIT 3;",
    ["先完成降序排序，再取前三。", "价格相同需要编号排序。", "在 ORDER BY 后追加 LIMIT 3。"],
    "排序定义名次，LIMIT 限制数量。少于三条时返回实际存在的记录，不补空行。", "sql",
    "CREATE TABLE products(id INTEGER PRIMARY KEY, name TEXT, price INTEGER);")

add(25, 4, "DISTINCT 去除重复分类",
    "SELECT DISTINCT category 会合并相同分类。判断缺失必须用 IS NULL / IS NOT NULL，不能用 = NULL。",
    "返回所有非 NULL 的唯一分类，每行一个分类，按 SQLite 默认 BINARY 文本升序；空字符串是合法分类。测试分类使用 ASCII。", DB,
    [([{"products": [[1,"book"],[2,"pen"],[3,"book"],[4,None]]}], [["book"],["pen"]]),
     ([{"products": []}], []), ([{"products": [[1,None],[2,None]]}], []),
     ([{"products": [[1,""],[2,"A"],[3,"a"],[4,""]]}], [[""],["A"],["a"]]),
     ([{"products": [[1,"z"],[2,"b"]]}], [["b"],["z"]])],
    "SELECT DISTINCT category FROM products WHERE category IS NOT NULL ORDER BY category;",
    ["WHERE 先排除 NULL。", "DISTINCT 写在 SELECT 后。", "最后按 category 升序排列。"],
    "过滤 NULL 后去重，保留空字符串。大小写不同的 ASCII 字符串在默认比较规则下是不同分类。", "sql",
    "CREATE TABLE products(id INTEGER PRIMARY KEY, category TEXT);")

add(25, 5, "聚合与 NULL 计数",
    "COUNT(*) 数所有行，COUNT(score) 只数非 NULL 值。SUM(score) 求和，但没有可求和值时为 NULL；COALESCE(value, 0) 可以提供默认值。",
    "返回一行 [总人数, 有分数人数, 分数总和]；空表返回 [[0, 0, 0]]，NULL 不参与求和。", DB,
    [([{"students": [[1,"A",80],[2,"B",None],[3,"C",0]]}], [[3,2,80]]),
     ([{"students": []}], [[0,0,0]]), ([{"students": [[1,"A",None]]}], [[1,0,0]]),
     ([{"students": [[1,"A",60],[2,"B",90]]}], [[2,2,150]]),
     ([{"students": [[1,"A",0],[2,"B",0]]}], [[2,2,0]])],
    "SELECT COUNT(*), COUNT(score), COALESCE(SUM(score), 0) FROM students;",
    ["不需要 GROUP BY，整个表作为一组。", "区分 COUNT(*) 和 COUNT(score)。", "用 COALESCE(SUM(score), 0) 处理空值。"],
    "三个聚合函数各产生一个值；即使输入没有行，无 GROUP BY 的聚合也返回一行。", "sql", STUDENTS)

add(25, 6, "GROUP BY 分类汇总",
    "GROUP BY category 按分类分组；每组可计算 SUM(amount)。SELECT 中普通列应属于分组键，避免不确定结果。",
    "销售金额为整数，分类是非 NULL ASCII 字符串。返回每类 [category, 总金额]，按分类升序；空表返回 []。", DB,
    [([{"sales": [[1,"book",10],[2,"pen",3],[3,"book",20]]}], [["book",30],["pen",3]]),
     ([{"sales": []}], []), ([{"sales": [[1,"a",0]]}], [["a",0]]),
     ([{"sales": [[1,"z",5],[2,"a",-2],[3,"a",2]]}], [["a",0],["z",5]]),
     ([{"sales": [[1,"x",1],[2,"x",1],[3,"x",1]]}], [["x",3]])],
    "SELECT category, SUM(amount) FROM sales GROUP BY category ORDER BY category;",
    ["用 category 作为组的标识。", "对每组 amount 求 SUM。", "GROUP BY 后仍需 ORDER BY category。"],
    "分组把相同分类的记录汇集起来，SUM 计算净金额，负数可表示退款。输出再按分类排序。", "sql",
    "CREATE TABLE sales(id INTEGER PRIMARY KEY, category TEXT, amount INTEGER);")

add(25, 7, "HAVING 筛选活跃用户",
    "WHERE 筛选单条记录，HAVING 筛选聚合后的分组。例如 GROUP BY user_id HAVING COUNT(*) >= 2 保留至少两条记录的用户。",
    "返回订单数至少为 2 的 [user_id, 订单数]，按订单数降序、user_id 升序。每行是一个订单，不按金额判断活跃度。", DB,
    [([{"orders": [[1,2,8],[2,1,9],[3,2,0],[4,1,2],[5,3,9]]}], [[1,2],[2,2]]),
     ([{"orders": []}], []), ([{"orders": [[1,1,10]]}], []),
     ([{"orders": [[1,4,0],[2,4,0],[3,4,0],[4,2,1],[5,2,1]]}], [[4,3],[2,2]]),
     ([{"orders": [[1,9,-1],[2,9,1]]}], [[9,2]])],
    "SELECT user_id, COUNT(*) AS n FROM orders GROUP BY user_id HAVING COUNT(*) >= 2 ORDER BY n DESC, user_id;",
    ["先按 user_id 分组并计数。", "聚合条件放在 HAVING 中。", "可以用 AS n 为计数命名，再 ORDER BY n DESC, user_id。"],
    "HAVING 在分组完成后过滤，金额不参与统计。别名 n 可用作最终排序键。", "sql",
    "CREATE TABLE orders(id INTEGER PRIMARY KEY, user_id INTEGER, amount INTEGER);")

JOIN_SCHEMA = "CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT);\nCREATE TABLE orders(id INTEGER PRIMARY KEY, user_id INTEGER, amount INTEGER);"
add(25, 8, "INNER JOIN 连接用户订单",
    "FROM orders AS o JOIN users AS u ON o.user_id = u.id 按外键含义连接两个表。INNER JOIN 只保留两侧匹配的记录；别名用于区分同名列。",
    "返回匹配到用户的订单 [订单id, 用户name, amount]，按订单 id 升序；找不到用户的订单忽略，重名用户仍按 id 匹配。", DB,
    [([{"users": [[1,"甲"],[2,"乙"]],"orders": [[2,1,20],[1,2,10]]}], [[1,"乙",10],[2,"甲",20]]),
     ([{"users": [],"orders": [[1,99,5]]}], []),
     ([{"users": [[1,"甲"]],"orders": []}], []),
     ([{"users": [[1,"同名"],[2,"同名"]],"orders": [[3,2,0],[1,1,8],[2,9,3]]}], [[1,"同名",8],[3,"同名",0]]),
     ([{"users": [[1,"A"]],"orders": [[2,1,-2],[1,1,5]]}], [[1,"A",5],[2,"A",-2]])],
    "SELECT o.id, u.name, o.amount FROM orders AS o JOIN users AS u ON o.user_id = u.id ORDER BY o.id;",
    ["订单的 user_id 对应 users.id。", "用表别名限定 id 来避免歧义。", "SELECT o.id, u.name, o.amount，最后 ORDER BY o.id。"],
    "ON 为每个订单寻找编号相同的用户，内连接丢弃未匹配记录。选出三列后按订单编号排序。", "sql", JOIN_SCHEMA)

add(25, 9, "LEFT JOIN 保留零订单用户",
    "LEFT JOIN 保留左表全部记录，缺少右侧记录时右侧列为 NULL。此时 COUNT(o.id) 为 0，而 COUNT(*) 会误算补出的空行。",
    "返回每位用户的 [用户id, 姓名, 订单数]，包括没有订单的用户，按用户 id 升序；孤立订单不影响结果。", DB,
    [([{"users": [[2,"B"],[1,"A"]],"orders": [[1,1,5],[2,1,6]]}], [[1,"A",2],[2,"B",0]]),
     ([{"users": [],"orders": [[1,9,5]]}], []),
     ([{"users": [[1,"A"]],"orders": []}], [[1,"A",0]]),
     ([{"users": [[1,"A"],[2,"A"]],"orders": [[1,2,0],[2,9,0]]}], [[1,"A",0],[2,"A",1]]),
     ([{"users": [[3,"C"]],"orders": [[1,3,2],[2,3,3],[3,3,4]]}], [[3,"C",3]])],
    "SELECT u.id, u.name, COUNT(o.id) FROM users AS u LEFT JOIN orders AS o ON o.user_id = u.id GROUP BY u.id, u.name ORDER BY u.id;",
    ["users 放在 LEFT JOIN 左侧。", "按用户编号和姓名分组。", "COUNT(o.id) 不会统计右侧补出的 NULL。"],
    "左连接为零订单用户保留一行，再通过 COUNT 的忽略 NULL 特性得到零。分组含用户 id，因此同名用户不会合并。", "sql", JOIN_SCHEMA)

add(25, 10, "WITH 分步查询超过均值者",
    "WITH totals AS (...) 为子查询起名，后续 SELECT 可把它当临时结果集使用。标量子查询 (SELECT AVG(total) FROM totals) 返回一个数值。",
    "先汇总每个 user_id 的 amount，再返回总额严格高于所有下单用户平均总额的 [user_id, total]，按 user_id 升序。只考虑 orders 中出现的用户；空表或全部相等时返回 []。", DB,
    [([{"orders": [[1,1,10],[2,1,20],[3,2,10],[4,3,20]]}], [[1,30]]),
     ([{"orders": []}], []), ([{"orders": [[1,4,8]]}], []),
     ([{"orders": [[1,1,5],[2,2,5]]}], []),
     ([{"orders": [[1,1,-5],[2,2,0],[3,3,8]]}], [[3,8]]),
     ([{"orders": [[1,1,10],[2,2,30],[3,3,40]]}], [[2,30],[3,40]])],
    "WITH totals AS (SELECT user_id, SUM(amount) AS total FROM orders GROUP BY user_id)\nSELECT user_id, total FROM totals WHERE total > (SELECT AVG(total) FROM totals) ORDER BY user_id;",
    ["先生成每个用户只有一行的汇总结果。", "平均值要对用户总额求，不能直接 AVG(amount)。", "WITH totals AS (...) 后使用子查询 AVG(total) 进行比较。"],
    "CTE 把两层聚合分开：先求每人的总额，再计算这些总额的均值。严格大于排除等于均值的用户。", "sql",
    "CREATE TABLE orders(id INTEGER PRIMARY KEY, user_id INTEGER, amount INTEGER);")

# Chapter 26: pure service functions, with explicit request/response models.
add(26, 1, "路由表分发请求",
    "后端路由通常由 HTTP 方法与路径共同决定。Python 可用字典 routes[(method, path)] 查找处理器，用 .get(key, default) 提供未找到分支。",
    "method 转成大写后匹配：GET /health 返回 {status:200, body:'ok'}；GET /items 返回 {status:200, body:[]}；POST /items 返回 {status:201, body:'created'}。其余组合统一返回 {status:404, body:'not_found'}。路径严格匹配，不去除斜杠。",
    [("method","str","请求方法"),("path","str","路径")],
    [(["get","/health"],{"status":200,"body":"ok"}),(["POST","/items"],{"status":201,"body":"created"}),
     (["GET","/items"],{"status":200,"body":[]}),(["DELETE","/items"],{"status":404,"body":"not_found"}),
     (["GET","/health/"],{"status":404,"body":"not_found"})],
    '''
    def solve(method, path):
        routes = {("GET", "/health"): (200, "ok"), ("GET", "/items"): (200, []), ("POST", "/items"): (201, "created")}
        status, body = routes.get((method.upper(), path), (404, "not_found"))
        return {"status": status, "body": body}
    ''', ["用元组保存方法和路径。","method.upper() 统一方法大小写。","字典查不到时返回默认的 404 元组。"],
    "分发函数用二元键避免 GET 与 POST 冲突。把状态和响应体装进统一结构后，调用方可以直接消费结果。")

add(26, 2, "验证创建用户的请求体",
    "入口验证应先检查类型再使用字符串方法。type(age) is int 可排除 bool，因为 isinstance(True, int) 为 True；strip() 清理两端空白。",
    "payload 是字典。name 必须是去空白后非空的字符串，age 必须为 0～120 的整数且不能是布尔值。按 name、age 顺序收集错误字段，失败返回 {ok:false, errors:[字段]}；成功返回 {ok:true, user:{name:清理后姓名, age:年龄}}。忽略额外字段。",
    [("payload","dict","待验证 JSON 对象")],
    [([{"name":" 小明 ","age":18}],{"ok":True,"user":{"name":"小明","age":18}}),
     ([{}],{"ok":False,"errors":["name","age"]}),([{"name":" ","age":True}],{"ok":False,"errors":["name","age"]}),
     ([{"name":"A","age":0,"role":"admin"}],{"ok":True,"user":{"name":"A","age":0}}),
     ([{"name":"B","age":121}],{"ok":False,"errors":["age"]}),
     ([{"name":9,"age":120}],{"ok":False,"errors":["name"]})],
    '''
    def solve(payload):
        name, age = payload.get("name"), payload.get("age")
        errors = []
        if not isinstance(name, str) or not name.strip():
            errors.append("name")
        if type(age) is not int or not 0 <= age <= 120:
            errors.append("age")
        return {"ok": False, "errors": errors} if errors else {"ok": True, "user": {"name": name.strip(), "age": age}}
    ''', ["缺失字段用 .get() 得到 None。","两项独立验证，不能发现一个错误就退出。","年龄用 type(age) is int，再检查闭区间。"],
    "先累积字段错误，再决定返回哪种响应。短路 or 确保非字符串不会执行 strip，避免验证代码自身报错。")

add(26, 3, "分页列表服务",
    "分页从 1 计数时，起点是 (page - 1) * size；列表切片 items[start:start + size] 不会因越界而报错。",
    "page、size 是正整数。返回 {items:本页切片, total:总条数, pages:总页数}；总页数向上取整，空列表为 0，超出最后一页时 items 为 []。",
    [("items","list","有序数据"),("page","int","页码 >= 1"),("size","int","每页条数 >= 1")],
    [([[1,2,3,4,5],2,2],{"items":[3,4],"total":5,"pages":3}),([[],1,3],{"items":[],"total":0,"pages":0}),
     ([[1],3,2],{"items":[],"total":1,"pages":1}),([[1,2,3,4],2,2],{"items":[3,4],"total":4,"pages":2}),
     ([["a","b"],1,10],{"items":["a","b"],"total":2,"pages":1})],
    '''
    def solve(items, page, size):
        start = (page - 1) * size
        return {"items": items[start:start + size], "total": len(items), "pages": (len(items) + size - 1) // size}
    ''', ["先算切片起点。","总页数可以用整数向上取整。","(len(items) + size - 1) // size 也适用于空列表。"],
    "切片取当前页，total 始终统计全部输入。整数公式避免浮点除法，零条数据计算出零页。")

add(26, 4, "按编号查询资源",
    "next((item for item in items if ...), None) 查找第一个匹配项，没有时返回默认值。REST 服务常用 200 表示成功、404 表示资源不存在。",
    "items 内每项是含唯一整数 id 的字典。找到 target_id 返回 {status:200, body:该项}，否则返回 {status:404, body:{error:'not_found'}}。",
    [("items","list[dict]","id 唯一"),("target_id","int","目标编号")],
    [([[{"id":1,"name":"A"},{"id":2,"name":"B"}],2],{"status":200,"body":{"id":2,"name":"B"}}),
     ([[],1],{"status":404,"body":{"error":"not_found"}}),
     ([[{"id":1}],9],{"status":404,"body":{"error":"not_found"}}),
     ([[{"id":0,"active":False}],0],{"status":200,"body":{"id":0,"active":False}}),
     ([[{"id":3,"tags":[]}],3],{"status":200,"body":{"id":3,"tags":[]}})],
    '''
    def solve(items, target_id):
        item = next((item for item in items if item["id"] == target_id), None)
        if item is None:
            return {"status": 404, "body": {"error": "not_found"}}
        return {"status": 200, "body": item}
    ''', ["遍历列表比较 id。","未找到和空列表走同一分支。","用 is None 判断未找到，返回固定错误对象。"],
    "查找逻辑与响应包装分开：先取得对象，再根据是否存在选择状态码，保留对象全部字段。")

add(26, 5, "创建资源并分配编号",
    "创建资源可复制列表后追加新字典。练习中用 max(ids, default=0) + 1 分配编号；真实并发数据库通常用数据库主键机制。",
    "items 的 id 为唯一正整数，name 为非空字符串。新编号是现有最大 id 加 1，空列表从 1 开始。返回 {status:201, item:新对象, items:追加后的列表}；新对象仅含 id、name，不清理 name。",
    [("items","list[dict]","现有资源"),("name","str","新名称")],
    [([[{"id":2,"name":"A"}],"B"],{"status":201,"item":{"id":3,"name":"B"},"items":[{"id":2,"name":"A"},{"id":3,"name":"B"}]}),
     ([[],"首项"],{"status":201,"item":{"id":1,"name":"首项"},"items":[{"id":1,"name":"首项"}]}),
     ([[{"id":8,"name":"A"},{"id":1,"name":"B"}],"C"],{"status":201,"item":{"id":9,"name":"C"},"items":[{"id":8,"name":"A"},{"id":1,"name":"B"},{"id":9,"name":"C"}]}),
     ([[]," X "],{"status":201,"item":{"id":1,"name":" X "},"items":[{"id":1,"name":" X "}]}),
     ([[{"id":99,"name":"同名"}],"同名"],{"status":201,"item":{"id":100,"name":"同名"},"items":[{"id":99,"name":"同名"},{"id":100,"name":"同名"}]})],
    '''
    def solve(items, name):
        item = {"id": max((row["id"] for row in items), default=0) + 1, "name": name}
        return {"status": 201, "item": item, "items": items + [item]}
    ''', ["编号不等于列表长度加一。","用 max 的 default 参数处理空列表。","items + [item] 保留原列表顺序并追加。"],
    "最大编号加一允许输入存在编号间隔。构建独立新对象并通过拼接生成返回列表，创建成功采用 201。")

add(26, 6, "PATCH 只更新允许字段",
    "部分更新可用字典解包 {**old, **changes}；后面的同名键覆盖前面的值。允许字段列表能防止客户端修改 id 等受保护字段。",
    "对 user 应用 patch，只接受 name、active 两个键，忽略其余键并保留 user 的其他字段。允许的字段若存在就原样更新，包括空字符串、false、null；不进行类型验证。",
    [("user","dict","现有对象"),("patch","dict","更新内容")],
    [([{"id":1,"name":"A","active":True},{"name":"B","id":9}],{"id":1,"name":"B","active":True}),
     ([{"id":1},{}],{"id":1}),([{"id":2,"active":True},{"active":False}],{"id":2,"active":False}),
     ([{"id":3,"name":"A"},{"name":"","active":None}],{"id":3,"name":"","active":None}),
     ([{"id":4,"role":"reader"},{"role":"admin","unknown":1}],{"id":4,"role":"reader"})],
    '''
    def solve(user, patch):
        changes = {key: value for key, value in patch.items() if key in {"name", "active"}}
        return {**user, **changes}
    ''', ["判断键是否允许，不要判断值的真假。","从 patch 筛出允许的键值对。","用 {**user, **changes} 覆盖字段。"],
    "先过滤可更新字段，再合并字典。这样 false 和空字符串仍能生效，id 和角色不会被意外覆盖。")

add(26, 7, "DELETE 删除并报告状态",
    "列表推导式可以保留不匹配目标编号的项。DELETE 成功后常用 204 表示没有响应体；本题返回结构包含保留下来的列表便于判题。",
    "输入项有唯一整数 id。存在 target_id 时删除对应项，返回 {status:204, items:剩余项}；不存在返回 {status:404, items:原列表}，保持顺序。",
    [("items","list[dict]","现有资源"),("target_id","int","待删除编号")],
    [([[{"id":1},{"id":2},{"id":3}],2],{"status":204,"items":[{"id":1},{"id":3}]}),
     ([[],1],{"status":404,"items":[]}),([[{"id":1}],1],{"status":204,"items":[]}),
     ([[{"id":1}],9],{"status":404,"items":[{"id":1}]}),
     ([[{"id":0,"name":"零"},{"id":4}],0],{"status":204,"items":[{"id":4}]})],
    '''
    def solve(items, target_id):
        kept = [item for item in items if item["id"] != target_id]
        return {"status": 204 if len(kept) < len(items) else 404, "items": kept}
    ''', ["保留编号不相同的项。","比较过滤前后的长度判断是否删除成功。","成功为 204，否则 404；都返回 kept。"],
    "一次过滤同时完成查找和删除。长度减少说明资源存在，列表推导式保留原相对顺序。")

add(26, 8, "统一 JSON 响应体",
    "json.dumps 把 Python 对象序列化为 JSON 字符串。ensure_ascii=False 保留中文，sort_keys=True 固定键顺序，separators=(',', ':') 去掉多余空格。",
    "把任意 JSON 可序列化 data 包装为 {status:输入status, headers:{Content-Type:'application/json; charset=utf-8'}, body:紧凑JSON字符串}。所有层级键按字典序排序，中文不转义；JSON 标量也允许。",
    [("data","JSON","响应数据"),("status","int","HTTP 状态码")],
    [([{"b":2,"a":"中文"},200],{"status":200,"headers":{"Content-Type":"application/json; charset=utf-8"},"body":'{"a":"中文","b":2}'}),
     ([None,204],{"status":204,"headers":{"Content-Type":"application/json; charset=utf-8"},"body":"null"}),
     ([[True,False],200],{"status":200,"headers":{"Content-Type":"application/json; charset=utf-8"},"body":"[true,false]"}),
     ([{"x":{"z":0,"a":1}},201],{"status":201,"headers":{"Content-Type":"application/json; charset=utf-8"},"body":'{"x":{"a":1,"z":0}}'}),
     (["a\nb",400],{"status":400,"headers":{"Content-Type":"application/json; charset=utf-8"},"body":'"a\\nb"'})],
    '''
    import json
    def solve(data, status):
        body = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return {"status": status, "headers": {"Content-Type": "application/json; charset=utf-8"}, "body": body}
    ''', ["body 需要字符串，不是原始字典。","用 json.dumps 的三个格式参数。","separators=(\",\", \":\") 生成紧凑 JSON。"],
    "序列化器处理布尔值、null 和转义；固定键顺序让字符串比较稳定。这个函数只建立响应模型，不发送 HTTP。")

add(26, 9, "中间件读取请求编号",
    "HTTP 头字段名不区分大小写，可以先转换为小写再查找。中间件常在处理请求前提取追踪编号，处理后附加到响应头。",
    "headers 是字符串键值字典，不会有仅大小写不同的重复键。读取 X-Request-ID（忽略键大小写），缺失或值为空字符串时用 fallback；其余值不清理。返回 {body:body, headers:{X-Request-ID:编号}}。",
    [("headers","dict[str,str]","请求头"),("body","JSON","响应数据"),("fallback","str","默认请求编号")],
    [([{"x-request-id":"abc"},{"ok":True},"new"],{"body":{"ok":True},"headers":{"X-Request-ID":"abc"}}),
     ([{},[],"r1"],{"body":[],"headers":{"X-Request-ID":"r1"}}),
     ([{"X-REQUEST-ID":""},None,"r2"],{"body":None,"headers":{"X-Request-ID":"r2"}}),
     ([{"X-Request-Id":"  "},0,"r3"],{"body":0,"headers":{"X-Request-ID":"  "}}),
     ([{"Accept":"json","X-Request-ID":"42"},"ok","r4"],{"body":"ok","headers":{"X-Request-ID":"42"}})],
    '''
    def solve(headers, body, fallback):
        normalized = {key.lower(): value for key, value in headers.items()}
        request_id = normalized.get("x-request-id") or fallback
        return {"body": body, "headers": {"X-Request-ID": request_id}}
    ''', ["先把头字段名规范成小写。","只在缺失或空字符串时使用 fallback。","取值可用 normalized.get('x-request-id') or fallback。"],
    "规范头名称解决大小写差异，保留头值本身。返回固定格式的响应头有助于调用链定位请求。")

add(26, 10, "业务异常映射为 API 错误",
    "服务层可先验证输入，再处理业务状态。返回明确状态码能区分无效请求（400）、资源不存在（404）、状态冲突（409）和成功（200）。",
    "stock 将商品字符串编号映射到非负整数库存。quantity 必须是正整数且不是 bool；验证失败先返回 {status:400,error:'invalid_quantity'}。之后商品缺失返回 404/not_found；库存不足返回 409/insufficient_stock；成功返回 {status:200,remaining:扣减后的库存}。不用修改其他商品。",
    [("stock","dict[str,int]","库存映射"),("item_id","str","商品编号"),("quantity","JSON","请求数量")],
    [([{"a":5},"a",2],{"status":200,"remaining":3}),([{},"x",0],{"status":400,"error":"invalid_quantity"}),
     ([{},"x",1],{"status":404,"error":"not_found"}),([{"a":0},"a",1],{"status":409,"error":"insufficient_stock"}),
     ([{"a":3},"a",3],{"status":200,"remaining":0}),([{"a":3},"a",True],{"status":400,"error":"invalid_quantity"})],
    '''
    def solve(stock, item_id, quantity):
        if type(quantity) is not int or quantity <= 0:
            return {"status": 400, "error": "invalid_quantity"}
        if item_id not in stock:
            return {"status": 404, "error": "not_found"}
        if stock[item_id] < quantity:
            return {"status": 409, "error": "insufficient_stock"}
        return {"status": 200, "remaining": stock[item_id] - quantity}
    ''', ["严格按题目的验证顺序分支。","先判断键是否存在，再读取库存。","不足用小于判断，相等库存允许成功。"],
    "提前返回使每个错误条件独立清楚。最后一条分支只处理验证通过、存在且库存足够的请求。")


# Chapter 27: HTTP concepts are practiced with deterministic values.  The two
# urllib exercises use practice_support.local_api, a loopback-only temporary
# server that is loaded by the local runner before learner code is executed.
add(27, 1, "拆解 URL 的路径和查询参数",
    "`urlsplit(url)` 把 URL 分成 path、query 等部分；`parse_qsl(query, keep_blank_values=True)` 会解码查询参数，并保留它们的顺序、重复键和空值。",
    "返回 {path:原始路径, query:[[键,值], ...]}。query 中的百分号编码和 `+` 要按 URL 规则解码；没有路径时 path 是空字符串。不要把片段（# 后内容）放进结果。",
    [("url","str","完整或相对 URL")],
    [(["https://example.test/items?q=Python%20book&tag=new"],{"path":"/items","query":[["q","Python book"],["tag","new"]]}),
     (["/search?tag=a&tag=b&empty="],{"path":"/search","query":[["tag","a"],["tag","b"],["empty",""]]}),
     (["https://a.test"],{"path":"","query":[]}),
     (["?q=%E4%B8%AD%E6%96%87#part"],{"path":"","query":[["q","中文"]]}),
     (["/a/b?x=1+2&flag"],{"path":"/a/b","query":[["x","1 2"],["flag",""]]})],
    '''
    from urllib.parse import parse_qsl, urlsplit

    def solve(url):
        parts = urlsplit(url)
        return {"path": parts.path, "query": [list(pair) for pair in parse_qsl(parts.query, keep_blank_values=True)]}
    ''', ["先用 urlsplit 取得 path 和 query。", "解析 query 时传入 keep_blank_values=True。", "把 parse_qsl 得到的每个二元组转换为列表。"],
    "路径本身直接来自 URL；查询串要另外解析。parse_qsl 同时完成百分号解码和 `+` 到空格的转换，且不会合并重复参数。")

add(27, 2, "安全编码查询字符串",
    "`urllib.parse.urlencode` 会把键值对编码为 `key=value&...`。空格通常编码为 `+`，`&`、`/` 等数据字符会被百分号编码，因此不应手工拼接用户输入。",
    "base 不含 `?` 或 `#`。pairs 是按顺序给出的 [键, 值] 字符串列表；返回 base 加上编码后的查询串。pairs 为空时直接返回 base，不添加问号。",
    [("base","str","不含查询串的基础地址"),("pairs","list[list[str]]","有序的查询键值对")],
    [(["https://example.test/items",[["q","Python book"],["tag","new"]]],"https://example.test/items?q=Python+book&tag=new"),
     (["/search",[]],"/search"),
     (["/search",[["中文","a&b"],["empty",""]]],"/search?%E4%B8%AD%E6%96%87=a%26b&empty="),
     (["/x",[["q","a/b"],["q","two words"]]],"/x?q=a%2Fb&q=two+words"),
     (["https://a.test/p",[["page","1"]]],"https://a.test/p?page=1")],
    '''
    from urllib.parse import urlencode

    def solve(base, pairs):
        query = urlencode([tuple(pair) for pair in pairs])
        return base + ("?" + query if query else "")
    ''', ["把整个 pairs 列表交给 urlencode。", "先保存编码后的 query。", "只有 query 非空时才连接 `?`。"],
    "urlencode 按给定列表顺序处理每一项，重复键也会保留。条件拼接避免了空参数时产生没有意义的尾随问号。")

add(27, 3, "按状态码分类 HTTP 响应",
    "HTTP 状态码的第一个数字表示类别：2xx 成功、3xx 重定向、4xx 客户端错误、5xx 服务器错误。状态码属于协议结果，不能只把 200 当作唯一成功。",
    "把 status 分类为 success、redirect、client_error、server_error 或 unknown。仅 200—599 中的对应百位范围有已定义类别；其余整数返回 unknown。",
    [("status","int","HTTP 状态码")],
    [([200],"success"),([204],"success"),([301],"redirect"),([404],"client_error"),([503],"server_error"),([199],"unknown"),([600],"unknown")],
    '''
    def solve(status):
        if 200 <= status < 300:
            return "success"
        if 300 <= status < 400:
            return "redirect"
        if 400 <= status < 500:
            return "client_error"
        if 500 <= status < 600:
            return "server_error"
        return "unknown"
    ''', ["依次判断 2xx、3xx、4xx、5xx 的半开区间。", "204 也在 2xx 范围内。", "所有范围外的值最后统一返回 unknown。"],
    "半开区间写法 `200 <= status < 300` 清楚地表达了完整类别。按从低到高的分支判断后，剩下的值就是未知类别。")

add(27, 4, "忽略大小写读取请求头",
    "HTTP 头字段名不区分大小写。字典键本身区分大小写，所以读取前可把待比较的两个名称都用 `.lower()` 规范化。",
    "headers 不会同时含有仅大小写不同的同名键。查找 name 对应的头值并返回；没有该头时返回 null。保留值原样，包括空字符串。",
    [("headers","dict[str,str]","请求或响应头"),("name","str","要读取的头字段名")],
    [([{"content-type":"application/json"},"Content-Type"],"application/json"),
     ([{"X-Request-ID":"abc"},"x-request-id"],"abc"),
     ([{},"Accept"],None),
     ([{"Accept":"","X":"1"},"ACCEPT"],""),
     ([{"Content-Type":"text/plain; charset=utf-8"},"content-type"],"text/plain; charset=utf-8")],
    '''
    def solve(headers, name):
        wanted = name.lower()
        for key, value in headers.items():
            if key.lower() == wanted:
                return value
        return None
    ''', ["先把 name 转成小写。", "遍历 headers 的键和值。", "键的小写形式匹配时立即返回；循环结束后返回 None。"],
    "不能直接用 `headers.get(name)`，因为字典不会自动忽略大小写。逐项比较规范形式即可，同时完整保留原始头值。")

add(27, 5, "构造 JSON POST 请求模型",
    "JSON API 常通过 `Content-Type: application/json; charset=utf-8` 声明请求体格式。`json.dumps` 把 Python 数据变成 JSON 字符串；`sort_keys=True` 让对象键顺序稳定。",
    "返回 {method:'POST', url:url, headers:{Content-Type:'application/json; charset=utf-8', Accept:'application/json'}, body:紧凑 JSON 字符串}。body 保留中文、递归按键排序，并且不含多余空格。这里只构造请求模型，不发送网络请求。",
    [("data","JSON","待发送的数据"),("url","str","接口地址")],
    [([{"b":2,"a":"中文"},"/api/items"],{"method":"POST","url":"/api/items","headers":{"Content-Type":"application/json; charset=utf-8","Accept":"application/json"},"body":"{\"a\":\"中文\",\"b\":2}"}),
     ([None,"/api/empty"],{"method":"POST","url":"/api/empty","headers":{"Content-Type":"application/json; charset=utf-8","Accept":"application/json"},"body":"null"}),
     ([[True,False],"/api/flags"],{"method":"POST","url":"/api/flags","headers":{"Content-Type":"application/json; charset=utf-8","Accept":"application/json"},"body":"[true,false]"}),
     ([{"x":{"z":0,"a":1}},"https://a.test/x"],{"method":"POST","url":"https://a.test/x","headers":{"Content-Type":"application/json; charset=utf-8","Accept":"application/json"},"body":"{\"x\":{\"a\":1,\"z\":0}}"}),
     (["a\nb","/api/text"],{"method":"POST","url":"/api/text","headers":{"Content-Type":"application/json; charset=utf-8","Accept":"application/json"},"body":"\"a\\nb\""})],
    '''
    import json

    def solve(data, url):
        body = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return {"method": "POST", "url": url,
                "headers": {"Content-Type": "application/json; charset=utf-8", "Accept": "application/json"},
                "body": body}
    ''', ["先用 json.dumps 得到 body 字符串。", "设置 ensure_ascii=False、sort_keys=True 和紧凑 separators。", "把方法、地址、头和 body 放入一个字典。"],
    "请求体和请求头是不同层的信息：body 是字符串，Content-Type 说明怎样解释它。固定序列化格式也便于测试和日志比较。")

add(27, 6, "按 Content-Type 解析响应体",
    "响应体是否是 JSON 取决于 `Content-Type`，常见形式是 `application/json; charset=utf-8`。媒体类型本身不区分大小写，分号后的参数不影响判断。",
    "返回 {status:status, ok:是否为 2xx, data:解析结果}。忽略头字段名大小写；当 Content-Type 的媒体类型是 application/json 时，将 body 作为有效 JSON 解码，否则直接保留 body 字符串。测试中声明为 JSON 的 body 保证有效。",
    [("status","int","HTTP 状态码"),("headers","dict[str,str]","响应头"),("body","str","响应体文本")],
    [([200,{"Content-Type":"application/json; charset=utf-8"},'{"name":"小明"}'],{"status":200,"ok":True,"data":{"name":"小明"}}),
     ([404,{"content-type":"application/json"},'{"error":"not_found"}'],{"status":404,"ok":False,"data":{"error":"not_found"}}),
     ([204,{"Content-Type":"text/plain"},""],{"status":204,"ok":True,"data":""}),
     ([500,{"Content-Type":"text/plain; charset=utf-8"},"retry"],{"status":500,"ok":False,"data":"retry"}),
     ([201,{"CONTENT-TYPE":" Application/JSON ; charset=utf-8 "},"[1,true]"],{"status":201,"ok":True,"data":[1,True]})],
    '''
    import json

    def solve(status, headers, body):
        content_type = next((value for key, value in headers.items() if key.lower() == "content-type"), "")
        media_type = content_type.split(";", 1)[0].strip().lower()
        data = json.loads(body) if media_type == "application/json" else body
        return {"status": status, "ok": 200 <= status < 300, "data": data}
    ''', ["先用 next 从 headers 中找到 Content-Type。", "分号前的部分才是媒体类型。", "只有 JSON 媒体类型才调用 json.loads。"],
    "即使 404 等错误响应也可能有 JSON 错误对象，所以解析规则不应只由状态码决定。`ok` 单独反映 2xx 成功范围。")

add(27, 7, "添加可选 API 筛选参数",
    "把查询条件组织成键值对列表后再 `urlencode`，可以安全处理空格、中文和特殊字符。`None` 可表示该可选参数未提供，而空字符串是一个应保留的实际值。",
    "base 不含查询串。按 q、limit 的顺序加入非 null 参数，返回最终 URL；q 为空字符串和 limit 为 0 都要编码。若两个参数都为 null，直接返回 base。",
    [("base","str","基础接口地址"),("q","str|null","可选关键词"),("limit","int|null","可选条数")],
    [(["/items","Python",2],"/items?q=Python&limit=2"),(["/items",None,10],"/items?limit=10"),
     (["/items","a&b",None],"/items?q=a%26b"),(["/items","",0],"/items?q=&limit=0"),(["https://a.test/x",None,None],"https://a.test/x")],
    '''
    from urllib.parse import urlencode

    def solve(base, q, limit):
        pairs = []
        if q is not None:
            pairs.append(("q", q))
        if limit is not None:
            pairs.append(("limit", limit))
        return base + ("?" + urlencode(pairs) if pairs else "")
    ''', ["创建空的 pairs 列表。", "用 `is not None` 判断是否加入每个可选参数。", "最后统一 urlencode，而不是手工连接用户输入。"],
    "真假判断会错误丢弃 `''` 和 0，因此可选值要和 `None` 比较。键值对列表还明确规定了查询参数的输出顺序。")

add(27, 8, "用 urllib 请求本地 JSON API",
    "`urllib.request.urlopen` 会发出真实 HTTP 请求，读取到的是字节串，需要用 UTF-8 解码后再 `json.loads`。本题的 `local_api` 是每次调用临时启动的 127.0.0.1 服务，不访问互联网。",
    "items 中每项至少有 name。启动本地 API 后请求它的 `/items?q=...&limit=...`，返回服务器 JSON 对象 {items:匹配并截取后的项, total:截取前匹配数}。匹配忽略大小写；q 和 limit 均为合法值。",
    [("items","list[dict]","本地服务中的商品"),("q","str","名称关键词"),("limit","int","返回的最大条数，0—100")],
    [([ [{"id":1,"name":"Python 入门"},{"id":2,"name":"JavaScript"},{"id":3,"name":"python 工具"}], "python", 2],{"items":[{"id":1,"name":"Python 入门"},{"id":3,"name":"python 工具"}],"total":2}),
     ([ [], "", 10],{"items":[],"total":0}),
     ([ [{"id":1,"name":"书 A"},{"id":2,"name":"书 B"},{"id":3,"name":"笔"}], "书", 1],{"items":[{"id":1,"name":"书 A"}],"total":2}),
     ([ [{"id":1,"name":"A"},{"id":2,"name":"B"}], "", 0],{"items":[],"total":2}),
     ([ [{"id":1,"name":"Alpha"},{"id":2,"name":"beta"},{"id":3,"name":"Gamma"}], "A", 10],{"items":[{"id":1,"name":"Alpha"},{"id":2,"name":"beta"},{"id":3,"name":"Gamma"}],"total":3})],
    '''
    import json
    from urllib.parse import urlencode
    from urllib.request import urlopen
    from practice_support import local_api

    def solve(items, q, limit):
        with local_api(items) as base:
            url = base + "/items?" + urlencode({"q": q, "limit": limit})
            with urlopen(url, timeout=2) as response:
                return json.loads(response.read().decode("utf-8"))
    ''', ["local_api(items) 用 with 语句给出临时基础地址。", "用 urlencode 构造 q 和 limit。", "读取 response 的字节并 UTF-8 解码，再用 json.loads。"],
    "这次确实经过了 HTTP 请求、状态行和响应头，只是服务器固定在本机并在测试后关闭。`total` 由服务器在截取前计算，因此不能用返回 items 的长度代替。")

add(27, 9, "用 urllib POST JSON 并读取响应",
    "`urllib.request.Request` 可设置请求方法、字节请求体和头字段。发送 JSON 时先 `json.dumps(...).encode('utf-8')`，并声明 `Content-Type: application/json`。",
    "把 data 作为 JSON POST 到本地 `/echo`，返回 {status:HTTP状态码, content_type:响应媒体类型, data:解码后的JSON}。本题服务会把原始 JSON 放在 `received` 字段；它仅运行在本机临时端口。",
    [("data","JSON","要发送的 JSON 值")],
    [([{"name":"小明"}],{"status":200,"content_type":"application/json","data":{"received":{"name":"小明"}}}),
     ([[1,True,None]],{"status":200,"content_type":"application/json","data":{"received":[1,True,None]}}),
     (["中文"],{"status":200,"content_type":"application/json","data":{"received":"中文"}}),
     ([0],{"status":200,"content_type":"application/json","data":{"received":0}}),
     ([{"nested":{"a":1},"ok":False}],{"status":200,"content_type":"application/json","data":{"received":{"nested":{"a":1},"ok":False}}})],
    '''
    import json
    from urllib.request import Request, urlopen
    from practice_support import local_api

    def solve(data):
        with local_api([]) as base:
            payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
            request = Request(base + "/echo", data=payload,
                              headers={"Content-Type": "application/json"}, method="POST")
            with urlopen(request, timeout=2) as response:
                return {"status": response.status, "content_type": response.headers.get_content_type(),
                        "data": json.loads(response.read().decode("utf-8"))}
    ''', ["先把 data 序列化并编码成 bytes。", "创建 method 为 POST 的 Request，并设置 Content-Type。", "从响应读取状态、媒体类型和 JSON 数据。"],
    "HTTP 请求体传输的是字节，不是 Python 字典。服务端成功解析后返回新的 JSON 响应，客户端再按 UTF-8 和 JSON 两步反向转换。")

add(27, 10, "处理 HTTPError 的错误响应",
    "对非 2xx 响应，`urlopen` 会抛出 `urllib.error.HTTPError`；异常对象仍带有 `code` 和可读取的响应体。客户端应读取错误体，而不是把所有失败信息丢掉。",
    "使用含一个 Alpha 商品的本地服务对 path 发 GET 请求。无论成功还是 HTTP 错误，都返回 {status:状态码, body:服务返回的 JSON}。path 以 `/` 开头；测试只使用该本地服务支持的路径。",
    [("path","str","本地接口相对路径，可带查询串")],
    [(["/items?limit=0"],{"status":200,"body":{"items":[],"total":1}}),
     (["/items?limit=101"],{"status":400,"body":{"error":"invalid_limit"}}),
     (["/missing"],{"status":404,"body":{"error":"not_found"}}),
     (["/echo"],{"status":404,"body":{"error":"not_found"}}),
     (["/items?q=ALPHA&limit=1"],{"status":200,"body":{"items":[{"id":1,"name":"Alpha"}],"total":1}})],
    '''
    import json
    from urllib.error import HTTPError
    from urllib.request import urlopen
    from practice_support import local_api

    def solve(path):
        with local_api([{"id": 1, "name": "Alpha"}]) as base:
            try:
                with urlopen(base + path, timeout=2) as response:
                    return {"status": response.status, "body": json.loads(response.read().decode("utf-8"))}
            except HTTPError as error:
                return {"status": error.code, "body": json.loads(error.read().decode("utf-8"))}
    ''', ["从 urllib.error 导入 HTTPError。", "成功分支从 response 读取状态和 body。", "except 中用 error.code 和 error.read() 构造同样的结果。"],
    "异常并不表示没有 HTTP 响应：这里的 400 和 404 都有结构化 JSON 错误体。让成功和失败返回同一种数据形状，调用方就能统一处理。")


# Chapter 28 uses JavaScript functions that return HTML/CSS source strings.
# Node checks the exact string; it does not create a browser DOM or render CSS.
add(28, 1, "转义并生成一级标题",
    "HTML 文本中的 `&`、`<`、`>`、双引号和单引号有特殊含义。生成包含外部文本的标记前，使用 `replace` 按字符替换为实体可避免把文本当作标签。",
    "返回恰好形如 `<h1>已转义标题</h1>` 的 HTML 字符串。把 `& < > \" '` 分别转为 `&amp; &lt; &gt; &quot; &#39;`。本题只比较 Node.js 返回的字符串，不会在浏览器中渲染。",
    [("title","string","标题文本")],
    [(["欢迎"],"<h1>欢迎</h1>"),(["A & B"],"<h1>A &amp; B</h1>"),(["<script>"],"<h1>&lt;script&gt;</h1>"),(["\"单引号'"],"<h1>&quot;单引号&#39;</h1>"),([""],"<h1></h1>")],
    '''
    function solve(title) {
      const entities = {"&": "&amp;", "<": "&lt;", ">": "&gt;", "\\\"": "&quot;", "'": "&#39;"};
      const escaped = title.replace(/[&<>"']/g, character => entities[character]);
      return `<h1>${escaped}</h1>`;
    }
    ''', ["先写一个字符到实体的映射对象。", "用正则 `/[&<>\"']/g` 找到所有需要替换的字符。", "把 escaped 放进模板字符串的 h1 标签。"],
    "替换必须先处理 `&`，否则后来写入的实体又会被重复转义。这里返回的是 HTML 源码文本，安全性规则仍和真实模板渲染相同。", "javascript")

add(28, 2, "生成已转义的无序列表",
    "数组的 `map` 可把每个数据项变成一个 `<li>` 字符串，`join('')` 把这些片段紧密连接。页面模板中的数据仍需先转义。",
    "将 items 中的每个字符串转义后包进 `<li>`，并整体包进 `<ul>`，不添加空格或换行。空数组必须返回 `<ul></ul>`。本题检查 HTML 源码字符串，不检查浏览器 DOM。",
    [("items","string[]","列表文本")],
    [([["苹果","香蕉"]],"<ul><li>苹果</li><li>香蕉</li></ul>"),([[]],"<ul></ul>"),([["A & B","<新>"]],"<ul><li>A &amp; B</li><li>&lt;新&gt;</li></ul>"),([[""]],"<ul><li></li></ul>"),([["\"x\"","it's"]],"<ul><li>&quot;x&quot;</li><li>it&#39;s</li></ul>")],
    '''
    function solve(items) {
      const entities = {"&": "&amp;", "<": "&lt;", ">": "&gt;", "\\\"": "&quot;", "'": "&#39;"};
      const escapeHtml = text => text.replace(/[&<>"']/g, character => entities[character]);
      return `<ul>${items.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
    }
    ''', ["先写 escapeHtml 辅助函数。", "map 的每一项返回一个 li 字符串。", "用 join(\"\") 连接，再在外层加 ul。"],
    "`map` 对空数组会得到空数组，`join('')` 则得到空字符串，所以同一段代码自然覆盖空列表。每一项独立转义，数据不会改变标签结构。", "javascript")

add(28, 3, "生成固定格式的 CSS 卡片规则",
    "模板字符串可把变量插入 CSS 源码。CSS 中 `padding: 12px` 的单位 `px` 需要和数字连接；分号分隔声明。",
    "color 是不含分号和花括号的有效 CSS 颜色值，padding 是非负整数。返回恰好 `.card{background:颜色;padding:数字px;}`，没有额外空格。本题比较 CSS 字符串，Node.js 不会计算样式。",
    [("color","string","已验证的 CSS 颜色值"),("padding","number","内边距像素数")],
    [(["#fff",12],".card{background:#fff;padding:12px;}"),(["red",0],".card{background:red;padding:0px;}"),(["rgb(1, 2, 3)",8],".card{background:rgb(1, 2, 3);padding:8px;}"),(["var(--brand)",24],".card{background:var(--brand);padding:24px;}"),(["transparent",1],".card{background:transparent;padding:1px;}")],
    '''
    function solve(color, padding) {
      return `.card{background:${color};padding:${padding}px;}`;
    }
    ''', ["CSS 类选择器以 `.card` 开头。", "在模板字符串中插入 color 和 padding。", "不要漏掉两个声明后的分号和 px 单位。"],
    "这里的输入被题目限定为安全的颜色值，重点是 CSS 声明格式。真实项目若直接使用不可信数据，还要做更严格的白名单校验。", "javascript")

add(28, 4, "生成 BEM 类名列表",
    "BEM 常用 `块__元素--修饰符` 命名：没有元素时基类是块名，有元素时基类是 `block__element`。数组 `map` 很适合批量生成修饰类。",
    "element 要么为空字符串，要么是元素名；modifiers 是按顺序给出的修饰名。返回基础类加所有修饰类，以单个空格分隔；修饰类以基础类加 `--` 组成。本题只返回 class 属性会使用的字符串。",
    [("block","string","BEM 块名"),("element","string","元素名或空字符串"),("modifiers","string[]","有序修饰名")],
    [(["button","",["primary","large"]],"button button--primary button--large"),(["card","title",[]],"card__title"),(["nav","item",["active"]],"nav__item nav__item--active"),(["tag","",[]],"tag"),(["menu","icon",["small","muted"]],"menu__icon menu__icon--small menu__icon--muted")],
    '''
    function solve(block, element, modifiers) {
      const base = element ? `${block}__${element}` : block;
      return [base, ...modifiers.map(modifier => `${base}--${modifier}`)].join(" ");
    }
    ''', ["先根据 element 计算 base。", "用 map 将每个 modifier 变成 `${base}--${modifier}`。", "把 base 和修饰类放进数组后用单个空格 join。"],
    "扩展运算符 `...` 把 map 结果展开到同一个数组。没有修饰符时数组只含 base，join 仍返回正确的单个类名。", "javascript")

add(28, 5, "生成内联 style 属性",
    "CSS 声明可写成 `property:value`，多条声明用分号连接。用二维数组而非对象能明确保留声明顺序。",
    "entries 按输出顺序给出 [CSS属性, CSS值]，两者都是已验证、不含引号和分号的字符串。返回 `style=\"...\"` 属性文本；相邻声明间只有一个分号，空 entries 返回 `style=\"\"`。这里不执行浏览器样式。",
    [("entries","string[][]","有序 CSS 属性和值")],
    [([[["color","red"],["margin-top","8px"]]],"style=\"color:red;margin-top:8px\""),([[]],"style=\"\""),([[["display","grid"]]],"style=\"display:grid\""),([[["--gap","12px"],["gap","var(--gap)"]]],"style=\"--gap:12px;gap:var(--gap)\""),([[["font-weight","700"],["line-height","1.5"]]],"style=\"font-weight:700;line-height:1.5\"")],
    '''
    function solve(entries) {
      return `style="${entries.map(([property, value]) => `${property}:${value}`).join(";")}"`;
    }
    ''', ["map 的参数可用 `[property, value]` 解构。", "每一项生成 `属性:值`。", "用 `;` join 后放入双引号属性值。"],
    "二维数组让输出顺序成为输入的一部分，避免依赖对象遍历细节。空数组 join 后为空字符串，正好生成空 style 属性。", "javascript")

add(28, 6, "生成 label 和 input 标记",
    "表单控件的 `<label for>` 应与 `<input id>` 相同，这样点击标签可聚焦控件。文本和属性值中的特殊字符都要转义。",
    "返回没有空格或换行的 `<label for=\"...\">...</label><input id=\"...\" name=\"...\" value=\"...\">`。label、field、value 都按 HTML 实体规则转义。本题只验证标记字符串，不创建真实表单。",
    [("label","string","标签显示文本"),("field","string","字段名"),("value","string","初始值")],
    [(["姓名","name","小明"],"<label for=\"name\">姓名</label><input id=\"name\" name=\"name\" value=\"小明\">"),(["邮箱","email",""],"<label for=\"email\">邮箱</label><input id=\"email\" name=\"email\" value=\"\">"),(["A & B","user-name","x<y"],"<label for=\"user-name\">A &amp; B</label><input id=\"user-name\" name=\"user-name\" value=\"x&lt;y\">"),(["\"提示\"","quote","it's"],"<label for=\"quote\">&quot;提示&quot;</label><input id=\"quote\" name=\"quote\" value=\"it&#39;s\">"),(["<标签>","a&b","\""],"<label for=\"a&amp;b\">&lt;标签&gt;</label><input id=\"a&amp;b\" name=\"a&amp;b\" value=\"&quot;\">")],
    '''
    function solve(label, field, value) {
      const entities = {"&": "&amp;", "<": "&lt;", ">": "&gt;", "\\\"": "&quot;", "'": "&#39;"};
      const escapeHtml = text => text.replace(/[&<>"']/g, character => entities[character]);
      const safeField = escapeHtml(field);
      return `<label for="${safeField}">${escapeHtml(label)}</label><input id="${safeField}" name="${safeField}" value="${escapeHtml(value)}">`;
    }
    ''', ["写一个可复用的 escapeHtml。", "field 转义后同时用于 for、id 和 name。", "使用模板字符串按指定顺序拼接两个元素。"],
    "`for` 与 `id` 使用同一安全字段值建立关联。即使示例字符串不会渲染，属性转义依然是模板生成的基本规则。", "javascript")

add(28, 7, "计算盒模型的外部宽度",
    "默认 content-box 盒模型中，元素总宽度 = 内容宽度 + 左右 padding + 左右 border。左右值相同为 p 和 b 时，公式是 `contentWidth + 2 * (p + b)`。",
    "contentWidth、padding、border 都是非负像素数，且左右两侧相同。返回元素在水平方向占用的总像素数；不考虑 margin。本题用 JavaScript 数值模拟 CSS 盒模型，不渲染页面。",
    [("contentWidth","number","内容宽度"),("padding","number","单侧内边距"),("border","number","单侧边框宽度")],
    [([320,16,1],354),([0,0,0],0),([100,10,0],120),([100,0,2],104),([1,3,4],15)],
    '''
    function solve(contentWidth, padding, border) {
      return contentWidth + 2 * (padding + border);
    }
    ''', ["左右各有一份 padding 和 border。", "先相加单侧的 padding 与 border。", "乘以 2 后再加内容宽度。"],
    "常见的宽度溢出来自只把 CSS `width` 当成最终宽度。题目采用默认 content-box；若设置 `box-sizing: border-box`，含义会不同。", "javascript")

add(28, 8, "根据断点选择布局类",
    "响应式 CSS 常以断点改变布局。这里用传入的 viewportWidth 模拟浏览器视口：小于 768 是 mobile，768—1023 是 tablet，1024 及以上是 desktop。",
    "返回 `layout layout--mobile`、`layout layout--tablet` 或 `layout layout--desktop`。宽度为非负整数；768 和 1024 要落入较大的新断点。本题返回应由页面使用的 class 字符串，不读取真实窗口大小。",
    [("viewportWidth","number","模拟视口宽度（px）")],
    [([767],"layout layout--mobile"),([768],"layout layout--tablet"),([1023],"layout layout--tablet"),([1024],"layout layout--desktop"),([0],"layout layout--mobile")],
    '''
    function solve(viewportWidth) {
      if (viewportWidth < 768) return "layout layout--mobile";
      if (viewportWidth < 1024) return "layout layout--tablet";
      return "layout layout--desktop";
    }
    ''', ["先判断最小的 mobile 上界。", "第二个条件只需要判断 `< 1024`。", "剩下的宽度就是 desktop。"],
    "按升序写半开区间能清晰处理临界值。实际页面可以让 CSS media query 为这些类定义不同布局。", "javascript")

add(28, 9, "生成带状态类的卡片标记",
    "条件表达式 `featured ? A : B` 可根据布尔状态选择类名。结构化卡片通常把标题放在 h2、正文放在 p，并对动态文本做 HTML 转义。",
    "featured 为 true 时类名是 `card card--featured`，否则为 `card`。返回 `<article class=\"类名\"><h2>已转义title</h2><p>已转义text</p></article>`，没有额外空格或换行。Node 只检查返回的 HTML 字符串。",
    [("title","string","卡片标题"),("text","string","卡片正文"),("featured","boolean","是否突出显示")],
    [(["笔记","价格 10 元",False],"<article class=\"card\"><h2>笔记</h2><p>价格 10 元</p></article>"),(["新品","限时",True],"<article class=\"card card--featured\"><h2>新品</h2><p>限时</p></article>"),(["<b>","A & B",True],"<article class=\"card card--featured\"><h2>&lt;b&gt;</h2><p>A &amp; B</p></article>"),(["","",False],"<article class=\"card\"><h2></h2><p></p></article>"),(["\"x\"","it's",False],"<article class=\"card\"><h2>&quot;x&quot;</h2><p>it&#39;s</p></article>")],
    '''
    function solve(title, text, featured) {
      const entities = {"&": "&amp;", "<": "&lt;", ">": "&gt;", "\\\"": "&quot;", "'": "&#39;"};
      const escapeHtml = value => value.replace(/[&<>"']/g, character => entities[character]);
      const className = featured ? "card card--featured" : "card";
      return `<article class="${className}"><h2>${escapeHtml(title)}</h2><p>${escapeHtml(text)}</p></article>`;
    }
    ''', ["先根据 featured 选择 className。", "标题和正文各自调用转义函数。", "按 article、h2、p 的固定嵌套结构拼接。"],
    "状态类只改变卡片的样式钩子，不改变数据文本。把结构、状态和文本分别处理，模板会更容易维护。", "javascript")

add(28, 10, "生成主题 CSS 自定义属性",
    "CSS 自定义属性以 `--` 开头，常在 `:root` 中定义，再通过 `var(--name)` 在其他规则中复用。模板字符串能生成一段固定格式的主题源码。",
    "primary 和 background 是不含分号、花括号的有效 CSS 值。返回 `:root{--color-primary:primary;--color-background:background;}`，没有多余空格。本题返回 CSS 源码字符串，并不实际应用主题。",
    [("primary","string","主色 CSS 值"),("background","string","背景色 CSS 值")],
    [(["#2563eb","#ffffff"],":root{--color-primary:#2563eb;--color-background:#ffffff;}"),(["red","transparent"],":root{--color-primary:red;--color-background:transparent;}"),(["var(--brand)","#f5f5f5"],":root{--color-primary:var(--brand);--color-background:#f5f5f5;}"),(["rgb(1, 2, 3)","rgb(255, 255, 255)"],":root{--color-primary:rgb(1, 2, 3);--color-background:rgb(255, 255, 255);}"),(["currentColor","Canvas"],":root{--color-primary:currentColor;--color-background:Canvas;}")],
    '''
    function solve(primary, background) {
      return `:root{--color-primary:${primary};--color-background:${background};}`;
    }
    ''', ["选择器固定写成 `:root`。", "自定义属性名必须以两个短横线开始。", "在模板字符串中依次插入两个值并保留分号。"],
    "集中定义颜色变量后，其他 CSS 规则可以复用它们。题目限定输入为有效 CSS 值，因此重点是变量声明的结构。", "javascript")


# Chapter 29 models frontend interaction as deterministic JavaScript functions.
# Results are data or source strings checked in Node; no browser DOM is assumed.
add(29, 1, "规范化搜索框文本",
    "输入框常需要先去掉首尾空白，再统一大小写，以便搜索时不把 ` Python ` 和 `python` 当成不同关键词。字符串方法 `.trim()` 和 `.toLowerCase()` 都返回新字符串。",
    "返回 raw 去掉首尾空白并转为小写后的字符串；保留中间空白和非英文字符。本题把 raw 当作事件目标的 value 模拟值，Node.js 只检查函数返回值。",
    [("raw","string","输入框原始文本")],
    [([" Python "],"python"),([""],""),(["  中 文  "],"中 文"),(["ABC\n"],"abc"),([" MiXeD  Case "],"mixed  case")],
    '''
    function solve(raw) {
      return raw.trim().toLowerCase();
    }
    ''', ["先调用 trim 去掉两端空白。", "再对结果调用 toLowerCase。", "不要用 split，否则会错误改变中间空格。"],
    "规范化最好发生在比较或发请求之前，原始输入仍可单独保留给界面展示。链式调用按从左到右的顺序依次得到新字符串。", "javascript")

add(29, 2, "根据 data-action 更新计数器",
    "按钮常以 `data-action` 表示动作，而事件处理函数根据动作更新状态。`switch` 适合多个离散字符串分支，默认分支可保留原状态。",
    "action 可能为 increase、decrease、reset 或其他字符串。increase 加 1，decrease 减 1 但结果不得小于 0，reset 变为 0，其他动作保持 count。返回新的数值；这里模拟点击逻辑，不绑定真实按钮。",
    [("count","number","当前非负整数"),("action","string","按钮的 data-action")],
    [([0,"increase"],1),([3,"decrease"],2),([0,"decrease"],0),([8,"reset"],0),([5,"unknown"],5)],
    '''
    function solve(count, action) {
      switch (action) {
        case "increase": return count + 1;
        case "decrease": return Math.max(0, count - 1);
        case "reset": return 0;
        default: return count;
      }
    }
    ''', ["为每种已知 action 写一个 case。", "减少时用 Math.max 防止负数。", "default 返回原 count。"],
    "界面事件可以把 `event.target.dataset.action` 传给这类纯函数。纯函数不读写 DOM，因此更容易用不同状态单独测试。", "javascript")

add(29, 3, "验证注册表单字段",
    "前端验证需要分别检查每个字段，并按固定顺序汇总错误。`typeof value === 'number'` 和 `Number.isInteger(value)` 可以排除字符串数字与小数。",
    "form 可缺少 name、email、age。name 必须是去空白后非空字符串；email 必须是字符串、恰好包含一个 `@`，且 @ 两侧非空；age 必须是 0—120 的整数。返回错误字段名数组，顺序固定为 name、email、age。",
    [("form","object","表单数据对象")],
    [([{"name":" 小明 ","email":"a@b.com","age":18}],[]),([{}],["name","email","age"]),([{"name":" ","email":"plain","age":-1}],["name","email","age"]),([{"name":"A","email":"@b","age":20.5}],["email","age"]),([{"name":"A","email":"a@b","age":0}],[])],
    '''
    function solve(form) {
      const errors = [];
      const {name, email, age} = form;
      if (typeof name !== "string" || !name.trim()) errors.push("name");
      const at = typeof email === "string" ? email.indexOf("@") : -1;
      if (at <= 0 || at !== email.lastIndexOf("@") || at === email.length - 1) errors.push("email");
      if (typeof age !== "number" || !Number.isInteger(age) || age < 0 || age > 120) errors.push("age");
      return errors;
    }
    ''', ["创建 errors 数组，并按字段顺序依次验证。", "email 用 indexOf 和 lastIndexOf 判断恰好一个 @。", "年龄同时检查类型、整数性和闭区间。"],
    "一次提交时返回全部字段错误，比发现第一个错误就停止更适合表单体验。前端验证提升反馈速度，服务端仍应重复验证所有外部输入。", "javascript")

add(29, 4, "按关键词筛选商品列表",
    "列表筛选可用 `filter`，它返回新数组而不改动原数组。将关键词和名称都 `.trim().toLowerCase()` 后比较，可以实现忽略大小写的包含匹配。",
    "items 中每项至少有 name，可能还有其他字段。用 q 去首尾空白后进行忽略大小写的名称包含筛选，保留原顺序和原对象字段；空 q 匹配所有项。这里返回供前端渲染的数据，不访问浏览器。",
    [("items","object[]","商品列表"),("q","string","搜索关键词")],
    [([[{"id":1,"name":"Python 入门"},{"id":2,"name":"JavaScript"},{"id":3,"name":"python 工具"}]," py "],[{"id":1,"name":"Python 入门"},{"id":3,"name":"python 工具"}]),
     ([[],"a"],[]),
     ([[{"id":1,"name":"A"},{"id":2,"name":"B"}],""],[{"id":1,"name":"A"},{"id":2,"name":"B"}]),
     ([[{"id":1,"name":"Alpha"},{"id":2,"name":"beta"},{"id":3,"name":"Gamma"}],"A"],[{"id":1,"name":"Alpha"},{"id":2,"name":"beta"},{"id":3,"name":"Gamma"}]),
     ([[{"id":1,"name":"中文笔记"},{"id":2,"name":"笔"}],"笔记"],[{"id":1,"name":"中文笔记"}])],
    '''
    function solve(items, q) {
      const keyword = q.trim().toLowerCase();
      return items.filter(item => item.name.toLowerCase().includes(keyword));
    }
    ''', ["先把 q 规范成 keyword。", "filter 的回调对每项 name 做小写包含比较。", "空字符串被任何字符串 includes，因此自然保留全部项。"],
    "filter 不改变 items 的顺序，适合让界面稳定显示搜索结果。题目使用 `toLowerCase` 处理普通大小写示例；复杂语言排序和分词需要更专门的规则。", "javascript")

add(29, 5, "计算购物车数量和分价总额",
    "金额用整数分保存能避免二进制浮点数带来的显示误差。`reduce` 可累积多个字段，例如商品数量和总价。",
    "items 每项有非负整数 unitPrice（分）和 quantity。返回 {quantity:总件数, totalCents:所有 unitPrice × quantity 之和}；空购物车返回两个 0。函数只计算展示用摘要，不修改 items。",
    [("items","object[]","购物车行项目")],
    [([[{"unitPrice":199,"quantity":2},{"unitPrice":50,"quantity":1}]],{"quantity":3,"totalCents":448}),
     ([[]],{"quantity":0,"totalCents":0}),
     ([[{"unitPrice":0,"quantity":5}]],{"quantity":5,"totalCents":0}),
     ([[{"unitPrice":100,"quantity":0},{"unitPrice":250,"quantity":3}]],{"quantity":3,"totalCents":750}),
     ([[{"unitPrice":1,"quantity":1},{"unitPrice":2,"quantity":2},{"unitPrice":3,"quantity":3}]],{"quantity":6,"totalCents":14})],
    '''
    function solve(items) {
      return items.reduce(
        (summary, item) => ({
          quantity: summary.quantity + item.quantity,
          totalCents: summary.totalCents + item.unitPrice * item.quantity
        }),
        {quantity: 0, totalCents: 0}
      );
    }
    ''', ["把初始摘要设为两个 0。", "每一项同时增加 quantity 和 unitPrice × quantity。", "reduce 最终返回累积的摘要对象。"],
    "以分为单位能让所有测试和结算规则使用整数。reduce 的初始值确保空数组不会报错，并直接得到零摘要。", "javascript")

add(29, 6, "切换待办完成状态",
    "前端状态更新通常保持不可变：用 `map` 创建新数组，用对象展开 `{...todo}` 创建新对象。这样旧状态仍可用于比较、撤销或框架渲染判断。",
    "todos 中 id 唯一且 done 为布尔值。targetId 匹配的项将 done 取反，其他字段和其他项保持不变；目标不存在时仍返回内容相同的新列表。不要修改传入的对象或数组。",
    [("todos","object[]","待办列表"),("targetId","number","要切换的编号")],
    [([[{"id":1,"text":"读书","done":False},{"id":2,"text":"练习","done":True}],2],[{"id":1,"text":"读书","done":False},{"id":2,"text":"练习","done":False}]),
     ([[],1],[]),
     ([[{"id":1,"text":"A","done":False}],1],[{"id":1,"text":"A","done":True}]),
     ([[{"id":1,"text":"A","done":True,"tag":"x"},{"id":2,"text":"B","done":False}],9],[{"id":1,"text":"A","done":True,"tag":"x"},{"id":2,"text":"B","done":False}]),
     ([[{"id":0,"text":"零","done":False},{"id":3,"text":"三","done":False}],0],[{"id":0,"text":"零","done":True},{"id":3,"text":"三","done":False}])],
    '''
    function solve(todos, targetId) {
      return todos.map(todo =>
        todo.id === targetId ? {...todo, done: !todo.done} : {...todo}
      );
    }
    ''', ["用 map 遍历每一条待办。", "编号匹配时通过对象展开保留字段，再覆盖 done。", "未匹配项也复制为新对象，避免返回原对象引用。"],
    "对象展开中后写的 `done` 会覆盖原值。此函数可以直接作为点击复选框后的状态更新器，而不会就地改写先前状态。", "javascript")

add(29, 7, "在客户端切分分页结果",
    "页码从 1 开始时，当前页起点为 `(page - 1) * size`。数组 `slice(start, end)` 超出长度时返回可用部分或空数组，不会抛错。",
    "page 和 size 都是正整数。返回 {items:当前页切片, total:原数组长度, pages:向上取整后的页数}；空数组 pages 为 0，超出最后一页时 items 为 []。这是前端展示逻辑，不发 API 请求。",
    [("items","JSON[]","有序数据"),("page","number","从 1 开始的页码"),("size","number","每页条数")],
    [([[1,2,3,4,5],2,2],{"items":[3,4],"total":5,"pages":3}),([[],1,3],{"items":[],"total":0,"pages":0}),
     ([[1],3,2],{"items":[],"total":1,"pages":1}),([[1,2,3,4],2,2],{"items":[3,4],"total":4,"pages":2}),
     ([["a","b"],1,10],{"items":["a","b"],"total":2,"pages":1})],
    '''
    function solve(items, page, size) {
      const start = (page - 1) * size;
      return {items: items.slice(start, start + size), total: items.length, pages: Math.ceil(items.length / size)};
    }
    ''', ["先计算从 0 开始的 start。", "slice 的结束位置是 start + size。", "用 Math.ceil 计算总页数。"],
    "客户端分页适合数据已经在内存中的场景。数据量大时通常把 page 和 size 发送给服务端，但同样的页码公式仍然适用。", "javascript")

add(29, 8, "把筛选状态同步到 URL 查询串",
    "可分享的筛选状态常放在 URL 查询参数中。`URLSearchParams` 会完成 URL 编码；空格编码为 `+`，特殊字符不会破坏参数结构。",
    "先对 query 去首尾空白。非空 query 按 q 加入，page 不等于 1 时按 page 加入，顺序固定为 q、page。无参数时返回空字符串，否则返回以 `?` 开头的查询串。这里返回 URL 的一部分，不调用浏览器 history。",
    [("query","string","搜索文本"),("page","number","当前页码")],
    [(["Python",1],"?q=Python"),([" A & B ",3],"?q=A+%26+B&page=3"),(["",1],""),(["",2],"?page=2"),(["中文",1],"?q=%E4%B8%AD%E6%96%87")],
    '''
    function solve(query, page) {
      const params = new URLSearchParams();
      const text = query.trim();
      if (text) params.set("q", text);
      if (page !== 1) params.set("page", String(page));
      const encoded = params.toString();
      return encoded ? `?${encoded}` : "";
    }
    ''', ["新建 URLSearchParams，再取得 trim 后的文本。", "按题目顺序用 set 加入 q 和 page。", "toString 非空时再添加前导问号。"],
    "只省略默认页 1，可让 `/items` 表示默认列表。URLSearchParams 负责编码，避免手工拼接 `&` 时遗漏转义。", "javascript")

add(29, 9, "生成无障碍提示消息",
    "动态提示可用 `role=\"status\"` 让辅助技术感知内容变化。消息文本来自数据时仍应做 HTML 转义；状态类让 CSS 根据 kind 着色。",
    "kind 是 success、error 或 info 之一。返回 `<div class=\"toast toast--kind\" role=\"status\">已转义message</div>`，无额外空格或换行。Node.js 比较源码字符串，不创建或更新页面元素。",
    [("message","string","提示文本"),("kind","string","提示类型")],
    [(["已保存","success"],"<div class=\"toast toast--success\" role=\"status\">已保存</div>"),(["网络错误","error"],"<div class=\"toast toast--error\" role=\"status\">网络错误</div>"),(["A & B","info"],"<div class=\"toast toast--info\" role=\"status\">A &amp; B</div>"),(["<重试>","error"],"<div class=\"toast toast--error\" role=\"status\">&lt;重试&gt;</div>"),(["\"ok\"","success"],"<div class=\"toast toast--success\" role=\"status\">&quot;ok&quot;</div>")],
    '''
    function solve(message, kind) {
      const entities = {"&": "&amp;", "<": "&lt;", ">": "&gt;", "\\\"": "&quot;", "'": "&#39;"};
      const escaped = message.replace(/[&<>"']/g, character => entities[character]);
      return `<div class="toast toast--${kind}" role="status">${escaped}</div>`;
    }
    ''', ["先定义特殊字符到实体的映射。", "用 replace 得到 escaped message。", "把 kind 放入类名，把 escaped 放入 div 内容。"],
    "提示类型是受控状态，因此可直接用于 class 名；消息则是文本数据，需要转义。把可访问性角色放在固定模板中，调用处不会遗忘。", "javascript")

add(29, 10, "序列化本地保存的偏好",
    "浏览器 localStorage 只能保存字符串，通常用 `JSON.stringify` 写入、`JSON.parse` 读回。空值合并运算符 `??` 只在值为 null 或 undefined 时使用默认值，不会误覆盖 0。",
    "settings 可缺少 theme、pageSize 或将它们设为 null。返回紧凑 JSON 字符串，键顺序固定为 theme、pageSize；theme 默认 `light`，pageSize 默认 10，但 0 必须保留。本题只生成将要保存的字符串，不访问 localStorage。",
    [("settings","object","偏好对象")],
    [([{"theme":"dark","pageSize":20}],'{"theme":"dark","pageSize":20}'),([{}],'{"theme":"light","pageSize":10}'),([{"theme":"system"}],'{"theme":"system","pageSize":10}'),([{"pageSize":0}],'{"theme":"light","pageSize":0}'),([{"theme":None,"pageSize":None}],'{"theme":"light","pageSize":10}')],
    '''
    function solve(settings) {
      return JSON.stringify({
        theme: settings.theme ?? "light",
        pageSize: settings.pageSize ?? 10
      });
    }
    ''', ["构造一个新对象以固定输出键顺序。", "theme 和 pageSize 分别使用 `??` 设置默认值。", "对该新对象调用 JSON.stringify。"],
    "新对象避免把未定义或多余字段写入保存内容。`??` 与 `||` 的区别在于它会保留合法的 0 页大小。", "javascript")


# Chapter 30 combines the contracts used by database queries, Python services,
# and JavaScript clients.  SQL fixtures remain in-memory and JavaScript still
# returns deterministic data or source strings in Node.
PRODUCTS_API_SCHEMA = "CREATE TABLE products(id INTEGER PRIMARY KEY, name TEXT, price_cents INTEGER, stock INTEGER);"
SALES_API_SCHEMA = "CREATE TABLE products(id INTEGER PRIMARY KEY, category TEXT);\nCREATE TABLE order_lines(id INTEGER PRIMARY KEY, product_id INTEGER, quantity INTEGER);"
DASHBOARD_SCHEMA = "CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT);\nCREATE TABLE orders(id INTEGER PRIMARY KEY, user_id INTEGER, total_cents INTEGER);"

add(30, 1, "为商品 API 查询可售列表",
    "一个商品列表接口通常只暴露可购买的商品。SQL 的 `WHERE stock > 0` 在排序前过滤无库存行，`ORDER BY price_cents ASC, id ASC` 让客户端获得稳定顺序。",
    "返回可售商品的 [id, name, price_cents]。stock 为 0 的商品不返回；先按价格分（升序）排序，同价按 id 升序。输入对象中的 products 行依次为 id、name、price_cents、stock。",
    DB,
    [([{"products":[[1,"笔",199,4],[2,"笔记本",1599,0],[3,"贴纸",99,9],[4,"书",199,1]]}],[[3,"贴纸",99],[1,"笔",199],[4,"书",199]]),
     ([{"products":[]}],[]),([{"products":[[1,"A",100,0]]}],[]),
     ([{"products":[[2,"B",10,1],[1,"A",10,2]]}],[[1,"A",10],[2,"B",10]]),
     ([{"products":[[7,"免费",0,1],[8,"缺货",0,0],[9,"贵",500,3]]}],[[7,"免费",0],[9,"贵",500]])],
    "SELECT id, name, price_cents FROM products WHERE stock > 0 ORDER BY price_cents ASC, id ASC;",
    ["先在 WHERE 中排除 stock 为 0 的行。", "SELECT 只列出接口要返回的三个字段。", "价格排序后补充 id 作为同价的稳定排序键。"],
    "数据库按金额分保存价格，避免浮点金额误差。服务层可把这个有序结果编码为 JSON，前端就不必猜测商品排列方式。", "sql", PRODUCTS_API_SCHEMA)

add(30, 2, "统计分类销量供图表接口使用",
    "图表接口往往需要先把订单行连接到商品分类。`LEFT JOIN` 保留没有销量的商品，`COALESCE(SUM(...), 0)` 把没有可求和行时的 NULL 转成 0。",
    "返回每个已存在商品分类的 [category, units]，units 是该分类所有订单行 quantity 的和。包含零销量分类；孤立 order_lines（找不到商品）忽略。按 units 降序、category 升序。products 行为 id、category；order_lines 行为 id、product_id、quantity。",
    DB,
    [([{"products":[[1,"book"],[2,"pen"],[3,"book"]],"order_lines":[[1,1,2],[2,2,5],[3,3,1]]}],[["pen",5],["book",3]]),
     ([{"products":[],"order_lines":[]}],[]),([{"products":[[1,"a"],[2,"b"]],"order_lines":[]}],[["a",0],["b",0]]),
     ([{"products":[[1,"a"],[2,"a"],[3,"z"]],"order_lines":[[1,1,2],[2,2,3],[3,3,4]]}],[["a",5],["z",4]]),
     ([{"products":[[1,"x"]],"order_lines":[[1,9,99],[2,1,0]]}],[["x",0]])],
    "SELECT p.category, COALESCE(SUM(o.quantity), 0) AS units\nFROM products AS p LEFT JOIN order_lines AS o ON o.product_id = p.id\nGROUP BY p.category\nORDER BY units DESC, p.category ASC;",
    ["从 products 开始做 LEFT JOIN，才能保留零销量分类。", "按 p.category 分组并对 quantity 求和。", "用 COALESCE 处理完全没有匹配订单行的分组。"],
    "同一分类的多件商品会在 GROUP BY 后汇总成一行。先左连接再聚合使分类维度来自商品表，订单表中的无效外键不会凭空生成分类。", "sql", SALES_API_SCHEMA)

add(30, 3, "实现商品列表服务的查询参数",
    "完整接口会把 URL 查询参数转成服务层输入，再返回统一的状态码和 JSON 数据。缺省参数可使用默认值，但类型和范围要在使用前验证。",
    "query 可含 q 和 limit，额外键忽略。q 缺省时为 `''`，但存在时必须是字符串；limit 缺省为 20，且必须是 0—100 的 int（bool 不算 int）。先验证 q，再验证 limit；失败分别返回 {status:400,body:{error:'invalid_q'}} 或 invalid_limit。成功时用 q 去首尾空白、忽略大小写筛选 items 的 name，并返回 {status:200,body:{items:至多limit项,total:筛选前数量}}。",
    [("items","list[dict]","商品数据，每项至少有 name"),("query","dict","解析后的查询参数")],
    [([[{"id":1,"name":"Python 入门"},{"id":2,"name":"JavaScript"},{"id":3,"name":"python 工具"}],{"q":" py ","limit":1}],{"status":200,"body":{"items":[{"id":1,"name":"Python 入门"}],"total":2}}),
     ([[],{}],{"status":200,"body":{"items":[],"total":0}}),
     ([[{"id":1,"name":"A"}],{"q":4,"limit":1}],{"status":400,"body":{"error":"invalid_q"}}),
     ([[],{"limit":True}],{"status":400,"body":{"error":"invalid_limit"}}),
     ([[{"id":1,"name":"A"},{"id":2,"name":"B"}],{"q":"","limit":0}],{"status":200,"body":{"items":[],"total":2}}),
     ([[{"id":1,"name":"Alpha"},{"id":2,"name":"beta"}],{"q":"A"}],{"status":200,"body":{"items":[{"id":1,"name":"Alpha"},{"id":2,"name":"beta"}],"total":2}})],
    '''
    def solve(items, query):
        q = query.get("q", "")
        limit = query.get("limit", 20)
        if not isinstance(q, str):
            return {"status": 400, "body": {"error": "invalid_q"}}
        if type(limit) is not int or not 0 <= limit <= 100:
            return {"status": 400, "body": {"error": "invalid_limit"}}
        term = q.strip().casefold()
        selected = [item for item in items if term in item["name"].casefold()]
        return {"status": 200, "body": {"items": selected[:limit], "total": len(selected)}}
    ''', ["从 query.get 读取 q 和 limit 的默认值。", "先检查 q 类型，再用 type(limit) is int 排除 bool。", "筛选后先保存全部 selected 的长度，再对列表切片。"],
    "API 的 `total` 描述筛选命中的数量，不是本页数组长度。把解析、验证、筛选和响应模型集中在函数中，HTTP 处理器只需负责读取请求和写回 JSON。")

add(30, 4, "把数据库商品行转换为 API DTO",
    "数据库字段通常使用 snake_case，而 JSON API 可按客户端约定使用 camelCase。DTO（数据传输对象）只暴露接口需要的字段，避免把数据库内部列直接泄露给页面。",
    "row 包含 id、name、price_cents、stock，也可能含其他内部字段。返回 {id, name, priceCents, inStock}；inStock 在 stock 大于 0 时为 true。不要修改 row，也不要返回任何额外字段。",
    [("row","dict","一行数据库商品数据")],
    [([{"id":1,"name":"笔","price_cents":199,"stock":2}],{"id":1,"name":"笔","priceCents":199,"inStock":True}),
     ([{"id":2,"name":"本","price_cents":1599,"stock":0}],{"id":2,"name":"本","priceCents":1599,"inStock":False}),
     ([{"id":0,"name":"免费","price_cents":0,"stock":1,"supplier_cost":0}],{"id":0,"name":"免费","priceCents":0,"inStock":True}),
     ([{"id":3,"name":"退货","price_cents":50,"stock":0,"hidden":True}],{"id":3,"name":"退货","priceCents":50,"inStock":False}),
     ([{"id":9,"name":"最后","price_cents":1,"stock":100,"notes":"内部"}],{"id":9,"name":"最后","priceCents":1,"inStock":True})],
    '''
    def solve(row):
        return {"id": row["id"], "name": row["name"],
                "priceCents": row["price_cents"], "inStock": row["stock"] > 0}
    ''', ["只从 row 读取题目指定的四类信息。", "price_cents 映射到新的 priceCents 键。", "用 `row['stock'] > 0` 计算布尔的 inStock。"],
    "DTO 建立了明确的数据边界：数据库添加供应商成本等列后，客户端响应也不会意外变化。金额仍以整数分传输，客户端可以再格式化显示。")

add(30, 5, "实现不修改原数据的下单预览服务",
    "一次结算需要把客户端购物车与服务端库存和价格核对。先验证数量，再检查商品存在和库存，最后才计算结果，能给客户端返回准确的 HTTP 风格错误。",
    "products 中 id 唯一，每项有 price_cents、stock；cart 是 id 唯一的 [product_id, quantity] 列表。cart 为空返回 400/empty_cart。先检查所有 quantity 必须是正 int 且不是 bool，失败返回 400/invalid_quantity；再按 cart 顺序检查商品，不存在返回 404/{error:'product_not_found',id:编号}，库存不足返回 409/{error:'insufficient_stock',id:编号}。成功返回 {status:201,body:{totalCents:总分价,remainingStock:[[购物车顺序的id,扣减后库存],...]}}。不得修改 products。",
    [("products","list[dict]","服务端商品和库存"),("cart","list[list[int]]","客户端购物车行")],
    [([[{"id":1,"price_cents":100,"stock":3},{"id":2,"price_cents":250,"stock":2}],[[2,1],[1,2]]],{"status":201,"body":{"totalCents":450,"remainingStock":[[2,1],[1,1]]}}),
     ([[{"id":1,"price_cents":100,"stock":1}],[]],{"status":400,"body":{"error":"empty_cart"}}),
     ([[{"id":1,"price_cents":100,"stock":1}],[[1,True]]],{"status":400,"body":{"error":"invalid_quantity"}}),
     ([[{"id":1,"price_cents":100,"stock":1}],[[9,1]]],{"status":404,"body":{"error":"product_not_found","id":9}}),
     ([[{"id":1,"price_cents":100,"stock":1}],[[1,2]]],{"status":409,"body":{"error":"insufficient_stock","id":1}}),
     ([[{"id":1,"price_cents":99,"stock":1}],[[1,1]]],{"status":201,"body":{"totalCents":99,"remainingStock":[[1,0]]}})],
    '''
    def solve(products, cart):
        if not cart:
            return {"status": 400, "body": {"error": "empty_cart"}}
        for _, quantity in cart:
            if type(quantity) is not int or quantity <= 0:
                return {"status": 400, "body": {"error": "invalid_quantity"}}
        by_id = {product["id"]: product for product in products}
        for product_id, _ in cart:
            if product_id not in by_id:
                return {"status": 404, "body": {"error": "product_not_found", "id": product_id}}
        for product_id, quantity in cart:
            if by_id[product_id]["stock"] < quantity:
                return {"status": 409, "body": {"error": "insufficient_stock", "id": product_id}}
        total = sum(by_id[product_id]["price_cents"] * quantity for product_id, quantity in cart)
        remaining = [[product_id, by_id[product_id]["stock"] - quantity] for product_id, quantity in cart]
        return {"status": 201, "body": {"totalCents": total, "remainingStock": remaining}}
    ''', ["先单独处理空购物车和不合法数量。", "用 id 到商品的字典快速做存在和库存检查。", "全部检查通过后再用 sum 和列表推导构造成功响应。"],
    "此函数是预览：它计算扣减后的库存，却不写回 products。真实下单还需要在数据库事务中重新核对库存并持久化，避免并发请求同时卖出最后一件商品。")

add(30, 6, "把商品 API DTO 转为前端视图模型",
    "服务端 DTO 适合传输，前端视图模型则可准备好显示文本和交互状态。分价除以 100 后用 `.toFixed(2)` 能稳定显示两位小数。",
    "body 的 items 是第 30.4 题形状的 {id,name,priceCents,inStock} 数组。返回 {count:项目数, products:[{id,title,priceText,available}, ...]}，其中 title 取 name，priceText 形如 `¥1.99`，available 取 inStock。保留原顺序；本题仅返回数据，不更新 DOM。",
    [("body","object","商品列表 API 响应体")],
    [([{"items":[{"id":1,"name":"笔","priceCents":199,"inStock":True},{"id":2,"name":"本","priceCents":50,"inStock":False}]}],{"count":2,"products":[{"id":1,"title":"笔","priceText":"¥1.99","available":True},{"id":2,"title":"本","priceText":"¥0.50","available":False}]}),
     ([{"items":[]}],{"count":0,"products":[]}),
     ([{"items":[{"id":0,"name":"免费","priceCents":0,"inStock":True}]}],{"count":1,"products":[{"id":0,"title":"免费","priceText":"¥0.00","available":True}]}),
     ([{"items":[{"id":3,"name":"小数","priceCents":5,"inStock":False}]}],{"count":1,"products":[{"id":3,"title":"小数","priceText":"¥0.05","available":False}]}),
     ([{"items":[{"id":9,"name":"大额","priceCents":123456,"inStock":True}]}],{"count":1,"products":[{"id":9,"title":"大额","priceText":"¥1234.56","available":True}]})],
    '''
    function solve(body) {
      const products = body.items.map(item => ({
        id: item.id,
        title: item.name,
        priceText: `¥${(item.priceCents / 100).toFixed(2)}`,
        available: item.inStock
      }));
      return {count: products.length, products};
    }
    ''', ["用 map 把每个 API DTO 转成新对象。", "金额先除以 100，再调用 toFixed(2)。", "保存 products 后用其 length 填入 count。"],
    "传输字段 priceCents 保持精确整数，显示字段 priceText 才带货币符号和小数点。这样的分层让服务端和视图各自承担清晰职责。", "javascript")

add(30, 7, "渲染商品视图模型为安全卡片字符串",
    "前端拿到视图模型后，可用 `map` 生成重复卡片结构。动态文字必须 HTML 转义；可售状态决定按钮文本与是否添加 `disabled` 属性。",
    "products 是第 30.6 题输出的 products 数组。返回 `<section class=\"products\">...</section>`；每项按输入顺序生成 `<article class=\"product\" data-id=\"id\"><h2>标题</h2><p>价格</p>按钮</article>`。available 为 true 的按钮是 `<button type=\"button\">加入购物车</button>`，否则是 `<button type=\"button\" disabled>缺货</button>`。转义 title 和 priceText；本题比较 Node 返回的 HTML 源码，不渲染页面。",
    [("products","object[]","前端商品视图模型")],
    [([[{"id":1,"title":"笔","priceText":"¥1.99","available":True},{"id":2,"title":"本","priceText":"¥0.50","available":False}]],"<section class=\"products\"><article class=\"product\" data-id=\"1\"><h2>笔</h2><p>¥1.99</p><button type=\"button\">加入购物车</button></article><article class=\"product\" data-id=\"2\"><h2>本</h2><p>¥0.50</p><button type=\"button\" disabled>缺货</button></article></section>"),
     ([[]],"<section class=\"products\"></section>"),
     ([[{"id":0,"title":"<新>","priceText":"¥0.00","available":True}]],"<section class=\"products\"><article class=\"product\" data-id=\"0\"><h2>&lt;新&gt;</h2><p>¥0.00</p><button type=\"button\">加入购物车</button></article></section>"),
     ([[{"id":3,"title":"A & B","priceText":"\"5\"","available":False}]],"<section class=\"products\"><article class=\"product\" data-id=\"3\"><h2>A &amp; B</h2><p>&quot;5&quot;</p><button type=\"button\" disabled>缺货</button></article></section>"),
     ([[{"id":9,"title":"it's","priceText":"¥1.00","available":True}]],"<section class=\"products\"><article class=\"product\" data-id=\"9\"><h2>it&#39;s</h2><p>¥1.00</p><button type=\"button\">加入购物车</button></article></section>")],
    '''
    function solve(products) {
      const entities = {"&": "&amp;", "<": "&lt;", ">": "&gt;", "\\\"": "&quot;", "'": "&#39;"};
      const escapeHtml = value => value.replace(/[&<>"']/g, character => entities[character]);
      const cards = products.map(product => {
        const button = product.available
          ? '<button type="button">加入购物车</button>'
          : '<button type="button" disabled>缺货</button>';
        return `<article class="product" data-id="${product.id}"><h2>${escapeHtml(product.title)}</h2><p>${escapeHtml(product.priceText)}</p>${button}</article>`;
      }).join("");
      return `<section class="products">${cards}</section>`;
    }
    ''', ["定义 escapeHtml，并用 map 逐项生成卡片。", "用条件表达式选择两种固定按钮字符串。", "把 cards join 后包进 section。"],
    "按钮属性由受控的布尔状态决定，标题和价格则按文本转义。把渲染函数保持为纯字符串函数，便于先验证结构，再接入真实 DOM。", "javascript")

add(30, 8, "构造带分页链接的 API 响应",
    "分页接口除了当前页数据，还可返回 total、pages 和 self/prev/next 链接，客户端无需自己猜测下一页地址。`urlencode` 负责统一构造查询参数。",
    "page、size 均为正整数，basePath 不含查询串。返回 {status:200,body:{items:当前切片,pagination:{page,size,total,pages},links:{self,prev,next}}}。链接查询参数顺序固定为 page、size；prev 仅在 page 大于 1 时有值，next 仅在 page 小于 pages 时有值，其余为 null。空列表 pages 为 0。",
    [("items","list[JSON]","所有可分页数据"),("page","int","从 1 开始的页码"),("size","int","每页数量"),("basePath","str","接口路径")],
    [([[1,2,3,4,5],2,2,"/api/items"],{"status":200,"body":{"items":[3,4],"pagination":{"page":2,"size":2,"total":5,"pages":3},"links":{"self":"/api/items?page=2&size=2","prev":"/api/items?page=1&size=2","next":"/api/items?page=3&size=2"}}}),
     ([[],1,3,"/api/items"],{"status":200,"body":{"items":[],"pagination":{"page":1,"size":3,"total":0,"pages":0},"links":{"self":"/api/items?page=1&size=3","prev":None,"next":None}}}),
     ([[1],1,2,"/v1/products"],{"status":200,"body":{"items":[1],"pagination":{"page":1,"size":2,"total":1,"pages":1},"links":{"self":"/v1/products?page=1&size=2","prev":None,"next":None}}}),
     ([[1,2,3,4],2,2,"/x"],{"status":200,"body":{"items":[3,4],"pagination":{"page":2,"size":2,"total":4,"pages":2},"links":{"self":"/x?page=2&size=2","prev":"/x?page=1&size=2","next":None}}}),
     ([["a","b"],1,10,"/search"],{"status":200,"body":{"items":["a","b"],"pagination":{"page":1,"size":10,"total":2,"pages":1},"links":{"self":"/search?page=1&size=10","prev":None,"next":None}}})],
    '''
    from urllib.parse import urlencode

    def solve(items, page, size, basePath):
        total = len(items)
        pages = (total + size - 1) // size
        start = (page - 1) * size

        def link(number):
            return basePath + "?" + urlencode([("page", number), ("size", size)])

        return {"status": 200,
                "body": {"items": items[start:start + size],
                         "pagination": {"page": page, "size": size, "total": total, "pages": pages},
                         "links": {"self": link(page), "prev": link(page - 1) if page > 1 else None,
                                   "next": link(page + 1) if page < pages else None}}}
    ''', ["先计算 total、pages 和当前页切片起点。", "定义 link 辅助函数，按 page、size 顺序 urlencode。", "根据 page 与 pages 条件填入 prev 和 next 或 None。"],
    "响应把数据、分页元数据和导航链接一起交给客户端。即使没有数据，self 链接仍描述本次请求，而 prev、next 明确表示没有可导航页面。")

add(30, 9, "查询用户订单仪表盘数据",
    "用户仪表盘需要把用户维度与订单事实表连接。`LEFT JOIN` 加 `COUNT(o.id)` 能给零订单用户返回 0；`COALESCE(SUM(...), 0)` 处理金额和。",
    "返回每位用户的 [id, name, order_count, total_cents]，包括零订单用户。孤立订单忽略；按 total_cents 降序、id 升序。users 行是 id、name；orders 行是 id、user_id、total_cents。",
    DB,
    [([{"users":[[2,"B"],[1,"A"],[3,"C"]],"orders":[[1,1,100],[2,1,50],[3,2,250]]}],[[2,"B",1,250],[1,"A",2,150],[3,"C",0,0]]),
     ([{"users":[],"orders":[[1,9,5]]}],[]),([{"users":[[1,"A"]],"orders":[]}],[[1,"A",0,0]]),
     ([{"users":[[1,"A"],[2,"B"]],"orders":[[1,9,99],[2,2,0]]}],[[1,"A",0,0],[2,"B",1,0]]),
     ([{"users":[[3,"C"],[1,"A"]],"orders":[[1,3,-5],[2,1,10]]}],[[1,"A",1,10],[3,"C",1,-5]])],
    "SELECT u.id, u.name, COUNT(o.id) AS order_count, COALESCE(SUM(o.total_cents), 0) AS total\nFROM users AS u LEFT JOIN orders AS o ON o.user_id = u.id\nGROUP BY u.id, u.name\nORDER BY total DESC, u.id ASC;",
    ["以 users 为左表，使用 LEFT JOIN orders。", "同时计算 COUNT(o.id) 和 COALESCE(SUM(...), 0)。", "按金额别名 total 降序，再按 u.id 升序。"],
    "这类聚合结果可以直接作为管理端图表或表格的 API 数据。计数使用 o.id 而不是 COUNT(*)，避免把左连接补出的空行误计为一笔订单。", "sql", DASHBOARD_SCHEMA)

add(30, 10, "把 API 状态映射为客户端提示状态",
    "客户端收到响应后不应只显示原始状态码，而应转换为稳定的界面状态和用户可理解的消息。2xx 是成功；409 和 5xx 通常值得提示重试。",
    "response 至少有 status。返回 {state:'success'|'error', message:固定中文提示, retryable:布尔值}：2xx 为 success/操作成功/false；400 为 请求数据有误/false；404 为 资源不存在/false；409 为 当前状态冲突，请刷新后重试/true；500—599 为 服务暂时不可用，请稍后重试/true；其他状态为 请求失败/false。函数只生成前端状态数据，不显示 DOM。",
    [("response","object","API 响应对象")],
    [([{"status":201,"body":{"id":1}}],{"state":"success","message":"操作成功","retryable":False}),
     ([{"status":400,"body":{"error":"invalid_quantity"}}],{"state":"error","message":"请求数据有误","retryable":False}),
     ([{"status":404}],{"state":"error","message":"资源不存在","retryable":False}),
     ([{"status":409}],{"state":"error","message":"当前状态冲突，请刷新后重试","retryable":True}),
     ([{"status":503}],{"state":"error","message":"服务暂时不可用，请稍后重试","retryable":True}),
     ([{"status":418}],{"state":"error","message":"请求失败","retryable":False})],
    '''
    function solve(response) {
      const {status} = response;
      if (status >= 200 && status < 300) return {state: "success", message: "操作成功", retryable: false};
      if (status === 400) return {state: "error", message: "请求数据有误", retryable: false};
      if (status === 404) return {state: "error", message: "资源不存在", retryable: false};
      if (status === 409) return {state: "error", message: "当前状态冲突，请刷新后重试", retryable: true};
      if (status >= 500 && status < 600) return {state: "error", message: "服务暂时不可用，请稍后重试", retryable: true};
      return {state: "error", message: "请求失败", retryable: false};
    }
    ''', ["先用 2xx 范围处理所有成功响应。", "为 400、404、409 分别返回固定对象。", "最后用 5xx 范围和默认分支覆盖剩余状态。"],
    "把响应解释集中在一个函数，组件只需根据 state、message 和 retryable 渲染。重试提示只出现在可能因暂时性服务或状态冲突而恢复的情形。", "javascript")
