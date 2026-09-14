# PyStep implementation contract

Local Python learning app, Chinese, 300 exercises / 30 chapters / 10 per chapter. Standard library HTTP server + vanilla HTML/CSS/JS. No CDN required. Bind 127.0.0.1 only. Python 3.10+.

## Expanded scope (latest user request)
Add curriculum/algorithms.py (chapters 19–24, advanced curriculum agent) and curriculum/web.py (chapters 25–30, root). Dynamic totals everywhere. Chapters 19–24: 机考输入输出与复杂度; 排序与二分查找; 栈、队列与链表; 树、堆与并查集; 图与搜索; 递归、贪心与动态规划. Chapters 25–30: SQL 查询与关系数据库; Python 后端基础; HTTP 与服务器 API; HTML 与 CSS 页面基础; JavaScript 与前端交互; 全栈综合练习.

Problem language defaults to python; can be sql/javascript. SQL setup_sql is trusted CREATE TABLE script; each case args is [{table_name:[row arrays]}], student writes actual SELECT/WITH query, judge returns list of result rows. JavaScript starter defines solve and runs in local Node.js; await async solve allowed. Frontend HTML/CSS exercises use JavaScript solve returning exact HTML/CSS strings, with explicit formatting rules and illustrative syntax lessons; no browser DOM assumed in Node. Requirement `node` available in meta. Never pretend string exercises are full browser rendering checks. API demo endpoints: GET /api/demo/items?q=&limit=, GET /api/demo/items/<id>, POST /api/demo/echo. Real browser frontend itself calls backend via fetch. Additional language code execution remains local trusted-code only.

## Curriculum
`curriculum/beginner.py` exports `PROBLEMS` chapters 1–9, root agent owns it.
`curriculum/advanced.py` exports `PROBLEMS` chapters 10–18, curriculum agent owns it.
`curriculum/schema.py` supplies `problem(chapter, number, title, concept, description, parameters, tests, solution, hints, explanation, difficulty='入门', requires=None, starter=None)`.
Each parameter is `(name, type_text, description)`. Each test is `(args_list, expected)`; use first 2 tests as visible examples and at least 5 tests per exercise. Helper builds integer id `(chapter-1)*10+number`, chapter info, tags, `starter` with `def solve(params):`, `tests=[{args, expected}]`, `examples=tests[:2]`. Solution is Python code defining `solve` with those same parameters. All input / expected values JSON serializable. Tests deterministic. Avoid mutable shared globals and test file system side effects. Advanced modules return ordinary JSON compatible Python values. Dependencies are package import names (`numpy`, `pandas`, `matplotlib`, `sklearn`).

Problem keys: id, chapter, chapter_title, title, concept (mini syntax lesson, multiline Markdown text), description (task with precise edge-case rules), parameters (array {name,type,description}), difficulty, tags (chapter name + dependency names), requires, starter, tests, examples, hints (3 progressive Chinese strings), solution (complete code), explanation (Chinese solution walkthrough).

Chapters: 1 值、变量与运算; 2 条件判断; 3 循环与累积; 4 字符串; 5 列表与元组; 6 字典与集合; 7 函数与参数; 8 推导式与迭代器; 9 异常、文件与数据格式; 10 类、模块与类型提示; 11 collections、itertools 与 functools; 12 数学、时间与随机数; 13 正则、路径与数据库; 14 NumPy 数组基础; 15 NumPy 计算与线性代数; 16 pandas 表格基础; 17 pandas 数据分析; 18 可视化与机器学习入门.

## HTTP API
GET `/api/problems`: `{problems:[all problem fields except tests,solution,explanation,hints,concept,starter],chapters:[{id,title,count}],total:180}` (parameters/examples can remain).
GET `/api/problems/<int>`: all fields except `tests` (has hints, solution, explanation).
GET `/api/meta`: `{python,dependencies:{numpy:{available,version},pandas:...,matplotlib:...,sklearn:...},execution_timeout:12}`.
POST `/api/run`: `{problem_id:int, code:string, mode:'run'|'submit', custom_args?:array}`. Run checks 2 public examples (or one custom args if provided); submit checks all tests. Custom expected unknown: passed true if no exception and label '执行成功', not submission success.
Response `{status:'accepted'|'wrong_answer'|'syntax_error'|'runtime_error'|'timeout'|'missing_dependency'|'error',passed:int,total:int,cases:[{passed,args,expected,actual,stdout,error?}],error?:{type,message,line,hint,traceback},duration_ms:number,mode}`. Case custom may have expected null + custom true. Top-level `error` object or null. HTTP 400 invalid body, 404 invalid problem, 429 busy. Limit output/body/code and wall-clock; show helpful Chinese error hints and user-code line numbers. Do not advertise as sandbox.

Frontend localStorage tracks drafts by problem id, accepted ids, attempts, notes, starred, theme. Curriculum browsing, chapter filter/search/difficulty/status, roadmap/dashboard, detail lessons, hints/answers, code editing with line numbers/tab indentation/Ctrl+Enter, run/submit/results, reset code, custom JSON argument array input, progress export/import, keyboard navigation, responsive and accessible. Keep all UI Chinese.

## Ownership
Frontend agent: `static/` only. Backend agent: `server.py`, `runner.py`, `verify.py`, `tests/` only. Curriculum agent: `curriculum/advanced.py` only. Root: schema, beginner, docs, start scripts, integration fixes.
