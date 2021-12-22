import ply.lex as lex
from ply.lex import TOKEN

tokens = [
    'ID',  # 标识符，即变量名、函数名、常量名
    'STRING_LITERAL',  #字符串原文
    'CONSTANCE',  # 常量
    'ELLIPSIS',   # 省略
    'EQUAL',   # 判断是否相等，即==
    # AO打头的都是赋值运算符
    'AO_PLUS',  # +=
    'AO_SUB',   # -=
    'AO_MUL',   # *=
    'AO_DIV',   # /=
    'AO_SL',  # 左移赋值，即Shift left，<<=
    'AO_SR',  # 右移赋值，即shift right, >>=
    'AO_MOD',  # 取余数赋值
    'AO_AND',  # 和赋值
    'AO_OR',  #或赋值
    'AO_XOR',  #或赋值
    'INC',  #++
    'DEC',  #--
    'AND',  #&&
    'OR',  #||
    'SHIFT_LEFT',  #<<
    'SHIFT_RIGHT',  #>>
    'PTR',   #->
    'GE',  #greater than or equal,大于等于,>=
    'LE',  #less than or equal,小于等于,<=
    'NE',  #not equal,不等于,!=
]

#保留的c语言关键字
reserved = {
    'auto': 'AUTO',
    'bool': 'BOOL',
    'break': 'BREAK',
    'case': 'CASE',
    'const': 'CONST',
    'continue': 'CONTINUE',
    'char': 'CHAR',
    'default': 'DEFAULT',
    'do': 'DO',
    'double': 'DOUBLE',
    'else': 'ELSE',
    'enum': 'ENUM',
    'extern': 'EXTERN',
    'float': 'FLOAT',
    'for': 'FOR',
    'goto': 'GOTO',
    'if': 'IF',
    'inline': 'INLINE',
    'int': 'INT',
    'long': 'LONG',
    'register': 'REGISTER',
    'restrict': 'RESTRICT',
    'return': 'RETURN',
    'short': 'SHORT',
    'signed': 'SIGNED',
    'sizeof': 'SIZEOF',
    'static': 'STATIC',
    'struct': 'STRUCT',
    'switch': 'SWITCH',
    'typedef': 'TYPEDEF',
    'union': 'UNION',
    'unsigned': 'UNSIGNED',
    'volatile' : 'VOLATILE',
    'void': 'VOID',
    'while': 'WHILE',
}

tokens = tokens + list(reserved.values())

literals = ';,:=.&![]{}~()+-*/%><^|?'

t_EQUAL = r'=='
t_AO_PLUS = r'\+='
t_AO_SUB = r'-='
t_AO_MUL = r'\*='
t_AO_DIV = r'/='
t_AO_SL = r'<<='
t_AO_SR = r'>>='
t_AO_MOD = r'%='
t_AO_AND = r'&='
t_AO_OR = r'\|='
t_AO_XOR = r'^='
t_INC = r'\+\+'
t_DEC = r'--'
t_AND = r'&&'
t_OR = r'\|\|'
t_SHIFT_LEFT = r'<<'
t_SHIFT_RIGHT = r'>>'
t_PTR = r'->'
t_GE = r'>='
t_LE = r'<='
t_NE = r'!='
t_ELLIPSIS = r'\.\.\.'

# 十六进制数
H = r'[0-9a-fA-F]'
# 科学计数法后缀
E = r'[Ee][+-]?[0-9]+'
# 浮点数修饰符
FS = r'(f|F|l|L)'
# 整型数修饰符
IS = r'(u|U|l|L)*'

# 布尔
boolean = r'(true|false)'
# 整型数
integer = r'(0[xX]%s+%s?|[0-9]+%s%s?|[0-9]+%s?)' % (H, IS, E, IS, IS)
# 浮点数（小数）
decimal = r'(([0-9]+\.[0-9]*(%s)?%s?)|([0-9]*\.[0-9]+(%s)?%s?))' % (E, FS, E, FS)
# 字符
char = r'(\'(\\.|[^\\\'])+\')'
# 常量
constant = r'(%s|%s|%s|%s)' % (decimal, integer, char, boolean)

#常量
@TOKEN(constant)
def t_CONSTANCE(t):
    return t

#标识符
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'ID')    # 也有可能是保留关键字
    return t

# 行号
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# 字符串的内容
def t_STRING_LITERAL(t):
    r'"(\\.|[^\\"])*"'
    return t

# 空白字符（空格、换行忽略掉）
t_ignore = ' \t\v\f'

# 注释
def t_COMMENT(t):
    r'//[^\n]*'
    pass

# 错误处理
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# 构建词法分析器
lexer = lex.lex()

# 测试程序
if __name__ == '__main__':
    while True:
        try:
            data = input('"input a sentence:" > ')
            lex.input(data)
            while True:
                tok = lexer.token()
                if not tok:
                    break
                print(tok)
        except EOFError:
            break


