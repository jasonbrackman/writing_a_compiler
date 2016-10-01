# coding=utf-8
#
# Filename: 
#
# Create Date: 2016-09-30
#
# ------------------------------------------------------------------

import pytest
import tokenizer

test_data = [
    ('var x int = 10;', [('VAR', 'var'),
                         ('ID', 'x'),
                         ('ID', 'int'),
                         ('ASSIGN', '='),
                         ('INTEGER', 10),
                         ('SEMI', ';')]),

    ('const var x float = 10.0', [
                         ('CONST', 'const'),
                         ('VAR', 'var'),
                         ('ID', 'x'),
                         ('ID', 'float'),
                         ('ASSIGN', '='),
                         ('FLOAT', 10.0),
                         ('SEMI', ';')])]


@pytest.mark.parametrize("test_input, expected", test_data)
def test_tokenizer(test_input, expected):
    lexer = tokenizer.GoneLexer()
    results = [(tok.type, tok.value) for tok in lexer.tokenize(test_input)]
    for k, v in zip(results, expected):
        assert k == v

