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

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, ' '.join(['%s=%s' % (f, getattr(self, f)) for f in self._fields]))

    def dump(self):
        for depth, node in flatten(self):
            print('%s%s' % (' ' * (4 * depth), node))

# ----------------------------------------------------------------------
# Specific AST nodes.
#
# For each of these nodes, you need to add the appropriate _fields = []
# specification that indicates what fields are to be stored.  Just as
# an example, for a binary operator, you might store the operator, the
# left expression, and the right expression like this:
#
#    class BinOp(AST):
#        _fields = ['op', 'left', 'right']
#
# In the parser.py file, you're going to create nodes using code
# similar to this:
#
#    class GoneParser(Parser):
#        ...
#        @_('expr PLUS expr')
#        def expr(self, p):
#            return BinOp(p[1], p.expr0, p.expr1)
#
# ----------------------------------------------------------------------


class Program(AST):
    """
    program expression
    """
    _fields = ['statements']


class Statements(AST):
    """
    statements can be more than one.
    """
    _fields = ['statements']

    def append(self, stmt):
        self.statements.append(stmt)

    def __len__(self):
        return len(self.statements)


class PrintStatement(AST):
    """
    print expression ;
    """
    _fields = ['expr']


class Literal(AST):
    """
    A literal value such as 2, 2.5, or "two"
    """
    _fields = ['value', 'typename']


class Typename(AST):
    '''
    The name of a datatype such as 'int', 'float', or 'string'
    '''
    _fields = ['name']


class StoreVariable(AST):
    '''
    A variable name being used as the left-hand-side of an assignment.
    For example, in an assignment a = 2, the 'a' refers to StoreVariable.
    '''
    _fields = ['name']


class ConstDeclaration(AST):
    """
    A constant declaration such as const pi = 3.14159;
    """
    _fields = ['name', 'expr']


class VarDeclaration(AST):
    """
    Assigning something to a variable: float pi = 3.14159;
    """
    _fields = ['name', 'typename', 'expr']


class FunctionDeclaration(AST):
    '''
    A definition of a function
    '''
    _fields = ['prototype', 'statements']


class ExternFunction(AST):
    '''
    An external function declaration.   extern func foo(x int) int;
    '''
    _fields = ['prototype']


class ParmDeclaration(AST):
    '''
    A parameter declaration of name and type
    '''
    _fields = ['name', 'typename']

class FunctionCall(AST):
    '''
    A function call such as foo(2,3)
    '''

    _fields = ['name', 'arguments']

class AssignmentStatement(AST):
    '''
    An assignment statement such as x = expr.  The left hand side
    is a location and the right hand side is an expression.
    '''
    _fields = ['location', 'value']


class FunctionPrototype(AST):
    '''
    A function prototype giving the name and types of the function.
    '''
    _fields = ['name', 'parameters', 'typename']


class ReadLocation(AST):
    """
    Location of item.
    """
    _fields = ['location']


class VarLocation(AST):
    """
    Location of variable?
    """
    _fields = ['name']


class UnaryOp(AST):
    """
    -1
    """
    _fields = ['op', 'right']


class BinOp(AST):
    '''
    A Binary operator such as 2 + 3 or x * y
    '''
    _fields = ['op', 'left', 'right']

# Conditions and while loops (Project 7)
class IfElseStatement(AST):
    '''
    An if-else statement
    '''
    _fields = ['condition', 'if_statements', 'else_statements']

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
