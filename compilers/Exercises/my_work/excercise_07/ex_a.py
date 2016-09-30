# coding=utf-8
#
# Filename: 
#
# Create Date: 2016-09-30
#
# ------------------------------------------------------------------
import dis


def foo(a, b):
    if a < b:
        print("yes")
    else:
        print("no")


def countdown(n):
    while n > 0:
        print("T-minus", n)
        n -= 1


if __name__ == "__main__":
    #  dis.dis(foo)
    dis.dis(countdown)
