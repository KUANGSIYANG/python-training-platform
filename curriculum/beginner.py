"""90 scaffolded exercises: syntax before algorithms."""
from .schema import problem

PROBLEMS = []


def add(ch, n, title, syntax, task, params, tests, body, clues, why, difficulty='入门'):
    names = ', '.join(p[0] for p in params)
    source = 'def solve(' + names + '):\n' + '\n'.join('    ' + line if line else '' for line in body.splitlines())
    lesson = ('平台已经写好函数外壳。参数就是测试时传入的数据；把答案用 return 交回平台。'
              'print 只用于观察中间过程，不能代替 return。函数内部每行缩进 4 个空格。\n\n' + syntax)
    PROBLEMS.append(problem(ch, n, title, lesson, task, params, tests, source,
                            clues, why, difficulty=difficulty))


# 01 · 最初的十次成功
add(1,1,'把数据交还给平台','return 值：结束函数并返回一个结果。\n例如：return 7',
    '返回传入的整数 n，不要修改它。', [('n','int','任意整数')],
    [([7],7),([0],0),([-8],-8),([100],100),([42],42)],
    'return n', ['先找到参数 n。','在缩进的位置写 return。','return 后面直接写 n。'], '测试会调用 solve(7)，return n 就会得到整数 7。')
add(1,2,'两个数相加','+ 可以把两个数相加；变量名不加引号。',
    '返回整数 a 与 b 的和。',[('a','int','第一个数'),('b','int','第二个数')],
    [([2,3],5),([0,0],0),([-4,9],5),([-2,-3],-5),([100,200],300)],
    'return a + b',['确认有两个参数。','加法运算符是 +。','把 a + b 放在 return 后。'],'表达式 a + b 先计算，再把结果返回。')
add(1,3,'长方形周长','括号先计算；* 是乘法。\narea = width * height',
    '返回长为 length、宽为 width 的长方形周长，输入为非负整数。',[('length','int','长'),('width','int','宽')],
    [([3,2],10),([1,1],4),([0,0],0),([5,0],10),([10,7],34)],
    'return 2 * (length + width)',['周长是四条边之和。','先把长与宽相加。','返回 2 * (length + width)。'],'括号保证先求半周长，然后乘 2。')
add(1,4,'除法与平均数','/ 总是得到浮点数；// 是向下取整的除法。',
    '返回 a、b 的算术平均数，允许小数。',[('a','int','第一个数'),('b','int','第二个数')],
    [([2,4],3.0),([1,2],1.5),([-3,3],0.0),([0,0],0.0),([10,13],11.5)],
    'return (a + b) / 2',['平均数是和除以数量。','这里需要 /，不是 //。','先用括号把 a + b 括起来。'],'/ 保留小数部分；平台对浮点结果使用小误差容忍。')
add(1,5,'温度换算','可以把计算结果赋给变量：result = expression。',
    '把摄氏温度 c 转为华氏温度，公式为 c × 9 / 5 + 32。',[('c','float','摄氏温度')],
    [([0],32),([100],212),([-40],-40),([20],68),([37],98.6)],
    'fahrenheit = c * 9 / 5 + 32\nreturn fahrenheit',['乘除优先于加减。','可以用 fahrenheit 保存结果。','最后 return fahrenheit。'],'变量把中间结果起一个有意义的名字，方便阅读与调试。')
add(1,6,'分钟变成时和分','// 求整商；% 求余数；[a, b] 创建列表。',
    '将非负总分钟数 minutes 转成 [小时数, 剩余分钟数]，小时可以超过 24。',[('minutes','int','非负总分钟数')],
    [([135],[2,15]),([60],[1,0]),([0],[0,0]),([59],[0,59]),([1500],[25,0])],
    'return [minutes // 60, minutes % 60]',['每小时 60 分钟。','整除得到小时，取余得到余下分钟。','把两个数放入列表返回。'],'例如 135 = 2 × 60 + 15，// 和 % 分别取出 2 与 15。')
add(1,7,'三位数拆位','n // 100 取百位；n % 10 取个位。',
    '给定 100 到 999 的整数 n，返回三个数位之和。',[('n','int','100 ≤ n ≤ 999')],
    [([123],6),([100],1),([999],27),([508],13),([470],11)],
    'return n // 100 + n // 10 % 10 + n % 10',['分别取百位、十位、个位。','十位先整除 10，再对 10 取余。','把三个数位相加。'],'n // 10 去掉个位，接着 % 10 留下十位。')
add(1,8,'交换两个变量','Python 支持同时赋值：a, b = b, a。',
    '把两个整数交换位置，返回 [原来的 b, 原来的 a]。',[('a','int','第一个整数'),('b','int','第二个整数')],
    [([1,2],[2,1]),([0,0],[0,0]),([-1,3],[3,-1]),([9,9],[9,9]),([100,-20],[-20,100])],
    'a, b = b, a\nreturn [a, b]',['不需要临时变量也能交换。','同时赋值右边会先求值。','交换后按 [a, b] 返回。'],'同时赋值避免先覆盖 a 导致原值丢失。')
add(1,9,'第一条格式化字符串','f"你好，{name}" 会把变量嵌入字符串。',
    '返回字符串「你好，名字！」，使用中文逗号和全角感叹号，不加空格。',[('name','str','名字，可以为空字符串')],
    [(['小明'],'你好，小明！'),(['Ada'],'你好，Ada！'),([''],'你好，！'),(['Python'],'你好，Python！'),(['李 雷'],'你好，李 雷！')],
    'return f"你好，{name}！"',['答案是字符串。','字符串前面加 f。','把 name 放入花括号。'],'f-string 可读性比多次字符串拼接更好。名字原样保留。')
add(1,10,'字符串变成整数','int("12") 得到 12；str(12) 得到 "12"。',
    'a、b 是合法整数字符串（可能有首尾空白或正负号），返回转换后的整数之和。',[('a','str','整数字符串'),('b','str','整数字符串')],
    [(['12','3'],15),(['-2','5'],3),([' 7 ','+1'],8),(['0','0'],0),(['001','09'],10)],
    'return int(a) + int(b)',['字符串相加会拼接。','分别调用 int 转换。','转换之后再相加。'],'"12" + "3" 是 "123"，而 int 转换后才能做数值加法。')

# 02 · 条件判断
add(2,1,'奇数还是偶数','if 条件:\n    ...\nelse:\n    ...',
    '偶数返回 "even"，奇数返回 "odd"，负数规则相同。',[('n','int','任意整数')],
    [([2],'even'),([3],'odd'),([0],'even'),([-3],'odd'),([-8],'even')],
    'if n % 2 == 0:\n    return "even"\nreturn "odd"',['用余数判断。','n % 2 == 0 表示偶数。','分支返回题目指定的英文字符串。'],'== 比较是否相等，= 用于赋值，两者用途不同。')
add(2,2,'数的正负','elif 表示前一个条件不成立时再判断。',
    '正数返回 "positive"，零返回 "zero"，负数返回 "negative"。',[('n','float','一个数')],
    [([3],'positive'),([0],'zero'),([-1],'negative'),([0.5],'positive'),([-0.5],'negative')],
    'if n > 0:\n    return "positive"\nelif n == 0:\n    return "zero"\nelse:\n    return "negative"',['需要三个分支。','先判断大于零，再判断等于零。','余下情况就是负数。'],'if / elif / else 中只有一个分支执行。')
add(2,3,'两个数中的较大值','a >= b 包含相等情况。',
    '用条件判断返回 a、b 中较大的一个。',[('a','int','整数'),('b','int','整数')],
    [([3,8],8),([9,2],9),([4,4],4),([-2,-7],-2),([0,-1],0)],
    'if a >= b:\n    return a\nreturn b',['比较两个参数。','a >= b 时返回 a。','否则返回 b。'],'相等时返回任意一个都正确。')
add(2,4,'成绩分档','多个 elif 应按从高到低或从低到高的顺序组织。',
    'score 为 0–100 的整数。90及以上返回 A，80及以上 B，60及以上 C，其余 D。',[('score','int','0–100')],
    [([90],'A'),([80],'B'),([60],'C'),([59],'D'),([100],'A'),([0],'D')],
    'if score >= 90:\n    return "A"\nif score >= 80:\n    return "B"\nif score >= 60:\n    return "C"\nreturn "D"',['先判断最高分档。','return 会立即结束函数。','边界 90、80、60 都属于较高一档。'],'若先判断 >=60 并返回，会误把高分也归入 C。')
add(2,5,'同时满足两个条件','and 要求两边都成立；or 至少一边成立。',
    '年龄 age 在 18 到 60 之间（含边界），且 has_ticket 为 True 时返回 True，否则 False。',[('age','int','年龄'),('has_ticket','bool','是否有票')],
    [([18,True],True),([60,True],True),([17,True],False),([30,False],False),([61,True],False)],
    'return 18 <= age <= 60 and has_ticket',['Python 允许连续比较。','年龄条件和票条件用 and 连接。','布尔表达式可以直接返回。'],'不必把 True/False 再包进冗长的 if 分支。')
add(2,6,'判断闰年','% 的优先级高于 ==，and 的优先级高于 or。',
    '正整数 year 能被 400 整除，或能被 4 整除但不能被 100 整除时为闰年，返回布尔值。',[('year','int','正整数年份')],
    [([2000],True),([1900],False),([2024],True),([2023],False),([2100],False)],
    'return year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)',['分成两个可行条件。','!= 表示不等于。','用括号使逻辑更清楚。'],'世纪年必须能被 400 整除；普通年份只需能被 4 整除。')
add(2,7,'安全除法','分母为 0 时执行 / 会触发 ZeroDivisionError。',
    'b 为 0 时返回 None，否则返回 a / b。None 在结果面板中显示为 JSON 的 null。',[('a','float','被除数'),('b','float','除数')],
    [([6,3],2),([1,0],None),([0,5],0),([-5,2],-2.5),([0,0],None)],
    'if b == 0:\n    return None\nreturn a / b',['先处理不合法的除数。','None 不是字符串。','正常分支再除法。'],'提前返回能防止程序进入会报错的计算。')
add(2,8,'区间裁剪','可以先处理下界，再处理上界。',
    '已知 low <= high，把 x 限制在闭区间 [low, high]：小于下界返回 low，大于上界返回 high，否则返回 x。',[('x','int','待裁剪数'),('low','int','下界'),('high','int','上界')],
    [([5,0,10],5),([-3,0,10],0),([20,0,10],10),([0,0,10],0),([7,4,4],4)],
    'if x < low:\n    return low\nif x > high:\n    return high\nreturn x',['有三种位置关系。','等于边界时无需改变。','顺序判断两种越界情况。'],'裁剪经常用于图像像素、概率和数值计算。')
add(2,9,'空值与默认值','空字符串的布尔值为 False；非空字符串为 True。',
    'name 为空字符串时返回 "匿名"，否则原样返回 name，空格字符串不算空。',[('name','str','可能为空的名字')],
    [([''],'匿名'),(['Ada'],'Ada'),([' '],' '),(['0'],'0'),(['小王'],'小王')],
    'return name or "匿名"',['不要调用 strip。','or 会返回第一个真值或最后一个值。','name or "匿名" 就能处理。'],'or 不一定返回布尔值，它也常用于简单的默认值选择。')
add(2,10,'三角形是否合法','三角形任意两边之和必须严格大于第三边。',
    'a、b、c 为整数，只有三边均为正且满足三角形不等式时返回 True。',[('a','int','边长'),('b','int','边长'),('c','int','边长')],
    [([3,4,5],True),([1,2,3],False),([0,1,1],False),([-1,2,2],False),([2,2,2],True)],
    'return a > 0 and b > 0 and c > 0 and a + b > c and a + c > b and b + c > a',['先排除非正边长。','等于也不能组成三角形。','把全部条件用 and 连接。'],'本题训练把自然语言规则翻译成布尔表达式。')

# 03 · 循环
add(3,1,'从 1 加到 n','for i in range(1, n + 1): 遍历 1 到 n。range 的右端不包含。',
    'n 为非负整数，用循环返回 1+2+…+n；n=0 时返回 0。',[('n','int','0–10000')],
    [([3],6),([0],0),([1],1),([10],55),([100],5050)],
    'total = 0\nfor i in range(1, n + 1):\n    total += i\nreturn total',['累加器初始为 0。','+= 表示在原值上加。','return 应放在循环外。'],'如果把 return 缩进到循环里，程序只会累加第一项。')
add(3,2,'阶乘','乘法累积的初始值是 1。',
    '返回非负整数 n 的阶乘；0! 定义为 1。n ≤ 12。',[('n','int','0–12')],
    [([4],24),([0],1),([1],1),([5],120),([7],5040)],
    'result = 1\nfor i in range(2, n + 1):\n    result *= i\nreturn result',['不要把累乘结果初始化成 0。','从 2 乘到 n。','空循环会保留初始值 1。'],'边界 n=0 和 n=1 无需特殊分支。')
add(3,3,'统计正数','for value in values: 依次取出列表元素。',
    '返回 nums 中严格大于 0 的元素数量，空列表返回 0。',[('nums','list[int]','整数列表')],
    [([[1,-2,3,0]],2),([[]],0),([[-1,-2]],0),([[0,0]],0),([[1,1,1]],3)],
    'count = 0\nfor x in nums:\n    if x > 0:\n        count += 1\nreturn count',['循环访问每个元素。','条件成立才累加计数。','0 不计入正数。'],'这是筛选与计数的通用模板。')
add(3,4,'找到第一个偶数','return 能在循环中提前结束整个函数。',
    '返回列表中的第一个偶数；不存在则返回 None。',[('nums','list[int]','整数列表')],
    [([[1,4,2]],4),([[1,3]],None),([[]],None),([[0,2]],0),([[-3,-2,8]],-2)],
    'for x in nums:\n    if x % 2 == 0:\n        return x\nreturn None',['按原顺序遍历。','找到后立即返回。','没有找到的返回语句放到循环后。'],'最坏访问 n 个元素，时间复杂度 O(n)。')
add(3,5,'while 统计数位','while 条件: 会不断执行，直到条件为 False。',
    '返回整数 n 的十进制数位数量，负号不算，0 的位数为 1。',[('n','int','整数')],
    [([123],3),([0],1),([-400],3),([9],1),([10000],5)],
    'n = abs(n)\nif n == 0:\n    return 1\ncount = 0\nwhile n > 0:\n    count += 1\n    n //= 10\nreturn count',['先用 abs 去掉负号。','每次整除 10 去掉一位。','必须更新 n，避免无限循环。'],'while 循环应有明确的状态更新和结束条件。')
add(3,6,'跳过负数','continue 跳过当前轮次，继续下一次循环。',
    '返回 nums 中所有非负数的和。',[('nums','list[int]','整数列表')],
    [([[1,-2,3]],4),([[]],0),([[-1,-2]],0),([[0,5]],5),([[2,2,-9]],4)],
    'total = 0\nfor x in nums:\n    if x < 0:\n        continue\n    total += x\nreturn total',['负数不参与累加。','遇到负数执行 continue。','累加语句写在条件之后。'],'continue 只跳过一次循环，break 则结束整个循环。')
add(3,7,'读到终止符','break 结束最近的一层循环。',
    '从左到右累加 nums，遇到第一个 0 就停止；0 后面的元素全部忽略。',[('nums','list[int]','整数列表')],
    [([[2,3,0,99]],5),([[0,9]],0),([[]],0),([[1,2]],3),([[-1,5,0,8]],4)],
    'total = 0\nfor x in nums:\n    if x == 0:\n        break\n    total += x\nreturn total',['停止条件是等于 0。','先判断停止，再累加。','break 后返回目前的总和。'],'这和机考中用特殊值结束输入的处理方式一致。')
add(3,8,'带编号的元素','enumerate(values, start=1) 同时给出编号和元素。',
    '给每个字符串添加从 1 开始的编号，返回如 ["1.苹果", "2.香蕉"] 的列表。',[('items','list[str]','字符串列表')],
    [([['苹果','香蕉']],['1.苹果','2.香蕉']),([[]],[]),([['a']],['1.a']),([['','x']],['1.','2.x']),([['a','b','c']],['1.a','2.b','3.c'])],
    'result = []\nfor i, item in enumerate(items, start=1):\n    result.append(f"{i}.{item}")\nreturn result',['创建空结果列表。','enumerate 的默认编号是 0，需要 start=1。','append 每次添加一个元素。'],'不用自己维护计数器，enumerate 更不易产生边界错误。')
add(3,9,'九九乘法矩形','嵌套 for 循环可生成二维列表，行与列各有一个循环。',
    '返回 rows 行 cols 列的乘法表，第 i 行第 j 列为 (i+1)*(j+1)。rows、cols 非负，任一维为 0 按对应形状返回。',[('rows','int','0–10'),('cols','int','0–10')],
    [([2,3],[[1,2,3],[2,4,6]]),([0,3],[]),([2,0],[[],[]]),([1,1],[[1]]),([3,2],[[1,2],[2,4],[3,6]])],
    'table = []\nfor i in range(1, rows + 1):\n    row = []\n    for j in range(1, cols + 1):\n        row.append(i * j)\n    table.append(row)\nreturn table',['每行都新建一个列表。','外层控制行，内层控制列。','完成一行后再添加到 table。'],'处理 R×C 个单元，时间复杂度 O(RC)。')
add(3,10,'判断质数','range(2, int(n ** 0.5) + 1) 只检查到平方根。',
    'n 为整数，若 n≥2 且只有 1 和自身两个正因子则返回 True。n≤1000000。',[('n','int','≤1000000')],
    [([2],True),([1],False),([9],False),([97],True),([-7],False),([49],False)],
    'if n < 2:\n    return False\nfor d in range(2, int(n ** 0.5) + 1):\n    if n % d == 0:\n        return False\nreturn True',['小于 2 都不是质数。','如果有因子，一定有一个不超过平方根。','平方根也要检查，所以 range 末尾 +1。'],'通过平方根界限把试除次数从 O(n) 降为 O(√n)。','基础')

# 04 · 字符串
add(4,1,'首尾去空白','text.strip() 返回移除首尾空白后的新字符串，不改变中间空白。',
    '去掉 text 首尾的空格、制表符和换行，保留中间内容。',[('text','str','任意字符串')],
    [(['  hi  '],'hi'),(['\n a b\t'],'a b'),([''],'') ,(['   '],''),(['x y'],'x y')],
    'return text.strip()',['字符串方法写在点号后。','strip 不带参数会去掉常见空白。','不要使用 replace 删除所有空格。'],'字符串是不可变对象，strip 会返回新值。')
add(4,2,'统一小写','text.lower() 返回小写版本。',
    '将 text 中的字母转为小写，数字和符号保持不变。',[('text','str','ASCII 字符串')],
    [(['PyTHON'],'python'),(['A1!'],'a1!'),([''],''),(['hello'],'hello'),(['ABC XYZ'],'abc xyz')],
    'return text.lower()',['不需要手动遍历每个字符。','使用 lower 方法。','记得方法后面的括号。'],'lower() 处理整条字符串，常用于忽略大小写的比较。')
add(4,3,'字符串反转','s[start:stop:step] 是切片；s[::-1] 使用负步长。',
    '返回 text 的字符倒序结果。',[('text','str','普通文本')],
    [(['abc'],'cba'),(['你好'],'好你'),([''],''),(['a'],'a'),(['a b'],'b a')],
    'return text[::-1]',['切片不需要逐个 append。','省略起止位置。','步长写为 -1。'],'切片产生新字符串，原字符串保持原值。')
add(4,4,'取前 k 个字符','s[:k] 取下标 0 到 k-1；超出长度也不会报错。',
    '返回 text 的前 k 个字符，k 为非负整数。',[('text','str','文本'),('k','int','非负')],
    [(['python',2],'py'),(['abc',0],''),(['abc',9],'abc'),(['',3],''),(['你好世界',3],'你好世')],
    'return text[:k]',['切片右端不包含。','从开头开始可省略 0。','不用自己判断 k 是否太大。'],'索引越界会报错，但切片会自动截断到合法范围。')
add(4,5,'按空白分词','text.split() 按连续空白分割；结果是列表。',
    '按任意连续空白拆分 text，结果不包含空字符串。',[('text','str','可能含空格/换行/tab')],
    [(['a  b'],['a','b']),(['\nhi\tthere '],['hi','there']),([''],[]),(['  '],[]),(['one'],['one'])],
    'return text.split()',['无参数 split 会合并连续空白。','split(" ") 与 split() 不同。','直接返回列表。'],'split() 很适合解析机考中以空白分隔的数据。')
add(4,6,'连接多个词','separator.join(words) 把字符串列表连接起来。',
    '使用英文逗号连接 words，不添加额外空格。空列表返回空字符串。',[('words','list[str]','字符串列表')],
    [([['a','b']],'a,b'),([[]],''),([['x']],'x'),([['','a']],',a'),([['1','2','3']],'1,2,3')],
    'return ",".join(words)',['join 的调用者是分隔符。','列表里的元素都已经是字符串。','使用 ",".join(words)。'],'join 会只在元素之间加入分隔符，不在末尾多加。')
add(4,7,'替换内容','text.replace(old, new) 替换所有不重叠的匹配。',
    '把 text 中的所有 old 替换成 new，old 保证非空。',[('text','str','原文'),('old','str','非空旧片段'),('new','str','新片段')],
    [(['banana','na','X'],'baXX'),(['aaa','aa','b'],'ba'),(['abc','z','x'],'abc'),(['','a','b'],''),(['a-b-a','a',''],'-b-')],
    'return text.replace(old, new)',['不需要写循环。','replace 的两个参数依次是旧值、新值。','返回替换后的新字符串。'],'匹配按从左到右、不重叠的方式进行。')
add(4,8,'统计子串','s.count(sub) 统计不重叠出现的次数。',
    '返回非空子串 sub 在 text 中不重叠出现的次数，区分大小写。',[('text','str','原文'),('sub','str','非空子串')],
    [(['aaaa','aa'],2),(['banana','ana'],1),(['abc','x'],0),(['','a'],0),(['AaA','A'],2)],
    'return text.count(sub)',['注意不是统计重叠匹配。','Python 已有 count 方法。','count 返回整数。'],'banana 中两个 ana 有重叠，因此 count 只计 1 次。')
add(4,9,'文件扩展名检查','s.endswith(suffix) 检查结尾；方法可以连续调用。',
    '文件名以 .py 结尾时返回 True，忽略大小写，不忽略首尾空白。',[('filename','str','文件名')],
    [(['main.py'],True),(['A.PY'],True),(['py'],False),(['x.py '],False),([''],False)],
    'return filename.lower().endswith(".py")',['先统一大小写。','扩展名包含点号。','不要把包含 .py 当成以 .py 结尾。'],'链式调用把小写后的结果继续交给 endswith。')
add(4,10,'固定两位小数','f"{value:.2f}" 将数字格式化为两位小数的字符串。',
    '返回金额字符串，前缀为英文 ¥ 符号，后面保留两位小数。测试不包含恰好处于舍入中点的数。',[('value','float','金额')],
    [([3],'¥3.00'),([1.236],'¥1.24'),([0],'¥0.00'),([-2.3],'¥-2.30'),([12.991],'¥12.99')],
    'return f"¥{value:.2f}"',['返回值应是字符串。','格式说明放在冒号后。','.2f 表示两位小数。'],'格式化只改变显示形式，不改变原始 value。')

# 05 · 列表与元组
add(5,1,'列表首尾','nums[0] 是首项，nums[-1] 是末项。',
    '非空列表返回 [首项, 末项]；空列表返回 []。',[('nums','list[int]','整数列表')],
    [([[2,4,6]],[2,6]),([[]],[]),([[5]],[5,5]),([[-1,0]],[-1,0]),([[9,8,7,6]],[9,6])],
    'if not nums:\n    return []\nreturn [nums[0], nums[-1]]',['先防止空列表访问下标。','负下标从末尾倒着数。','只有一个元素时首尾相同。'],'访问前检查空值可避免 IndexError。')
add(5,2,'添加一个元素','list.append(x) 原地修改列表，返回 None。',
    '返回 nums 末尾追加 value 的新列表，推荐复制后 append。',[('nums','list[int]','原列表'),('value','int','新元素')],
    [([[1,2],3],[1,2,3]),([[],9],[9]),([[0],0],[0,0]),([[-1],2],[-1,2]),([[4,5],-6],[4,5,-6])],
    'result = nums.copy()\nresult.append(value)\nreturn result',['不要 return nums.append(value)。','用 copy 创建新列表。','先 append，再 return result。'],'许多原地修改方法返回 None，必须返回列表本身。')
add(5,3,'合并两个列表','a + b 返回拼接后的新列表；extend 则原地扩展。',
    '返回 a 的全部元素后面接上 b 的全部元素。',[('a','list[int]','第一段'),('b','list[int]','第二段')],
    [([[1],[2,3]],[1,2,3]),([[],[]],[]),([[],[5]],[5]),([[8],[]],[8]),([[1,1],[1]],[1,1,1])],
    'return a + b',['顺序保持不变。','列表也支持 +。','重复元素不需要去掉。'],'列表相加是拼接，与 NumPy 的逐元素相加不同。')
add(5,4,'升序排序','sorted(nums) 返回新列表；nums.sort() 原地修改并返回 None。',
    '返回 nums 从小到大排序后的列表，保留重复值。',[('nums','list[int]','整数列表')],
    [([[3,1,2]],[1,2,3]),([[]],[]),([[2,2,1]],[1,2,2]),([[-1,-3,0]],[-3,-1,0]),([[5]],[5])],
    'return sorted(nums)',['排序用 sorted。','默认就是升序。','注意 sort 和 sorted 的返回值差异。'],'内置排序的通常时间复杂度为 O(n log n)。')
add(5,5,'每隔一个取元素','nums[::2] 从下标 0 开始，每隔两个下标取一个元素。',
    '返回 nums 中下标为 0、2、4……的元素。',[('nums','list[int]','整数列表')],
    [([[0,1,2,3,4]],[0,2,4]),([[]],[]),([[8]],[8]),([[1,2]],[1]),([[9,8,7,6]],[9,7])],
    'return nums[::2]',['这是下标为偶数，不是值为偶数。','切片第三个位置是步长。','省略起止位置即可。'],'切片能简洁地表达有规律的索引选择。')
add(5,6,'删除第一个匹配','result.remove(x) 删除第一个匹配；不存在时会报 ValueError。',
    '删除 nums 中第一次出现的 target；不存在时原样返回列表。',[('nums','list[int]','列表'),('target','int','目标')],
    [([[1,2,1],1],[2,1]),([[1,2],9],[1,2]),([[],0],[]),([[3,3],3],[3]),([[0],0],[])],
    'result = nums.copy()\nif target in result:\n    result.remove(target)\nreturn result',['先复制列表。','用 in 检查是否存在。','remove 只移除第一项匹配。'],'remove 按值删除，pop 按下标删除。')
add(5,7,'弹出最后一个元素','pop() 移除并返回最后一项。',
    '非空 nums 返回 {"last": 被移除末项, "rest": 剩余列表}；空列表 last 为 None。',[('nums','list[int]','列表')],
    [([[1,2]],{'last':2,'rest':[1]}),([[]],{'last':None,'rest':[]}),([[9]],{'last':9,'rest':[]}),([[0,0]],{'last':0,'rest':[0]}),([[-1,3,4]],{'last':4,'rest':[-1,3]})],
    'rest = nums.copy()\nlast = rest.pop() if rest else None\nreturn {"last": last, "rest": rest}',['返回一个包含两个字段的字典。','空列表不能直接 pop。','条件表达式可写 value if condition else other。'],'pop 的返回值是被删除的元素，与 append 的行为不同。')
add(5,8,'矩阵的一列','row[index] 取一行指定位置；二维列表没有 matrix[:,i] 语法。',
    '返回矩形 matrix 的第 col 列；matrix 可以为空，非空时 col 保证合法。',[('matrix','list[list[int]]','矩阵'),('col','int','从0开始列下标')],
    [([[[1,2],[3,4]],1],[2,4]),([[],0],[]),([[[8]],0],[8]),([[[1,2,3]],2],[3]),([[[0],[1],[2]],0],[0,1,2])],
    'result = []\nfor row in matrix:\n    result.append(row[col])\nreturn result',['遍历每一行。','从每行取同一个下标。','把取出的值放进新列表。'],'内置列表按行存储，用循环组合出列。')
add(5,9,'解包坐标','x, y = point 将恰好两个元素解包为变量。',
    'point 为 [x,y]，返回它到原点的曼哈顿距离 |x|+|y|。',[('point','list[int]','长度恰好为2')],
    [([[3,-4]],7),([[0,0]],0),([[-2,-5]],7),([[8,1]],9),([[0,-6]],6)],
    'x, y = point\nreturn abs(x) + abs(y)',['解包的变量数量应与元素数量一致。','abs 计算绝对值。','曼哈顿距离不用开平方。'],'列表和元组都支持解包；JSON 中元组用数组表示。')
add(5,10,'列表复制的细节','[row.copy() for row in matrix] 同时复制外层与每一行。',
    '复制非空矩形 matrix，把副本左上角设为 value，返回 {"original": 原矩阵, "changed": 副本}。原矩阵不得被改变。',[('matrix','list[list[int]]','至少1行1列'),('value','int','新值')],
    [([[[1,2],[3,4]],9],{'original':[[1,2],[3,4]],'changed':[[9,2],[3,4]]}),([[[0]],5],{'original':[[0]],'changed':[[5]]}),([[[1,1]],0],{'original':[[1,1]],'changed':[[0,1]]}),([[[2],[3]],-1],{'original':[[2],[3]],'changed':[[-1],[3]]}),([[[7]],7],{'original':[[7]],'changed':[[7]]})],
    'changed = []\nfor row in matrix:\n    changed.append(row.copy())\nchanged[0][0] = value\nreturn {"original": matrix, "changed": changed}',['只复制外层还会共享内层行。','每一行也要 copy。','修改副本后同时返回两份数据。'],'对二维列表，浅复制外层不能隔离内层对象的修改。','基础')

# 06 · 字典和集合
add(6,1,'安全读取字典','mapping.get(key, default) 在键不存在时返回默认值。',
    '返回 data 中 key 对应的值，键不存在时返回 default。已有值为 None 时应保留 None。',[('data','dict','字典'),('key','str','键'),('default','any','默认值')],
    [([{'a':1},'a',0],1),([{},'x',9],9),([{'x':None},'x',3],None),([{'x':0},'x',7],0),([{'x':False},'y','?'],'?')],
    'return data.get(key, default)',['不要把不存在和假值混为一谈。','get 的第二个参数是默认值。','已有 None 也算键存在。'],'data.get(key) or default 会错误替换 0、False 等合法值。')
add(6,2,'更新一个字段','result[key] = value 可以新增或覆盖字典字段。',
    '返回 data 的副本，并将 key 设置为 value。',[('data','dict','原字典'),('key','str','键'),('value','any','新值')],
    [([{'a':1},'a',2],{'a':2}),([{},'x',0],{'x':0}),([{'a':1},'b',3],{'a':1,'b':3}),([{},'n',None],{'n':None}),([{'x':False},'x',True],{'x':True})],
    'result = data.copy()\nresult[key] = value\nreturn result',['字典也有 copy。','用中括号赋值。','返回更新后的字典。'],'读取不存在的中括号键会报错，但给新键赋值是合法的。')
add(6,3,'词频统计','counts.get(word, 0) + 1 可实现从零开始的计数。',
    '统计 words 中各字符串的次数，返回字典，区分大小写。',[('words','list[str]','词列表')],
    [([['a','b','a']],{'a':2,'b':1}),([[]],{}),([['A','a']],{'A':1,'a':1}),([['','']],{'':2}),([['x']],{'x':1})],
    'counts = {}\nfor word in words:\n    counts[word] = counts.get(word, 0) + 1\nreturn counts',['用字符串作键，次数作值。','第一次出现默认次数为 0。','每看到一次就加 1。'],'字典查找平均 O(1)，整个计数平均 O(n)。')
add(6,4,'遍历键值对','for key, value in data.items(): 同时取键和值。',
    '返回所有值严格大于 threshold 的键，按键的字典序升序排列。',[('data','dict[str,int]','数值字典'),('threshold','int','阈值')],
    [([{'b':3,'a':5,'c':1},2],['a','b']),([{},0],[]),([{'x':2},2],[]),([{'z':-1,'a':0},-2],['a','z']),([{'a':1},9],[])],
    'result = []\nfor key, value in data.items():\n    if value > threshold:\n        result.append(key)\nreturn sorted(result)',['items 返回键值对。','筛选后只保留键。','最后排序保证稳定结果。'],'不要依赖输入字典的键顺序来代替题目要求的排序。')
add(6,5,'合并配置','dict.update(other) 用 other 中的字段覆盖同名键。',
    '合并 defaults 和 overrides，同名键以 overrides 为准。',[('defaults','dict','默认配置'),('overrides','dict','覆盖配置')],
    [([{'a':1,'b':2},{'b':9}],{'a':1,'b':9}),([{},{}],{}),([{}, {'x':1}],{'x':1}),([{'x':1},{}],{'x':1}),([{'x':True},{'x':False}],{'x':False})],
    'result = defaults.copy()\nresult.update(overrides)\nreturn result',['先复制默认配置。','update 原地更新，返回 None。','最后返回 result。'],'这是常见的配置覆盖模式。')
add(6,6,'排序去重','set(nums) 去掉重复值；集合本身不保证排序。',
    '返回 nums 去重后按升序排列的列表。',[('nums','list[int]','整数列表')],
    [([[3,1,3,2]],[1,2,3]),([[]],[]),([[1,1]],[1]),([[-2,0,-2]],[-2,0]),([[9,8]],[8,9])],
    'return sorted(set(nums))',['先 set 去重。','再 sorted 排序。','结果需要列表而不是集合。'],'集合非常适合去重与快速成员查询。')
add(6,7,'集合交集','set(a) & set(b) 是同时出现在两边的元素集合。',
    '返回 a、b 的公共元素，去重后升序排列。',[('a','list[int]','列表'),('b','list[int]','列表')],
    [([[1,2,2],[2,3]],[2]),([[],[1]],[]),([[1],[2]],[]),([[3,1],[1,3]],[1,3]),([[-1,0],[-1]],[-1])],
    'return sorted(set(a) & set(b))',['集合交集运算符是 &。','相同值只保留一次。','返回前排序。'],'集合还有并集 |、差集 - 和对称差集 ^。')
add(6,8,'集合差集','set(a) - set(b) 保留只在 a 中、不在 b 中的元素。',
    '返回 a 中未出现在 b 的值，去重后升序排列。',[('a','list[int]','候选值'),('b','list[int]','排除值')],
    [([[1,2,3],[2]],[1,3]),([[],[]],[]),([[1,1],[]],[1]),([[1],[1]],[]),([[-1,0,2],[0]],[-1,2])],
    'return sorted(set(a) - set(b))',['差集有方向。','左边是 a，右边是 b。','排序后返回列表。'],'a-b 和 b-a 通常不同，留意参数的语义。')
add(6,9,'保留首次出现顺序','seen = set() 用于快速判断；result = [] 用于保存顺序。',
    '去掉 nums 的重复值，保留每个值第一次出现的相对顺序。',[('nums','list[int]','整数列表')],
    [([[3,1,3,2,1]],[3,1,2]),([[]],[]),([[0,0]],[0]),([[-1,2,-1]],[-1,2]),([[4,3,2]],[4,3,2])],
    'seen = set()\nresult = []\nfor x in nums:\n    if x not in seen:\n        seen.add(x)\n        result.append(x)\nreturn result',['集合不负责输出顺序。','没见过才添加到结果。','添加之后立刻记入 seen。'],'用集合加列表兼顾平均 O(n) 时间和稳定顺序。')
add(6,10,'按首字母分组','groups.setdefault(key, []) 在键不存在时创建默认列表。',
    '将非空 words 按首字符分组，组内保留输入顺序，区分大小写。',[('words','list[str]','每个词非空')],
    [([['apple','ant','bee']],{'a':['apple','ant'],'b':['bee']}),([[]],{}),([['A','a']],{'A':['A'],'a':['a']}),([['x','x']],{'x':['x','x']}),([['你好','你们']],{'你':['你好','你们']})],
    'groups = {}\nfor word in words:\n    groups.setdefault(word[0], []).append(word)\nreturn groups',['每个键对应一个列表。','setdefault 返回已有值或新建默认值。','对返回的列表调用 append。'],'这为后面的 defaultdict 和 pandas groupby 建立直觉。','基础')

# 07 · 函数
add(7,1,'定义并调用辅助函数','def square(x):\n    return x * x\n定义函数后，用 square(3) 调用。',
    '定义辅助函数 square，返回 a²+b²。',[('a','int','整数'),('b','int','整数')],
    [([3,4],25),([0,0],0),([-2,3],13),([1,1],2),([5,-5],50)],
    'def square(x):\n    return x * x\nreturn square(a) + square(b)',['辅助函数也需要缩进。','分别调用 square(a) 和 square(b)。','本题建议用函数复用平方计算。'],'把重复逻辑提取到函数中，减少重复代码。')
add(7,2,'默认参数','def greet(name, prefix="Hello") 为 prefix 提供默认值。',
    'prefix 为 None 时使用 "Hello"，否则使用给定 prefix；返回 prefix + ", " + name。建议用带默认参数的辅助函数。',[('name','str','名字'),('prefix','str | None','前缀')],
    [(['Ada',None],'Hello, Ada'),(['李雷','你好'],'你好, 李雷'),(['','Hi'],'Hi, '),(['A',''],', A'),(['Bob','Welcome'],'Welcome, Bob')],
    'def greet(name, prefix="Hello"):\n    return f"{prefix}, {name}"\nif prefix is None:\n    return greet(name)\nreturn greet(name, prefix=prefix)',['只有 None 代表缺省，空字符串不是。','省略实参才会使用默认值。','关键字参数写 prefix=prefix。'],'显式传入 None 不会自动触发默认参数，所以需要先判断。')
add(7,3,'接收任意数量的参数','def total(*values): 把多余的位置实参收集成元组。\nf(*items) 把列表展开成实参。',
    '使用 *args 辅助函数返回 nums 总和，空列表返回 0。',[('nums','list[int]','整数列表')],
    [([[1,2,3]],6),([[]],0),([[-1,1]],0),([[9]],9),([[2,2,2]],6)],
    'def total(*values):\n    return sum(values)\nreturn total(*nums)',['定义处的 * 是收集。','调用处的 * 是展开。','sum 可处理空元组。'],'同一个星号语法在定义和调用中分别对应打包与解包。')
add(7,4,'关键字参数打包','def build(**kwargs): 接收任意关键字参数；build(**data) 展开字典。',
    '把 data 的每个键值对转换为 "键=值" 字符串，按键排序后返回列表。值只含整数或字符串。',[('data','dict[str,int|str]','字段')],
    [([{'b':2,'a':1}],['a=1','b=2']),([{}],[]),([{'name':'Ada'}],['name=Ada']),([{'x':''}],['x=']),([{'z':0,'a':-1}],['a=-1','z=0'])],
    'def build(**kwargs):\n    return [f"{key}={kwargs[key]}" for key in sorted(kwargs)]\nreturn build(**data)',['**kwargs 是字典。','sorted(kwargs) 对键排序。','使用 **data 传入各字段。'],'关键字参数可以让配置项和可选参数更容易阅读。')
add(7,5,'lambda 作为排序规则','sorted(items, key=lambda x: x[1]) 按第二项排序；排序是稳定的。',
    'records 每项为 [姓名,分数]，按分数降序；同分保持原顺序。',[('records','list[list]','姓名分数记录')],
    [([[['A',70],['B',90]]],[['B',90],['A',70]]),([[]],[]),([[['A',5],['B',5]]],[['A',5],['B',5]]),([[['Z',0]]],[['Z',0]]),([[['A',-1],['B',2],['C',0]]],[['B',2],['C',0],['A',-1]])],
    'return sorted(records, key=lambda row: row[1], reverse=True)',['key 是函数，不是结果。','lambda row: row[1] 取分数。','reverse=True 表示降序。'],'稳定排序保证相同 key 的元素保留原来的相对顺序。')
add(7,6,'函数组合','可以把一个函数的返回值传给另一个函数。',
    '对每个整数先加 1 再平方，返回结果列表。',[('nums','list[int]','整数列表')],
    [([[1,2]],[4,9]),([[]],[]),([[-1]],[0]),([[0]],[1]),([[-2,3]],[1,16])],
    'def increment(x):\n    return x + 1\ndef square(x):\n    return x * x\nreturn [square(increment(x)) for x in nums]',['计算顺序是先内后外。','先调用 increment。','把结果交给 square。'],'square(increment(x)) 和 increment(square(x)) 是不同的运算。')
add(7,7,'避免可变默认参数','默认参数在函数定义时只创建一次；使用 None 再创建新列表。',
    '使用辅助函数 add_item(item, bucket=None)，分别独立调用两次，返回 [[a],[b]]；两次不应共享列表。',[('a','int','第一项'),('b','int','第二项')],
    [([1,2],[[1],[2]]),([0,0],[[0],[0]]),([-1,3],[[-1],[3]]),([9,8],[[9],[8]]),([4,4],[[4],[4]])],
    'def add_item(item, bucket=None):\n    if bucket is None:\n        bucket = []\n    bucket.append(item)\n    return bucket\nreturn [add_item(a), add_item(b)]',['不要写 bucket=[] 作为默认值。','在函数内部创建新列表。','两次调用都省略 bucket。'],'可变默认值会跨调用保留内容，这是 Python 常见陷阱。','基础')
add(7,8,'闭包保存配置','内部函数可以读取外部函数的局部变量，这叫闭包。',
    '定义 make_multiplier(factor) 返回一个乘法函数；用它将 nums 每项乘以 factor。',[('nums','list[int]','列表'),('factor','int','乘数')],
    [([[1,2],3],[3,6]),([[],5],[]),([[2,-1],0],[0,0]),([[-2,3],-1],[2,-3]),([[5],2],[10])],
    'def make_multiplier(factor):\n    def multiply(x):\n        return x * factor\n    return multiply\nf = make_multiplier(factor)\nreturn [f(x) for x in nums]',['返回函数本身，不要立即调用。','内部函数记住 factor。','获得 f 后再逐个处理数据。'],'闭包可以创建带配置的函数，常用于回调与装饰器。','基础')
add(7,9,'递归累加','递归函数调用自己；必须有不再递归的终止条件。',
    '用递归计算 1 到 n 的和，0≤n≤100。',[('n','int','0–100')],
    [([4],10),([0],0),([1],1),([10],55),([100],5050)],
    'if n == 0:\n    return 0\nreturn n + solve(n - 1)',['先处理 n=0。','问题缩小为 n-1。','不要漏掉当前的 n。'],'每次递归都缩小问题；机考大输入通常应改用循环以避免递归深度限制。','基础')
add(7,10,'为函数加计数装饰器','装饰器接收函数并返回包装函数；nonlocal 允许修改外层局部变量。',
    '对 nums 每项调用一次被计数装饰器包装的平方函数，返回 {"values": 平方列表, "calls": 调用次数}。',[('nums','list[int]','整数列表')],
    [([[2,3]],{'values':[4,9],'calls':2}),([[]],{'values':[],'calls':0}),([[0]],{'values':[0],'calls':1}),([[-1,1]],{'values':[1,1],'calls':2}),([[1,2,3]],{'values':[1,4,9],'calls':3})],
    'calls = 0\ndef counted(func):\n    def wrapper(x):\n        nonlocal calls\n        calls += 1\n        return func(x)\n    return wrapper\n@counted\ndef square(x):\n    return x * x\nvalues = [square(x) for x in nums]\nreturn {"values": values, "calls": calls}',['计数变量放在 solve 中。','wrapper 每次调用时累加。','@counted 等价于 square = counted(square)。'],'这道拓展题建立装饰器直觉；第一次学习可先看分步提示。','进阶')

# 08 · 推导式与迭代
add(8,1,'列表推导式','[表达式 for x in iterable] 创建一个新列表。',
    '返回 nums 中每项的平方列表。',[('nums','list[int]','整数列表')],
    [([[1,2,3]],[1,4,9]),([[]],[]),([[-2,0]],[4,0]),([[5]],[25]),([[-1,1]],[1,1])],
    'return [x * x for x in nums]',['表达式放在最前。','for 的后面是数据来源。','不用 append。'],'列表推导式是普通 for 加 append 的简写。')
add(8,2,'带过滤的推导式','[x for x in nums if 条件] 只保留满足条件的项。',
    '返回 nums 中的正偶数，保持顺序。',[('nums','list[int]','整数列表')],
    [([[-2,0,2,3,4]],[2,4]),([[]],[]),([[1,3]],[]),([[2,2]],[2,2]),([[8,-4,6]],[8,6])],
    'return [x for x in nums if x > 0 and x % 2 == 0]',['同时满足正数和偶数。','过滤条件写在 for 后。','0 不是正数。'],'推导式先遍历、再过滤、最后计算最前面的表达式。')
add(8,3,'字典推导式','{key: value for item in items} 创建字典。',
    '返回每个词到其长度的映射；重复词自然合并。',[('words','list[str]','字符串列表')],
    [([['hi','python']],{'hi':2,'python':6}),([[]],{}),([['']],{'':0}),([['a','a']],{'a':1}),([['你好']],{'你好':2})],
    'return {word: len(word) for word in words}',['键是单词，值是长度。','使用花括号与冒号。','len 返回字符数量。'],'字典的键不能重复，后来的同名键会覆盖先前的值。')
add(8,4,'配对两个序列','zip(a, b) 配对对应位置，默认到较短序列结束。',
    '返回 a、b 对应位置的和，长度以较短列表为准。',[('a','list[int]','序列'),('b','list[int]','序列')],
    [([[1,2],[3,4]],[4,6]),([[1,2],[5]],[6]),([[],[1]],[]),([[0],[0]],[0]),([[-1,2],[1,-2,9]],[0,0])],
    'return [x + y for x, y in zip(a, b)]',['zip 每次产生一对。','用 x, y 解包。','不用手动取 min 长度。'],'zip 是惰性迭代器，可与 for 和推导式组合。')
add(8,5,'用 map 转换','map(func, items) 对每项调用 func，返回迭代器。',
    '将 texts 中所有合法整数字符串转换为整数列表。',[('texts','list[str]','整数字符串列表')],
    [([['1','-2']],[1,-2]),([[]],[]),([[' 3 ','+4']],[3,4]),([['00']],[0]),([['9','10','11']],[9,10,11])],
    'return list(map(int, texts))',['int 本身可以作为函数传入。','不要写 int() 当作 map 的函数参数。','用 list 消费迭代器。'],'map 只描述转换规则，list 才把所有结果收集起来。')
add(8,6,'any 与 all','any 检查是否至少一个为真，all 检查是否全部为真。',
    '返回 {"any_positive": 是否有正数, "all_positive": 是否全是正数}。空列表规定前者 False，后者 True。',[('nums','list[int]','列表')],
    [([[1,-1]],{'any_positive':True,'all_positive':False}),([[]],{'any_positive':False,'all_positive':True}),([[2,3]],{'any_positive':True,'all_positive':True}),([[0]],{'any_positive':False,'all_positive':False}),([[-2,-1]],{'any_positive':False,'all_positive':False})],
    'return {"any_positive": any(x > 0 for x in nums),\n        "all_positive": all(x > 0 for x in nums)}',['使用生成器表达式生成条件值。','不要用 bool(nums) 代替逐项判断。','留意空集合上的 all 定义。'],'any 和 all 都能短路，答案确定后就不再继续取值。')
add(8,7,'展平二维列表','[x for row in matrix for x in row] 的 for 顺序与嵌套循环相同。',
    '按行把 matrix 展平为一维列表，各行可以为空或长度不同。',[('matrix','list[list[int]]','二维列表')],
    [([[[1,2],[3]]],[1,2,3]),([[]],[]),([[[],[1],[]]],[1]),([[[0]]],[0]),([[[1],[2,3],[4]]],[1,2,3,4])],
    'return [x for row in matrix for x in row]',['先遍历行。','再遍历该行中的元素。','最前面的输出表达式是 x。'],'推导式里的多个 for 从左到右对应由外到内的循环。')
add(8,8,'手动取下一个值','it = iter(items)；next(it, default) 在耗尽时返回默认值。',
    '从 nums 的迭代器连续取三次，取不到的位置用 None 补齐，返回长度为3的列表。',[('nums','list[int]','列表')],
    [([[1,2]],[1,2,None]),([[]],[None,None,None]),([[8]],[8,None,None]),([[1,2,3,4]],[1,2,3]),([[0,0,0]],[0,0,0])],
    'it = iter(nums)\nreturn [next(it, None) for _ in range(3)]',['只创建一次迭代器。','next 第二个参数防止 StopIteration。','多余输入不需要取。'],'迭代器保存当前位置，取过的元素不会自动重新开始。')
add(8,9,'yield 生成累积和','含 yield 的函数返回生成器；每次 yield 产出一个值后暂停。',
    '编写生成器，返回 nums 的累积和列表，例如 [2,3,-1] 变成 [2,5,4]。',[('nums','list[int]','列表')],
    [([[2,3,-1]],[2,5,4]),([[]],[]),([[0]],[0]),([[-1,-2]],[-1,-3]),([[1,1,1]],[1,2,3])],
    'def running(values):\n    total = 0\n    for x in values:\n        total += x\n        yield total\nreturn list(running(nums))',['生成器里维护 total。','每一步累加后 yield。','用 list 把生成值收集给判题器。'],'yield 不像 return 那样永久结束函数，下一次迭代会从暂停处继续。','基础')
add(8,10,'分批处理数据','range(0, len(nums), size) 按批次起点前进，切片取每一批。',
    '把 nums 分成大小不超过 size 的连续批次，size 为正整数；最后不足一批也保留。',[('nums','list[int]','数据'),('size','int','正整数')],
    [([[1,2,3,4,5],2],[[1,2],[3,4],[5]]),([[],3],[]),([[1,2],5],[[1,2]]),([[1,2],1],[[1],[2]]),([[0,1,2,3],2],[[0,1],[2,3]])],
    'return [nums[i:i + size] for i in range(0, len(nums), size)]',['起点依次是 0、size、2*size。','切片超出末尾会自动截断。','空输入自然产生空结果。'],'批处理常用于 API 分页、训练数据加载与数据库写入。','基础')

# 09 · 异常、文件与数据交换
add(9,1,'捕获转换错误','try:\n    ...\nexcept ValueError:\n    ...',
    'text 能转换为整数时返回整数，否则返回 None。输入保证是字符串。',[('text','str','待转换文本')],
    [(['12'],12),(['abc'],None),(['  -3 '],-3),(['1.2'],None),([''],None)],
    'try:\n    return int(text)\nexcept ValueError:\n    return None',['把可能失败的 int 放入 try。','只捕获预期的 ValueError。','不要用裸 except 隐藏所有错误。'],'异常处理把正常路径和失败路径分开。')
add(9,2,'多个异常分支','except 可以分别处理不同异常；用精确异常类型描述预期失败。',
    '将 a、b 两个字符串转换为整数并相除。转换失败返回 "invalid"；除数为0返回 "zero"；否则返回商。先完成两个转换。',[('a','str','被除数文本'),('b','str','除数文本')],
    [(['6','2'],3),(['x','2'],'invalid'),(['1','0'],'zero'),(['x','0'],'invalid'),(['0','7'],0)],
    'try:\n    x, y = int(a), int(b)\n    return x / y\nexcept ValueError:\n    return "invalid"\nexcept ZeroDivisionError:\n    return "zero"',['转换和除法都放在 try 中。','错误类型决定返回结果。','先转换两个参数，再做除法。'],'不要把所有失败都显示为同一句话，分类信息更有帮助。')
add(9,3,'内存中的文本文件','from io import StringIO\nwith StringIO(text) as f:\n    lines = f.readlines()',
    '把 text 当作文本文件，返回非空行列表。每行 strip 后为空就忽略，其余返回 strip 后的内容。',[('text','str','文件内容')],
    [([' a\n\n b \n'],['a','b']),([''],[]),([' \n\t'],[]),(['x'],['x']),(['a\r\nb'],['a','b'])],
    'from io import StringIO\nwith StringIO(text) as f:\n    return [line.strip() for line in f if line.strip()]',['StringIO 的用法和文本文件类似。','with 会在退出时关闭文件。','每行清理后再过滤。'],'先用内存文件练习读写，避免依赖电脑上某个固定路径。')
add(9,4,'真正的文件读写','with open(path, "w", encoding="utf-8") as f: 写文件；"r" 读取。',
    '使用临时目录创建 UTF-8 文本文件，写入 text 后再读出并返回内容，保留全部空白。题目不需要你提供磁盘路径。',[('text','str','文本')],
    [(['你好'],'你好'),(['a\nb'],'a\nb'),([''],''),([' x '],' x '),(['123'],'123')],
    'from tempfile import TemporaryDirectory\nfrom pathlib import Path\nwith TemporaryDirectory() as folder:\n    path = Path(folder) / "note.txt"\n    with open(path, "w", encoding="utf-8", newline="") as f:\n        f.write(text)\n    with open(path, "r", encoding="utf-8", newline="") as f:\n        return f.read()',['用 TemporaryDirectory 自动清理。','写完退出 with 后再打开读取。','明确 encoding="utf-8"。'],'临时目录退出后自动删除；newline="" 防止跨平台换行转换。','基础')
add(9,5,'解析 JSON','import json\njson.loads(text) 把 JSON 字符串转换为 Python 对象。',
    '解析合法 JSON 文本 text 并返回对象。JSON 的 null/true/false 对应 None/True/False。',[('text','str','合法 JSON')],
    [(['{"a":1}'],{'a':1}),(['[1,2]'],[1,2]),(['null'],None),(['true'],True),(['"你好"'],'你好')],
    'import json\nreturn json.loads(text)',['loads 的 s 表示从字符串读取。','不用 eval 解析数据。','返回解析后的对象。'],'JSON 是 API 请求、响应和配置文件中最常用的数据格式之一。')
add(9,6,'输出紧凑 JSON','json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))',
    '将 data 序列化为 JSON 字符串：键排序、不转义中文、不添加多余空格。数据不含 NaN。',[('data','any','JSON兼容对象')],
    [([{'b':2,'a':1}],'{"a":1,"b":2}'),([{'名字':'小明'}],'{"名字":"小明"}'),([[]],'[]'),([None],'null'),([[True,False]],'[true,false]')],
    'import json\nreturn json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))',['dumps 返回字符串。','ensure_ascii=False 保留中文。','separators 去掉默认空格。'],'确定的键顺序和空白规则便于测试与数据比较。')
add(9,7,'读取 CSV 表格','csv.DictReader(f) 用第一行作字段名，之后每行返回字典。',
    '读取含 name,score 表头的 CSV 文本，返回分数≥60的姓名列表，保持行顺序。score 保证合法整数。CSV 引号中允许逗号。',[('text','str','CSV 文本')],
    [(['name,score\nAda,90\nBob,50\n'],['Ada']),(['name,score\n'],[]),(['name,score\n"Li, Lei",60\n'],['Li, Lei']),(['name,score\nx,59\ny,60'],['y']),(['name,score\na,100\nb,70'],['a','b'])],
    'import csv\nfrom io import StringIO\nrows = csv.DictReader(StringIO(text))\nreturn [row["name"] for row in rows if int(row["score"]) >= 60]',['不要简单 split(",") 解析 CSV。','DictReader 会处理带引号的字段。','CSV 读出的 score 是字符串。'],'标准库能正确处理字段中的逗号等情况，手写分割容易出错。','基础')
add(9,8,'写入 CSV','csv.writer(f, lineterminator="\\n") 负责必要的引号转义。',
    '将 rows（字符串二维列表）写成 CSV 文本。每行以 \n 结尾，使用默认英文逗号与双引号规则；空列表返回空字符串。',[('rows','list[list[str]]','每行至少一个字段')],
    [([[['a','b'],['1','2']]],'a,b\n1,2\n'),([[]],''),([[['x,y','z']]],'"x,y",z\n'),([[['a"b','c']]],'"a""b",c\n'),([[['']]],'""\n')],
    'import csv\nfrom io import StringIO\nf = StringIO(newline="")\nwriter = csv.writer(f, lineterminator="\\n")\nwriter.writerows(rows)\nreturn f.getvalue()',['用 StringIO 接收输出。','writerows 一次写多行。','getvalue 获取最终文本。'],'CSV writer 会为包含逗号和引号的字段添加正确转义。','基础')
add(9,9,'finally 确保执行','finally 中的代码无论 try 成功或异常都会执行。',
    '尝试把 text 转成整数。返回 {"value": 整数或None, "log": ["opened","closed"]}，用 finally 记录 closed。',[('text','str','文本')],
    [(['7'],{'value':7,'log':['opened','closed']}),(['bad'],{'value':None,'log':['opened','closed']}),(['0'],{'value':0,'log':['opened','closed']}),(['-2'],{'value':-2,'log':['opened','closed']}),([''],{'value':None,'log':['opened','closed']})],
    'log = ["opened"]\ntry:\n    value = int(text)\nexcept ValueError:\n    value = None\nfinally:\n    log.append("closed")\nreturn {"value": value, "log": log}',['异常时也要记录 closed。','不要在 finally 中随意 return。','最后统一返回字典。'],'清理资源通常优先使用 with；finally 适合需要明确执行收尾逻辑的场景。')
add(9,10,'校验配置文件','isinstance(x, dict) 判断类型；bool 是 int 的子类，严格整数可用 type(x) is int。',
    '解析 JSON text。只有最外层为对象，且字段 port 是 1–65535 的整数（布尔值不算）时返回 port；任何解析或校验失败返回 None。',[('text','str','配置文本')],
    [(['{"port":8080}'],8080),(['oops'],None),(['{"port":true}'],None),(['{"port":0}'],None),(['[]'],None),(['{"port":65535}'],65535)],
    'import json\ntry:\n    data = json.loads(text)\nexcept json.JSONDecodeError:\n    return None\nif not isinstance(data, dict):\n    return None\nport = data.get("port")\nif type(port) is int and 1 <= port <= 65535:\n    return port\nreturn None',['解析成功不代表数据符合业务规则。','先验证容器类型，再读字段。','排除 True/False 这样的布尔值。'],'真实程序通常依次检查语法、结构、类型和取值范围。','基础')
