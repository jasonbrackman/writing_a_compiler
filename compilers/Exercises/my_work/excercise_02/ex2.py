# coding=utf-8
#
# Filename: ex2.py
#
# Create Date: 2016-09-26
#
# ------------------------------------------------------------------

import ast
from simpleast import *

def test_01():
    """
        Module(body=[Assign(targets=[Name(id='a', ctx=Store())],
           value=BinOp(left=Num(n=2), op=Add(),
           right=BinOp(left=Num(n=3), op=Mult(),
           right=BinOp(left=Num(n=4), op=Add(), right=Num(n=5)))))])
    :return:
    """
    text = "a = 2 + 3 * (4 + 5)"

    c = ast.parse(text)
    print(ast.dump(c))


def test_02():
    location = Identifier('a')
    left1 = Number(2)
    left2 = Number(3)
    left3 = Number(4)
    right3 = Number(5)
    right2 = BinOp('+', left3, right3)  # (4 + 5)
    right1 = BinOp('*', left2, right2)  # 3 * (4 + 5)
    value = BinOp('+', left1, right1)  # 2 + 3 * (4 + 5)
    node = Assignment(location, value)

if __name__ == "__main__":
    test_01()
    test_02()