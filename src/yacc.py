import re
import ply.yacc as yacc
from lex import tokens, reserved
from AST import AST_InternalNode
from AST import AST_LeafNode

# 开始节点 -> 全局声明列表
def p_start_node(p):
    ''' start_node : start_node global_declaration
                         |  global_declaration'''
    p[0] = AST_InternalNode('start_node', p[1:])

# 全局声明 -> 函数定义 | 变量 or 函数声明
def p_global_declaration(p):
    ''' global_declaration : function_definition
                             | declaration  '''
    p[0] = AST_InternalNode('global_declaration', p[1:])

# 变量声明 -> 声明修饰符(extern 等); / 声明修饰符 + 声明列表;
def p_declaration(p):
    ''' declaration : declaration_specifiers ';'
                    | declaration_specifiers init_declarator_list ';' '''
    p[0] = AST_InternalNode('declaration', p[1:])

# 声明列表 -> 逗号分隔的声明
def p_init_declarator_list(p):
    ''' init_declarator_list : init_declarator
                             | init_declarator_list ',' init_declarator '''
    p[0] = AST_InternalNode('init_declarator_list', p[1:])

# 声明 -> 只声明变量 | 声明时赋值
def p_init_declarator(p):
    ''' init_declarator : declarator
                        | declarator '=' initializer '''
    p[0] = AST_InternalNode('init_declarator', p[1:])

# 声明修饰符 -> 存储类型 | 函数 | 类型 修饰符列表
def p_declaration_specifiers(p):
    ''' declaration_specifiers 	: storage_class_specifier declaration_specifiers_no_s
                                | type_specifier
                                | type_specifier declaration_specifiers_no_ts
                                | type_qualifier declaration_specifiers'''
    p[0] = AST_InternalNode('declaration_specifiers', p[1:])

# 不能定义多个存储类型
def p_declaration_specifiers_no_s(p):
    ''' declaration_specifiers_no_s : type_specifier
                                | type_specifier declaration_specifiers_no_ts_s
                                | type_qualifier declaration_specifiers_no_s'''
    p[0] = AST_InternalNode('declaration_specifiers', p[1:])

# 不能定义多个变量类型, 且必须有一个
def p_declaration_specifiers_no_ts(p):
    ''' declaration_specifiers_no_ts : storage_class_specifier
                                | storage_class_specifier declaration_specifiers_no_ts_s
                                | type_qualifier
                                | type_qualifier declaration_specifiers_no_ts'''
    p[0] = AST_InternalNode('declaration_specifiers', p[1:])

# 见上, 可以定义多个类型限定符
def p_declaration_specifiers_no_ts_s(p):
    ''' declaration_specifiers_no_ts_s : type_qualifier
                                | type_qualifier declaration_specifiers_no_ts_s'''
    p[0] = AST_InternalNode('declaration_specifiers', p[1:])

# 储存修饰符
def p_storage_class_specifier(p):
    ''' storage_class_specifier : TYPEDEF
                                | EXTERN
                                | STATIC
                                | AUTO
                                | REGISTER '''
    p[0] = AST_InternalNode('storage_class_specifier', p[1:])

# 类型修饰符, 简化版本实现， 修饰符只能放在一起。
def p_type_specifier(p):
    ''' type_specifier : VOID
                       | CHAR
                       | SHORT
                       | SHORT INT
                       | INT SHORT
                       | INT
                       | LONG
                       | LONG INT
                       | INT LONG
                       | FLOAT
                       | DOUBLE
                       | FLOAT LONG
                       | LONG FLOAT
                       | DOUBLE LONG
                       | LONG DOUBLE
                       | SIGNED
                       | SIGNED INT
                       | SIGNED SHORT
                       | SIGNED SHORT INT
                       | SIGNED INT SHORT
                       | SIGNED LONG
                       | SIGNED LONG INT
                       | SIGNED INT LONG
                       | UNSIGNED
                       | UNSIGNED INT
                       | UNSIGNED SHORT
                       | UNSIGNED SHORT INT
                       | UNSIGNED INT SHORT
                       | UNSIGNED LONG
                       | UNSIGNED LONG INT
                       | UNSIGNED INT LONG
                       | struct_or_union_specifier
                       | enum_specifier
                       | BOOL '''
    p[0] = AST_InternalNode('type_specifier', p[1:])

# 类型限定符，vs实测不支持Restrict，因此略过
def p_type_qualifier(p):
    ''' type_qualifier : CONST
                       | VOLATILE
                       | RESTRICT '''
    p[0] = AST_InternalNode('type_qualifier', p[1:])

# 枚举类型
def p_enum_specifier(p):
    ''' enum_specifier : ENUM '{' enumerator_list '}'
                        | ENUM identifier '{' enumerator_list '}'
                        | ENUM '{' enumerator_list ',' '}'
                        | ENUM identifier '{' enumerator_list ',' '}'
                        | ENUM identifier '''
    p[0] = AST_InternalNode('enum_specifier', p[1:])

# 枚举类型  枚举项列表
def p_enumerator_list(p):
    ''' enumerator_list : enumerator
                        | enumerator_list ',' enumerator '''
    p[0] = AST_InternalNode('enumerator_list', p[1:])

# 枚举类型  枚举项
def p_enumerator(p):
    ''' enumerator : identifier
                   | identifier '=' constant_expression '''
    p[0] = AST_InternalNode('enumerator', p[1:])

# 结构体，联合类型定义
def p_struct_or_union_specifier(p):
    ''' struct_or_union_specifier : struct_or_union identifier '{' struct_declaration_list '}'
                                  | struct_or_union '{' struct_declaration_list '}'
                                  | struct_or_union identifier '''
    p[0] = AST_InternalNode('struct_or_union_specifier', p[1:])

# struct和union关键字
def p_struct_or_union(p):
    ''' struct_or_union : STRUCT
                        | UNION '''
    p[0] = AST_InternalNode('struct_or_union', p[1:])

# 结构体或联合类型中的成员变量
def p_struct_declaration_list(p):
    ''' struct_declaration_list : struct_declaration
                                | struct_declaration_list struct_declaration '''
    p[0] = AST_InternalNode('struct_declaration_list', p[1:])

# 结构体或联合的单个成员变量
def p_struct_declaration(p):
    ''' struct_declaration : specifier_qualifier_list struct_declarator_list ';' '''
    p[0] = AST_InternalNode('struct_declaration', p[1:])

# 类型标识符和类型限定符列表
def p_specifier_qualifier_list(p):
    ''' specifier_qualifier_list : type_specifier specifier_qualifier_list_no_ts
                                 | type_specifier
                                 | type_qualifier specifier_qualifier_list
                                 | type_qualifier  '''
    p[0] = AST_InternalNode('specifier_qualifier_list', p[1:])

# 不能定义多个变量类型
def p_specifier_qualifier_list_no_ts(p):
    ''' specifier_qualifier_list_no_ts : type_qualifier specifier_qualifier_list_no_ts
                                        | type_qualifier  '''
    p[0] = AST_InternalNode('specifier_qualifier_list', p[1:])

# 某个类型的多个标识符
def p_struct_declarator_list(p):
    ''' struct_declarator_list : struct_declarator
                               | struct_declarator_list ',' struct_declarator '''
    p[0] = AST_InternalNode('struct_declarator_list', p[1:])

# 单个成员变量
def p_struct_declarator(p):
    ''' struct_declarator : declarator
                          | ':' constant_expression
                          | declarator ':' constant_expression '''
    p[0] = AST_InternalNode('struct_declarator', p[1:])

# 单个成员变量
def p_declarator(p):
    ''' declarator : pointer direct_declarator
                   | direct_declarator '''
    p[0] = AST_InternalNode('declarator', p[1:])

# 指针类型
def p_pointer(p):
    ''' pointer : '*'
                | '*' type_qualifier_list
                | '*' pointer
                | '*' type_qualifier_list pointer '''
    p[0] = AST_InternalNode('pointer', p[1:])

# 类型限定符列表
def p_type_qualifier_list(p):
    ''' type_qualifier_list : type_qualifier
                            | type_qualifier_list type_qualifier '''
    p[0] = AST_InternalNode('type_qualifier_list', p[1:])

# 直接声明
def p_direct_declarator(p):
    ''' direct_declarator : direct_declarator_forlist
                        | '(' declarator ')'
                        | direct_function_declarator '''
    p[0] = AST_InternalNode('direct_declarator', p[1:])

# 直接声明
def p_direct_declarator_forlist(p):
    ''' direct_declarator_forlist : identifier
                                | '(' pointer direct_declarator_forlist ')'
                                | '(' direct_declarator_forlist ')'
                                | direct_declarator_forlist '[' constant_expression ']'
                                | identifier '[' constant_expression ']'
                                | identifier '[' ']' '''
    if len(p) == 2 or (len(p) == 4 and p[2] == '['):
        p[1] = AST_LeafNode('identifier', p[1])
    p[0] = AST_InternalNode('direct_declarator_forlist', p[1:])

# 函数参数 列表
def p_parameter_list(p):
    ''' parameter_list : parameter_list_definition
                       | parameter_declaration
                       | parameter_declaration ',' parameter_list '''
    p[0] = AST_InternalNode('parameter_list', p[1:])


# 函数单个参数声明
def p_parameter_declaration(p):
    ''' parameter_declaration : declaration_specifiers declarator
                              | declaration_specifiers abstract_declarator
                              | declaration_specifiers '''
    p[0] = AST_InternalNode('parameter_declaration', p[1:])

# 纯常量表达式
def p_constant_expression(p):
    ''' constant_expression : conditional_expression '''
    p[0] = AST_InternalNode('constant_expression', p[1:])

# 条件表达式
def p_conditional_expression(p):
    ''' conditional_expression : logical_or_expression
                               | logical_or_expression '?' expression ':' conditional_expression '''
    p[0] = AST_InternalNode('conditional_expression', p[1:])

# 逻辑 or 表达式
def p_logical_or_expression(p):
    ''' logical_or_expression : logical_and_expression
                              | logical_or_expression OR logical_and_expression '''
    p[0] = AST_InternalNode('logical_or_expression', p[1:])

# 逻辑 and 表达式
def p_logical_and_expression(p):
    ''' logical_and_expression : inclusive_or_expression
                               | logical_and_expression AND inclusive_or_expression '''
    p[0] = AST_InternalNode('logical_and_expression', p[1:])

# 或运算表达式（或运算）
def p_inclusive_or_expression(p):
    ''' inclusive_or_expression : exclusive_or_expression
                                | inclusive_or_expression '|' exclusive_or_expression '''
    p[0] = AST_InternalNode('inclusive_or_expression', p[1:])

# 异或运算表达式（异或运算）
def p_exclusive_or_expression(p):
    ''' exclusive_or_expression : and_expression
                                | exclusive_or_expression '^' and_expression '''
    p[0] = AST_InternalNode('exclusive_or_expression', p[1:])

# 与运算表达式（与运算）
def p_and_expression(p):
    ''' and_expression : equality_expression
                       | and_expression '&' equality_expression '''
    p[0] = AST_InternalNode('and_expression', p[1:])

# 等值判断表达式（相等、不等）
def p_equality_expression(p):
    ''' equality_expression : relational_expression
                            | equality_expression EQUAL relational_expression
                            | equality_expression NE relational_expression '''
    p[0] = AST_InternalNode('equality_expression', p[1:])

# 关系表达式（大于、小于、大于等于、小于等于）
def p_relational_expression(p):
    ''' relational_expression : shift_expression
                              | relational_expression '<' shift_expression
                              | relational_expression '>' shift_expression
                              | relational_expression LE shift_expression
                              | relational_expression GE shift_expression '''
    p[0] = AST_InternalNode('relational_expression', p[1:])

# 位移表达式（左移、右移）
def p_shift_expression(p):
    ''' shift_expression : additive_expression
                         | shift_expression SHIFT_LEFT additive_expression
                         | shift_expression SHIFT_RIGHT additive_expression '''
    p[0] = AST_InternalNode('shift_expression', p[1:])

# 加法表达式（加减）
def p_additive_expression(p):
    ''' additive_expression : multiplicative_expression
                            | additive_expression '+' multiplicative_expression
                            | additive_expression '-' multiplicative_expression '''
    p[0] = AST_InternalNode('additive_expression', p[1:])

# 乘法表达式（乘除模）
def p_multiplicative_expression(p):
    ''' multiplicative_expression : cast_expression
                                  | multiplicative_expression '*' cast_expression
                                  | multiplicative_expression '/' cast_expression
                                  | multiplicative_expression '%' cast_expression '''
    p[0] = AST_InternalNode('multiplicative_expression', p[1:])

# 类型转化表达式
def p_cast_expression(p):
    ''' cast_expression : unary_expression
                        | '(' specifier_qualifier_list ')' cast_expression '''
    p[0] = AST_InternalNode('cast_expression', p[1:])

# 一元表达式
def p_unary_expression(p):
    ''' unary_expression : primary_expression
                         | unary_operator cast_expression
                         | SIZEOF unary_expression
                         | SIZEOF '(' specifier_qualifier_list ')' '''
    p[0] = AST_InternalNode('unary_expression', p[1:])

# 一元运算符(常量)
def p_unary_operator(p):
    ''' unary_operator : '+'
                       | '-'
                       | '~'
                       | '!' '''
    p[0] = AST_InternalNode('unary_operator', p[1:])

# 主要表达式(无变量)
def p_primary_expression(p):
    ''' primary_expression : CONSTANCE
                           | STRING_LITERAL
                           | '(' expression ')' '''
    p[0] = AST_InternalNode('primary_expression', p[1:])

# 表达式(常量)
def p_expression(p):
    ''' expression : constant_expression
                   | expression ',' constant_expression '''
    p[0] = AST_InternalNode('expression', p[1:])

# 抽象声明
def p_abstract_declarator(p):
    ''' abstract_declarator : pointer
                            | direct_abstract_declarator
                            | pointer direct_abstract_declarator '''
    p[0] = AST_InternalNode('abstract_declarator', p[1:])

# 直接抽象声明
def p_direct_abstract_declarator(p):
    ''' direct_abstract_declarator : '(' abstract_declarator ')'
                                   | '[' ']'
                                   | '[' constant_expression ']'
                                   | direct_abstract_declarator '[' constant_expression ']'
                                   | parameter_type_list_definition '''
    p[0] = AST_InternalNode('direct_abstract_declarator', p[1:])

# 书签=================================

# 函数定义。这里指针内部不支持括号
def p_function_definition(p):
    ''' function_definition : declaration_specifiers pointer direct_function_declarator compound_statement
                            | declaration_specifiers direct_function_declarator compound_statement '''
    p[0] = AST_InternalNode('function_definition', p[1:])

# 直接声明
def p_direct_function_declarator(p):
    ''' direct_function_declarator : '(' direct_function_declarator ')'
                                    | identifier parameter_type_list_definition '''
    p[0] = AST_InternalNode('direct_function_declarator', p[1:])

def p_identifier(p):
    ''' identifier : '(' identifier ')'
                    | ID '''
    if p[1] != '(':
        p[1] = AST_LeafNode('ID', p[1])

# 函数参数 列表（定义时）
def p_parameter_type_list_definition(p):
    ''' parameter_type_list_definition : '(' ')'
                                       | '(' parameter_type_list_definition ')'
                                       | '(' parameter_list ')' '''
    p[0] = AST_InternalNode('parameter_type_list_definition', p[1:])

# 函数参数 列表（定义时）
def p_parameter_list_definition(p):
    ''' parameter_list_definition : parameter_declaration '=' constant_expression  ',' parameter_list_definition
                                  | parameter_declaration '=' constant_expression 
                                  | ELLIPSIS '''
    p[0] = AST_InternalNode('parameter_list_definition', p[1:])


# 复合语句（代码块）
def p_compound_statement(p):
    ''' compound_statement : '{' '}'
                           | '{' block_item_list '}' '''
    p[0] = AST_InternalNode('compound_statement', p[1:])


# 代码块元素 列表
def p_block_item_list(p):
    ''' block_item_list : block_item
                        | block_item_list block_item '''
    p[0] = AST_InternalNode('block_item_list', p[1:])


# 代码块元素
def p_block_item(p):
    ''' block_item : declaration
                   | statement '''
    p[0] = AST_InternalNode('block_item', p[1:])

# 语句
# 推导 -> 标记语句（labeled_statement）|
def p_statement(p):
    ''' statement : labeled_statement
                  | compound_statement
                  | expression_statement
                  | selection_statement
                  | iteration_statement
                  | jump_statement '''
    p[0] = AST_InternalNode('statement', p[1:])

# 标记语句
def p_labeled_statement(p):
    ''' labeled_statement : identifier ':' '''
    p[0] = AST_InternalNode('labeled_statement', p[1:])

# 表达式语句
def p_expression_statement(p):
    ''' expression_statement : ';'
                             | expression_variable ';' '''
    p[0] = AST_InternalNode('expression_statement', p[1:])

# 表达式（含变量）
def p_expression_variable(p):
    ''' expression_variable : assignment_expression
                            | expression_variable ',' assignment_expression '''
    p[0] = AST_InternalNode('expression', p[1:])

# 赋值表达式
def p_assignment_expression(p):
    ''' assignment_expression : conditional_expression_v
                              | unary_expression_v assignment_operator assignment_expression '''
    p[0] = AST_InternalNode('assignment_expression', p[1:])

# 赋值运算符
def p_assignment_operator(p):
    ''' assignment_operator : '='
                            | AO_MUL
                            | AO_DIV
                            | AO_MOD
                            | AO_PLUS
                            | AO_SUB
                            | AO_SL
                            | AO_SR
                            | AO_AND
                            | AO_XOR
                            | AO_OR '''
    p[0] = AST_InternalNode('assignment_operator', p[1:])

# 条件表达式
def p_conditional_expression_v(p):
    ''' conditional_expression_v : logical_or_expression_v
                               | logical_or_expression_v '?' expression_variable ':' conditional_expression_v '''
    p[0] = AST_InternalNode('conditional_expression_v', p[1:])


# 逻辑 or 表达式
def p_logical_or_expression_v(p):
    ''' logical_or_expression_v : logical_and_expression_v
                              | logical_or_expression_v OR logical_and_expression_v '''
    p[0] = AST_InternalNode('logical_or_expression_v', p[1:])


# 逻辑 and 表达式
def p_logical_and_expression_v(p):
    ''' logical_and_expression_v : inclusive_or_expression_v
                               | logical_and_expression_v AND inclusive_or_expression_v '''
    p[0] = AST_InternalNode('logical_and_expression_v', p[1:])


# 或运算表达式（或运算）
def p_inclusive_or_expression_v(p):
    ''' inclusive_or_expression_v : exclusive_or_expression_v
                                | inclusive_or_expression_v '|' exclusive_or_expression_v '''
    p[0] = AST_InternalNode('inclusive_or_expression_v', p[1:])


# 异或运算表达式（异或运算）
def p_exclusive_or_expression_v(p):
    ''' exclusive_or_expression_v : and_expression_v
                                | exclusive_or_expression_v '^' and_expression_v'''
    p[0] = AST_InternalNode('exclusive_or_expression_v', p[1:])


# 与运算表达式（与运算）
def p_and_expression_v(p):
    ''' and_expression_v : equality_expression_v
                       | and_expression_v '&' equality_expression_v '''
    p[0] = AST_InternalNode('and_expression_v', p[1:])


# 等值判断表达式（相等、不等）
def p_equality_expression_v(p):
    ''' equality_expression_v : relational_expression_v
                            | equality_expression_v EQUAL relational_expression_v
                            | equality_expression_v NE relational_expression_v '''
    p[0] = AST_InternalNode('equality_expression_v', p[1:])


# 关系表达式（大于、小于、大于等于、小于等于）
def p_relational_expression_v(p):
    ''' relational_expression_v : shift_expression_v
                              | relational_expression_v '<' shift_expression_v
                              | relational_expression_v '>' shift_expression_v
                              | relational_expression_v LE shift_expression_v
                              | relational_expression_v GE shift_expression_v '''
    p[0] = AST_InternalNode('relational_expression_v', p[1:])


# 位移表达式（左移、右移）
def p_shift_expression_v(p):
    ''' shift_expression_v : additive_expression_v
                         | shift_expression_v SHIFT_LEFT additive_expression_v
                         | shift_expression_v SHIFT_RIGHT additive_expression_v '''
    p[0] = AST_InternalNode('shift_expression_v', p[1:])


# 加法表达式（加减）
def p_additive_expression_v(p):
    ''' additive_expression_v : multiplicative_expression_v
                            | additive_expression_v '+' multiplicative_expression_v
                            | additive_expression_v '-' multiplicative_expression_v '''
    p[0] = AST_InternalNode('additive_expression_v', p[1:])


# 乘法表达式（乘除模）
def p_multiplicative_expression_v(p):
    ''' multiplicative_expression_v : cast_expression_v
                                  | multiplicative_expression_v '*' cast_expression_v
                                  | multiplicative_expression_v '/' cast_expression_v
                                  | multiplicative_expression_v '%' cast_expression_v '''
    p[0] = AST_InternalNode('multiplicative_expression_v', p[1:])


# 类型转化表达式, 这里开始区分变量与非变量
def p_cast_expression_v(p):
    ''' cast_expression_v : unary_expression_v
                        | unary_expression_v_constance
                        | '(' specifier_qualifier_list ')' cast_expression_v '''
    p[0] = AST_InternalNode('cast_expression_v', p[1:])

# 一元表达式常数版
def p_unary_expression_v_constance(p):
    ''' unary_expression_v_constance : primary_expression_v
                         | SIZEOF unary_expression_v_constance
                         | SIZEOF '(' specifier_qualifier_list ')' '''
    p[0] = AST_InternalNode('unary_expression_v', p[1:])

# 一元表达式变量版
def p_unary_expression_v(p):
    ''' unary_expression_v : postfix_expression_v
                         | INC unary_expression_v
                         | DEC unary_expression_v
                         | unary_operator_v cast_expression_v
                         | SIZEOF unary_expression_v '''
    p[0] = AST_InternalNode('unary_expression_v', p[1:])


# 一元运算符
def p_unary_operator_v(p):
    ''' unary_operator_v : '&'
                       | '*'
                       | '+'
                       | '-'
                       | '~'
                       | '!' '''
    p[0] = AST_InternalNode('unary_operator_v', p[1:])


# 后缀表达式。编译器实测不支持++test--之类的写法，我觉得没必要就仍然支持。这里处理变量。
# 注意.和PTR不支持ID带括号
def p_postfix_expression_v(p):
    ''' postfix_expression_v : postfix_expression_v_no_func
                           | postfix_expression_v '[' expression ']'
                           | identifier '(' ')'
                           | identifier '(' argument_expression_list ')'
                           | postfix_expression_v '.' ID
                           | postfix_expression_v PTR ID
                           | postfix_expression_v_no_func INC
                           | postfix_expression_v_no_func DEC '''
    if len(p) == 4 and p[2] != '(':
        p[3] = AST_LeafNode('ID', p[3])
    p[0] = AST_InternalNode('postfix_expression_v', p[1:])

# 实测函数返回值不支持后置++和--，前置仍然支持
def p_postfix_expression_v_no_func(p):
    ''' postfix_expression_v_no_func : identifier
                                | '(' postfix_expression_v_no_func ')'
                                | postfix_expression_v_no_func '[' expression ']'
                                | postfix_expression_v_no_func '.' ID
                                | postfix_expression_v_no_func PTR ID  '''
    if len(p) == 4 and p[1] != '(':
        p[3] = AST_LeafNode('ID', p[3])
    p[0] = AST_InternalNode('postfix_expression_v_no_func', p[1:])

# 主要表达式, 处理非ID的情况
def p_primary_expression_v(p):
    ''' primary_expression_v : CONSTANCE
                           | STRING_LITERAL
                           | '(' expression_variable ')' '''
    p[0] = AST_InternalNode('primary_expression_v', p[1:])

# 选择语句
def p_selection_statement(p):
    ''' selection_statement : IF '(' expression_variable ')' statement ELSE statement
                            | IF '(' expression_variable ')' statement
                            | SWITCH '(' expression_variable ')' statement_switch '''
    p[0] = AST_InternalNode('selection_statement', p[1:])

# 复合语句（代码块）
def p_compound_statement_switch(p):
    ''' compound_statement_switch : '{' '}'
                           | '{' block_item_list_switch '}' '''
    p[0] = AST_InternalNode('compound_statement', p[1:])


# 代码块元素 列表
def p_block_item_list_switch(p):
    ''' block_item_list_switch : block_item_switch
                        | block_item_list_switch block_item_switch '''
    p[0] = AST_InternalNode('block_item_list_switch', p[1:])


# 代码块元素
def p_block_item_switch(p):
    ''' block_item_switch : declaration
                   | statement_switch '''
    p[0] = AST_InternalNode('block_item_switch', p[1:])

# 语句
# 推导 -> 标记语句（labeled_statement）|
def p_statement_switch(p):
    ''' statement_switch : labeled_statement_switch
                        | compound_statement_switch
                        | expression_statement
                        | selection_statement
                        | iteration_statement
                        | jump_statement '''
    p[0] = AST_InternalNode('statement', p[1:])

# 标记语句，不支持ID带括号
def p_labeled_statement_switch(p):
    ''' labeled_statement_switch : ID ':'
                            | CASE constant_expression ':' statement
                            | DEFAULT ':' statement '''
    if len(p) == 3:
        p[1] = AST_LeafNode('ID', p[1])
    p[0] = AST_InternalNode('labeled_statement', p[1:])

# 循环语句
def p_iteration_statement(p):
    ''' iteration_statement : WHILE '(' expression_variable ')' statement
                            | DO statement WHILE '(' expression_variable ')' ';'
                            | FOR '(' expression_statement expression_statement ')' statement
                            | FOR '(' expression_statement expression_statement expression_variable ')' statement
                            | FOR '(' declaration expression_statement ')' statement
                            | FOR '(' declaration expression_statement expression_variable ')' statement '''
    p[0] = AST_InternalNode('iteration_statement', p[1:])

# 跳转语句，不支持ID带括号
def p_jump_statement(p):
    ''' jump_statement : GOTO ID ';'
                       | CONTINUE ';'
                       | BREAK ';'
                       | RETURN ';'
                       | RETURN expression_variable ';' '''
    if len(p) == 4 and p[1] == 'goto':
        p[2] = AST_LeafNode('ID', p[2])
    p[0] = AST_InternalNode('jump_statement', p[1:])


# 暂时放着不管
# 初始化 列表

# 实参表达式 列表
def p_argument_expression_list(p):
    ''' argument_expression_list : assignment_expression
                                 | argument_expression_list ',' assignment_expression '''
    p[0] = AST_InternalNode('argument_expression_list', p[1:])

def p_initializer_list(p):
    ''' initializer_list : initializer
                         | designation initializer
                         | initializer_list ',' initializer
                         | initializer_list ',' designation initializer '''
    p[0] = AST_InternalNode('initializer_list', p[1:])


# 初始化 项
def p_initializer(p):
    ''' initializer : assignment_expression
                    | '{' initializer_list '}'
                    | '{' initializer_list ',' '}' '''
    p[0] = AST_InternalNode('initializer', p[1:])


def p_designation(p):
    ''' designation : designator_list '=' '''
    p[0] = AST_InternalNode('designation', p[1:])


# 指示符 列表
def p_designator_list(p):
    ''' designator_list : designator
                        | designator_list designator '''
    p[0] = AST_InternalNode('designator_list', p[1:])


# 指示符
# 例如 -> [XX]  .XX
def p_designator(p):
    ''' designator : '[' constant_expression ']'
                   | '.' ID '''
    if len(p) == 3:
        p[2] = AST_LeafNode('ID', p[2])
    p[0] = AST_InternalNode('designator', p[1:])

# 语法分析  错误处理
def p_error(p):
    print('[Error]: type - %s, value - %s, lineno - %d, lexpos - %d' % (p.type, p.value, p.lineno, p.lexpos))

parser = yacc.yacc()

# 测试程序
if __name__ == '__main__':
    while True:
        try:
            s = input('yacc > ')
            with open(s, 'r') as file:
                result = parser.parse(file.read())
                print("result=\n",result)
        except EOFError:
            break
