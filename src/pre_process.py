import os
import re


def pre_process_file(input_file_path):
    """
    预处理一个文件，返回值有两个：
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
    except:
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
        if this_line[0] == "#":
            words_list = this_line[1:].split(" ", 2)
            flag_check_ok = True
            if words_list[0] == "define":
                marco_define_list.append((words_list[1], words_list[2]))
            elif words_list[0] == "include":
                if words_list[1][0] == "\"" and words_list[1][-1] == "\"":
                    macro_include_list.append(
                        os.path.join(folder, words[1][1:-1]))
                elif words_list[1][0] == "<" and words_list[1][-1] == ">":
                    pass
                else:
                    flag_check_ok = False
            else:
                flag_check_ok = False
        if not flag_check_ok:
            return False, "文件{}中含有未知字符, 本行是:\n{}".format(input_file_path, this_line)
        index += 1
    # while 结束
    # 处理define
