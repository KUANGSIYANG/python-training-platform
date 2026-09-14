# PyStep：从 Python 入门到复试机考与全栈基础

一个面向刚会 `if / else` 的 AI 本科生的中文本地练习平台。共 **300 道题、30 章**，每题提供语法小课、输入说明、两个公开示例、三个逐步提示、完整参考答案、解题说明，以及至少五个自动测试。

## 最快开始

Windows 下双击 **`启动学习平台.bat`**。它会启动本地服务并打开浏览器。学习期间保持服务窗口运行；关闭服务窗口即可停止。

也可以在本目录打开终端运行：

```powershell
python -X utf8 server.py
```

然后打开 <http://127.0.0.1:8765>。如果端口被占用，运行 `python -X utf8 server.py --port 8766`，再打开对应地址。

基础 Python、SQL、算法和 Python 后端练习只需要 Python 3.10 或更高版本。SQL 使用 Python 自带的 SQLite，不必额外安装数据库服务器。JavaScript 练习需要 Node.js 18 或更高版本；科学计算章节需要 NumPy、pandas、Matplotlib、scikit-learn。当前开发电脑已具备这些依赖。其他电脑可运行：

```powershell
python -m pip install -r requirements.txt
```

界面会显示依赖检测结果。页面本身不依赖 CDN、账号或外部服务；真实 HTTP 练习使用本机临时测试服务器，无需互联网。安装依赖时需要联网。

## VS Code 风格练习工作台

打开任意题目后，页面会进入深色工作台：左边是活动栏和题目说明，中间是带行号、文件标签和语言标记的编辑器，底部有“问题 / 输出 / 终端 / 测试”面板。它们显示的都是本次真实运行结果：

- “问题”显示语法错误、运行错误和错误行定位；
- “输出”显示 `print()` 或 `console.log()`；
- “终端”显示本次执行状态、测试数量和耗时；
- “测试”比较输入、预期输出和实际返回值。

在编辑器中按 `Tab` 缩进，按 `Shift + Tab` 反缩进，按 `Ctrl + Enter`（macOS 为 `⌘ + Enter`）运行公开示例，按 `Ctrl + Shift + Enter` 提交全部测试。`Alt + ← / →` 可以在题目间移动。界面采用 VS Code 的布局和信息层级，但仍是为初学者设计的本地练习平台，不是 VS Code 的替代品。

## 学习顺序

| 题号 | 章节 | 重点 |
|---|---|---|
| 1–90 | 1–9 | 变量、运算、条件、循环、字符串、列表、字典、集合、函数、推导式、异常、文件、JSON、CSV |
| 91–130 | 10–13 | 类与类型提示、常用容器、迭代工具、数学、时间、随机、正则、路径与数据库入门 |
| 131–180 | 14–18 | NumPy、pandas、Matplotlib、scikit-learn |
| 181–240 | 19–24 | 机考输入输出、复杂度、排序、二分、栈队列、链表、树堆、并查集、图搜索、递归、贪心、动态规划 |
| 241–270 | 25–27 | 真正的 SQL 查询、Python 后端业务逻辑、HTTP 请求与 API 调用 |
| 271–300 | 28–30 | HTML/CSS、JavaScript、前端状态处理、前后端数据交互与全栈综合 |

建议先每天做 3–5 题，每次 45–90 分钟。基础题先读“语法小课”，自己尝试 10–15 分钟；遇到困难先看第一条提示，再逐条展开。阅读参考答案后，回到空白模板重新写一遍，隔一天再独立复做。以能解释每行代码、能处理新输入为目标，不必为了通过而背答案。

准备机考时，完成前 90 题后可以先进入第 19–24 章；NumPy 与全栈章节可按学习时间穿插。这里的算法题是**通用复试机考训练题**，不是历年真题汇编。408 笔试中的操作系统、计算机组成原理、计算机网络还需要单独学习理论；本平台不能替代完整的 408 复习。各校机考允许的语言和题型不同，请以目标院校要求为准。

## 第一道题怎么写

平台通常已经准备好：

```python
def solve(n):
    # 在这里写代码
    pass
```

如果要求返回输入的整数，改成：

```python
def solve(n):
    return n
```

`n` 是平台传入的数据，不需要再写 `input()`。`return` 把结果交给判题器；`print()` 只把调试信息显示在输出面板。保留 `def solve(...)` 和参数名，函数体缩进四个空格。

“运行示例”只检查公开输入，用来快速调试；“提交检查”会运行全部测试，全部通过才记为完成。自定义输入是**参数数组**：`solve(a, b)` 输入 `[2, 3]`；`solve(nums)` 输入 `[[1, 2, 3]]`。自定义输入只展示执行结果，没有标准答案，不会记为完成。

输入输出章节会把机考的标准输入整体作为 `text` 参数传入，并要求返回输出文本。转成机考程序时，可把同一个解析函数和下方入口放在一起：

```python
import sys

if __name__ == "__main__":
    print(solve(sys.stdin.read()))
```

SQL 题写实际查询语句，系统为每个测试创建独立 SQLite 数据库。表结构显示在题目中；返回行顺序需要通过 `ORDER BY` 满足题意。JavaScript 题在本机 Node.js 执行 `function solve(...)` 或 `async function solve(...)`。HTML/CSS 题练习生成页面和样式字符串，按题目指定格式检查，**不等同于浏览器渲染或完整 DOM 自动化测试**。

自动检查比较运行结果，不强制你必须使用某一种语法；题目建议使用的语法是学习目标。超时能发现无限循环，但这里的小型测试不能证明你的算法对任意大输入都满足复杂度要求，请同时阅读复杂度说明。

## 进度与代码

草稿、通过状态、收藏和笔记保存在当前浏览器的本地存储。页面提供 JSON 导出和导入，建议定期备份。清理浏览器数据、切换浏览器或换端口后不会自动共享进度；可以用导出的备份恢复。无需注册，也不向外部服务器上传代码。

## 实际调用这个平台的 API

先启动平台，然后尝试：

```python
import json
from urllib.request import Request, urlopen

with urlopen("http://127.0.0.1:8765/api/demo/items?q=Python&limit=2", timeout=5) as response:
    result = json.load(response)
    print(result["items"])

data = json.dumps({"name": "小明", "progress": 3}).encode("utf-8")
request = Request(
    "http://127.0.0.1:8765/api/demo/echo",
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urlopen(request, timeout=5) as response:
    print(json.load(response))
```

浏览器中的 API 实验室可以发同样的请求并查看 HTTP 状态和响应体。真实项目中，把网址换成服务提供的地址，并根据它的文档添加鉴权、超时和错误处理。

| 接口 | 用途 |
|---|---|
| `GET /api/problems` | 题目列表与章节 |
| `GET /api/problems/1` | 第 1 题详细信息 |
| `POST /api/run` | 执行代码；JSON 字段为 `problem_id`、`code`、`mode` |
| `GET /api/meta` | Python、Node 与常用库的可用状态 |
| `GET /api/demo/items?q=Python&limit=2` | 按名称筛选商品，total 为截断前数量 |
| `GET /api/demo/items/1` | 查看一个商品，不存在时返回 404 |
| `POST /api/demo/echo` | 原样返回收到的 JSON：`{"received": ...}` |

## 阅读源码的顺序

1. `curriculum/schema.py`：题目如何用字典表示。
2. `curriculum/beginner.py`：题目、样例、答案如何组织。
3. `static/app.js`、`static/workbench.css`：前端如何用 `fetch` 请求接口，并把练习页组织成 VS Code 风格工作台。
4. `server.py`：Python 如何处理 GET、POST、JSON 和静态资源。
5. `runner.py`、`node_runner.js`：如何执行学习代码、比较结果、捕获异常。
6. `practice_support.py`：HTTP 练习使用的本地测试服务。

## 验证与维护

```powershell
python -X utf8 verify.py
python -X utf8 -m unittest discover -s tests -v
```

`verify.py` 检查编号、每章题数、必要字段，并执行全部参考答案的全部测试。用 `--chapter 1` 可只检查一章。

平台只监听 `127.0.0.1`，适合个人学习。学习代码在临时工作目录的子进程运行，有 12 秒超时和输出上限；这**不是安全沙箱**，代码仍拥有当前用户的权限。不要在此运行来历不明的代码，也不要直接开放到公网。Windows 超时只保证终止直接执行进程，学生自行创建的子进程不在这个保证范围内。
