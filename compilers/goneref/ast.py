# gone/ast.py
'''
Abstract Syntax Tree (AST) objects.

This file defines classes for different kinds of nodes of an Abstract
Syntax Tree.  During parsing, you will create these nodes and connect
them together.  In general, you will have a different AST node for
each kind of grammar rule.  A few sample AST nodes can be found at the
top of this file.  You will need to add more on your own.
'''

# DO NOT MODIFY
class AST(object):
    '''
    Base class for all of the AST nodes.  Each node is expected to
    define the _fields attribute which lists the names of stored
    attributes.   The __init__() method below takes positional
    arguments and assigns them to the appropriate fields.  Any
    additional arguments specified as keywords are also assigned. 
    '''
    _fields = []
    def __init__(self, *args, **kwargs):
        assert len(args) == len(self._fields)
        for name, value in zip(self._fields, args):
            setattr(self, name, value)
        # Assign additional keyword arguments if supplied
        for name, value in kwargs.items():
            setattr(self, name, value)

# ----------------------------------------------------------------------
# Specific AST nodes.
#
# For each of these nodes, you need to add the appropriate _fields = []
# specification that indicates what fields are to be stored.  Just as
# an example, for a binary operator, you might store the operator, the
# left expression, and the right expression like this:
#
#    class Binop(AST):
#        _fields = ['op','left','right']
#
# Suggestion:  The nodes are listed here in a suggested order of work
# on your parse.  You should start simple and incrementally work your
# way up to building the complete grammar
# ----------------------------------------------------------------------

class Literal(AST):
    '''
    A literal value such as an integer, float, or string constant.
    '''
    _fields = ['value', 'typename']        


class Typename(AST):
    '''
    The name of a datatype such as 'int', 'float', or 'string'
    '''
    _fields = ['name']         

class ArrayType(AST):
    '''
    An array datatype.  For example 'int [50]'
    '''
    _fields = ['typename', 'size']

class LoadVariable(AST):
    '''
    A variable name loaded inside of an expression.  For example, 
    in an expression "2 + a", the 'a' refers to a LoadVariable
    '''
    _fields = ['name']     


class LoadArray(AST):
    '''
    An array appearing the right hand side of an assignment.
    For example in the expression "2 + a[n]"
    '''
    _fields = ['name', 'index']

class StoreArray(AST):
    '''
    An array appearing the left-hand-side of an assignment.
    For example in the expression "a[n] = 2"
    '''
    _fields = ['name', 'index']
    
class Unaryop(AST):
    '''
    A unary operator such as +expr or -expr
    '''
    _fields = ['op','expr']         

class Binop(AST):
    '''
    A binary operator such as expr + expr.
    '''
    _fields = ['op','left','right'] 

class FunctionCall(AST):
    '''
    A function call such as foo(2,3)
    '''
    _fields = ['name','arglist']

class AssignmentStatement(AST):
    '''
    An assignment statement such as x = expr.  The left hand side
    is a location and the right hand side is an expression.
    '''
    _fields = ['store_location','expr']   

class PrintStatement(AST):
    '''
    A print statement such as print(expr)
    '''
    _fields = ['expr']          # YOU MUST DEFINE


class Statements(AST):
    '''
    A sequence of zero or more statements.
    '''
    _fields = ['statements']          # YOU MUST DEFINE

    def append(self,stmt):
        self.statements.append(stmt)

    def __len__(self):
        return len(self.statements)


class Program(AST):
    '''
    A node representing an entire program.  A program
    consists of a series of statements.
    '''
    _fields = ['statements'] 

class VarDeclaration(AST):
    '''
    A variable declaration such as var x int = 42;
    '''
    _fields = ['name','typename','expr']
    
class ConstDeclaration(AST):
    '''
    A constant declaration such as const pi = 3.14159;
    '''
    _fields = ['name','expr']

class ParmDeclaration(AST):
    '''
    A parameter declaration of name and type
    '''
    _fields = ['name', 'typename']

class FunctionPrototype(AST):
    '''
    A function prototype giving the name and types of the function.
    '''
    _fields = ['name', 'parameters', 'typename']

class ExternFunctionDeclaration(AST):
    '''
    An external function declaration.   extern func foo(x int) int;
    '''
    _fields = ['prototype']

# Conditions and while loops (Project 7)
class IfElseStatement(AST):
    '''
    An if-else statement
    '''
    _fields = ['condition', 'if_statements','else_statements']

class WhileStatement(AST):
    '''
    A while-loop
    '''
    _fields = ['condition', 'statements']

# Functions (Project 8)
class ReturnStatement(AST):
    '''
    Return statement
    '''
    _fields = ['expr']

class FunctionDeclaration(AST):
    '''
    A definition of a function
    '''
    _fields = ['prototype','statements']

# ----------------------------------------------------------------------
#                  DO NOT MODIFY ANYTHING BELOW HERE
# ----------------------------------------------------------------------

# The following classes for visiting and rewriting the AST are taken
# from Python's ast module.   

# DO NOT MODIFY
class NodeVisitor(object):
    '''
    Class for visiting nodes of the parse tree.  This is modeled after
    a similar class in the standard library ast.NodeVisitor.  For each
    node, the visit(node) method calls a method visit_NodeName(node)
    which should be implemented in subclasses.  The generic_visit() method
    is called for all nodes where there is no matching visit_NodeName() method.

    Here is a example of a visitor that examines binary operators:

        class VisitOps(NodeVisitor):
            visit_Binop(self,node):
                print('Binary operator', node.op)
                self.visit(node.left)
                self.visit(node.right)
            visit_Unaryop(self,node):
                print('Unary operator', node.op)
                self.visit(node.expr)

        tree = parse(txt)
        VisitOps().visit(tree)
    '''
    def visit(self,node):
        '''
        Execute a method of the form visit_NodeName(node) where
        NodeName is the name of the class of a particular node.
        '''
        if node:
            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method, self.generic_visit)
            return visitor(node)
        else:
            return None
    
    def generic_visit(self,node):
        '''
        Method executed if no applicable visit_ method can be found.
        This examines the node to see if it has _fields, is a list,
        or can be further traversed.
        '''
        for field in getattr(node, '_fields'):
            value = getattr(node, field, None)
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, AST):
                        self.visit(item)
            elif isinstance(value, AST):
                self.visit(value)

# DO NOT MODIFY
def flatten(top):
    '''
    Flatten the entire parse tree into a list for the purposes of
    debugging and testing.  This returns a list of tuples of the
    form (depth, node) where depth is an integer representing the
    parse tree depth and node is the associated AST node.
    '''
    class Flattener(NodeVisitor):
        def __init__(self):
            self.depth = 0
            self.nodes = []
        def generic_visit(self, node):
            self.nodes.append((self.depth, node))
            self.depth += 1
            NodeVisitor.generic_visit(self, node)
            self.depth -= 1

    d = Flattener()
    d.visit(top)
    return d.nodes
