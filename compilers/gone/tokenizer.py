# gone/tokenizer.py
r'''
Project 1 - Write a Lexer
=========================
In the first project, you are going to write a simple lexer for the
Gone language.  The project is presented as code that you must
read and extend (this file).  Please read the complete contents of
this file and carefully complete the steps indicated by comments.

Overview:
---------
The process of lexing is that of taking input text and breaking it
down into a stream of tokens. Each token is like a valid word from the
dictionary.  Essentially, the role of the lexer is to simply make sure
that the input text consists of valid symbols and tokens prior to any
further processing related to parsing.

Each token is defined by a regular expression.  Thus, your primary task
in this first project is to define a set of regular expressions for
the language.  The actual job of lexing will be handled by SLY
(https://github.com/dabeaz/sly)

Specification:
--------------
Your lexer must recognize the following symbols and tokens.  The name
on the left is the token name, the value on the right is the matching
text.  Note: Additional features will be added in later projects.

Reserved Keywords:
    CONST   : 'const'
    VAR     : 'var'  
    PRINT   : 'print'
    FUNC    : 'func'
    EXTERN  : 'extern'

Identifiers (Same rules as for Python):
    ID      : Text starting with a letter or '_', followed by any number
              number of letters, digits, or underscores.
              Examples:  'abc' 'ABC' 'abc123' '_abc' 'a_b_c'

Operators and Delimiters:
    PLUS     : '+'
    MINUS    : '-'
    TIMES    : '*'
    DIVIDE   : '/'
    ASSIGN   : '='
    SEMI     : ';'
    LPAREN   : '('
    RPAREN   : ')'
    COMMA    : ','
    LBRACKET : '['
    RBRACKET : ']'

Literals:
    INTEGER : '123'   (decimal)

    FLOAT   : '1.234'
              '1.234e1'
              '1.234e+1'
              '1.234e-1'
              '1e2'
              '.1234'
              '1234.'

    STRING  : '"Hello World"'

Comments:  To be ignored by your lexer
     //             Skips the rest of the line
     /* ... */      Skips a block (no nesting allowed)

Errors: Your lexer must recognized and report the following error messages:

     lineno: Illegal char 'c'         
     lineno: Unterminated string     
     lineno: Unterminated comment

Testing
-------
For initial development, try running the lexer on a sample input file
such as:

     bash % python3 -m gone.tokenizer sample.g

Carefully study the output of the lexer and make sure that it makes sense.
Once you are reasonably happy with the output, try running some of the
more tricky tests:

     bash % python3 -m gone.tokenizer testlex1.g
     bash % python3 -m gone.tokenizer testlex2.g

Bonus: How would you go about turning these tests into proper unit tests?
'''

# ----------------------------------------------------------------------
# The following import loads a function error(lineno, msg) that should be
# used to report all error messages issued by your lexer.  Unit tests and
# other features of the compiler will rely on this function.  See the
# file errors.py for more documentation about the error handling mechanism.
from gone.errors import error

# -----------------------------------------------------------------------
# The SLY package. https://github.com/dabeaz/sly
from sly import Lexer

# -----------------------------------------------------------------------
# Lexers are defined by a class that inherits from sly.Lexer.  Follow
# the instructions contained in the class below.

class GoneLexer(Lexer):
    # ----------------------------------------------------------------------
    # Keyword set. This set lists all of the special names used in the
    # language such as 'if', 'else', 'while', 'return', etc.
    keywords = { 'var', 'const', 'print', 'func', 'extern', }

    # ----------------------------------------------------------------------
    # Token set. This set identifies the complete list of token names
    # to be recognized by your lexer.  Do not change any of these names.
    tokens = {
        # keywords (incorporates upper cased versions of keywords above)
        * { kw.upper() for kw in keywords },
                 
        # Identifiers
        'ID', 

        # Literals
        'INTEGER', 'FLOAT', 'STRING',

        # Operators and delimiters
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE',

        # Delimiters and other symbols
        'ASSIGN', 'LPAREN', 'RPAREN', 'SEMI', 'COMMA', 
        'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET',

    }

    # ----------------------------------------------------------------------
    # Ignored characters (whitespace)
    #
    # The following characters are ignored completely by the lexer. 
    # Do not change.
    ignore = ' \t\r'

    # ----------------------------------------------------------------------
    # Ignored patterns.  Fill in the regexs below to ignore comments
    #

    # C-style comment (/* ... */)
    @_(r'/\*(.|\n)*?\*/')
    def COMMENT(self, t):
        self.lineno += t.value.count('\n')

    # C++-style comment (//...)
    @_(r'//.*\n')
    def CPPCOMMENT(self, t):
        self.lineno += 1

    # Unterminated C-style comment. This is an error you should report
    @_(r'/\*(.|\n)*$')
    def COMMENT_UNTERM(self, t):
        error(self.lineno, "Unterminated comment")

    # ----------------------------------------------------------------------
    # *** YOU MUST COMPLETE : write the regexs indicated below ***
    # 
    # Tokens for simple symbols: + - * / = ( ) ; < > , etc.
    #
    # Caution: Definition order matters. Longer symbols should appear 
    # before shorter symbols that are a substring (for example, the
    # pattern for <= should go before <).

    PLUS      = r'\+'
    MINUS     = r'-'
    TIMES     = r'\*'
    DIVIDE    = r'/'
    SEMI      = r';'
    LPAREN    = r'\('
    RPAREN    = r'\)'
    COMMA     = r','
    LBRACKET  = r'\['
    RBRACKET  = r'\]'
    ASSIGN = r'='
    #LE = r'<='
    #LT = r'<'
    #GE = r'>='
    #GT = r'[>]'
    #NE = r'!='
    #EQ = r'=='

    # ----------------------------------------------------------------------
    # *** YOU MUST COMPLETE : write the regexs and additional code below ***
    #
    # Tokens for literals, INTEGER, FLOAT, STRING. 

    # Floating point constant.   You must recognize floating point numbers in
    # the following formats:
    #
    #   1.23
    #   123.
    #   .123
    #
    # Bonus: Recognize floating point numbers in scientific notation 
    #
    #   1.23e1
    #   1.23e+1
    #   1.23e-1
    #   1e1
    #
    # The value should be converted to a Python float when lexed

    @_(r'([0-9]+\.[0-9]+)|(\.\d+)|(\d+\.)')
    def FLOAT(self, t):
        t.value = float(t.value)
        return t

    # Integer literal
    #
    #     1234             (decimal)
    #
    # The value should be converted to a Python int when lexed.
    #
    # Bonus: Recognize integers in different bases such as 0x1a, 0o13 or 0b111011.
    @_(r'\d+')
    def INTEGER(self, t):
        # Conversion to a Python int
        t.value = int(t.value)
        return t

    # String constant. You must recognize text enclosed in quotes.
    # For example:
    #
    #     "Hello World"
    #
    # The quotes are not included as part of the value.
    #
    # Bonus:   How would you recognize string escape codes like \" or \n?
    @_(r'\".*?\"')
    def STRING(self, t):
        t.value = t.value[1:-1]
        return t

    # Unterminated string literal (an error)
    @_(r'\"(\.|.)*?\n')
    def STRING_UNTERM(self, t):
        error(self.lineno, "Unterminated string literal")
        self.lineno += 1

    # ----------------------------------------------------------------------
    # *** YOU MUST COMPLETE : Write the regex and add keywords ***
    #
    # Identifiers and keywords. 
    #
    # Match a raw identifier.  Identifiers follow the same rules as Python.
    # That is, they start with a letter or underscore (_) and can contain
    # an arbitrary number of letters, digits, or underscores after that.
    # Language keywords such as "if" and "while" are also matched as 
    # identifiers. You need to catch these and change their token type
    # to match the appropriate keyword.

    @_(r'[a-zA-Z_][a-zA-Z0-9_]*')
    def ID(self, t):
        # *** YOU IMPLEMENT ***
        # Add code to look for keywords such as 'var', 'const', 'print', etc.
        # Change the token type as needed. For example:
        #
        # if t.value == 'var':
        #     t.type = 'VAR"

        if t.value in self.keywords:
            t.type = t.value.upper()

        return t

    # ----------------------------------------------------------------------
    # Method that ignores one or more newlines and increments the line number
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += len(t.value)

    # ----------------------------------------------------------------------
    # Bad character error handling
    def error(self, value):
        error(self.lineno,"Illegal character %r" % value[0])
        self.index += 1
    
# ----------------------------------------------------------------------
#                DO NOT CHANGE ANYTHING BELOW THIS PART
#
# Use this main program to test/debug your lexer.  Run it using the -m option
#
#    bash % python3 -m gone.tokenizer filename.g
#
# ----------------------------------------------------------------------
def main():
    '''
    Main program. For debugging purposes.
    '''
    import sys

    #sys.argv = ['', r'/Users/jasonbrackman/PycharmProjects/writing_a_compiler/compilers/Tests/parsetest3.g']

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 -m gone.tokenizer filename\n")
        raise SystemExit(1)

    lexer = GoneLexer()
    text = open(sys.argv[1]).read()
    for tok in lexer.tokenize(text):
        print(tok)

if __name__ == '__main__':
    # From Terminal: python3 -m gone.tokenizer Tests/test_comment.g
    main()

