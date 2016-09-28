from .errors import error
from .ast import *
from .typesys import check_binop, check_unaryop, builtin_types

class CheckProgramVisitor(NodeVisitor):
    '''
    Program checking class.   This class uses the visitor pattern as described
    in ast.py.   You need to define methods of the form visit_NodeName()
    for each kind of AST node that you want to process.  You may need to
    adjust the method names here if you've picked different AST node names.
    '''
    def __init__(self):
        # Initialize the symbol table.  It maps names to types
        self.symbols = { }

        # Add built-in type names to the symbol table
        for name in builtin_types:
            self.symbols[name] = name

    # ------------------------------------------------------------
    # Operators
    #
    # Operatos need to visit their operands and then check their
    # types.  A result type needs to be propagated by setting it on
    # the node.
    # ------------------------------------------------------------
    def visit_UnaryOp(self, node):
        # 1. Make sure that the operation is supported by the type
        # 2. Set the result type
        #
        # Hint: Use the check_unaryop() function in typesys.py
        self.visit(node.value)
        node.type = check_unaryop(node.op, node.value.type)
        if node.type is None and node.value.type:
            error(node.lineno, 'Type error. %s %s' % (node.op, node.value.type))

    def visit_BinOp(self, node):
        # 1. Make sure left and right operands have the same type
        # 2. Make sure the operation is supported
        # 3. Assign the result type
        #
        # Hint: Use the check_binop() function in typesys.py
        self.visit(node.left)
        self.visit(node.right)
        node.type = check_binop(node.left.type, node.op, node.right.type)
        if node.type is None and node.left.type and node.right.type:
            error(node.lineno, 'Type error. %s %s %s' %
                  (node.left.type, node.op, node.right.type))

    def visit_FunctionCall(self, node):
        # 1. Visit each of the expressions in the expression list
        # 2. Look up the function in the symbol table
        # 3. Set type to return type of function

        decl = self.symbols.get(node.name)
        if decl is None:
            error(node.lineno, '%s is not defined' % node.name)
        elif not isinstance(decl, FunctionPrototype):
            error(node.lineno, '%s is not a function' % node.name)
        else:
            # Need to verify the number of arguments
            # Need to visit each of the expressions in the function
            # Verify that the argument types match
            ...

            # Result type is function return type
            node.type = decl.type

    def visit_VarLocation(self, node):
        # 1. A simple variable location
        decl = self.symbols.get(node.name)
        if decl is None:
            error(node.lineno, '%r undefined' % node.name)
            node.type = None
        elif not isinstance(VarDeclaration, ConstDeclaration):
            error(node.lineno, '%s not a valid location' % node.name)
            node.type = None
        else:
            node.type = decl.type

    def visit_AssignStatement(self, node):
        # 1. Make sure the location of the assignment is defined
        # 2. Visit the expression on the right hand side
        # 3. Check that the types match

        # Visit the location
        self.visit(node.location)

        # Visit the right hand side
        self.visit(node.value)

        if (
            node.location.type         # Location is properly defined
            and node.value.type        # Value is defined (no errors)
            and node.location.type != node.value.type  # Same type
            ):
               error(node.lineno, 'Type error. %s = %s' % (node.location.type,
                                                           node.value.type))

    # ------------------------------------------------------------
    # Declarations
    #
    # Declarations add new entries to the symbol table.
    #
    #   const a = 42;       --> 'a' : ConstDeclaration
    #   var b float;        --> 'b' : FloatDeclaration
    #   func foo() int;     --> 'foo' : FunctionPrototype
    #
    # ------------------------------------------------------------
    def visit_ConstDeclaration(self, node):
        # 1. Check that the constant name is not already defined
        # 2. Add an entry to the symbol table

        self.visit(node.value)
        node.type = node.value.type
        if node.name in self.symbols:
            error(node.lineno, '%r already defined.' % node.name)
        else:
            self.symbols[node.name] = node

    def visit_VarDeclaration(self, node):
        # 1. Check that the variable name is not already defined
        # 2. Add an entry to the symbol table
        # 3. Check that the type of the expression (if any) is the same

        if node.value:
            self.visit(node.value)
            if node.type != node.value.type and node.value.type:
                error(node.lineno, 'Type error. %s = %s' % (node.type, node.value.type))

        if node.name in self.symbols:
            error(node.lineno, '%r already defined.' % node.name)
        else:
            self.symbols[node.name] = node

    def visit_FunctionPrototype(self, node):
        if node.name in self.symbols:
            error(node.lineno, '%r already defined.' % node.name)
        else:
            # For a function. Record a function "type" in the symbol
            # table. For now, make up a name like <func>
            self.symbols[node.name] = node