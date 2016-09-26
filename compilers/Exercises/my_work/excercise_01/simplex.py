# simplelex.py

from sly import Lexer


class SimpleLexer(Lexer):
    # Token names
    tokens = { 'NUMBER', 'ID', 'NE', 'EQ', 'ASSIGN', 'PLUS', 'LPAREN', 'RPAREN', 'TIMES', 'LE', 'GE', 'LT', 'GT' }

    # Ignored characters
    ignore = ' \t'

    # Token regexs

    LPAREN = r'[(]'
    RPAREN = r'[)]'
    NUMBER = r'\d+'
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    LE = r'<='
    LT = r'<'
    GE = r'>='
    GT = r'[>]'
    NE = r'!='
    EQ = r'=='
    ASSIGN = r'='
    PLUS = r'\+'
    TIMES = r'\*'

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    @_(r'[a-zA-Z_][a-zA-Z0-9_]*')
    def ID(self, t):
        keywords = {'if', 'else', 'while'}
        if t.value in keywords:
            t.type = t.value.upper()
        return t

    def error(self, value):
        print('Bad character %r' % value[0])
        self.index += 1


def lexify(text):
    lexer = SimpleLexer()
    return [tok for tok in lexer.tokenize(text)]


# Example
if __name__ == '__main__':
    text = 'abc 123 $ cde 456'
    text = 'a = 3 + (4 * 5)'
    text = '''
               a < b
               a <= b
               a > b
               a >= b
               a == b
               a != b
        '''
    text = '''
               if a < b
               else a <= b
               while a > b
               a >= b
               a == b
               a != b
        '''
    lexer = SimpleLexer()
    for tok in lexer.tokenize(text):
        print(tok)

