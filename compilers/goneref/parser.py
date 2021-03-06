# gone/parser.py
'''
Project 2:  Write a parser
==========================
In this project, you write the basic shell of a parser for Gone.  A
formal BNF of the language follows.  Your task is to write parsing
rules and build the AST for this grammar using SLY.

program : statements
        | empty

statements :  statements statement
           |  statement

statement :  const_declaration
          |  var_declaration
          |  extern_declaration
          |  assign_statement
          |  print_statement
          |  if_statement
          |  while_statement
          |  return_statement
          |  func_declaration
    
const_declaration : CONST ID = expression ;

var_declaration : VAR ID datatype ;
                | VAR ID datatype = expression ;

extern_declaration : EXTERN func_prototype ;

assign_statement : location = expression ;

print_statement : PRINT expression ;

if_statement : IF expression { statements }
             | IF expression { statements } ELSE { statements }

while_statement : WHILE expression { statements }

return_statement : RETURN expression ;

func_declaration : func_prototype { statements }

func_prototype : FUNC ID LPAREN parameters RPAREN datatype

parameters : parameters , parm_declaration
           | parm_declaration
           | empty

parm_declaration : ID datatype

expression :  + expression
           |  - expression
           |  ! expression
           | expression + expression
           | expression - expression
           | expression * expression
           | expression / expression
           | expression < expression
           | expression <= expression
           | expression > expression
           | expression >= expression
           | expression == expression
           | expression != expression
           | expression && expression
           | expression || expression
           | ( expression )
           | ID ( exprlist ) 
           | location
           | literal

exprlist : | exprlist , expression
           | expression
           | empty

literal : INTEGER     
        | FLOAT       
        | STRING      
        | TRUE
        | FALSE

location : ID
         | ID [ expression ]
         ;

datatype : typename
         : typename [ expression ]
         : typename [ ]
         ;

typename : ID

empty    :

To do the project, follow the instructions contained below.
'''

# ----------------------------------------------------------------------
# parsers are defined using SLY.  You inherit from the Parser class
#
# See http://sly.readthedocs.io/en/latest/
# ----------------------------------------------------------------------
from sly import Parser

# ----------------------------------------------------------------------
# The following import loads a function error(lineno,msg) that should be
# used to report all error messages issued by your parser.  Unit tests and
# other features of the compiler will rely on this function.  See the
# file errors.py for more documentation about the error handling mechanism.
from .errors import error

# ----------------------------------------------------------------------
# Import the lexer class.  It's token list is needed to validate and
# build the parser object.
from .tokenizer import GoneLexer

# ----------------------------------------------------------------------
# Get the AST nodes.  
# Read instructions in ast.py
from .ast import *

class GoneParser(Parser):
    # Same token set as defined in the lexer
    tokens = GoneLexer.tokens

    # ----------------------------------------------------------------------
    # Operator precedence table.   Operators must follow the same 
    # precedence rules as in Python.  Instructions to be given in the project.

    precedence = (
        ('left', 'LOR'),
        ('left', 'LAND'),
        ('nonassoc', 'LT','LE','GT','GE','EQ','NE'),
        ('left','PLUS','MINUS'),
        ('left','TIMES','DIVIDE'),
        ('right','UNARY'),
    )

    # ----------------------------------------------------------------------
    # YOUR TASK.   Translate the BNF in the string below into a collection
    # of parser functions.  For example, a rule such as :
    #
    #   program : statements
    #
    # Gets turned into a Python method like this:
    #
    # @_('statements')
    # def program(self, p):
    #      return Program(p.statements)
    #
    # For symbols such as '(' or '+', you'll need to replace with the name
    # of the corresponding token such as LPAREN or PLUS.
    #
    # In the body of each rule, create an appropriate AST node and return it
    # as shown above.
    #
    # For the purposes of lineno number tracking, you should assign a line number
    # to each AST node as appropriate.  To do this, I suggest pulling the 
    # line number off of any nearby terminal symbol.  For example:
    #
    # @_('PRINT expr SEMI')
    # def print_statement(self, p):
    #     return PrintStatement(p.expr, lineno=p.lineno)
    #

    @_('basicblock')
    def program(self, p):
        return Program(p.basicblock)

    @_('statements')
    def basicblock(self, p):
        return p.statements

    @_('empty')
    def basicblock(self, p):
        return None

    @_('statements statement')
    def statements(self, p):
        p.statements.append(p.statement)
        return p.statements

    @_('statement')
    def statements(self, p):
        return Statements([p.statement])

    @_('const_declaration',
       'var_declaration',
       'func_declaration',
       'extern_declaration',
       'assign_statement',
       'print_statement',
       'ifelse_statement',
       'while_statement',
       'return_statement')
    def statement(self, p):
        return p[0]
    
    @_('CONST ID ASSIGN expression SEMI')
    def const_declaration(self, p):
        return ConstDeclaration(p.ID, p.expression, lineno=p.lineno)

    @_('VAR ID datatype SEMI')
    def var_declaration(self, p):
        return VarDeclaration(p.ID, p.datatype, None, lineno=p.lineno)

    @_('VAR ID datatype ASSIGN expression SEMI')
    def var_declaration(self, p):
        return VarDeclaration(p.ID, p.datatype, p.expression, lineno=p.lineno)

    @_('func_prototype LBRACE basicblock RBRACE')
    def func_declaration(self, p):
        return FunctionDeclaration(p.func_prototype, p.basicblock, lineno=p.lineno)

    @_('EXTERN func_prototype SEMI')
    def extern_declaration(self, p):
        return ExternFunctionDeclaration(p.func_prototype, lineno=p.lineno)

    @_('FUNC ID LPAREN parameters RPAREN datatype')
    def func_prototype(self, p):
        return FunctionPrototype(p.ID, p.parameters, p.datatype, lineno=p.lineno)

    @_('FUNC ID LPAREN RPAREN datatype')
    def func_prototype(self, p):
        return FunctionPrototype(p.ID, [], p.datatype, lineno=p.lineno)

    @_('parameters COMMA parm_declaration')
    def parameters(self, p):
        p.parameters.append(p.parm_declaration)
        return p.parameters

    @_('parm_declaration')
    def parameters(self, p):
        return [ p.parm_declaration ]

    @_('ID datatype')
    def parm_declaration(self, p):
        return ParmDeclaration(p.ID, p.datatype, lineno=p.lineno)

    @_('store_location ASSIGN expression SEMI')
    def assign_statement(self, p):
        return AssignmentStatement(p.store_location, p.expression, lineno=p.lineno)

    @_('PRINT expression SEMI')
    def print_statement(self, p):
        return PrintStatement(p.expression, lineno=p.lineno)

    @_('IF expression LBRACE basicblock RBRACE')
    def ifelse_statement(self, p):
        return IfElseStatement(p.expression, p.basicblock, None, lineno=p.lineno)

    @_('IF expression LBRACE basicblock RBRACE ELSE LBRACE basicblock RBRACE')
    def ifelse_statement(self, p):
        return IfElseStatement(p.expression, p.basicblock0, p.basicblock1, lineno=p.lineno)

    @_('WHILE expression LBRACE basicblock RBRACE')
    def while_statement(self, p):
        return WhileStatement(p.expression, p.basicblock, lineno=p.lineno)

    @_('RETURN expression SEMI')
    def return_statement(self, p):
        return ReturnStatement(p.expression, lineno=p.lineno)

    @_('PLUS expression %prec UNARY',
       'MINUS expression %prec UNARY',
       'LNOT expression %prec UNARY')
    def expression(self, p):
        return Unaryop(p[0], p.expression, lineno=p.lineno)

    @_('expression PLUS expression',
       'expression MINUS expression',
       'expression TIMES expression',
       'expression DIVIDE expression')
    def expression(self, p):
        return Binop(p[1], p.expression0, p.expression1, lineno=p.lineno)

    @_('expression LT expression',
       'expression LE expression',
       'expression GT expression',
       'expression GE expression',
       'expression EQ expression',
       'expression NE expression',
       'expression LOR expression',
       'expression LAND expression')
    def expression(self, p):
        return Binop(p[1], p.expression0, p.expression1, lineno=p.lineno)

    @_('LPAREN expression RPAREN')
    def expression(self, p):
        return p.expression

    @_('ID LPAREN exprlist RPAREN')
    def expression(self, p):
        return FunctionCall(p.ID, p.exprlist, lineno=p.lineno)

    @_('ID LPAREN RPAREN')
    def expression(self, p):
        return FunctionCall(p.ID, [], lineno=p.lineno)

    @_('load_location')
    def expression(self, p):
        return p.load_location

    @_('literal')
    def expression(self, p):
        return p.literal

    @_('exprlist COMMA expression')
    def exprlist(self, p):
        p.exprlist.append(p.expression)
        return p.exprlist

    @_('expression')
    def exprlist(self, p):
        return [ p.expression ]

    @_('INTEGER')
    def literal(self, p):
        return Literal(p.INTEGER, 'int', lineno=p.lineno)

    @_('FLOAT')
    def literal(self, p):
        return Literal(p.FLOAT, 'float', lineno=p.lineno)

    @_('STRING')
    def literal(self, p):
        return Literal(p.STRING, 'string', lineno=p.lineno)

    @_('TRUE',
       'FALSE')
    def literal(self, p):
        if p[0] == 'true':
            val = True
        else:
            val = False
        return Literal(val, 'bool', lineno=p.lineno)

    @_('ID')
    def load_location(self, p):
        return LoadVariable(p.ID, lineno=p.lineno)

    @_('ID LBRACKET expression RBRACKET')
    def load_location(self, p):
        return LoadArray(p.ID, p.expression, lineno=p.lineno)

    @_('ID')
    def store_location(self, p):
        return StoreVariable(p.ID, lineno=p.lineno)

    @_('ID LBRACKET expression RBRACKET')
    def store_location(self, p):
        return StoreArray(p.ID, p.expression, lineno=p.lineno)

    @_('typename')
    def datatype(self, p):
        return p.typename

    @_('typename LBRACKET expression RBRACKET')
    def datatype(self, p):
        return ArrayType(p.typename, p.expression, lineno=p.lineno)

    @_('typename LBRACKET RBRACKET')
    def datatype(self, p):
        return ArrayType(p.typename, None, lineno=p.lineno)

    @_('ID')
    def typename(self, p):
        return Typename(p.ID, lineno=p.lineno)

    @_('')
    def empty(self, p):
        return None

    # ----------------------------------------------------------------------
    # DO NOT MODIFY
    #
    # catch-all error handling.   The following function gets called on any
    # bad input.  p is the offending token or None if end-of-file (EOF).
    def error(self, p):
        if p:
            error(p.lineno, "Syntax error in input at token '%s'" % p.value)
        else:
            error('EOF','Syntax error. No more input.')

# ----------------------------------------------------------------------
#                     DO NOT MODIFY ANYTHING BELOW HERE
# ----------------------------------------------------------------------

def parse(source):
    '''
    Parse source code into an AST. Return the top of the AST tree.
    '''
    lexer = GoneLexer()
    parser = GoneParser()
    ast = parser.parse(lexer.tokenize(source))
    return ast

def main():
    '''
    Main program. Used for testing.
    '''
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write('Usage: python3 -m gone.parser filename\n')
        raise SystemExit(1)

    # Parse and create the AST
    ast = parse(open(sys.argv[1]).read())

    # Output the resulting parse tree structure
    for depth, node in flatten(ast):
        print('%s%s' % (' '*(4*depth), node))

if __name__ == '__main__':
    main()

