# coding=utf-8
#
# Filename: 
#
# Create Date: 2016-09-27
#
# ------------------------------------------------------------------

import ast

if __name__ == '__main__':

    node = ast.parse("a = 1 + 2")

    print(ast.dump(node))
