# coding=utf-8

import sys
from translate import *


def main():
    in_file = "..\\test\\another.c"
    translator = Translator()
    out_file = "test.py"
    translator.translate(in_file, out_file)


if __name__ == '__main__':
    main()
