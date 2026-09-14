"""Chapters 10–18: runnable, incremental lessons for a first Python course."""

from .schema import problem

PROBLEMS = []
_counts = {}


def add(chapter, title, lesson, syntax, task, params, tests, code, hints, explanation,
        requires=None, difficulty='进阶'):
    """Keep the shared presentation consistent; all lesson content is specific."""
    _counts[chapter] = _counts.get(chapter, 0) + 1
    PROBLEMS.append(problem(
        chapter, _counts[chapter], title,
        lesson + '\n\n```python\n' + syntax.strip() + '\n```',
        task, params, tests, code, hints, explanation,
        difficulty=difficulty, requires=requires,
    ))


# Chapter 10 — classes, reusable interfaces, modules, and type annotations.
add(10, '你的第一个矩形类',
    'class 定义一种对象；__init__ 在创建对象时保存属性。方法的第一个参数 self 代表当前对象，self.width 是它自己的宽度。',
    'class Rectangle:\n    def __init__(self, width):\n        self.width = width\n    def double(self):\n        return self.width * 2\nr = Rectangle(3)\nr.double()  # 6',
    '在 solve 内定义 Rectangle 类，保存 width、height，并提供 area() 和 perimeter()。返回 {"area": 面积, "perimeter": 周长}。宽高为 0～100 的整数，允许退化矩形。',
    [('width', 'int', '非负宽度'), ('height', 'int', '非负高度')],
    [([3, 4], {'area': 12, 'perimeter': 14}), ([0, 5], {'area': 0, 'perimeter': 10}),
     ([1, 1], {'area': 1, 'perimeter': 4}), ([0, 0], {'area': 0, 'perimeter': 0}),
     ([7, 2], {'area': 14, 'perimeter': 18})],
    '''def solve(width, height):
    class Rectangle:
        def __init__(self, width, height):
            self.width = width
            self.height = height
        def area(self):
            return self.width * self.height
        def perimeter(self):
            return 2 * (self.width + self.height)
    rectangle = Rectangle(width, height)
    return {"area": rectangle.area(), "perimeter": rectangle.perimeter()}
''',
    ['把传入的宽高存到 self 的属性上。', 'area 和 perimeter 都从 self 读取宽高，不需要额外传入它们。', '先创建 rectangle = Rectangle(width, height)，再调用两个方法组装字典。'],
    '构造方法把两个数绑定到同一个矩形对象。面积方法计算乘积，周长方法计算两倍的和；最后调用方法取得普通数值。')

add(10, '用对象记录计数变化',
    '对象可以保存多次操作之间的状态。方法里给 self.value 赋值，会改变这个对象；同一对象的下一次方法调用能读到新值。',
    'class Counter:\n    def __init__(self, value):\n        self.value = value\n    def add(self, amount):\n        self.value += amount',
    '定义 Counter 类，从非负 initial 开始依次应用 changes 中的整数变化。每次变化后若小于 0，立即设为 0。返回每次变化后的数值列表，不包含初始值；空 changes 返回 []。',
    [('initial', 'int', '0～100 的初值'), ('changes', 'list[int]', '至多 20 次变化，每次 -100～100')],
    [([2, [3, -8, 1]], [5, 0, 1]), ([0, []], []), ([0, [-1, -2, 5]], [0, 0, 5]),
     ([10, [0, -3]], [10, 7]), ([1, [-1, 2, -1]], [0, 2, 1])],
    '''def solve(initial, changes):
    class Counter:
        def __init__(self, value):
            self.value = value
        def add(self, amount):
            self.value = max(0, self.value + amount)
            return self.value
    counter = Counter(initial)
    return [counter.add(change) for change in changes]
''',
    ['只创建一个 Counter，让它处理全部变化。', '用 max(0, 新数值) 在每一步限制下界。', 'add 方法返回本次更新后的 value，把所有返回值收集起来。'],
    '同一个 counter 被反复更新，负数截断必须发生在每一步。若只对最终总和截断，会在 [3, -8, 1] 这类输入上得到错误结果。')

add(10, '只读属性：摄氏转华氏',
    '@property 把一个方法包装成属性，读取时写 obj.fahrenheit 而不是 obj.fahrenheit()。适合由已有属性计算出的值。',
    'class Temperature:\n    @property\n    def fahrenheit(self):\n        return self.celsius * 9 / 5 + 32',
    '定义 Temperature 类，存储 celsius，提供只读 fahrenheit 属性。返回华氏温度，四舍五入保留 2 位小数。输入为 -100～200 的数字；返回数字而非字符串。',
    [('celsius', 'float', '摄氏温度')],
    [([0], 32.0), ([100], 212.0), ([-40], -40.0), ([37.5], 99.5), ([20], 68.0)],
    '''def solve(celsius):
    class Temperature:
        def __init__(self, celsius):
            self.celsius = celsius
        @property
        def fahrenheit(self):
            return self.celsius * 9 / 5 + 32
    return round(Temperature(celsius).fahrenheit, 2)
''',
    ['构造方法只需要保存摄氏温度。', '在计算华氏温度的方法前写 @property。', '使用 Temperature(celsius).fahrenheit 读取结果，再 round(..., 2)。'],
    'fahrenheit 不需要重复存储；读取时根据 celsius 计算即可。属性访问不带括号，round 返回数值而不是固定小数位的文本。')

add(10, '继承与方法重写',
    'class Child(Parent) 让子类继承父类。子类定义同名方法会替换父类实现；super() 可以调用父类的方法。',
    'class Student(Person):\n    def introduce(self):\n        return super().introduce() + "，我是学生"',
    '定义 Person，introduce() 返回 "你好，我是" 加 name。再定义 Student(Person)，重写 introduce()，在父类结果末尾加 "，我是学生"。kind 只可能是 "person" 或 "student"，返回对应对象的介绍。姓名可为空字符串。',
    [('name', 'str', '长度不超过 20 的姓名'), ('kind', 'str', 'person 或 student')],
    [(['小林', 'student'], '你好，我是小林，我是学生'), (['Ada', 'person'], '你好，我是Ada'),
     (['', 'person'], '你好，我是'), (['李雷', 'person'], '你好，我是李雷'), (['A', 'student'], '你好，我是A，我是学生')],
    '''def solve(name, kind):
    class Person:
        def __init__(self, name):
            self.name = name
        def introduce(self):
            return "你好，我是" + self.name
    class Student(Person):
        def introduce(self):
            return super().introduce() + "，我是学生"
    person = Student(name) if kind == "student" else Person(name)
    return person.introduce()
''',
    ['父类负责保存名字和共有的介绍。', 'Student 不必重复 __init__，可以直接继承。', '在 Student.introduce 中调用 super().introduce()，然后拼接学生后缀。'],
    'Student 自动继承姓名初始化逻辑，只覆盖介绍行为。两类对象都可以调用 introduce，这就是统一接口带来的便利。')

add(10, 'dataclass 商品记录',
    '@dataclass 根据带类型标注的字段自动生成 __init__。asdict(obj) 将数据类转换成字典；类型标注说明用途，但不会自动检查传入值。',
    'from dataclasses import dataclass, asdict\n@dataclass\nclass Product:\n    name: str\n    price: int\np = Product("笔", 3)\nasdict(p)  # {"name": "笔", "price": 3}',
    '定义 Product 数据类，字段依次为 name、price、quantity。创建对象后将它转为字典，并补上 total = price * quantity。价格用整数元表示，价格和数量均非负。',
    [('name', 'str', '商品名'), ('price', 'int', '0～1000'), ('quantity', 'int', '0～100')],
    [(['笔', 3, 4], {'name': '笔', 'price': 3, 'quantity': 4, 'total': 12}),
     (['书', 20, 0], {'name': '书', 'price': 20, 'quantity': 0, 'total': 0}),
     (['', 0, 1], {'name': '', 'price': 0, 'quantity': 1, 'total': 0}),
     (['杯', 15, 2], {'name': '杯', 'price': 15, 'quantity': 2, 'total': 30}),
     (['A', 1, 1], {'name': 'A', 'price': 1, 'quantity': 1, 'total': 1})],
    '''from dataclasses import dataclass, asdict

def solve(name, price, quantity):
    @dataclass
    class Product:
        name: str
        price: int
        quantity: int
    product = Product(name, price, quantity)
    result = asdict(product)
    result["total"] = product.price * product.quantity
    return result
''',
    ['用三行类型标注声明三个字段。', 'Product(name, price, quantity) 会调用自动生成的初始化方法。', '先 asdict(product)，再向字典增加 total 键。'],
    '数据类减少保存结构化数据时的重复代码。asdict 得到可返回的普通字典，总价从对象的两个数值字段相乘计算。')

add(10, '数据类的自动排序',
    '@dataclass(order=True) 生成比较方法，按字段定义顺序逐个比较。把优先级字段放前面，就能用 sorted 排序对象。',
    '@dataclass(order=True)\nclass Entry:\n    score: int\n    name: str\n# 先比 score，相等时再比 name',
    'records 的每条记录是 [name, score]。定义可排序的 Entry 数据类，按分数从小到大、同分时姓名字典序从小到大排序，返回姓名列表。保留重复记录；空列表返回 []。',
    [('records', 'list[list]', '至多 20 条 [字符串姓名, 整数分数]')],
    [([[['Bob', 2], ['Ada', 1], ['Ann', 2]]], ['Ada', 'Ann', 'Bob']),
     ([[]], []), ([[['X', 0]]], ['X']), ([[['b', 1], ['a', 1]]], ['a', 'b']),
     ([[['x', -1], ['x', -1], ['y', -2]]], ['y', 'x', 'x'])],
    '''from dataclasses import dataclass

def solve(records):
    @dataclass(order=True)
    class Entry:
        score: int
        name: str
    entries = [Entry(score, name) for name, score in records]
    return [entry.name for entry in sorted(entries)]
''',
    ['排序优先级取决于字段声明顺序。', 'Entry 的参数顺序应为 score、name，和输入记录相反。', '生成 Entry 列表并 sorted，最后取出每个对象的 name。'],
    'score 放在 name 之前，因此数据类的默认比较正好满足题意。输入的 [name, score] 需要解包后调整顺序。')

add(10, 'classmethod：从文本创建对象',
    '@classmethod 接收类本身 cls，适合提供另一种构造方式。使用 cls(...) 可创建当前类的实例。',
    '@classmethod\ndef from_text(cls, text):\n    name, age = text.split(":")\n    return cls(name, int(age))',
    '实现 Person.from_text 类方法，将 "姓名:年龄" 解析为对象。返回 {"name": 姓名, "age": 整数年龄}。恰好含一个冒号，姓名非空且无冒号，年龄为 0～120 的十进制整数文本，允许前导零。',
    [('text', 'str', '格式为 姓名:年龄')],
    [(['小林:20'], {'name': '小林', 'age': 20}), (['Ada:07'], {'name': 'Ada', 'age': 7}),
     (['A:0'], {'name': 'A', 'age': 0}), (['B:120'], {'name': 'B', 'age': 120}), (['Lee:18'], {'name': 'Lee', 'age': 18})],
    '''def solve(text):
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age
        @classmethod
        def from_text(cls, text):
            name, age = text.split(":")
            return cls(name, int(age))
    person = Person.from_text(text)
    return {"name": person.name, "age": person.age}
''',
    ['split(":") 得到两个字符串。', '类方法首参数是 cls，用 int 将年龄转换为整数。', 'from_text 最后返回 cls(name, int(age))，然后读取对象属性。'],
    'from_text 把解析逻辑与普通构造过程分开。int("07") 等于 7，因此结果里的 age 是整数而非原始文本。')

add(10, 'staticmethod：范围裁剪工具',
    '@staticmethod 表示方法不需要 self 或 cls。可以把与类相关、但不依赖对象状态的工具函数放进去。',
    'class Bounds:\n    @staticmethod\n    def clamp(value, low, high):\n        return min(high, max(low, value))\nBounds.clamp(9, 0, 5)  # 5',
    '定义 Bounds.clamp 静态方法，将每个 values 元素限制到闭区间 [low, high]。低于 low 变成 low，高于 high 变成 high，其余不变。low <= high，输入均为整数；空列表返回 []。',
    [('values', 'list[int]', '至多 30 个整数'), ('low', 'int', '下界'), ('high', 'int', '上界')],
    [([[-2, 0, 3, 9], 0, 5], [0, 0, 3, 5]), ([[], 1, 2], []),
     ([[1, 2, 3], 2, 2], [2, 2, 2]), ([[-9, -3, 0], -5, -1], [-5, -3, -1]), ([[0, 5], 0, 5], [0, 5])],
    '''def solve(values, low, high):
    class Bounds:
        @staticmethod
        def clamp(value, low, high):
            return min(high, max(low, value))
    return [Bounds.clamp(value, low, high) for value in values]
''',
    ['先用 max 确保值不低于 low。', '再用 min 确保结果不高于 high。', '静态方法不写 self，通过 Bounds.clamp(...) 在推导式里调用。'],
    'max 处理下界，min 处理上界。静态方法只是组织函数的一种方式，无需为了调用它创建 Bounds 对象。')

add(10, '类型提示与可选返回值',
    '函数参数后的冒号声明类型，-> 声明返回类型。Optional[int] 等价于 int | None，表示可能返回整数，也可能没有结果。标注本身不会执行类型验证。',
    'from typing import Sequence, Optional\ndef find(values: Sequence[int], target: int) -> Optional[int]:\n    return None',
    '为 solve 添加参数和返回值类型提示，寻找 target 在 values 中第一次出现的下标。找到返回从 0 开始的整数下标；找不到返回 None。不要返回 -1。',
    [('values', 'list[int]', '至多 50 个整数'), ('target', 'int', '目标值')],
    [([[4, 8, 4], 4], 0), ([[4, 8], 3], None), ([[], 0], None), ([[9], 9], 0), ([[-2, 0, 7], 7], 2)],
    '''from typing import Sequence, Optional

def solve(values: Sequence[int], target: int) -> Optional[int]:
    for index, value in enumerate(values):
        if value == target:
            return index
    return None
''',
    ['返回值可能是 int，也可能是 None。', 'enumerate 同时给出下标和元素。', '在循环中找到就 return index；循环结束仍未找到时 return None。'],
    '提前返回保证得到第一次出现的位置。类型提示让调用者知道缺失结果的表达方式，None 会在页面结果中显示为 null。')

add(10, '导入模块中的字符常量',
    'import module 导入模块，from module import name 只导入指定名称。string.ascii_letters 包含英文字母大小写，string.digits 只包含 0～9。',
    'from string import ascii_letters, digits\n"A" in ascii_letters  # True\n"7" in digits        # True\n"中" in ascii_letters  # False',
    '使用 string 的字符常量统计 text 中 ASCII 英文字母、ASCII 数字及其他字符的数量，返回 {"letters": ..., "digits": ..., "other": ...}。中文、空格、标点和全角数字都归入 other。',
    [('text', 'str', '长度不超过 100')],
    [(['Hi 12!'], {'letters': 2, 'digits': 2, 'other': 2}), (['中文３'], {'letters': 0, 'digits': 0, 'other': 3}),
     ([''], {'letters': 0, 'digits': 0, 'other': 0}), (['aZ09'], {'letters': 2, 'digits': 2, 'other': 0}),
     ([' A\n'], {'letters': 1, 'digits': 0, 'other': 2})],
    '''from string import ascii_letters, digits

def solve(text):
    result = {"letters": 0, "digits": 0, "other": 0}
    for char in text:
        if char in ascii_letters:
            result["letters"] += 1
        elif char in digits:
            result["digits"] += 1
        else:
            result["other"] += 1
    return result
''',
    ['这题只认可 ASCII 字符，不能直接用 isalpha 判断。', '从 string 导入 ascii_letters 和 digits，分别做成员检查。', '使用 if/elif/else，让每个字符恰好进入一个计数。'],
    '标准库已提供常用字符集合，避免手写字母表。ASCII 限制使全角数字不被当成普通数字，这与 isdigit 的行为不同。')


# Chapter 11 — collections, itertools, functools.
add(11, 'Counter 统计词频',
    'Counter 是专门计数的字典。Counter(items) 统计每个元素出现的次数，items() 可取得元素与次数，dict(...) 可转换为普通字典。',
    'from collections import Counter\nCounter(["a", "b", "a"])  # Counter({"a": 2, "b": 1})',
    '统计 words 中每个完整单词的出现次数，大小写不同的单词分开统计。返回普通字典，空列表返回 {}。不拆分单词，也不去除空字符串。',
    [('words', 'list[str]', '至多 50 个字符串')],
    [([['a', 'b', 'a']], {'a': 2, 'b': 1}), ([[]], {}), ([['A', 'a']], {'A': 1, 'a': 1}),
     ([['', '', 'x']], {'': 2, 'x': 1}), ([['猫', '猫', '狗']], {'猫': 2, '狗': 1})],
    '''from collections import Counter

def solve(words):
    return dict(Counter(words))
''',
    ['计数单位是列表元素，直接把 words 交给 Counter。', 'Counter 会自动为第一次出现的单词建立计数。', '返回 dict(Counter(words))，无需自己初始化每个键。'],
    'Counter 遍历列表并累加次数。转换为 dict 让返回值保持平台要求的普通 JSON 对象形式。')

add(11, 'defaultdict 按首字母分组',
    'defaultdict(list) 在访问缺失键时自动创建空列表，因此可以直接 groups[key].append(value)，不必提前判断键是否存在。',
    'from collections import defaultdict\ngroups = defaultdict(list)\ngroups["a"].append("apple")',
    '按单词的第一个字符把 words 分组，返回字典。每组保留原始出现顺序；区分大小写。单词均非空，words 可以为空。',
    [('words', 'list[str]', '至多 40 个非空单词')],
    [([['ant', 'bee', 'apple']], {'a': ['ant', 'apple'], 'b': ['bee']}), ([[]], {}),
     ([['A', 'a']], {'A': ['A'], 'a': ['a']}), ([['猫咪', '猫粮']], {'猫': ['猫咪', '猫粮']}),
     ([['one', 'one', 'two']], {'o': ['one', 'one'], 't': ['two']})],
    '''from collections import defaultdict

def solve(words):
    groups = defaultdict(list)
    for word in words:
        groups[word[0]].append(word)
    return dict(groups)
''',
    ['分组键是 word[0]。', '把 defaultdict 的默认工厂设为 list，而不是 list()。', '依次执行 groups[word[0]].append(word)，最后转换成 dict。'],
    '每个新首字符对应一个独立的空列表。按输入顺序追加，所以同组元素的相对顺序自然不变。')

add(11, 'deque 实现循环轮转',
    'deque 是双端队列，可以高效从两端增删元素。rotate(k) 原地向右轮转 k 步，负数向左；它的返回值是 None。',
    'from collections import deque\nqueue = deque([1, 2, 3])\nqueue.rotate(1)\nlist(queue)  # [3, 1, 2]',
    '将 values 向右循环移动 k 步，返回新列表。k 可以为负或大于列表长度；空列表始终返回 []。',
    [('values', 'list[int]', '至多 30 个整数'), ('k', 'int', '-100～100')],
    [([[1, 2, 3], 1], [3, 1, 2]), ([[1, 2, 3], -1], [2, 3, 1]), ([[], 5], []),
     ([[1, 2, 3], 7], [3, 1, 2]), ([[9], -20], [9])],
    '''from collections import deque

def solve(values, k):
    queue = deque(values)
    queue.rotate(k)
    return list(queue)
''',
    ['先将列表转成 deque。', 'rotate 会修改队列，不要把它的返回值当作队列。', '调用 queue.rotate(k) 后，再 return list(queue)。'],
    'deque 自动处理负方向、多圈轮转和空队列。转换回列表后得到可直接展示的结果。')

add(11, 'namedtuple 给坐标起名字',
    'namedtuple 创建带字段名称的元组类型。对象既可用 p[0] 访问，也可用 p.x 访问；字段不可重新赋值。',
    'from collections import namedtuple\nPoint = namedtuple("Point", ["x", "y"])\np = Point(2, 3)\np.x + p.y  # 5',
    '把 points 中每个 [x, y] 转成 Point 命名元组，用字段访问计算所有 x 的和、所有 y 的和，返回 [x总和, y总和]。空列表返回 [0, 0]。',
    [('points', 'list[list[int]]', '至多 30 个二维整数坐标')],
    [([[[1, 2], [3, 4]]], [4, 6]), ([[]], [0, 0]), ([[[-1, 5]]], [-1, 5]),
     ([[[2, -2], [-2, 2]]], [0, 0]), ([[[0, 0], [0, 1], [4, 0]]], [4, 1])],
    '''from collections import namedtuple

def solve(points):
    Point = namedtuple("Point", ["x", "y"])
    records = [Point(x, y) for x, y in points]
    return [sum(p.x for p in records), sum(p.y for p in records)]
''',
    ['Point 是新建的类型，Point(x, y) 是它的实例。', '将每条二维坐标解包成 x 和 y。', '分别用 sum(p.x for p in records) 和 y 字段求和。'],
    '字段名称提高可读性，让坐标意义不依赖记住下标。sum 在空序列上返回 0，恰好满足空输入约定。')

add(11, 'chain 展平一层列表',
    'chain.from_iterable 接收多个可迭代对象，依次产生它们的元素。它只展平一层，结果是惰性迭代器，需要 list 才得到列表。',
    'from itertools import chain\nlist(chain.from_iterable([[1, 2], [], [3]]))  # [1, 2, 3]',
    '将 groups 的一层二维整数列表按顺序拼成一个列表。保留重复元素；允许外层和内层为空。',
    [('groups', 'list[list[int]]', '至多 20 组，每组至多 20 个数')],
    [([[[1, 2], [], [3]]], [1, 2, 3]), ([[]], []), ([[[], []]], []),
     ([[[4], [4, -1]]], [4, 4, -1]), ([[[0, 1, 2]]], [0, 1, 2])],
    '''from itertools import chain

def solve(groups):
    return list(chain.from_iterable(groups))
''',
    ['目标是依次读取每个小列表里的元素。', '使用 chain.from_iterable(groups)，无需对 groups 使用 *。', '用 list 包裹迭代器得到最终结果。'],
    'chain 按外层顺序遍历各组，空组不产生元素。它不排序、不去重，因此所有元素的原顺序被保留。')

add(11, 'combinations 选择搭档',
    'combinations(items, 2) 按输入位置选出不重复的二元组合，不同时生成 [a,b] 和 [b,a]。生成顺序遵循输入顺序。',
    'from itertools import combinations\nlist(combinations(["a", "b", "c"], 2))\n# [("a", "b"), ("a", "c"), ("b", "c")]',
    '返回 names 中任选两人的所有组合，每个组合转为列表。姓名互不重复，结果顺序与 itertools.combinations 一致；不足两人时返回 []。',
    [('names', 'list[str]', '0～6 个互异姓名')],
    [([['a', 'b', 'c']], [['a', 'b'], ['a', 'c'], ['b', 'c']]), ([[]], []), ([['a']], []),
     ([['z', 'a']], [['z', 'a']]), ([['A', 'B', 'C', 'D']], [['A', 'B'], ['A', 'C'], ['A', 'D'], ['B', 'C'], ['B', 'D'], ['C', 'D']])],
    '''from itertools import combinations

def solve(names):
    return [list(pair) for pair in combinations(names, 2)]
''',
    ['这题选择的是组合，搭档交换顺序不算新组合。', 'combinations 的第二个参数固定为 2。', '它产生元组，用 list(pair) 转成要求的列表。'],
    '库函数负责避免重复选择与反向重复。不要先排序姓名，否则会改变题目要求的输入顺序。')

add(11, 'product 生成小型密码表',
    'product(pool, repeat=n) 生成 n 个位置的笛卡尔积，每一位都可选 pool 中任意元素。最右边的位变化最快。',
    'from itertools import product\n["".join(chars) for chars in product("ab", repeat=2)]\n# ["aa", "ab", "ba", "bb"]',
    'alphabet 是由互异字符组成的字符串，返回用这些字符组成的所有长度为 length 的字符串。遵循 alphabet 的原始顺序；length=0 时返回 [""]，空 alphabet 且 length>0 时返回 []。字符最多 3 个，length 为 0～3。',
    [('alphabet', 'str', '0～3 个互异字符'), ('length', 'int', '0～3')],
    [(['ab', 2], ['aa', 'ab', 'ba', 'bb']), (['xy', 0], ['']), (['', 2], []),
     (['z', 3], ['zzz']), (['ba', 1], ['b', 'a'])],
    '''from itertools import product

def solve(alphabet, length):
    return ["".join(chars) for chars in product(alphabet, repeat=length)]
''',
    ['每个字符位置使用相同的候选池，因此设置 repeat。', 'product 产生的是字符元组，不是字符串。', '对每个元组使用 "".join(chars)，长度为零的元组会变成空字符串。'],
    '笛卡尔积相当于 length 层嵌套循环。零个位置只有一种选择：空字符串，所以它的结果不应是空列表。')

add(11, 'groupby 压缩连续片段',
    'groupby 只把连续相同的元素归为一组，和按值汇总全部元素不同。每个分组迭代器需要在继续下一组之前消费。',
    'from itertools import groupby\n[(key, len(list(group))) for key, group in groupby("aaba")]\n# [("a", 2), ("b", 1), ("a", 1)]',
    '将 text 连续相同字符压缩为 [字符, 连续次数] 列表，保留片段顺序。不要排序 text；分隔开的相同字符必须分别记录。空文本返回 []。',
    [('text', 'str', '长度 0～100')],
    [(['aaabb a'], [['a', 3], ['b', 2], [' ', 1], ['a', 1]]), ([''], []),
     (['aba'], [['a', 1], ['b', 1], ['a', 1]]), (['中中'], [['中', 2]]), (['xxxx'], [['x', 4]])],
    '''from itertools import groupby

def solve(text):
    return [[char, sum(1 for _ in group)] for char, group in groupby(text)]
''',
    ['aaba 中的两个 a 片段不能合并。', 'groupby(text) 依次返回字符和该连续段的迭代器。', '用 sum(1 for _ in group) 统计当前段，再组成二元素列表。'],
    'groupby 逐段扫描，因此天然保持连续片段顺序。立即消费 group 计算长度，避免迭代器随外层推进而失效。')

add(11, 'reduce 连乘与初始值',
    'reduce(function, items, initial) 反复将累计值与下一个元素交给 function。initial 指定起点，也决定空序列的返回值。',
    'from functools import reduce\nreduce(lambda total, x: total * x, [2, 3, 4], 1)  # 24',
    '使用 functools.reduce 返回 numbers 的乘积。空列表的乘积约定为 1；整数可为负数或 0。',
    [('numbers', 'list[int]', '0～10 个 -10～10 的整数')],
    [([[2, 3, 4]], 24), ([[]], 1), ([[0, 5]], 0), ([[-2, -3, 4]], 24), ([[7]], 7)],
    '''from functools import reduce

def solve(numbers):
    return reduce(lambda total, number: total * number, numbers, 1)
''',
    ['每一步用当前乘积乘下一个数。', '乘法的中性元素是 1，不是 0。', '第三个参数传 1，既初始化累计结果，也处理空列表。'],
    'reduce 把列表折叠成一个值。初值 1 不改变非空列表的乘积，并让空输入无需额外分支。')

add(11, 'lru_cache 缓存斐波那契',
    '@lru_cache(maxsize=None) 缓存函数在相同参数下的返回值。递归函数反复遇到同一个 n 时，可直接复用答案；参数必须可哈希。',
    'from functools import lru_cache\n@lru_cache(maxsize=None)\ndef fib(n):\n    if n < 2:\n        return n\n    return fib(n - 1) + fib(n - 2)',
    '在 solve 内定义带 lru_cache 的递归函数，返回第 n 个斐波那契数。约定 F(0)=0、F(1)=1，其后 F(n)=F(n-1)+F(n-2)。n 为 0～30。',
    [('n', 'int', '0～30')],
    [([6], 8), ([0], 0), ([1], 1), ([10], 55), ([30], 832040)],
    '''from functools import lru_cache

def solve(n):
    @lru_cache(maxsize=None)
    def fib(value):
        if value < 2:
            return value
        return fib(value - 1) + fib(value - 2)
    return fib(n)
''',
    ['递归先处理 n=0 和 n=1 的终止情况。', '一般情况返回 fib(n-1)+fib(n-2)。', '在内部 fib 上加 @lru_cache(maxsize=None)，避免指数级重复计算。'],
    '每个不同的 value 只实际计算一次。缓存定义在 solve 内，每次测试都有独立缓存，不依赖之前提交的状态。')

# Chapter 12 — numeric tools and deterministic dates/randomness.
add(12, 'ceil 计算需要的箱数',
    'math.ceil(x) 返回不小于 x 的最小整数；用于有余量也要增加一份的情况。整数整除 // 会向下取整。',
    'import math\nmath.ceil(7 / 3)  # 3',
    '有 count 件物品，每箱最多 capacity 件，返回至少需要几个箱子。count 为 0～10000；capacity 为 1～100。零件物品需要零个箱子。',
    [('count', 'int', '物品数量'), ('capacity', 'int', '每箱容量')],
    [([7, 3], 3), ([0, 5], 0), ([6, 3], 2), ([1, 9], 1), ([100, 1], 100)],
    'import math\ndef solve(count, capacity):\n    return math.ceil(count / capacity)',
    ['先求数量与容量的比值。', '存在余数时必须再使用一个箱子。', '对 count / capacity 调用 math.ceil。'],
    '向上取整将非整数箱数提升到足够容纳全部物品的整数，整除时不额外加箱。')

add(12, 'gcd 与 lcm 的整数工具',
    'math.gcd 求最大公约数，math.lcm 求最小公倍数。返回值非负；与零的最大公约数是另一数的绝对值，含零的最小公倍数是零。',
    'from math import gcd, lcm\ngcd(12, 18)  # 6\nlcm(12, 18)  # 36',
    '返回两个整数 a、b 的 [最大公约数, 最小公倍数]。输入在 -1000～1000；允许负数与零，两个数均为零时返回 [0, 0]。',
    [('a', 'int', '第一个整数'), ('b', 'int', '第二个整数')],
    [([12, 18], [6, 36]), ([0, 5], [5, 0]), ([-6, 4], [2, 12]), ([0, 0], [0, 0]), ([7, 3], [1, 21])],
    'from math import gcd, lcm\ndef solve(a, b):\n    return [gcd(a, b), lcm(a, b)]',
    ['标准库已经处理负数和零。', '结果顺序先 gcd 后 lcm。', '直接分别调用 gcd(a, b) 和 lcm(a, b) 并装入列表。'],
    '直接使用整数算法，不必手动用除法推导最小公倍数，也就避免了两个零带来的除零问题。')

add(12, 'hypot 计算二维距离',
    'math.hypot(dx, dy) 计算直角三角形斜边，即 sqrt(dx**2 + dy**2)。两点坐标先相减得到位移。',
    'from math import hypot\nhypot(3, 4)  # 5.0',
    '返回二维点 p、q 之间的欧氏距离，使用 round(..., 6) 保留六位小数。每个点都是两个 -100～100 的整数，相同点距离为零。',
    [('p', 'list[int]', '[x, y]'), ('q', 'list[int]', '[x, y]')],
    [([[0, 0], [3, 4]], 5.0), ([[1, 1], [1, 1]], 0.0), ([[-1, -1], [2, 3]], 5.0),
     ([[0, 0], [1, 1]], 1.414214), ([[5, 2], [-7, 7]], 13.0)],
    'from math import hypot\ndef solve(p, q):\n    return round(hypot(p[0] - q[0], p[1] - q[1]), 6)',
    ['分别计算横向和纵向坐标差。', 'hypot 接受这两个差值，不需要先平方。', '用 round(hypot(dx, dy), 6) 返回数值。'],
    '距离取决于位移长度，坐标差的正负不会影响结果。六位舍入统一了浮点计算的展示精度。')

add(12, 'statistics 均值与中位数',
    'statistics.mean 求算术平均数；median 求排序后中间值，偶数个元素时取中间两个的均值。两者都要求数据非空。',
    'from statistics import mean, median\nmean([1, 2, 9])  # 4\nmedian([1, 2, 9])  # 2',
    '返回 numbers 的 {"mean": 均值, "median": 中位数}，两项均 round 到六位。numbers 为 1～50 个整数。原始输入不一定有序。',
    [('numbers', 'list[int]', '非空整数列表')],
    [([[1, 2, 9]], {'mean': 4, 'median': 2}), ([[4, 1, 3, 2]], {'mean': 2.5, 'median': 2.5}),
     ([[8]], {'mean': 8, 'median': 8}), ([[-3, 0, 3]], {'mean': 0, 'median': 0}),
     ([[1, 1, 2]], {'mean': 1.333333, 'median': 1})],
    'from statistics import mean, median\ndef solve(numbers):\n    return {"mean": round(mean(numbers), 6), "median": round(median(numbers), 6)}',
    ['均值与中位数是不同统计量，不能相互替代。', 'median 会处理排序与偶数长度。', '分别调用 mean 和 median，再按题目键名组装字典。'],
    '极端值会显著影响均值，中位数只由排序后的中间位置决定。两个函数都不会要求调用者先排序原列表。')

add(12, 'multimode 找出全部众数',
    'statistics.multimode 返回出现次数最多的所有值。可能不止一个众数；返回顺序默认与首次出现顺序有关，可用 sorted 统一排序。',
    'from statistics import multimode\nmultimode([2, 1, 2, 1, 3])  # [2, 1]',
    '返回 numbers 的全部众数，并按数值升序排列。空列表返回 []；若每个数字只出现一次，则所有数字都是众数。',
    [('numbers', 'list[int]', '至多 50 个整数')],
    [([[2, 1, 2, 1, 3]], [1, 2]), ([[]], []), ([[3, 1, 2]], [1, 2, 3]),
     ([[5, 5, 5]], [5]), ([[-1, 0, -1, 0, 2]], [-1, 0])],
    'from statistics import multimode\ndef solve(numbers):\n    return sorted(multimode(numbers))',
    ['单个 mode 不足以返回所有并列第一的值。', 'multimode 会自动返回空列表的空结果。', '对 multimode(numbers) 调用 sorted。'],
    '先求并列最高频的集合，再排序满足稳定的输出约定。排序对象是众数列表，不是原始数据。')

add(12, '可复现的随机抽样',
    'random.Random(seed) 创建独立随机数生成器。相同种子和相同调用顺序得到相同结果；sample(pool, k) 无放回抽样，不修改 pool。',
    'import random\nrng = random.Random(0)\nrng.sample(list(range(5)), 3)  # [3, 4, 0]',
    '从编号 0～n-1 中使用 random.Random(seed).sample 抽取 min(3, n) 个编号，按抽取顺序返回，不排序。n 为 0～20，seed 为非负整数。必须创建局部生成器，以免其他测试影响结果。',
    [('n', 'int', '人数'), ('seed', 'int', '随机种子')],
    [([5, 0], [3, 4, 0]), ([0, 2], []), ([3, 42], [2, 0, 1]), ([1, 7], [0]), ([6, 1], [1, 4, 0])],
    'import random\ndef solve(n, seed):\n    rng = random.Random(seed)\n    return rng.sample(list(range(n)), min(3, n))',
    ['不要调用没有固定种子的全局 random.sample。', '人数不足三人时，抽样数量必须改为 n。', '用 rng.sample(list(range(n)), min(3, n)) 保留抽样顺序。'],
    '独立生成器隔离了随机状态。sample 保证结果中无重复编号，固定种子则让测试和调试能够复现。')

add(12, '日期加上若干天',
    'date.fromisoformat 读取 YYYY-MM-DD；timedelta(days=k) 表示日期间隔。日期加间隔会自动跨月、跨年并处理闰年。',
    'from datetime import date, timedelta\n(date.fromisoformat("2024-02-28") + timedelta(days=1)).isoformat()\n# "2024-02-29"',
    '将合法 ISO 日期 text 增加 days 天，返回 YYYY-MM-DD 字符串。days 可为负；输入和结果年份都在 1900～2100 内。',
    [('text', 'str', 'YYYY-MM-DD'), ('days', 'int', '-365～365')],
    [(['2024-02-28', 1], '2024-02-29'), (['2023-12-31', 1], '2024-01-01'),
     (['2024-03-01', -1], '2024-02-29'), (['2025-06-01', 0], '2025-06-01'), (['2023-03-01', -1], '2023-02-28')],
    'from datetime import date, timedelta\ndef solve(text, days):\n    return (date.fromisoformat(text) + timedelta(days=days)).isoformat()',
    ['先把字符串变成 date 对象。', '用 timedelta 表达天数，避免自己计算每个月有几天。', '相加后的日期对象用 isoformat() 转回字符串。'],
    '日期运算交给标准库处理日历规则。负时间差自然向过去移动，闰年的二月二十九日也可正确保留。')

add(12, 'strptime 读取时刻与星期',
    'datetime.strptime 按指定格式解析文本；%Y、%m、%d 表示年月日，%H、%M 表示时分。isoweekday 返回周一=1 到周日=7。',
    'from datetime import datetime\ndt = datetime.strptime("2024/01/01 09:30", "%Y/%m/%d %H:%M")\ndt.hour  # 9\ndt.isoweekday()  # 1',
    '解析合法文本 YYYY/MM/DD HH:MM，返回 {"weekday": ISO星期数, "minutes": 自零点经过的分钟数}。不涉及时区或夏令时。',
    [('text', 'str', '固定格式的日期时间')],
    [(['2024/01/01 09:30'], {'weekday': 1, 'minutes': 570}), (['2024/01/07 00:00'], {'weekday': 7, 'minutes': 0}),
     (['2024/02/29 23:59'], {'weekday': 4, 'minutes': 1439}), (['2023/12/31 12:00'], {'weekday': 7, 'minutes': 720}),
     (['2025/01/01 01:05'], {'weekday': 3, 'minutes': 65})],
    'from datetime import datetime\ndef solve(text):\n    dt = datetime.strptime(text, "%Y/%m/%d %H:%M")\n    return {"weekday": dt.isoweekday(), "minutes": dt.hour * 60 + dt.minute}',
    ['解析格式中的斜线、空格、冒号要与输入一致。', 'isoweekday 与 weekday 不同，前者从 1 开始。', '零点起的分钟数等于 hour * 60 + minute。'],
    'strptime 把固定格式拆成日期时间字段，再读取星期与时分即可。这里计算一天内的钟表分钟数，不是时间戳。')

add(12, 'Decimal 精确计算金额',
    'Decimal 从十进制字符串创建能避免先经过二进制浮点数。quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) 将金额按半入规则保留两位。',
    'from decimal import Decimal, ROUND_HALF_UP\nDecimal("2.675").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)\n# Decimal("2.68")',
    'prices 为十进制金额字符串列表，先精确求和，再使用 ROUND_HALF_UP 保留两位小数，返回固定两位的字符串。允许负金额，空列表返回 "0.00"。每项绝对值小于 10000，小数位至多 4。',
    [('prices', 'list[str]', '至多 30 个合法十进制字符串')],
    [([['0.1', '0.2']], '0.30'), ([['2.675']], '2.68'), ([[]], '0.00'),
     ([['1.004', '1.004']], '2.01'), ([['-1.235']], '-1.24')],
    'from decimal import Decimal, ROUND_HALF_UP\ndef solve(prices):\n    total = sum((Decimal(value) for value in prices), Decimal("0"))\n    return format(total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), ".2f")',
    ['直接 Decimal(value)，不要先转成 float。', '先求完整总和，最后只舍入一次。', 'quantize 后用 format(..., ".2f") 保证尾部零也显示。'],
    '逐项舍入会改变总额，所以先精确相加。ROUND_HALF_UP 对恰好半分的负数也向远离零的方向舍入。')

add(12, 'Fraction 精确分数相加',
    'Fraction(numerator, denominator) 自动约分并规范分母符号。两个 Fraction 相加仍是精确分数，可读取 numerator 和 denominator。',
    'from fractions import Fraction\nx = Fraction(1, 3) + Fraction(1, 6)\n[x.numerator, x.denominator]  # [1, 2]',
    'a、b 都是 [分子, 分母]，返回两分数相加并约分后的 [分子, 分母]。分母非零，可为负；结果分母必须为正，零表示为 [0, 1]。整数绝对值至多 100。',
    [('a', 'list[int]', '第一个分数'), ('b', 'list[int]', '第二个分数')],
    [([[1, 3], [1, 6]], [1, 2]), ([[1, 2], [-1, 2]], [0, 1]),
     ([[1, -2], [1, 4]], [-1, 4]), ([[2, 3], [4, 3]], [2, 1]), ([[0, 7], [2, 8]], [1, 4])],
    'from fractions import Fraction\ndef solve(a, b):\n    result = Fraction(*a) + Fraction(*b)\n    return [result.numerator, result.denominator]',
    ['把两个二元素列表分别转换成 Fraction。', '*a 可将列表解包成分子、分母两个参数。', '相加之后读取 result.numerator 和 result.denominator。'],
    'Fraction 内部处理通分、约分和符号，不需要经过可能损失精度的小数表示。')

# Chapter 13 — text patterns, pure paths, SQL, URLs.
add(13, '正则提取带符号整数',
    're.findall 返回所有不重叠的匹配。字符类 [0-9] 表示 ASCII 数字，+ 表示至少一个，? 表示前一部分可有可无。原始字符串 r"..." 方便书写正则。',
    'import re\nre.findall(r"[+-]?[0-9]+", "x=-12,y=+3")  # ["-12", "+3"]',
    '按从左到右顺序提取 text 中匹配 [+-]?[0-9]+ 的片段，转换为整数列表。这是词法提取，不解析小数："1.5" 得到 [1,5]。全角数字不匹配；没有匹配时返回 []。',
    [('text', 'str', '长度不超过 200')],
    [(['x=-12,y=+3'], [-12, 3]), (['abc'], []), (['1.5'], [1, 5]), (['--2 +007 ０'], [-2, 7]), (['0 -0 9'], [0, 0, 9])],
    'import re\ndef solve(text):\n    return [int(part) for part in re.findall(r"[+-]?[0-9]+", text)]',
    ['正负号整体最多出现一次，数字至少出现一次。', 'findall 返回字符串列表，需要逐项 int。', '使用 r"[+-]?[0-9]+"，不要用会匹配更多 Unicode 数字的 \\d。'],
    '规则只认识整数片段，因此点号会中断匹配。明确限定 ASCII 数字让行为不受文本中的其他数字字符影响。')

add(13, 'fullmatch 验证用户名',
    're.fullmatch 要求整个字符串都符合规则。{m,n} 限制重复次数；[A-Za-z] 表示 ASCII 字母。匹配成功得到对象，失败得到 None。',
    'import re\nbool(re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{2,11}", "Ada_2"))',
    '用户名长度须为 3～12，第一位为 ASCII 字母，其余只允许 ASCII 字母、数字、下划线。返回布尔值。空字符串、中文、空格以及换行均不合法。',
    [('name', 'str', '长度不超过 30')],
    [(['Ada_2'], True), (['2ada'], False), (['ab'], False), (['abcdefghijkl'], True),
     (['abcdefghijklm'], False), (['a中b'], False), (['abc\n'], False)],
    'import re\ndef solve(name):\n    return re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{2,11}", name) is not None',
    ['先单独约束第一个字符。', '总长度 3～12，意味着后续部分重复 2～11 次。', '使用 fullmatch 并判断结果 is not None。'],
    'fullmatch 防止只验证字符串的一部分。把首字符与后续字符分开书写，长度和字符范围就能一次表达清楚。')

add(13, 'sub 统一空白字符',
    're.sub(pattern, replacement, text) 替换所有匹配。\\s 匹配空格、制表符、换行等 Unicode 空白，\\s+ 匹配一个连续空白段。',
    'import re\nre.sub(r"\\s+", " ", "a\\t\\nb")  # "a b"',
    '将 text 的每段连续空白替换为一个普通空格，并删除首尾空白。除空白外的字符原样保留；全为空白或空字符串时返回空字符串。',
    [('text', 'str', '长度不超过 200')],
    [(['  a\t\nb  '], 'a b'), (['\n\t '], ''), ([''], ''), (['Hello,  world!'], 'Hello, world!'), (['中\u3000文'], '中 文')],
    'import re\ndef solve(text):\n    return re.sub(r"\\s+", " ", text).strip()',
    ['用 \\s+ 匹配连续空白，而不是只匹配普通空格。', '替换内容固定为一个普通空格。', '对替换结果调用 strip() 清除首尾空格。'],
    'sub 负责压缩内部空白，strip 处理边界。两步合起来使空白文本也稳定得到空字符串。')

add(13, '正则捕获组重排日期',
    '正则中的 (...) 捕获匹配子串；替换字符串中的 \\g<1> 引用第一组。只捕获需要重排的部分可以简化文本变换。',
    're.sub(r"([0-9]{4})/([0-9]{2})/([0-9]{2})", r"\\g<3>-\\g<2>-\\g<1>", text)',
    '把 text 中所有形如四位数字/两位数字/两位数字的片段重排为 DD-MM-YYYY。仅按字符模式替换，不验证真实日期，也不要求词边界；其他内容原样保留。',
    [('text', 'str', '长度不超过 200')],
    [(['日期 2024/01/09'], '日期 09-01-2024'), (['2023/12/31;2024/01/01'], '31-12-2023;01-01-2024'),
     (['2024/1/09'], '2024/1/09'), ([''], ''), (['x2024/99/88y'], 'x88-99-2024y')],
    'import re\ndef solve(text):\n    return re.sub(r"([0-9]{4})/([0-9]{2})/([0-9]{2})", r"\\g<3>-\\g<2>-\\g<1>", text)',
    ['年月日分别用一个捕获组。', '组号按左括号出现顺序从 1 开始。', '替换字符串按第 3、2、1 组排列，中间放连字符。'],
    '捕获组保留原始数字文本，替换时只更换顺序与分隔符。这里练习正则重排，与真正验证日历日期是不同任务。')

add(13, 'PurePosixPath 拆解文件名',
    'PurePosixPath 只分析路径字符串，不访问文件系统，统一使用 /。name 是最后一段，stem 去掉最后一个扩展名，suffix 是最后一个扩展名。',
    'from pathlib import PurePosixPath\np = PurePosixPath("data/archive.tar.gz")\n[p.name, p.stem, p.suffix]  # ["archive.tar.gz", "archive.tar", ".gz"]',
    '返回 path 的 {"name": 文件名, "stem": 去最后扩展名的名称, "suffix": 最后扩展名}。路径为非空 POSIX 文件路径，最后一段不是 . 或 ..，不以 / 或 . 结尾；不实际读取文件。',
    [('path', 'str', 'POSIX 文件路径')],
    [(['data/archive.tar.gz'], {'name': 'archive.tar.gz', 'stem': 'archive.tar', 'suffix': '.gz'}),
     (['/tmp/a.txt'], {'name': 'a.txt', 'stem': 'a', 'suffix': '.txt'}), (['README'], {'name': 'README', 'stem': 'README', 'suffix': ''}),
     (['.gitignore'], {'name': '.gitignore', 'stem': '.gitignore', 'suffix': ''}), (['a/b.csv'], {'name': 'b.csv', 'stem': 'b', 'suffix': '.csv'})],
    'from pathlib import PurePosixPath\ndef solve(path):\n    p = PurePosixPath(path)\n    return {"name": p.name, "stem": p.stem, "suffix": p.suffix}',
    ['需要跨操作系统得到同样的 / 解析规则，使用 PurePosixPath。', 'name、stem、suffix 都是属性，读取不带括号。', '创建 p 后把三个属性按题目键名放进字典。'],
    '纯路径对象不依赖文件是否存在。多重扩展名只剥去最后一层，隐藏文件 .gitignore 没有后缀。')

add(13, '用斜线运算符拼接路径',
    '路径对象重载了 / 运算符，可以写 base / child。PurePosixPath 会合并重复斜线与 . 段，但不会消去 ..，因为它不访问真实目录。',
    'from pathlib import PurePosixPath\nstr(PurePosixPath("data") / "images" / "a.png")\n# "data/images/a.png"',
    '从 base 开始依次拼接 parts，返回 POSIX 路径字符串。base 非空；parts 各项都是非空相对路径，不以 / 开头。保留 .. 段，不调用 resolve；parts 可为空。',
    [('base', 'str', '起始路径'), ('parts', 'list[str]', '至多 10 个相对路径片段')],
    [(['data', ['images', 'a.png']], 'data/images/a.png'), (['/tmp/', ['a', '..', 'b']], '/tmp/a/../b'),
     (['.', ['x']], 'x'), (['a//b', []], 'a/b'), (['root', ['./a', 'b/c']], 'root/a/b/c')],
    'from pathlib import PurePosixPath\ndef solve(base, parts):\n    path = PurePosixPath(base)\n    for part in parts:\n        path = path / part\n    return str(path)',
    ['先把 base 转成路径对象。', '循环中使用 path = path / part，每步保存新路径。', '最后 str(path)；不要用字符串替换来消除 ..。'],
    '路径拼接比手动添加斜线更清楚，自动整理冗余分隔符。.. 的实际意义依赖目录结构，因此纯路径保留它。')

add(13, 'SQLite 参数化筛选成绩',
    'sqlite3.connect(":memory:") 创建内存数据库。execute 中用 ? 占位、第二参数传值，避免把输入拼成 SQL；fetchall 读取结果行。',
    'cursor = connection.execute("SELECT name FROM scores WHERE score >= ? ORDER BY name", (minimum,))\nrows = cursor.fetchall()',
    'records 为 [姓名, 整数分数] 列表。建立内存 scores 表，查询分数不低于 minimum 的姓名，按 SQLite 默认二进制文本顺序升序返回，重复记录保留。姓名为 ASCII，可含引号；不创建磁盘数据库。',
    [('records', 'list[list]', '至多 30 条记录'), ('minimum', 'int', '最低分')],
    [([[['Bob', 70], ['Ada', 90], ['Cal', 60]], 70], ['Ada', 'Bob']), ([[], 0], []),
     ([[["O'Neil", 80], ['A', 50]], 80], ["O'Neil"]), ([[['x', 1], ['x', 2]], 0], ['x', 'x']), ([[['A', 9]], 10], [])],
    '''import sqlite3
def solve(records, minimum):
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("CREATE TABLE scores (name TEXT, score INTEGER)")
        connection.executemany("INSERT INTO scores VALUES (?, ?)", records)
        rows = connection.execute("SELECT name FROM scores WHERE score >= ? ORDER BY name", (minimum,)).fetchall()
        return [row[0] for row in rows]
    finally:
        connection.close()
''',
    ['先 CREATE TABLE，再 executemany 插入输入记录。', 'minimum 用 ? 占位，单元素参数元组要写 (minimum,)。', 'SELECT name ... ORDER BY name 后 fetchall，每行取 row[0]；finally 关闭连接。'],
    '参数化插入能正确处理姓名里的引号。查询只选择需要的列，并明确排序；finally 让每次练习都释放独立的内存数据库。')

add(13, 'SQLite GROUP BY 汇总销售',
    'SQL 的 GROUP BY 将同类行汇集，SUM(amount) 在每组内求和。ORDER BY 明确结果顺序；SQL 行通常以元组返回。',
    'SELECT category, SUM(amount) FROM sales GROUP BY category ORDER BY category',
    'records 每项为 [ASCII 类别, 整数金额]，金额可为负。使用内存 SQLite 按类别合计，返回按类别升序排列的 [[类别, 总额], ...]。空输入返回 []。',
    [('records', 'list[list]', '至多 40 条销售记录')],
    [([[['b', 2], ['a', 3], ['b', 5]]], [['a', 3], ['b', 7]]), ([[]], []),
     ([[['x', 4], ['x', -4]]], [['x', 0]]), ([[['z', -3]]], [['z', -3]]), ([[['A', 1], ['a', 2]]], [['A', 1], ['a', 2]])],
    '''import sqlite3
def solve(records):
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("CREATE TABLE sales (category TEXT, amount INTEGER)")
        connection.executemany("INSERT INTO sales VALUES (?, ?)", records)
        rows = connection.execute("SELECT category, SUM(amount) FROM sales GROUP BY category ORDER BY category").fetchall()
        return [list(row) for row in rows]
    finally:
        connection.close()
''',
    ['建表需要文本 category 与整数 amount 两列。', 'GROUP BY category 配合 SUM(amount) 计算分组总额。', '增加 ORDER BY category，再把 fetchall 的每个元组转成列表。'],
    '数据库负责分组累加，负金额自然抵消正金额。即使组内总和是零，该类别仍应保留。')

add(13, 'urlsplit 读取链接结构',
    'urlsplit 将 URL 分成 scheme、netloc、path、query、fragment。hostname 是主机名，排除端口且统一为小写；缺失时是 None。此函数只解析，不发出网络请求。',
    'from urllib.parse import urlsplit\nu = urlsplit("https://Example.com:8080/a?q=1#top")\nu.hostname  # "example.com"',
    '返回 url 的 {"scheme": 协议, "host": 主机名或空字符串, "path": 路径, "query": 查询文本}。URL 为有效 http/https 绝对链接或以 / 开头的相对路径，不含凭据或 IPv6。路径与 query 不做百分号解码；忽略 fragment。',
    [('url', 'str', '长度不超过 200 的链接或路径')],
    [(['https://Example.com:8080/a?q=1#top'], {'scheme': 'https', 'host': 'example.com', 'path': '/a', 'query': 'q=1'}),
     (['/search?q=hi'], {'scheme': '', 'host': '', 'path': '/search', 'query': 'q=hi'}),
     (['http://a.com'], {'scheme': 'http', 'host': 'a.com', 'path': '', 'query': ''}),
     (['https://x.test/a%20b#x'], {'scheme': 'https', 'host': 'x.test', 'path': '/a%20b', 'query': ''}),
     (['/'], {'scheme': '', 'host': '', 'path': '/', 'query': ''})],
    'from urllib.parse import urlsplit\ndef solve(url):\n    parts = urlsplit(url)\n    return {"scheme": parts.scheme, "host": parts.hostname or "", "path": parts.path, "query": parts.query}',
    ['不必手动按 : 或 / 切割 URL。', 'host 要读 hostname，netloc 可能包含端口。', '用 parts.hostname or "" 处理相对路径没有主机名的情况。'],
    '结构解析将路径、查询和片段区分开，但不解码路径文本。没有路径的绝对 URL 返回空路径，而不是自动补一个斜线。')

add(13, 'parse_qs 解码查询参数',
    'parse_qs 将查询文本解析为字典，每个键的值始终是列表，以保留重复参数。keep_blank_values=True 保留空值；+ 解码为空格，%xx 按 UTF-8 解码。',
    'from urllib.parse import parse_qs\nparse_qs("tag=a&tag=b&empty=", keep_blank_values=True)\n# {"tag": ["a", "b"], "empty": [""]}',
    '解析不含开头 ? 的 query，返回参数字典。保留空值和同键多值的出现顺序；无等号的键也按空值处理。输入百分号编码合法。',
    [('query', 'str', '长度不超过 200 的查询字符串')],
    [(['tag=a&tag=b&empty='], {'tag': ['a', 'b'], 'empty': ['']}), (['q=hello+world'], {'q': ['hello world']}),
     ([''], {}), (['flag&x=1'], {'flag': [''], 'x': ['1']}), (['q=%E4%B8%AD&plus=%2B'], {'q': ['中'], 'plus': ['+']})],
    'from urllib.parse import parse_qs\ndef solve(query):\n    return parse_qs(query, keep_blank_values=True)',
    ['一个参数名可能出现多次，不能只保留一个字符串。', '默认会丢弃空值，所以必须指定 keep_blank_values=True。', 'parse_qs 会处理 + 与百分号解码，直接返回它的字典即可。'],
    '查询字符串不是简单的 & 和 = 分割：它还有编码与多值规则。parse_qs 统一处理这些细节，空查询自然得到空字典。')

# Chapter 14 — a first encounter with ndarray.
add(14, '认识数组的形状与维度',
    'np.array 将嵌套列表转换为数组。shape 是各轴长度的元组，ndim 是轴的数量，size 是元素总数；这些都是属性。',
    'import numpy as np\na = np.array([[1, 2, 3], [4, 5, 6]])\na.shape  # (2, 3)\na.ndim  # 2\na.size  # 6',
    '将 matrix 转为 NumPy 数组，返回 {"shape": 形状列表, "ndim": 维数, "size": 元素数}。matrix 是 1～10 行、1～10 列的非空矩形整数列表。返回普通 Python 数值和列表。',
    [('matrix', 'list[list[int]]', '非空且各行等长')],
    [([[[1, 2, 3], [4, 5, 6]]], {'shape': [2, 3], 'ndim': 2, 'size': 6}),
     ([[[9]]], {'shape': [1, 1], 'ndim': 2, 'size': 1}), ([[[1, 2]]], {'shape': [1, 2], 'ndim': 2, 'size': 2}),
     ([[[1], [2], [3]]], {'shape': [3, 1], 'ndim': 2, 'size': 3}), ([[[0, 0], [0, 0]]], {'shape': [2, 2], 'ndim': 2, 'size': 4})],
    'import numpy as np\ndef solve(matrix):\n    array = np.array(matrix)\n    return {"shape": list(array.shape), "ndim": array.ndim, "size": array.size}',
    ['二维列表的两条轴分别是行与列。', 'shape 是元组，要转成列表。', '读取 array.shape、array.ndim、array.size，按题目键名返回。'],
    '即使只有一行或一个元素，只要输入是二维嵌套列表，ndim 仍为 2。size 等于行数乘列数。', requires=['numpy'])

add(14, 'arange 生成等差数组',
    'np.arange(start, stop, step) 类似 range：包含起点，不包含终点。返回 ndarray，使用 tolist() 转成普通列表。',
    'np.arange(1, 8, 2).tolist()  # [1, 3, 5, 7]',
    '使用 np.arange 返回从 start 到 stop（不含 stop）、间隔为 step 的整数列表。step 为非零整数；允许负步长，方向不匹配时返回 []。输入绝对值不超过 100。',
    [('start', 'int', '起点'), ('stop', 'int', '不包含的终点'), ('step', 'int', '非零步长')],
    [([1, 8, 2], [1, 3, 5, 7]), ([5, 0, -2], [5, 3, 1]), ([0, 0, 1], []), ([1, 5, -1], []), ([-3, 4, 3], [-3, 0, 3])],
    'import numpy as np\ndef solve(start, stop, step):\n    return np.arange(start, stop, step).tolist()',
    ['起点包含在结果里，终点不包含。', '负步长直接交给 arange，无需反转结果。', 'np.arange(start, stop, step).tolist() 返回可展示的普通列表。'],
    '整数参数避免浮点步长误差。NumPy 根据步长方向判断是否有元素，方向不匹配时数组为空。', requires=['numpy'])

add(14, 'eye 创建单位矩阵',
    'np.eye(n, dtype=int) 创建 n×n 的单位矩阵：主对角线为 1，其余为 0。dtype 指定元素类型。',
    'np.eye(2, dtype=int).tolist()  # [[1, 0], [0, 1]]',
    '返回 n 阶整数单位矩阵的二维列表。n 为 0～5；n=0 时返回 []。',
    [('n', 'int', '矩阵阶数')],
    [([2], [[1, 0], [0, 1]]), ([0], []), ([1], [[1]]), ([3], [[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
     ([4], [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])],
    'import numpy as np\ndef solve(n):\n    return np.eye(n, dtype=int).tolist()',
    ['单位矩阵的行号等于列号时取 1。', 'eye 可以直接创建这种结构，不需要双层循环。', '指定 dtype=int 后 tolist()，返回整数矩阵。'],
    'eye 默认生成浮点数，显式指定 dtype 能让结果符合整数矩阵的表达习惯。零阶矩阵转换后为空列表。', requires=['numpy'])

add(14, 'zeros 与 ones 初始化',
    'np.zeros(n) 和 np.ones(n) 分别创建长度为 n 的全零、全一数组。二维形状使用元组，例如 np.zeros((2, 3))。',
    'np.zeros(3, dtype=int).tolist()  # [0, 0, 0]\nnp.ones(2, dtype=int).tolist()   # [1, 1]',
    '返回 {"zeros": 长度 n 的全零整数列表, "ones": 长度 n 的全一整数列表}。n 为 0～10，零长度时两个列表都为空。',
    [('n', 'int', '数组长度')],
    [([3], {'zeros': [0, 0, 0], 'ones': [1, 1, 1]}), ([0], {'zeros': [], 'ones': []}),
     ([1], {'zeros': [0], 'ones': [1]}), ([2], {'zeros': [0, 0], 'ones': [1, 1]}),
     ([4], {'zeros': [0, 0, 0, 0], 'ones': [1, 1, 1, 1]})],
    'import numpy as np\ndef solve(n):\n    return {"zeros": np.zeros(n, dtype=int).tolist(), "ones": np.ones(n, dtype=int).tolist()}',
    ['零数组和一数组使用两个不同的创建函数。', '显式指定 dtype=int。', '两个数组分别 tolist()，再放入 zeros 和 ones 键。'],
    '初始化数组是建立计数器、模型参数和占位数据的常见起点。创建函数直接接受目标长度。', requires=['numpy'])

add(14, 'reshape 将向量变成矩阵',
    'reshape(rows, cols) 改变数组形状，元素数量必须不变。默认按行填入：先填第一行，再填第二行。',
    'np.array([1, 2, 3, 4]).reshape(2, 2).tolist()\n# [[1, 2], [3, 4]]',
    '将 values 按行重排为 rows 行、cols 列的二维列表。rows、cols 为 1～6，保证 len(values)=rows*cols。',
    [('values', 'list[int]', '待重排数据'), ('rows', 'int', '行数'), ('cols', 'int', '列数')],
    [([[1, 2, 3, 4, 5, 6], 2, 3], [[1, 2, 3], [4, 5, 6]]), ([[8], 1, 1], [[8]]),
     ([[1, 2, 3], 3, 1], [[1], [2], [3]]), ([[3, 2, 1], 1, 3], [[3, 2, 1]]), ([[0, -1, 2, 3], 2, 2], [[0, -1], [2, 3]])],
    'import numpy as np\ndef solve(values, rows, cols):\n    return np.array(values).reshape(rows, cols).tolist()',
    ['先把列表转为一维 ndarray。', '形状参数按行数、列数排列。', 'array.reshape(rows, cols).tolist() 保持原始元素先后顺序。'],
    'reshape 改变的是索引方式，不做排序。元素数相同是能重排的前提，题目已保证这一点。', requires=['numpy'])

add(14, 'NumPy 切片的起止与步长',
    '一维 ndarray 支持 array[start:stop:step]，与列表切片一样不包含 stop，越界边界会自动截断。切片通常共享原数组数据。',
    'np.array([0, 1, 2, 3, 4])[1:5:2].tolist()  # [1, 3]',
    '返回 values 在 start:stop:step 切片后的列表。start、stop 是整数，可为负或越界；step 是非零整数。仅读取切片，不修改原数组。',
    [('values', 'list[int]', '至多 30 项'), ('start', 'int', '起始索引'), ('stop', 'int', '结束索引'), ('step', 'int', '非零步长')],
    [([[0, 1, 2, 3, 4], 1, 5, 2], [1, 3]), ([[0, 1, 2, 3], 3, 0, -1], [3, 2, 1]),
     ([[], 0, 9, 1], []), ([[1, 2, 3], -2, 10, 1], [2, 3]), ([[1, 2, 3], 2, 0, 1], [])],
    'import numpy as np\ndef solve(values, start, stop, step):\n    return np.array(values)[start:stop:step].tolist()',
    ['切片语法放在数组后的方括号里。', '负步长按反向遍历，仍然不包含 stop。', 'np.array(values)[start:stop:step] 后调用 tolist()。'],
    'NumPy 延续了 Python 切片规则。理解步长方向和终点排除，比记住某一种反转写法更通用。', requires=['numpy'])

add(14, '整数数组索引挑选元素',
    'array[[2, 0, 2]] 可一次按指定下标取多个元素，称为高级索引。顺序由索引列表决定，允许重复及负下标。',
    'np.array([10, 20, 30])[[2, 0, 2]].tolist()  # [30, 10, 30]',
    '按照 indices 给定的顺序从 values 取值，返回列表。values 非空，所有索引合法，indices 可以为空；重复索引须重复输出。',
    [('values', 'list[int]', '1～30 项'), ('indices', 'list[int]', '至多 30 个合法下标')],
    [([[10, 20, 30], [2, 0, 2]], [30, 10, 30]), ([[8], []], []), ([[1, 2, 3], [-1, -3]], [3, 1]),
     ([[5], [0, 0]], [5, 5]), ([[3, 4, 5], [0, 1, 2]], [3, 4, 5])],
    'import numpy as np\ndef solve(values, indices):\n    return np.array(values)[np.array(indices, dtype=int)].tolist()',
    ['一次传入一整组索引，和只传一个索引不同。', '空索引数组也必须明确为整数类型。', '将 indices 转成 np.array(indices, dtype=int)，再作为方括号里的索引。'],
    '高级索引按提供的索引顺序取值。显式整数 dtype 避免空列表转换成浮点数组后不能作索引的问题。', requires=['numpy'])

add(14, 'concatenate 拼接数组',
    'np.concatenate 接收一个数组序列，把它们沿已有的轴连接。一维数组连接后仍然是一维，而不是嵌套两行。',
    'np.concatenate((np.array([1, 2]), np.array([3]))).tolist()\n# [1, 2, 3]',
    '将整数列表 left 和 right 转成数组后连接，返回一维列表。保留顺序与重复项；任意一侧都可为空。',
    [('left', 'list[int]', '左侧数据'), ('right', 'list[int]', '右侧数据')],
    [([[1, 2], [3]], [1, 2, 3]), ([[], [4]], [4]), ([[5], []], [5]), ([[], []], []), ([[-1, 0], [0, 2]], [-1, 0, 0, 2])],
    'import numpy as np\ndef solve(left, right):\n    return np.concatenate((np.array(left, dtype=int), np.array(right, dtype=int))).tolist()',
    ['传给 concatenate 的是装着两个数组的元组。', '两个输入都使用 dtype=int，空数组也保持类型。', 'np.concatenate((a, b)).tolist() 得到一维结果。'],
    'concatenate 延长已有轴，区别于新增维度的 stack。第一个数组的全部元素出现在第二个数组之前。', requires=['numpy'])

add(14, 'stack 为数据增加一个维度',
    'np.stack((a, b), axis=0) 把等形状数组沿新轴堆叠。一维向量变为两行矩阵；所有输入形状必须相同。',
    'np.stack(([1, 2], [3, 4]), axis=0).tolist()  # [[1, 2], [3, 4]]',
    '将等长列表 first、second 沿 axis=0 堆成两行，返回二维列表。长度为 0～10；两个空列表返回 [[], []]。',
    [('first', 'list[int]', '第一行'), ('second', 'list[int]', '第二行，长度相同')],
    [([[1, 2], [3, 4]], [[1, 2], [3, 4]]), ([[], []], [[], []]), ([[9], [8]], [[9], [8]]),
     ([[0, 0], [1, 1]], [[0, 0], [1, 1]]), ([[-1, 2, 3], [4, 5, 6]], [[-1, 2, 3], [4, 5, 6]])],
    'import numpy as np\ndef solve(first, second):\n    return np.stack((np.array(first, dtype=int), np.array(second, dtype=int)), axis=0).tolist()',
    ['这里要新增行维度，而不是拼成更长的一维向量。', '使用 stack 并指定 axis=0。', '把两个等长数组放进元组，传给 np.stack 后 tolist。'],
    'stack 的新轴记录数据来自哪个输入。即使每行零个元素，仍然保留两行结构。', requires=['numpy'])

add(14, 'astype 转换数值类型',
    'astype(int) 将数组转换为整数类型。浮点转整数会朝零截断，和 floor 向负无穷取整不同。',
    'np.array(["2.9", "-2.9"], dtype=float).astype(int).tolist()\n# [2, -2]',
    'texts 是合法有限小数字符串列表。先转换为浮点数组，再 astype(int)，返回朝零截断的整数列表。数值绝对值小于 10000，不含 NaN 或无穷。空列表返回 []。',
    [('texts', 'list[str]', '至多 30 个数字文本')],
    [([['2.9', '-2.9']], [2, -2]), ([[]], []), ([['0.9', '-0.9', '0']], [0, 0, 0]),
     ([['5', '10.0']], [5, 10]), ([['1e2', '-3.1']], [100, -3])],
    'import numpy as np\ndef solve(texts):\n    return np.array(texts, dtype=float).astype(int).tolist()',
    ['含小数点的字符串不能直接当作整数文本解析。', '先 dtype=float，再 astype(int)。', '负数 -2.9 截断后是 -2，用 tolist 返回普通整数。'],
    '两次转换分别完成文本解析与数值类型转换。朝零截断丢掉小数部分，不是四舍五入。', requires=['numpy'])

# Chapter 15 — array computation and linear algebra.
add(15, '数组逐元素运算',
    'NumPy 中等形状数组的 +、-、* 是逐元素运算；Python 列表的 + 则是拼接。数组 ** 2 表示每个元素平方。',
    'a = np.array([1, 2])\nb = np.array([3, 4])\n(a * b).tolist()  # [3, 8]',
    '输入等长整数列表 a、b，返回每个位置 a[i]*b[i]+a[i] 的结果列表。长度 0～30，元素绝对值至多 100。',
    [('a', 'list[int]', '第一个向量'), ('b', 'list[int]', '等长第二向量')],
    [([[1, 2], [3, 4]], [4, 10]), ([[], []], []), ([[0, -2], [9, 3]], [0, -8]),
     ([[5], [-1]], [0]), ([[-1, 2, 3], [-2, 0, 1]], [1, 2, 6])],
    'import numpy as np\ndef solve(a, b):\n    left = np.array(a, dtype=int)\n    right = np.array(b, dtype=int)\n    return (left * right + left).tolist()',
    ['先将两个列表转为数组，否则 * 和 + 的意义不同。', '乘法和加法都可以一次作用于整个数组。', '计算 left * right + left，再调用 tolist。'],
    'NumPy 将公式应用到每一对对应元素，不需要显式 Python 循环。这类向量化表达更接近数学公式。', requires=['numpy'])

add(15, '广播：每行加同一个向量',
    '广播允许形状兼容的数组相加。形状 (rows, cols) 的矩阵加 (cols,) 向量时，这个向量会作用到每一行，不必手动复制。',
    '(np.array([[1, 2], [3, 4]]) + np.array([10, 20])).tolist()\n# [[11, 22], [13, 24]]',
    '给 matrix 的每一行逐项加上 offset，返回二维列表。矩阵为非空矩形，offset 长度等于列数；行列数均为 1～6。',
    [('matrix', 'list[list[int]]', '原始矩阵'), ('offset', 'list[int]', '每列偏移量')],
    [([[[1, 2], [3, 4]], [10, 20]], [[11, 22], [13, 24]]), ([[[5]], [-2]], [[3]]),
     ([[[1], [2], [3]], [10]], [[11], [12], [13]]), ([[[1, 2, 3]], [0, -2, 3]], [[1, 0, 6]]),
     ([[[0, 0], [0, 0]], [1, -1]], [[1, -1], [1, -1]])],
    'import numpy as np\ndef solve(matrix, offset):\n    return (np.array(matrix) + np.array(offset)).tolist()',
    ['offset 代表每列需要增加的值。', '广播从最右侧的维度比较大小，列数必须匹配。', '直接 np.array(matrix) + np.array(offset)，再 tolist。'],
    '广播隐式复用 offset，并不会要求你先建立一份重复矩阵。它是批量标准化和模型计算的常用机制。', requires=['numpy'])

add(15, 'axis：按行与按列求和',
    '二维数组 sum(axis=0) 沿着行方向压缩，留下每一列的和；sum(axis=1) 沿列方向压缩，留下每一行的和。',
    'a = np.array([[1, 2], [3, 4]])\na.sum(axis=0).tolist()  # [4, 6]\na.sum(axis=1).tolist()  # [3, 7]',
    '返回 matrix 的 {"rows": 每行之和, "columns": 每列之和}。矩阵非空且矩形，最多 6×6，元素为整数。',
    [('matrix', 'list[list[int]]', '非空整数矩阵')],
    [([[[1, 2], [3, 4]]], {'rows': [3, 7], 'columns': [4, 6]}), ([[[7]]], {'rows': [7], 'columns': [7]}),
     ([[[1, 2, 3]]], {'rows': [6], 'columns': [1, 2, 3]}), ([[[1], [-1]]], {'rows': [1, -1], 'columns': [0]}),
     ([[[0, 2], [0, -2], [1, 1]]], {'rows': [2, -2, 2], 'columns': [1, 1]})],
    'import numpy as np\ndef solve(matrix):\n    array = np.array(matrix)\n    return {"rows": array.sum(axis=1).tolist(), "columns": array.sum(axis=0).tolist()}',
    ['axis 指被压缩的轴，而不是结果的名称。', '每行结果用 axis=1，每列结果用 axis=0。', '两个 sum 结果分别 tolist，再组装 rows 与 columns。'],
    '沿某轴聚合后，该轴消失。检查输出长度也能防止写反：行和数量应等于行数，列和数量应等于列数。', requires=['numpy'])

add(15, '布尔掩码筛选及格值',
    'array >= threshold 会生成布尔数组，称为掩码。array[mask] 只保留 True 位置的元素，保持原始顺序。',
    'a = np.array([40, 80, 60])\na[a >= 60].tolist()  # [80, 60]',
    '返回 values 中大于或等于 threshold 的数值列表，保持顺序与重复。空列表或无人达标时返回 []。',
    [('values', 'list[int]', '至多 50 个数'), ('threshold', 'int', '包含边界的阈值')],
    [([[40, 80, 60], 60], [80, 60]), ([[], 0], []), ([[1, 2], 3], []),
     ([[2, 2, 1], 2], [2, 2]), ([[-5, 0, -1], -1], [0, -1])],
    'import numpy as np\ndef solve(values, threshold):\n    array = np.array(values, dtype=int)\n    return array[array >= threshold].tolist()',
    ['比较整个数组会得到一组布尔值。', '条件使用 >=，等于阈值也要保留。', '把 array >= threshold 放进 array 的索引方括号里。'],
    '布尔索引表达“选出满足条件的元素”。它只筛选，不会更改数值或排序。', requires=['numpy'])

add(15, 'where 进行条件替换',
    'np.where(condition, x, y) 在条件为 True 的位置取 x，否则取 y。与布尔筛选不同，它保留原数组形状。',
    'a = np.array([-2, 0, 3])\nnp.where(a < 0, 0, a).tolist()  # [0, 0, 3]',
    '将 values 中的负数替换为 0，其余保持不变，返回与输入等长的列表。允许空列表，元素为有限整数。',
    [('values', 'list[int]', '至多 50 个整数')],
    [([[-2, 0, 3]], [0, 0, 3]), ([[]], []), ([[-1, -9]], [0, 0]), ([[1, 2]], [1, 2]), ([[0, -1, 0]], [0, 0, 0])],
    'import numpy as np\ndef solve(values):\n    array = np.array(values, dtype=int)\n    return np.where(array < 0, 0, array).tolist()',
    ['不要把负数删除，需要保留它们的位置。', '条件为 array < 0，满足时选择 0。', 'np.where(array < 0, 0, array) 的第三参数保留原值。'],
    'where 是向量化的逐元素 if/else。输入有几个元素，结果就有几个元素。', requires=['numpy'])

add(15, 'dot 计算向量内积',
    '一维数组的 np.dot(a, b) 计算对应元素乘积的总和。结果是标量；NumPy 标量可用 int 或 float 转为 Python 数值。',
    'np.dot([1, 2, 3], [4, 5, 6])  # 32',
    '返回等长整数向量 a、b 的内积。长度 0～20，元素绝对值至多 100；空向量内积为 0。',
    [('a', 'list[int]', '第一向量'), ('b', 'list[int]', '第二向量')],
    [([[1, 2, 3], [4, 5, 6]], 32), ([[], []], 0), ([[1, 0], [0, 1]], 0),
     ([[-2, 3], [4, -1]], -11), ([[5], [6]], 30)],
    'import numpy as np\ndef solve(a, b):\n    return int(np.dot(np.array(a, dtype=int), np.array(b, dtype=int)))',
    ['内积结果是一个数，不是乘积列表。', 'np.dot 对一维数组自动求乘积的总和。', '用 int 包裹 np.dot 的结果，让它成为普通 Python 整数。'],
    '内积把两组特征组合成单个值，是线性模型预测的基础运算之一。空整数数组的内积为零。', requires=['numpy'])

add(15, '@ 实现矩阵乘法',
    '数组的 @ 运算符做矩阵乘法，* 做逐元素乘法。若 A 形状为 (m,k)、B 为 (k,n)，则 A @ B 形状为 (m,n)。',
    '(np.array([[1, 2]]) @ np.array([[3], [4]])).tolist()  # [[11]]',
    '返回 left 与 right 的矩阵乘积。两者都是非空矩形整数矩阵，保证 left 列数等于 right 行数，各维度 1～5。',
    [('left', 'list[list[int]]', '左矩阵'), ('right', 'list[list[int]]', '右矩阵')],
    [([[[1, 2]], [[3], [4]]], [[11]]), ([[[1, 0], [0, 1]], [[2, 3], [4, 5]]], [[2, 3], [4, 5]]),
     ([[[2]], [[3]]], [[6]]), ([[[1], [2]], [[3, 4]]], [[3, 4], [6, 8]]),
     ([[[1, -1], [2, 0]], [[1, 2], [3, 4]]], [[-2, -2], [2, 4]])],
    'import numpy as np\ndef solve(left, right):\n    return (np.array(left) @ np.array(right)).tolist()',
    ['结果第 i,j 项来自左矩阵第 i 行与右矩阵第 j 列的内积。', '矩阵乘法用 @，不要用 *。', '两边先转成 ndarray，再计算 @ 并 tolist。'],
    '矩阵乘法把多个内积集中表达，输出不一定与任一输入形状相同。公共维度负责求和并在结果中消失。', requires=['numpy'])

add(15, '最小最大值归一化',
    '数组 min() 与 max() 得到极值；(a-min)/(max-min) 将范围映射到 0～1。分母为零时必须明确处理。',
    'a = np.array([2, 4, 6], dtype=float)\n((a - a.min()) / (a.max() - a.min())).tolist()  # [0.0, 0.5, 1.0]',
    '对非空 values 做最小最大值归一化，各项 round 到六位。所有值相等时约定返回等长全零列表。输入为 1～30 个有限整数。',
    [('values', 'list[int]', '非空数值列表')],
    [([[2, 4, 6]], [0, 0.5, 1]), ([[5, 5]], [0, 0]), ([[8]], [0]),
     ([[-2, 0, 2]], [0, 0.5, 1]), ([[0, 1, 3]], [0, 0.333333, 1])],
    'import numpy as np\ndef solve(values):\n    array = np.array(values, dtype=float)\n    span = array.max() - array.min()\n    if span == 0:\n        return np.zeros(len(values)).tolist()\n    return np.round((array - array.min()) / span, 6).tolist()',
    ['先求最大值和最小值的差。', '差等于零时直接返回全零，避免除零。', '否则整个数组减最小值、除以差，再 np.round(..., 6)。'],
    '归一化保持相对大小。常量数组没有可区分的范围，所以题目定义它统一映射到零。', requires=['numpy'])

add(15, 'NaN 与忽略缺失值求均值',
    '浮点数组中的 np.nan 表示缺失值。np.isnan 检测缺失，np.nanmean 忽略缺失计算均值；普通 mean 会被 NaN 传播。',
    'a = np.array([1, np.nan, 3])\nnp.isnan(a).tolist()  # [False, True, False]\nnp.nanmean(a)  # 2.0',
    'values 中数字或 None 表示观测值与缺失值。忽略 None 求平均，round 到六位；若没有有效值（包括空列表），返回 None。不返回 NaN。',
    [('values', 'list[float | None]', '至多 30 项，非缺失数均有限')],
    [([[1, None, 3]], 2.0), ([[None, None]], None), ([[]], None), ([[0, None]], 0.0), ([[1, 2, 2]], 1.666667)],
    'import numpy as np\ndef solve(values):\n    array = np.array(values, dtype=float)\n    if not np.any(~np.isnan(array)):\n        return None\n    return round(float(np.nanmean(array)), 6)',
    ['转换为 dtype=float 时 None 会成为 np.nan。', '先检查是否至少有一个非 NaN 元素。', '有有效值再调用 np.nanmean，无有效值直接返回 None。'],
    '显式处理全缺失避免空均值警告，并保证返回合法 JSON。~ 对布尔掩码取反，np.any 判断是否存在有效元素。', requires=['numpy'])

add(15, 'linalg.solve 解线性方程组',
    'np.linalg.solve(A, b) 求满足 A @ x = b 的向量 x。A 必须为非奇异方阵；求解方程通常不需要先显式计算逆矩阵。',
    'np.linalg.solve([[2, 0], [0, 4]], [6, 8]).tolist()  # [3.0, 2.0]',
    '给定可逆的 2×2 系数矩阵 coefficients 和长度 2 的常数向量 target，返回解 [x,y]，各项四舍五入到六位。系数和目标均为绝对值至多 100 的整数。',
    [('coefficients', 'list[list[int]]', '非奇异 2×2 矩阵'), ('target', 'list[int]', '方程右侧常数')],
    [([[[2, 0], [0, 4]], [6, 8]], [3, 2]), ([[[1, 1], [1, -1]], [4, 2]], [3, 1]),
     ([[[1, 0], [0, 1]], [-2, 5]], [-2, 5]), ([[[3, 0], [0, 2]], [1, 1]], [0.333333, 0.5]),
     ([[[2, 1], [1, 3]], [0, 0]], [0, 0])],
    'import numpy as np\ndef solve(coefficients, target):\n    solution = np.linalg.solve(np.array(coefficients, dtype=float), np.array(target, dtype=float))\n    return np.round(solution, 6).tolist()',
    ['矩阵的每一行表示一个方程的系数。', '把矩阵和目标向量交给 np.linalg.solve。', '使用 np.round(solution, 6).tolist() 返回两项数值。'],
    '求解器使用数值线性代数算法处理方程组。输入保证唯一解，本题集中学习数组形状和求解接口。', requires=['numpy'])

# Chapter 16 — reading and transforming a DataFrame.
add(16, '创建第一张 DataFrame',
    'DataFrame 是带列名的二维表。用字典列表创建时，每个字典是一行。显式 columns 能保证空表也有列名。',
    'df = pd.DataFrame(rows, columns=["name", "score"])\ndf.shape  # (行数, 列数)\ndf.columns.tolist()',
    'rows 中每项为含 name、score 的字典。创建这两列的表，返回 {"shape": [行数,2], "columns": ["name","score"]}。',
    [('rows','list[dict]','姓名与分数记录，可以为空')],
    [([[{'name':'Ada','score':90}]],{'shape':[1,2],'columns':['name','score']}),([[]],{'shape':[0,2],'columns':['name','score']}),
     ([[{'name':'A','score':0},{'name':'B','score':1}]],{'shape':[2,2],'columns':['name','score']}),
     ([[{'name':'','score':-1}]],{'shape':[1,2],'columns':['name','score']}),
     ([[{'name':'A','score':1},{'name':'A','score':2},{'name':'C','score':3}]],{'shape':[3,2],'columns':['name','score']})],
    'import pandas as pd\ndef solve(rows):\n    df = pd.DataFrame(rows, columns=["name", "score"])\n    return {"shape": list(df.shape), "columns": df.columns.tolist()}',
    ['每个输入字典对应一行。','传入 columns，空输入仍保留两列。','shape 是元组，用 list 转成列表。'],
    '显式列顺序避免依赖字典字段顺序；后续可以用列名选择数据。', requires=['pandas'], difficulty='基础')
add(16, '选择一列变成 Series',
    'df["score"] 取出 Series；df[["score"]] 取出只有一列的 DataFrame。Series.tolist() 返回普通列表。',
    'scores = df["score"]\nscores.tolist()',
    'rows 为 [姓名,分数] 记录列表，返回按输入顺序排列的分数列表。',
    [('rows','list[list]','每项恰好两个元素')],
    [([[['A',90],['B',70]]],[90,70]),([[]],[]),([[['X',0]]],[0]),([[['A',-1],['A',2]]],[-1,2]),([[['',100]]],[100])],
    'import pandas as pd\ndef solve(rows):\n    df = pd.DataFrame(rows, columns=["name", "score"])\n    return df["score"].tolist()',
    ['先为两个位置指定列名。','用单层中括号选择 score。','转换成普通列表返回。'],
    'Series 是一维带索引数据；理解 Series 与 DataFrame 的区别能减少形状错误。', requires=['pandas'], difficulty='基础')
add(16, 'iloc 按位置取前几行',
    'df.iloc[:k] 按位置切片，右端不包含。to_dict("records") 把表转换为字典列表。',
    'df.iloc[:2].to_dict("records")',
    'rows 为含 name、score 的字典列表，返回前 k 行，仅保留这两列。k 非负，超出行数则全部返回。',
    [('rows','list[dict]','记录列表'),('k','int','非负行数')],
    [([[{'name':'A','score':1},{'name':'B','score':2}],1],[{'name':'A','score':1}]),([[],2],[]),
     ([[{'name':'A','score':1}],0],[]),([[{'name':'A','score':1}],9],[{'name':'A','score':1}]),
     ([[{'name':'X','score':0},{'name':'Y','score':9}],2],[{'name':'X','score':0},{'name':'Y','score':9}])],
    'import pandas as pd\ndef solve(rows, k):\n    df = pd.DataFrame(rows, columns=["name", "score"])\n    return df.iloc[:k].to_dict("records")',
    ['iloc 的 i 可以理解为整数位置。','使用 :k 切片。','records 格式每行一个字典。'],
    'loc 按标签选择，iloc 按整数位置选择；默认索引相同只是一个特例。', requires=['pandas'], difficulty='基础')
add(16, 'loc 与布尔条件筛选',
    'df.loc[条件, "列名"] 先选行再选列。多个 Series 条件使用 & 或 |，每个条件加括号。',
    'df.loc[df["score"] >= 60, "name"].tolist()',
    '返回 rows 中 score 不低于 threshold 的姓名，保持输入顺序。rows 每项为 [name,score]。',
    [('rows','list[list]','姓名分数'),('threshold','int','最低分')],
    [([[['A',59],['B',60]],60],['B']),([[],60],[]),([[['A',0]],0],['A']),([[['A',1]],2],[]),
     ([[['B',90],['A',80],['C',30]],80],['B','A'])],
    'import pandas as pd\ndef solve(rows, threshold):\n    df = pd.DataFrame(rows, columns=["name", "score"])\n    return df.loc[df["score"] >= threshold, "name"].tolist()',
    ['比较 score 列产生一列布尔值。','把布尔值作为 loc 的行条件。','第二个维度只选择 name。'],
    '对整列比较是向量化操作，无需逐行调用 Python if。', requires=['pandas'], difficulty='基础')
add(16, '添加一列计算结果',
    'df.assign(new_column=表达式) 返回添加新列后的表。列乘列按行对齐计算。',
    'df.assign(total=df["price"] * df["quantity"])',
    'rows 每项为 [整数单价,整数数量]，创建 total 列，返回各行总价列表。输入均非负。',
    [('rows','list[list[int]]','单价与数量')],
    [([[[3,2],[5,4]]],[6,20]),([[]],[]),([[[0,9]]],[0]),([[[7,0]]],[0]),([[[2,3],[2,1],[4,2]]],[6,2,8])],
    'import pandas as pd\ndef solve(rows):\n    df = pd.DataFrame(rows, columns=["price", "quantity"])\n    df = df.assign(total=df["price"] * df["quantity"])\n    return df["total"].tolist()',
    ['列之间直接使用 *。','assign 返回新表，需要接住返回值。','只返回 total 列。'],
    'DataFrame 会按索引对齐同一行的数据，适合批量生成衍生特征。', requires=['pandas'], difficulty='基础')
add(16, '按多个字段排序',
    'sort_values(["score", "name"], ascending=[False, True]) 分别指定两列的顺序。',
    'df.sort_values(["score", "name"], ascending=[False, True])',
    'rows 每项为 [姓名,分数]。按分数降序，同分按姓名字典序升序，返回姓名列表。',
    [('rows','list[list]','姓名仅含ASCII字母')],
    [([[['B',90],['A',90],['C',70]]],['A','B','C']),([[]],[]),([[['Z',0]]],['Z']),
     ([[['A',1],['B',2]]],['B','A']),([[['C',5],['B',5],['A',5]]],['A','B','C'])],
    'import pandas as pd\ndef solve(rows):\n    df = pd.DataFrame(rows, columns=["name", "score"])\n    return df.sort_values(["score", "name"], ascending=[False, True])["name"].tolist()',
    ['先按主排序列 score。','两个升降序标志应和列名一一对应。','最后提取 name。'],
    '多列排序直接表达排名中的主次规则，避免自行组合复杂循环。', requires=['pandas'])
add(16, '重命名列',
    'df.rename(columns={"old": "new"}) 按映射重命名列。',
    'df.rename(columns={"name": "student", "score": "points"})',
    'rows 含 name、score 字段，把它们分别改名为 student、points，返回字典列表。',
    [('rows','list[dict]','记录')],
    [([[{'name':'A','score':80}]],[{'student':'A','points':80}]),([[]],[]),([[{'name':'','score':0}]],[{'student':'','points':0}]),
     ([[{'name':'B','score':1},{'name':'C','score':2}]],[{'student':'B','points':1},{'student':'C','points':2}]),
     ([[{'name':'X','score':-1}]],[{'student':'X','points':-1}])],
    'import pandas as pd\ndef solve(rows):\n    df = pd.DataFrame(rows, columns=["name", "score"])\n    return df.rename(columns={"name": "student", "score": "points"}).to_dict("records")',
    ['rename 用 columns 参数处理列名。','字典左侧旧名，右侧新名。','方法默认返回新对象。'],
    '统一字段名有利于不同数据源之间的数据连接。', requires=['pandas'], difficulty='基础')
add(16, '统计每列缺失数量',
    'isna() 为每个单元返回布尔值；sum() 默认按列相加，True 按 1 计算。',
    'df.isna().sum().to_dict()',
    'rows 每项为 [a,b]，值为有限数字或 None。返回 {"a": a列缺失数, "b": b列缺失数}。',
    [('rows','list[list]','两列数据')],
    [([[[1,None],[None,2]]],{'a':1,'b':1}),([[]],{'a':0,'b':0}),([[[None,None]]],{'a':1,'b':1}),
     ([[[0,0],[2,3]]],{'a':0,'b':0}),([[[None,1],[None,2],[3,None]]],{'a':2,'b':1})],
    'import pandas as pd\ndef solve(rows):\n    df = pd.DataFrame(rows, columns=["a", "b"])\n    return {key: int(value) for key, value in df.isna().sum().items()}',
    ['None 进入数值列可能显示为 NaN。','不要用 == None 比较整列缺失。','布尔列求和就是数量。'],
    '显式转为 int 保证返回普通 Python 数字。', requires=['pandas'])
add(16, '填补缺失值',
    'Series.fillna(value) 用指定值替换缺失项，保留已有的 0。',
    'pd.Series([1, None, 0], dtype=float).fillna(9).tolist()',
    '把 values 中的 None 替换为 replacement，保留其他数值及顺序，返回列表。',
    [('values','list[float|None]','数值列表'),('replacement','float','有限替代值')],
    [([[1,None,0],9],[1,9,0]),([[],2],[]),([[None,None],-1],[-1,-1]),([[3,4],0],[3,4]),([[None,2],2],[2,2])],
    'import pandas as pd\ndef solve(values, replacement):\n    return pd.Series(values, dtype=float).fillna(replacement).tolist()',
    ['创建数值 Series。','fillna 只处理缺失，不会处理 0。','最后 tolist。'],
    '缺失值填补策略取决于业务，本题先练习指定常量的基本接口。', requires=['pandas'], difficulty='基础')
add(16, '按某一列去重',
    'drop_duplicates(subset="id", keep="last") 对相同 id 保留最后一行；留下的行仍按原位置排序。',
    'df.drop_duplicates(subset="id", keep="last")',
    'rows 每项为 [id,name]。相同 id 只保留最后一次出现的记录，最终按被保留记录在原输入中的位置排序，返回二维列表。',
    [('rows','list[list]','id为整数，name为字符串')],
    [([[[1,'old'],[2,'B'],[1,'new']]],[[2,'B'],[1,'new']]),([[]],[]),([[[1,'A']]],[[1,'A']]),
     ([[[1,'A'],[1,'B']]],[[1,'B']]),([[[3,'C'],[2,'B'],[4,'D']]],[[3,'C'],[2,'B'],[4,'D']])],
    'import pandas as pd\ndef solve(rows):\n    df = pd.DataFrame(rows, columns=["id", "name"])\n    return df.drop_duplicates(subset="id", keep="last").values.tolist()',
    ['重复的判定只看 id。','keep="last"，不是默认的 first。','结果不需要再按 id 排序。'],
    '去重依据和保留规则必须明确，否则可能误删业务数据。', requires=['pandas'])

# Chapter 17 — analysis, joins, reshape, and time series.
add(17, 'groupby 分组求和',
    'df.groupby("category")["amount"].sum() 按类别汇总一列。',
    'df.groupby("category")["amount"].sum().to_dict()',
    'rows 每项为 [类别字符串,整数金额]。返回每个类别的金额总和字典；空列表返回 {}。',
    [('rows','list[list]','类别金额')],
    [([[['A',2],['B',5],['A',3]]],{'A':5,'B':5}),([[]],{}),([[['A',0]]],{'A':0}),
     ([[['x',-1],['x',1]]],{'x':0}),([[['',2],['a',3]]],{'':2,'a':3})],
    'import pandas as pd\ndef solve(rows):\n    df = pd.DataFrame(rows, columns=["category", "amount"])\n    return {k: int(v) for k, v in df.groupby("category")["amount"].sum().items()}',
    ['先确定分组列和数值列。','groupby 后选择 amount。','对每组 sum 再转字典。'],
    '可以把 groupby 理解为拆分为多组、各组聚合、合并输出。', requires=['pandas'])
add(17, '一次计算多个统计量',
    'groupby(...).agg(["count", "mean"]) 为每组同时计算多个聚合。',
    'df.groupby("team")["score"].agg(["count", "mean"])',
    'rows 每项为 [组名,整数分数]。返回按组名字典序排序的 [组名,人数,平均分] 列表，平均分保留六位小数。',
    [('rows','list[list]','ASCII组名与分数')],
    [([[['B',4],['A',1],['A',2]]],[['A',2,1.5],['B',1,4]]),([[]],[]),([[['X',0]]],[['X',1,0]]),
     ([[['A',1],['A',1],['A',2]]],[['A',3,1.333333]]),([[['Z',-2],['Z',2]]],[['Z',2,0]])],
    'import pandas as pd\ndef solve(rows):\n    df = pd.DataFrame(rows, columns=["team", "score"])\n    if df.empty:\n        return []\n    stats = df.groupby("team", sort=True)["score"].agg(["count", "mean"])\n    return [[name, int(row["count"]), round(float(row["mean"]), 6)] for name, row in stats.iterrows()]',
    ['agg 接收聚合函数名列表。','默认按组名排序，也可显式 sort=True。','count 转 int，mean 做六位 round。'],
    '本题没有缺失值，所以 count 等于人数；有缺失时 count 只统计非缺失项。', requires=['pandas'])
add(17, 'merge 左连接',
    'left.merge(right, on="id", how="left") 保留左表的所有记录，右边缺失的字段填 NaN。',
    'people.merge(scores, on="id", how="left", sort=False)',
    'people 为 [id,name]，scores 为 [id,score]；两表各自 id 唯一。按 people 顺序返回 [name,score]，没有分数则使用 None。',
    [('people','list[list]','学生表'),('scores','list[list]','分数表')],
    [([[[1,'A'],[2,'B']],[[1,90]]],[['A',90],['B',None]]),([[],[[1,8]]],[]),
     ([[[1,'A']],[]],[['A',None]]),([[[2,'B'],[1,'A']],[[1,7],[2,8]]],[['B',8],['A',7]]),
     ([[[3,'C']],[[4,100]]],[['C',None]])],
    'import pandas as pd\ndef solve(people, scores):\n    if not people:\n        return []\n    left = pd.DataFrame(people, columns=["id", "name"])\n    right = pd.DataFrame(scores, columns=["id", "score"])\n    joined = left.merge(right, on="id", how="left", sort=False)\n    return [[row["name"], None if pd.isna(row["score"]) else int(row["score"])] for _, row in joined.iterrows()]',
    ['people 是左表。','明确 on="id" 与 how="left"。','将匹配失败产生的 NaN 转成 None。'],
    '数据库 JOIN 与 pandas merge 有相同的连接思想；键重复时可能产生多行组合。', requires=['pandas'])
add(17, 'pivot_table 生成交叉表',
    'pivot_table(index=..., columns=..., values=..., aggfunc="sum", fill_value=0) 聚合成二维表。',
    'df.pivot_table(index="team", columns="kind", values="amount", aggfunc="sum", fill_value=0)',
    'rows 每项为 [组名,类别,整数数量]，类别只能是 X 或 Y。按组名字典序输出 [组名,X总数,Y总数]，缺失类别补0。',
    [('rows','list[list]','交叉记录')],
    [([[['A','X',2],['A','Y',3],['B','Y',1]]],[['A',2,3],['B',0,1]]),([[]],[]),
     ([[['A','X',1],['A','X',2]]],[['A',3,0]]),([[['Z','Y',0]]],[['Z',0,0]]),
     ([[['B','X',4],['A','Y',5]]],[['A',0,5],['B',4,0]])],
    'import pandas as pd\ndef solve(rows):\n    if not rows:\n        return []\n    df = pd.DataFrame(rows, columns=["team", "kind", "amount"])\n    table = df.pivot_table(index="team", columns="kind", values="amount", aggfunc="sum", fill_value=0)\n    table = table.reindex(columns=["X", "Y"], fill_value=0).sort_index()\n    return [[name, int(row["X"]), int(row["Y"])] for name, row in table.iterrows()]',
    ['重复的组名和类别组合需要 sum 聚合。','可能整张表都没有 X，需要 reindex 补列。','按行索引排序后输出。'],
    'pivot_table 可处理重复键；普通 pivot 在组合键重复时会报错。', requires=['pandas'])
add(17, 'melt 宽表变成长表',
    'melt(id_vars="name", value_vars=["math","english"]) 把多列展开为变量名和值两列。',
    'df.melt(id_vars="name", var_name="subject", value_name="score")',
    'rows 每项为 [姓名,数学分数,英语分数]。返回 [姓名,科目,分数]；先输出所有 math 行，再所有 english 行，各科内部保持输入顺序。',
    [('rows','list[list]','成绩宽表')],
    [([[['A',1,2],['B',3,4]]],[['A','math',1],['B','math',3],['A','english',2],['B','english',4]]),([[]],[]),
     ([[['X',0,0]]],[['X','math',0],['X','english',0]]),([[['',-1,5]]],[['','math',-1],['','english',5]]),
     ([[['Z',90,80]]],[['Z','math',90],['Z','english',80]])],
    'import pandas as pd\ndef solve(rows):\n    df = pd.DataFrame(rows, columns=["name", "math", "english"])\n    return df.melt(id_vars="name", value_vars=["math", "english"], var_name="subject", value_name="score").values.tolist()',
    ['name 是保持不变的标识列。','value_vars 顺序决定科目展开顺序。','新列名指定为 subject 和 score。'],
    '长表更适合分组统计和很多绘图库的数据接口。', requires=['pandas'])
add(17, '日期列提取月份',
    'pd.to_datetime 转为日期；Series.dt 访问整列日期属性；strftime 格式化文本。',
    'pd.to_datetime(series, format="%Y-%m-%d").dt.strftime("%Y-%m")',
    'dates 是合法 YYYY-MM-DD 日期字符串列表，返回对应 YYYY-MM 月份字符串列表，保留顺序。年份在1900–2100。',
    [('dates','list[str]','日期列表')],
    [([['2024-01-02','2025-12-31']],['2024-01','2025-12']),([[]],[]),([['2000-02-29']],['2000-02']),
     ([['2023-09-01','2023-09-09']],['2023-09','2023-09']),([['1900-01-01']],['1900-01'])],
    'import pandas as pd\ndef solve(dates):\n    series = pd.Series(dates, dtype="str")\n    return pd.to_datetime(series, format="%Y-%m-%d").dt.strftime("%Y-%m").tolist()',
    ['先创建 Series。','使用明确的日期解析格式。','通过 dt 访问格式化方法。'],
    '显式日期格式减少歧义；真实数据可选择 errors="coerce" 把非法日期变成缺失值。', requires=['pandas'])
add(17, 'rolling 移动平均',
    'rolling(window=k, min_periods=1).mean() 计算截至当前行最近 k 项的平均。',
    'pd.Series([2,4,6]).rolling(window=2, min_periods=1).mean().tolist()',
    '返回 values 的向后移动平均列表，窗口 k 为正整数。开头不足 k 项时使用已有项；结果保留六位小数。',
    [('values','list[int]','序列'),('k','int','正整数窗口')],
    [([[2,4,6],2],[2,3,5]),([[],3],[]),([[1,2,3],1],[1,2,3]),([[2,4],9],[2,3]),([[1,2,2],3],[1,1.5,1.666667])],
    'import pandas as pd\ndef solve(values, k):\n    return pd.Series(values, dtype=float).rolling(window=k, min_periods=1).mean().round(6).tolist()',
    ['窗口包含当前项。','min_periods=1 避免开头产生缺失值。','对均值结果 round(6)。'],
    '移动统计常用于时间序列平滑；本题使用输入顺序，不自动按时间排序。', requires=['pandas'])
add(17, 'diff 相邻差分',
    'Series.diff() 用当前项减前一项，首项没有前驱，结果为 NaN。',
    'pd.Series([3,8,6]).diff()  # NaN, 5, -2',
    '返回 values 的相邻差分列表，第一项使用 None；空列表返回 []。输入为整数。',
    [('values','list[int]','观测值')],
    [([[3,8,6]],[None,5,-2]),([[]],[]),([[0]],[None]),([[2,2]],[None,0]),([[-2,1,5]],[None,3,4])],
    'import pandas as pd\ndef solve(values):\n    diff = pd.Series(values, dtype=float).diff()\n    return [None if pd.isna(x) else int(x) for x in diff]',
    ['差分方向是当前减前一项。','检测首项 NaN。','合法 JSON 用 None 表示缺失。'],
    '差分可以反映增长量；增长率需要额外除以前一项并处理零值。', requires=['pandas'])
add(17, 'concat 合并多批数据',
    'pd.concat([a,b], ignore_index=True) 纵向拼接，并重新编号行索引。',
    'combined = pd.concat([first, second], ignore_index=True)',
    'first、second 每项均为 [id,value]。按先 first 后 second 合并，返回 {"index": 从0开始的连续索引, "rows": 合并后的行列表}。不去重。',
    [('first','list[list[int]]','第一批'),('second','list[list[int]]','第二批')],
    [([[[1,2]],[[3,4]]],{'index':[0,1],'rows':[[1,2],[3,4]]}),([[],[]],{'index':[],'rows':[]}),
     ([[],[[9,0]]],{'index':[0],'rows':[[9,0]]}),([[[1,1]],[]],{'index':[0],'rows':[[1,1]]}),
     ([[[1,2]],[[1,2],[2,3]]],{'index':[0,1,2],'rows':[[1,2],[1,2],[2,3]]})],
    'import pandas as pd\ndef solve(first, second):\n    frames = [pd.DataFrame(rows, columns=["id", "value"]) for rows in (first, second)]\n    df = pd.concat(frames, ignore_index=True)\n    return {"index": df.index.tolist(), "rows": df.values.tolist()}',
    ['两批使用相同列名。','ignore_index=True 重建连续索引。','concat 不会自动删除重复记录。'],
    '不要在循环里反复向 DataFrame 追加一行；先收集批次，再一次 concat 更合适。', requires=['pandas'])
add(17, 'rank 计算密集名次',
    'rank(method="dense", ascending=False) 为大值分配小名次，同分同名次且下一名不跳号。',
    'pd.Series([90,80,90,70]).rank(method="dense", ascending=False)',
    '返回 scores 中各分数的密集排名，最高为1；同分同名次，名次不跳号；保持原输入顺序。',
    [('scores','list[int]','分数')],
    [([[90,80,90,70]],[1,2,1,3]),([[]],[]),([[5,5]],[1,1]),([[0]],[1]),([[-1,3,2]],[3,1,2])],
    'import pandas as pd\ndef solve(scores):\n    return pd.Series(scores, dtype=float).rank(method="dense", ascending=False).astype(int).tolist()',
    ['默认 rank 对并列取平均，不符合题意。','需要 method="dense"。','结果转整数列表。'],
    'min、average、dense 等并列规则各不相同，业务上应明确选择。', requires=['pandas'])

# Chapter 18 — inspect real plotting objects and build tiny ML pipelines.
add(18, 'Matplotlib 第一条折线',
    'fig, ax = plt.subplots() 创建画布和坐标轴。ax.plot 返回折线对象列表，可以读取对象数据。平台使用无窗口后端，本题检查图形数据。',
    'fig, ax = plt.subplots()\nline, = ax.plot([0,1], [2,3])\nline.get_ydata().tolist()\nplt.close(fig)',
    '用 x、y 绘制折线，返回 {"x": 折线横坐标列表, "y": 折线纵坐标列表}。长度相同，可以为空；创建后关闭图形。本题不检查屏幕渲染。',
    [('x','list[int]','横坐标'),('y','list[int]','纵坐标')],
    [([[0,1],[2,3]],{'x':[0,1],'y':[2,3]}),([[],[]],{'x':[],'y':[]}),([[1],[0]],{'x':[1],'y':[0]}),
     ([[-1,0,1],[1,0,1]],{'x':[-1,0,1],'y':[1,0,1]}),([[2,4],[5,-2]],{'x':[2,4],'y':[5,-2]})],
    'import matplotlib.pyplot as plt\ndef solve(x, y):\n    fig, ax = plt.subplots()\n    line, = ax.plot(x, y)\n    result = {"x": line.get_xdata().tolist(), "y": line.get_ydata().tolist()}\n    plt.close(fig)\n    return result',
    ['ax.plot 返回列表，用 line, 解包单条线。','使用 get_xdata 和 get_ydata。','得到结果后关闭画布。'],
    '独立运行桌面脚本时可使用 plt.show() 显示图形；本地判题以对象数据为准。', requires=['matplotlib'])
add(18, '柱状图的高度',
    'ax.bar(横坐标,高度) 返回包含多个 Rectangle 的容器；每个柱子有 get_height()。',
    'bars = ax.bar(range(len(values)), values)\nheights = [bar.get_height() for bar in bars]',
    '按 values 绘制柱状图，返回从左到右各柱子的高度列表。值为整数，允许负值和空列表。',
    [('values','list[int]','柱高')],
    [([[2,5,3]],[2,5,3]),([[]],[]),([[0]],[0]),([[-2,4]],[-2,4]),([[1,1]],[1,1])],
    'import matplotlib.pyplot as plt\ndef solve(values):\n    fig, ax = plt.subplots()\n    bars = ax.bar(range(len(values)), values)\n    result = [float(bar.get_height()) for bar in bars]\n    plt.close(fig)\n    return result',
    ['横坐标可用 range。','遍历 bar 容器。','读取高度后关闭图形。'],
    '柱图适合类别比较；本题让你认识绘图函数的返回对象，而不是只记一条调用语句。', requires=['matplotlib'])
add(18, '散点图的位置',
    'ax.scatter(x,y) 返回 PathCollection。get_offsets() 读取每个点的二维坐标。',
    'points = ax.scatter([1,2], [3,4])\npoints.get_offsets().tolist()',
    'x、y 为等长非空整数列表。绘制散点图后返回 [[x0,y0],[x1,y1],…]。',
    [('x','list[int]','非空横坐标'),('y','list[int]','非空纵坐标')],
    [([[1,2],[3,4]],[[1,3],[2,4]]),([[0],[0]],[[0,0]]),([[-1,1],[2,-2]],[[-1,2],[1,-2]]),
     ([[2,2],[4,5]],[[2,4],[2,5]]),([[0,1,2],[9,8,7]],[[0,9],[1,8],[2,7]])],
    'import matplotlib.pyplot as plt\ndef solve(x, y):\n    fig, ax = plt.subplots()\n    points = ax.scatter(x, y)\n    result = points.get_offsets().tolist()\n    plt.close(fig)\n    return result',
    ['scatter 与 plot 的返回对象类型不同。','从 get_offsets 读取坐标。','把数组转成普通列表。'],
    '散点图经常用于观察两个特征之间的关系。', requires=['matplotlib'])
add(18, '直方图与分箱边界',
    'ax.hist(values, bins=edges) 返回每个区间的数量、边界与柱对象。除最后一箱外，每箱左闭右开；最后一箱包含右端点。',
    'counts, edges, patches = ax.hist([0,1,2], bins=[0,1,2])\ncounts.tolist()  # [1,2]',
    '对 values 按固定边界 [0,2,4,6] 绘制直方图，返回三箱数量列表。输入为0–6整数；2属于第二箱，4和6属于第三箱。',
    [('values','list[int]','0–6之间的观测值')],
    [([[0,1,2,3,4,5,6]],[2,2,3]),([[]],[0,0,0]),([[2,2]],[0,2,0]),([[6]],[0,0,1]),([[0,4,4]],[1,0,2])],
    'import matplotlib.pyplot as plt\ndef solve(values):\n    fig, ax = plt.subplots()\n    counts, _, _ = ax.hist(values, bins=[0, 2, 4, 6])\n    result = counts.astype(int).tolist()\n    plt.close(fig)\n    return result',
    ['不要把 bins=3 与给定边界混淆。','只需要 hist 返回的第一项。','最后一个区间包含6。'],
    '显式分箱边界使不同数据集之间的统计口径保持一致。', requires=['matplotlib'])
add(18, '设置标题与坐标轴标签',
    'ax.set_title、set_xlabel、set_ylabel 设置图表语义。get_title 等方法可以读回文字。',
    'ax.set_title("Training")\nax.set_xlabel("Epoch")\nax.set_ylabel("Loss")',
    '创建图形，设置 title、xlabel、ylabel，返回读取到的三项字符串列表，保留空字符串与空白。',
    [('title','str','标题'),('xlabel','str','横轴名'),('ylabel','str','纵轴名')],
    [(['Training','Epoch','Loss'],['Training','Epoch','Loss']),(['','',''],['','','']),
     (['A','x','y'],['A','x','y']),(['Score','Time','%'],['Score','Time','%']),([' Demo ','X','Y'],[' Demo ','X','Y'])],
    'import matplotlib.pyplot as plt\ndef solve(title, xlabel, ylabel):\n    fig, ax = plt.subplots()\n    ax.set_title(title)\n    ax.set_xlabel(xlabel)\n    ax.set_ylabel(ylabel)\n    result = [ax.get_title(), ax.get_xlabel(), ax.get_ylabel()]\n    plt.close(fig)\n    return result',
    ['三个文本分别有对应 setter。','用 getter 检查设置结果。','保持文本原样，不调用 strip。'],
    '标题、坐标轴名和单位是图表可读性的组成部分。此题检查属性，不检查字体渲染。', requires=['matplotlib'])
add(18, '分开训练集与测试集',
    'train_test_split 将同一批特征和标签同步拆分。random_state 固定随机种子；shuffle=False 可保留时间顺序。',
    'from sklearn.model_selection import train_test_split\nx_train, x_test = train_test_split(values, test_size=2, shuffle=False)',
    'values 至少2项，test_count 在1到len(values)-1之间。使用 train_test_split，关闭打乱，返回 {"train": 前段, "test": 后test_count项}。',
    [('values','list[int]','至少2项数据'),('test_count','int','测试集数量')],
    [([[1,2,3,4],1],{'train':[1,2,3],'test':[4]}),([[1,2],1],{'train':[1],'test':[2]}),
     ([[0,1,2,3],2],{'train':[0,1],'test':[2,3]}),([[5,5,5],2],{'train':[5],'test':[5,5]}),
     ([[-1,0,1,2,3],3],{'train':[-1,0],'test':[1,2,3]})],
    'from sklearn.model_selection import train_test_split\ndef solve(values, test_count):\n    train, test = train_test_split(values, test_size=test_count, shuffle=False)\n    return {"train": train, "test": test}',
    ['test_size 接收整数时表示样本数量。','显式 shuffle=False。','返回两个列表并标注字段。'],
    '保留独立测试集是评估的基础。真实训练时不能先用全部数据拟合预处理器，再切分测试集。', requires=['sklearn'])
add(18, '只用训练集拟合标准化器',
    'StandardScaler.fit 学习训练数据的均值和标准差；transform 使用同一规则转换新数据。单特征也必须是二维数组。',
    'from sklearn.preprocessing import StandardScaler\nscaler = StandardScaler().fit([[1], [3]])\nscaler.transform([[2]]).tolist()  # [[0.0]]',
    'train 是非空单特征训练列表，query 是待转换列表。仅在 train 上 fit，再转换 query，返回一维结果，各项保留六位小数。常量训练集的缩放因子按库规则取1。',
    [('train','list[int]','非空训练特征'),('query','list[int]','待转换数据')],
    [([[1,3],[1,2,3]],[-1,0,1]),([[5,5],[5,7]],[0,2]),([[0,2],[]],[]),([[0,2,4],[2]],[0]),([[10],[8,10]],[-2,0])],
    'from sklearn.preprocessing import StandardScaler\ndef solve(train, query):\n    scaler = StandardScaler().fit([[x] for x in train])\n    if not query:\n        return []\n    return scaler.transform([[x] for x in query]).ravel().round(6).tolist()',
    ['把每个标量包装为 [x]，形成二维输入。','在 train 上 fit，不在 query 上重新 fit。','ravel 展平成一维再返回。'],
    '把测试数据用于 fit 会泄漏信息。StandardScaler 使用总体标准差，零方差特征按比例1处理。', requires=['sklearn'])
add(18, '拟合一元线性回归',
    'LinearRegression().fit(X,y) 学习直线，predict(X_new) 预测。特征 X 必须是二维，目标 y 通常是一维。',
    'from sklearn.linear_model import LinearRegression\nmodel = LinearRegression().fit([[0],[1]], [1,3])\nmodel.predict([[2]]).tolist()  # [5.0]',
    'x、y 为等长列表，至少两个不同x，数据保证精确共线。拟合带截距直线并预测 query，返回六位小数的一维列表；query 可为空。',
    [('x','list[int]','训练横坐标'),('y','list[int]','训练目标'),('query','list[int]','预测横坐标')],
    [([[0,1],[1,3],[2,3]],[5,7]),([[1,2,3],[2,4,6],[0]],[0]),([[0,2],[4,4],[1,9]],[4,4]),
     ([[-1,1],[3,-1],[0,2]],[1,-3]),([[0,1],[0,1],[]],[])],
    'from sklearn.linear_model import LinearRegression\ndef solve(x, y, query):\n    model = LinearRegression().fit([[v] for v in x], y)\n    if not query:\n        return []\n    return model.predict([[v] for v in query]).round(6).tolist()',
    ['输入是一个特征，不是一个样本。','[[v] for v in x] 正确组织形状。','predict 使用相同特征维度。'],
    '本题用精确共线数据集中学习 fit/predict 接口，真实数据的预测会存在误差。', requires=['sklearn'])
add(18, '分类的准确率与混淆矩阵',
    'accuracy_score 计算预测正确比例；confusion_matrix 的行是真实标签，列是预测标签。显式 labels=[0,1] 保证矩阵形状。',
    'from sklearn.metrics import accuracy_score, confusion_matrix\nconfusion_matrix([0,1], [1,1], labels=[0,1]).tolist()',
    'truth、pred 为等长非空0/1标签。返回 {"accuracy": 准确率保留六位, "matrix": 2×2混淆矩阵}，矩阵行列均按0、1排列。',
    [('truth','list[int]','真实标签'),('pred','list[int]','预测标签')],
    [([[0,1,1],[0,0,1]],{'accuracy':0.666667,'matrix':[[1,0],[1,1]]}),([[0],[0]],{'accuracy':1,'matrix':[[1,0],[0,0]]}),
     ([[1],[0]],{'accuracy':0,'matrix':[[0,0],[1,0]]}),([[0,1],[1,0]],{'accuracy':0,'matrix':[[0,1],[1,0]]}),
     ([[1,1],[1,1]],{'accuracy':1,'matrix':[[0,0],[0,2]]})],
    'from sklearn.metrics import accuracy_score, confusion_matrix\ndef solve(truth, pred):\n    return {"accuracy": round(float(accuracy_score(truth, pred)), 6),\n            "matrix": confusion_matrix(truth, pred, labels=[0, 1]).tolist()}',
    ['两个函数都按先真实、后预测传参。','labels 明确指定两个类别。','准确率是0到1的数，不是百分数字符串。'],
    '混淆矩阵显示哪种错误发生，信息比单独的准确率更丰富。', requires=['sklearn'])
add(18, '最近邻分类器',
    'KNeighborsClassifier(n_neighbors=1) 用训练集中距离最近的样本标签作预测。先 fit，再 predict。',
    'from sklearn.neighbors import KNeighborsClassifier\nmodel = KNeighborsClassifier(n_neighbors=1).fit([[0],[10]], [0,1])\nmodel.predict([[2]]).tolist()  # [0]',
    'x 为不同的整数特征，labels 为等长0/1类别，至少1项。使用1近邻分类 query，测试保证最近距离无并列；query为空时返回[]。',
    [('x','list[int]','训练特征'),('labels','list[int]','训练标签'),('query','list[int]','待预测特征')],
    [([[0,10],[0,1],[2,9]],[0,1]),([[5],[1],[0,100]],[1,1]),([[0,3],[1,0],[]],[]),
     ([[-5,5],[0,1],[-4,4]],[0,1]),([[0,10,20],[1,0,1],[11,19,1]],[0,1,1])],
    'from sklearn.neighbors import KNeighborsClassifier\ndef solve(x, labels, query):\n    model = KNeighborsClassifier(n_neighbors=1).fit([[v] for v in x], labels)\n    if not query:\n        return []\n    return model.predict([[v] for v in query]).tolist()',
    ['n_neighbors 设置为1。','训练特征和预测特征都转换为二维。','predict 输出类别，不是距离。'],
    '最近邻直观易懂，也会受特征量纲影响；多个量纲差异很大的特征通常需要适当缩放。', requires=['sklearn'])
