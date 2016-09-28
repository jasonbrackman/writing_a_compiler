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
        vals = [getattr(self, name) for name in self._fields]
        valstrs = []
        for val in vals:
            if not isinstance(val, AST):
                if not isinstance(val, list):
                    valstrs.append(repr(val))
                else:
                    valstrs.append('[...]')
            else:
                valstrs.append(type(val).__name__)

        argstr = ', '.join('%s=%s' % r for r in zip(self._fields, valstrs))
        return '%s(%s)' % (type(self).__name__, argstr)

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
    '''
    A list of statements
    '''
    _fields = ['statements']

class PrintStatement(AST):
    '''
    print expression ;
    '''
    _fields = ['expr']

class ConstDeclaration(AST):
    '''
    const pi = 3.14159;
    '''
    _fields = ['name', 'value']

class VarDeclaration(AST):
    '''
    var x int = 42;
    '''
    _fields = ['name', 'type', 'value']

class AssignStatement(AST):
    _fields = ['location', 'value']

class VarLocation(AST):
    _fields = ['name']

class ArrayLocation(AST):
    _fields = ['name', 'index']

class FunctionCall(AST):
    _fields = ['name', 'args']

class FunctionPrototype(AST):
    _fields = ['name', 'parmlist', 'type']

class ExternFunction(AST):
    _fields = ['prototype']

class Parm(AST):
    _fields = ['name', 'type']

class Literal(AST):
    '''
    A literal value such as 2, 2.5, or "two"
    '''
    _fields = ['value', 'type']

class BinOp(AST):
    '''
    A Binary operator such as 2 + 3 or x * y
    '''
    _fields = ['op', 'left', 'right']

class UnaryOp(AST):
    '''
    A Unary operator such as -3 or +3
    '''
    _fields = ['op', 'value']

class Typename(AST):
    '''
    The name of a type. For example, 'int', 'float'
    '''
    _fields = ['name']

class ArrayType(AST):
    '''
    The type of an array
    '''
    _fields = ['name', 'size']

# ----------------------------------------------------------------------
#                  DO NOT MODIFY ANYTHING BELOW HERE
# ----------------------------------------------------------------------

# The following classes for visiting and rewriting the AST are taken
# from Python's ast module.

def validate_visitor(cls):
    '''
    You give me a class cls, validate the visit_* methods
    '''
    for key in cls.__dict__:
        if key.startswith('visit_'):
            if key[6:] not in globals() or not issubclass(globals()[key[6:]], AST):
                raise TypeError('Bad visitor method: %s' % key)

    return cls

# Metaclass
class NodeVisitorMeta(type):
    def __init__(cls, *args):
        validate_visitor(cls)

# DO NOT MODIFY
class NodeVisitor(metaclass=NodeVisitorMeta):
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