# coding=utf-8
#
# Filename: test_example_from_justin.py
#
# Create Date: 2016-09-26
#
# ------------------------------------------------------------------

import pytest
from .tokenizer import GoneLexer

lexer = GoneLexer()

def token_assert(t, token_type, token_value):
    assert t.type == token_type
    assert t.value == token_value


@pytest.mark.parametrize(("input", "expected"),
                         [("12.", ('FLOAT', 12.)), ("1.2", ('FLOAT', 1.2)), (".12", ('FLOAT', .12)), ])
def test_float(input, expected):
    tokens = [x for x in lexer.tokenize(input)]
    token_assert(tokens[0], expected[0], expected[1])
