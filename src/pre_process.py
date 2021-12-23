import os
import re


def pre_process_file(input_file_path):
    """
    预处理一个文件，返回值有两个:
    bool success, string result
    success: 是否成功
    result: 结果
    """
    success = True
    result = ""
    try:
        # 获取文件的文件夹，因为它可能引用了其他的文件
        folder = os.path.dirname(input_file_path)
        file = open(input_file_path, "r", encoding="utf-8")
        file_raw_content = file.read()
        file.close()
    except Exception as e:
        print(e)
        return False, "打开文件{}失败".format(input_file_path)
    # 将文件的内容划分成多个行
    line_list = file_raw_content.split('\n')
    # 识别宏
    marco_define_list = []
    macro_include_list = []
    index = 0
    while index < len(line_list):
        this_line = line_list[index]
        # 剔除无用的行
        this_line = this_line.strip("\t")
        this_line = this_line.strip("\r")
        this_line = this_line.strip("\n")
        this_line = this_line.strip(" ")
        if len(this_line) <= 0:
            line_list.pop(index)
            continue
        # 判断是否是宏
        flag_check_ok = False
        if this_line[0] == "#":
            words_list = this_line[1:].split(" ", 2)
            flag_check_ok = True
            # 识别define，加入define列表准备替换
            if words_list[0] == "define":
                marco_define_list.append((words_list[1], words_list[2]))
            # 识别include，
            elif words_list[0] == "include":
                if words_list[1][0] == "\"" and words_list[1][-1] == "\"":
                    macro_include_list.append(
                        os.path.join(folder, words_list[1][1:-1]))
                elif words_list[1][0] == "<" and words_list[1][-1] == ">":
                    pass
                else:
                    flag_check_ok = False
            else:
                flag_check_ok = False
            if not flag_check_ok:
                return False, "文件{}中含有未知字符, 本行是:\n{}".format(input_file_path, this_line)
            line_list.pop(index)
            continue
        index += 1
    # while 结束
    # define 处理
    s = '\n'.join(line_list)
    for m in marco_define_list:
        s = re.sub(m[0], m[1], s)
    # include 处理
    i = ''
    for m in macro_include_list:
        inc = pre_process_file(m)
        if inc[0]:
            i = i + inc[1]
        else:
            return inc
    s = i + s + '\n'
    return True, s


def formatIndent(item, rank=-1):
    INDENT_STRING = '    '
    if type(item) == str:
        # 对于只声明不定义的变量需要补上=None
        if '(' not in item and ' ' not in item and '=' not in item and item != '' and item != 'break' \
                and item != 'continue' and item != 'pass' and item != 'else:' and item != 'if' and item != 'return':
            item += ' = None'
        return INDENT_STRING * rank + item
    if type(item) == list:
        lines = []
        for i in item:
            lines.append(formatIndent(i, rank + 1))
        return '\n'.join(lines)
