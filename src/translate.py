from AST import AST_InternalNode, AST_LeafNode
from yacc import parser as parser
from pre_process import pre_process_file
import os

TAIL = """
if __name__ == "__main__":
    main_0()
"""


class Translator:
    def __init__(self):
        self.functions = []
        self.declarations = []
        self.global_variables = []
        self.variable_table = {}
        self.head = ""
        self.tail = TAIL

    def translate(self, input_file_path, output_file_path):
        try:
            # 模拟预编译
            success, file_content = pre_process_file(input_file_path)
            if not success:
                print(file_content)
                return
            # 解析得到语法树
            tree = parser.parse(file_content)

            # 语义处理
            raw_outcome = self.process(tree)

            # 转化为正确格式，优化代码风格，加上首尾代码
            out = formatIndent(raw_outcome)
            out = self.head + out + self.tail

            # 输出
            with open(output_file_path, 'w+', encoding='utf-8') as output_file:
                output_file.write(out)
            print('{} 成功翻译为 {} 。'.format(input_file_path, output_file_path))
        except Exception as e:
            print(str(e))
