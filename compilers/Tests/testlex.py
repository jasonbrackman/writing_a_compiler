# coding=utf-8
#
# Filename: testlex.py
#
# Create Date: 2016-09-26
#
# Tests for pytest (3rd party)
#
# Run:  python3 -m pytest Tests/testlex.py

from gone.tokenizer import GoneLexer


def test_simple():
    lexer = GoneLexer()
    toks = list(lexer.tokenize('+ - * /'))
    types = [t.type for t in toks]
    vals = [t.value for t in toks]
    assert types == ['PLUS', 'MINUS', 'TIMES', 'DIVIDE']
    assert vals == ['+', '-', '*', '/']


def test_keywords():
    lexer = GoneLexer()
    toks = list(lexer.tokenize('const var func extern'))
    types = [t.type for t in toks]
    vals = [t.value for t in toks]
    assert types == ['CONST', 'VAR', 'FUNC', 'EXTERN']
