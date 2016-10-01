# coding=utf-8
#
# Filename: 
#
# Create Date: 2016-09-27
#
# ------------------------------------------------------------------

import _ast

if __name__ == '__main__':

    node = _ast.parse("a = 1 + 2")

    print(_ast.dump(node))
