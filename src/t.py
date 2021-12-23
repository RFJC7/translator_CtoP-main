import re
from AST1 import AST_InternalNode, AST_LeafNode
from yacc import parser as parser
from pre_process import pre_process_file, formatIndent
import os
import copy

TAIL = """
if __name__ == "__main__":
    main()
"""


class Translator:
    def __init__(self):
        self.functions = []
        self.declarations = []
        self.global_variables = []
        self.variable_table = {}
        self.head = ""
        self.tail = TAIL

    def process(self, tree):
        # 找到所有函数定义function_definition与声明declaration
        def handle_func(tree):
            if tree.key == 'function_definition':
                self.functions.append(tree)
            else:
                self.declarations.append(tree)

        while True:
            if tree.key == 'start_node':
                if len(tree.children) == 2:
                    handle_func(tree.children[1].children[0])
                    tree = tree.children[0]
                else:
                    handle_func(tree.children[0].children[0])
                    break

        # 测试输出获得的子子节点
        # print("self.functions:")
        # for item in self.functions:
        #     print(item.key)
        #     if(isinstance(item, AST_LeafNode)):
        #         print(item.value)
        # print("self.declarations:")
        # for item in self.declarations:
        #     print(item.key)
        #     if(isinstance(item, AST_LeafNode)):
        #         print(item.value)

        code_list = []
        # 处理所有子节点
        # 1.处理声明，函数声明与全局变量声明两种情况
        self.declarations = reversed(self.declarations)
        for declaration in self.declarations:
            if self.is_function_declaration(declaration):
                continue
            self.extract_global_declaration(declaration)
            code = self.traversal(declaration, [], 'declaration')
            code_list.extend(code)
            code_list.append('')  # 空行
        for function in self.functions:
            # 进入函数（作用域），备份变量表
            table_copy = copy.deepcopy(self.variable_table)
            # self.name_replacement(function)
            # 离开函数（作用域），恢复变量表
            self.variable_table = table_copy
            code = self.traversal(function, [], 'function')
            code_list.extend(code)
            code_list.append('')  # 空行
        return code_list

    # 翻译叶子节点
    def leaf_string(self, tree):
        if tree.value == ';':
            return ['']
        elif tree.value == '&&':
            return [' and ']
        elif tree.value == '||':
            return [' or ']
        elif tree.value == '!':
            return ['not ']
        elif tree.value == 'true':
            return ['True']
        elif tree.value == 'false':
            return ['False']
        elif tree.value == 'struct':
            return ['class']
        else:
            return [tree.value]

    # 遍历树得到翻译结果
    def traversal(self, tree, stack, type):
        stack.append(tree.key)
        code_list = []
        flag_list = []

        if isinstance(tree, AST_LeafNode):
            stack.pop()
            return self.leaf_string(tree)
        for child in tree.children:
            # 遍历树
            code = self.traversal(child, stack, type)
            code_list.append(code)

            # flag_list.append(flag)
        # try:
        #     # 计算flag属性的值
        #     flag_to_upper = self.flag_calculate(tree, flag_list)
        # except Exception as e:
        #     print(str(e))

        # 通过子节点的code属性和计算得到的flag属性计算此节点的code属性
        pycode = self.code_compose(tree, code_list)
        stack.pop()
        return pycode

    # 提取全局变量
    def extract_global_declaration(self, tree):
        if isinstance(tree, AST_LeafNode):
            return
        for child in tree.children:
            # print(child.key)
            if child.key == 'ID':
                self.global_variables.append(child.value)
            else:
                self.extract_global_declaration(child)

    # 判断是否是函数声明
    def is_function_declaration(self, tree):
        for child in tree.children:
            if isinstance(child, AST_LeafNode):
                return False
            if child.key == 'direct_declarator':
                if len(child.children) > 1 and isinstance(child.children[1], AST_LeafNode) \
                        and child.children[1].value == '(':
                    return True
                else:
                    return False
            else:
                if self.is_function_declaration(child):
                    return True
        return False

    def translate(self, input_file_path, output_file_path):
        try:
            # 模拟预编译
            success, file_content = pre_process_file(input_file_path)
            if not success:
                print(file_content)
                return
            # 解析得到语法树
            tree = parser.parse(file_content)
            print(tree)
            # 语义处理
            raw_outcome = self.process(tree)
            print("raw_outcome:")
            print(raw_outcome)
            # 转化为正确格式，优化代码风格，加上首尾代码
            out = formatIndent(raw_outcome)
            out = self.head + out + self.tail

            # 输出
            with open(output_file_path, 'w+', encoding='utf-8') as output_file:
                output_file.write(out)
            print('{} 成功翻译为 {} 。'.format(input_file_path, output_file_path))
        except Exception as e:
            print(str(e))

    # 翻译函数
    def code_compose(self, tree, code_list):
        # 变量声明
        if tree.key == 'init_declarator':
            print("init_declarator")
            print("tree:    "+str(tree))
            tmp = str(tree.children[0])
            while(True):
                if(tmp[0] == "(" and tmp[-1] == ")"):
                    tmp = str(tmp[2:-2])
                else:
                    break
            result = tmp
            for child in tree.children[1:]:
                result += str(child)
            print("result", result)
            print()
            return result
         # 函数声明
        elif tree.key == 'function_definition':
            print("function_definition")
            print("tree:    "+str(tree))
            if len(tree.children) == 4:
                pass
            elif len(tree.children) == 3:
                function_body = []
                # 无脑加入所有全局变量
                for global_var in self.global_variables:
                    function_body.append('global ' + global_var)
                for code in code_list[2]:
                    function_body.append(code)
                """
                def 函数名:
                    函数体（缩进+1）
                """
                result = ['def ' + code_list[1][0] + ':',
                          function_body]
                print(result)
                print()
                return result
        # return 语句
        elif tree.key == 'jump_statement' and tree.children[0].key == 'return':
            print("jump_statement && return ")
            print("tree:    "+str(tree))
            if len(tree.children) == 2:
                """
                return
                """
                result = ['return']
                print("result:  "+str(result))
                print()
                return result
            elif len(tree.children) == 3:
                """
                return 返回值
                """
                result = [code_list[0][0] + ' ' + code_list[1][0]]
                print("result:  "+str(result))
                print()
                return result
        # 去除{}
        elif tree.key == 'compound_statement':
            if len(tree.children) == 3:
                """
                    代码块（缩进+1）
                """
                return code_list[1]
            # {}内为空，Python需要有 pass
            elif len(tree.children) == 2:
                """
                    pass（缩进+1）
                """
                return ['pass']
        # 去除类型名
        elif tree.key == 'declaration_specifiers':
            return ''
        else:
            lst = []
            flag = True
            for code in code_list:
                if len(code) != 1:
                    flag = False
            if flag:
                s = ''
                for code in code_list:
                    s += code[0]
                lst.extend(s)
            else:
                for code in code_list:
                    lst.extend(code)
            return lst
