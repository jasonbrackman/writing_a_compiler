# gone/checker.py
'''
*** Do not start this project until you have fully completed Exercise 3. ***

In this project you need to perform semantic checks on your program.
This problem is multifaceted and complicated.  To make it somewhat
less brain exploding, you need to take it slow and in parts.

First, you will need to define a symbol table that keeps track of
previously declared identifiers.  The symbol table will be consulted
whenever the compiler needs to lookup information about variable and
constant declarations.  

Next, you will need to define objects that represent the different
builtin datatypes and record information about their capabilities.
See the file gone/typesys.py.

Finally, you'll need to write code that walks the AST and enforces
a set of semantic rules. Here is a list of the minimal set of things
that need to be checked:

1.  Names and symbols:

    All identifiers must be defined before they are used.  This
    includes variables, constants, and typenames.  For example, this
    kind of code generates an error:

       a = 3;              // Error. 'a' not defined.
       var a int;

    Note: typenames such as "int", "float", and "string" are built-in
    names that should already be defined at the start of checking.

2.  Types of literals and constants

    All literal symbols are implicitly typed and must be assigned a
    type of "int", "float", or "string".  This type is used to set
    the type of constants.  For example:

       const a = 42;         // Type "int"
       const b = 4.2;        // Type "float"
       const c = "forty";    // Type "string"


3.  Binary operator type checking

    Binary operators only operate on operands of the same type and produce a
    result of the same type.  Otherwise, you get a type error.  For example:

        var a int = 2;
        var b float = 3.14;

        var c int = a + 3;    // OK
        var d int = a + b;    // Error.  int + float
        var e int = b + 4.5;  // Error.  int = float

4.  Unary operator type checking.

    Unary operators always return a result that's the same type as the operand.

5.  Supported operators

    Here are the operators that need to be supported by each type:

    int:      binary { +, -, *, /}, unary { +, -}
    float:    binary { +, -, *, /}, unary { +, -}
    string:   binary { + }, unary { }

    Attempts to use unsupported operators should result in an error. 
    For example:

        var string a = "Hello" + "World";     // OK
        var string b = "Hello" * "World";     // Error (unsupported op *)

    Bonus: Support mixed-type operators in certain cases

        var string a = "Hello" * 4;          // OK. String replication
        var string b = 4 * "Hello";          // OK. String replication

6.  Assignment.

    The left and right hand sides of an assignment operation must be
    declared as the same type.

        var a int;
        a = 4 + 5;     // OK
        a = 4.5;       // Error. int = float

    Values can only be assigned to variable declarations, not
    to constants.

        var a int;
        const b = 42;

        a = 37;        // OK
        b = 37;        // Error. b is const

Implementation Strategy:
------------------------
You're going to use the NodeVisitor class defined in gone/ast.py to
walk the parse tree.   You will be defining various methods for
different AST node types.  For example, if you have a node BinaryOp,
you'll write a method like this:

      def visit_BinaryOp(self, node):
          ...

To start, make each method simply print out a message:

      def visit_BinaryOp(self, node):
          print('visit_BinaryOp:', node)
          ...

This will at least tell you that the method is firing.  Try some
simple code examples and make sure that all of your methods
are actually running when you walk the parse tree.

After you're satisfied that your methods are running, add support
for a symbol name and focus on the problem of managing names. 
Declarations such as:

      var a int;
      const b = 42;

put names into the symbol table.  The symbol table could be as
simple as a dict:
     
      { 'a': ...,  'b': .... }

Use of a name elsewhere such as in an expression "37 + b" look things
up in the symbol table. Write some test inputs that involve undefined
names and make sure it's working.   Note:  There is some extra complexity
in your symbol table in that you also need to check more than just types.
For example, if "b" is a constant, you can't assign to it.  You'll
need to have some way to check for that.

After names are working, move on to type propagation. Start with
literals.  Work your way through more complex operations such
as binary operators and unary operators.  You're going to be
checking and propagating types.  For example, your visit_BinaryOp() 
method might look roughly like this:

     def visit_BinaryOp(self, node):
         self.visit(node.left)
         self.visit(node.right)
         if node.left.type != node.right.type:
             # Type Error!
         else:
            node.type = node.left.type    # Propagate the type

After you're propagating types, shift your focus to the capabilities
of each type. For example, the '-' operator works with int and float
types, but not with strings.   You'll need to figure out some
way to check for this.

Wrap up by focusing on variable assignment and other details.
Make sure that the left and right sides have the same type.

General thoughts and tips
-------------------------
The main thing you need to be thinking about with checking is program
correctness.  Does this statement or operation that you're looking at
in the parse tree make sense?  If not, some kind of error needs to be
generated.  Use your own experiences as a programmer as a guide (think
about what would cause an error in your favorite programming
language).

One challenge is going to be the management of many fiddly details. 
You've got to track symbols, types, and different sorts of capabilities.
It's not always clear how to best organize all of that.  So, expect to
fumble around a bit at first.
'''

from .errors import error
from .ast import *
from .typesys import check_binop, check_unaryop, builtin_types, error_type, bool_type

class SymbolTable(object):
    '''
    Class representing a symbol table.   For now, this is just a dictionary
    that maps names to AST nodes.  There is some extra functionality to
    report errors.
    '''
    def __init__(self):
        self.symbols = {}

    def add(self, name, node):
        '''
        Add a new symbol to the table or report an error if already defined.
        '''
        if name in self.symbols:
            error(node.lineno, '%s already defined. Previous definition on line %s' % 
                  (name, getattr(self.symbols[name], 'lineno', '<unknown>')))
        else:
            self.symbols[name] = node

    def lookup(self, name):
        '''
        Lookup and return the node associated with a symbol (or None).
        '''
        return self.symbols.get(name)

class CheckProgramVisitor(NodeVisitor):
    '''
    Program checking class.   This class uses the visitor pattern as described
    in ast.py.   You need to define methods of the form visit_NodeName()
    for each kind of AST node that you want to process.
    '''
    def __init__(self):
        # Two-level scoping
        self.global_symtab = SymbolTable()
        self.local_symtab = None
        self.current_function = None

        # Add built-in type names (int, float, string) to the symbol table
        for ty in builtin_types:
            self.symtab_add(ty, ty)

    # Method for adding a symbol to the appropriate symbol table
    def symtab_add(self, name, node):
        if self.local_symtab:
            self.local_symtab.add(name, node)
        else:
            self.global_symtab.add(name, node)

    # Method for looking up a symbol (checks both symbol tables)
    def symtab_lookup(self, name):
        result = None
        if self.local_symtab:
            result = self.local_symtab.lookup(name)
        if result is None:
            result = self.global_symtab.lookup(name)
        return result

    def visit_Unaryop(self, node):
        # 1. Make sure that the operation is supported by the type
        # 2. Set the result type to the same as the operand
        self.visit(node.expr)
        node.type = check_unaryop(node.op, node.expr.type)
        if (node.expr.type != error_type and
            node.type == error_type):
            error(node.lineno, 'Type error: %s %s' % (node.op, node.expr.type))

    def visit_Binop(self, node):
        # 1. Make sure left and right operands have the same type
        # 2. Make sure the operation is supported
        # 3. Assign the result type
        self.visit(node.left)
        self.visit(node.right)
        node.type = check_binop(node.left.type, node.op, node.right.type)
        if (node.left.type != error_type and
            node.right.type != error_type and
            node.type == error_type):
            error(node.lineno, 'Type error: %s %s %s' % (node.left.type, node.op, node.right.type))

    def visit_FunctionCall(self, node):
        # 1. Make sure the name corresponds to a function
        # 2. Check the number of arguments
        # 3. Check the argument types for a match
        symnode = self.symtab_lookup(node.name)
        if symnode:
            if not isinstance(symnode, FunctionPrototype):
                error(node.lineno, '%s not a function' % node.name)
                node.type = error_type
            else:
                # A valid function prototype.  Check arguments and types
                if len(node.arglist) != len(symnode.parameters):
                    error(node.lineno, '%s expected %d arguments. Got %d.' % (node.name, len(symnode.parameters), len(node.arglist)))
                for n, (arg, parm) in enumerate(zip(node.arglist, symnode.parameters), start=1):
                    self.visit(arg)
                    if arg.type != parm.type:
                        error(arg.lineno, 'Type error. Argument %d must be %s' % (n, parm.type))
                node.type = symnode.type
        else:
            error(node.lineno, 'Undefined name %s' % node.name)
            node.type = error_type
                  

    def visit_AssignmentStatement(self, node):
        # 1. Make sure the location of the assignment is defined
        # 2. Visit the expression on the RHS
        # 3. Check that the types match
        # 4. Propagate the expression value over to the storage node
        self.visit(node.store_location)
        self.visit(node.expr)
        if (node.store_location.type != node.expr.type and 
            node.store_location.type != error_type and
            node.expr.type != error_type):
            error(node.lineno,'Type error %s = %s' % (node.store_location.type, node.expr.type))
        node.store_location.expr = node.expr

    def visit_ConstDeclaration(self, node):
        # 1. Check that the constant name is not already defined
        # 2. Add an entry to the symbol table
        self.visit(node.expr)
        node.type = node.expr.type
        self.symtab_add(node.name, node)
        node.is_global = False if self.current_function else True

    def visit_VarDeclaration(self, node):
        # 1. Check that the variable name is not already defined
        # 2. Add an entry to the symbol table
        # 3. Check that the type of the expression (if any) is the same
        # 4. If there is no expression, set an initial value for the value
        self.visit(node.typename)
        node.type = node.typename.type
        if node.expr:
            self.visit(node.expr)
            if (node.expr.type != node.type and 
                node.expr.type != error_type): 
                error(node.lineno,'Type error %s = %s' % (node.type, node.expr.type))
        self.symtab_add(node.name, node)
        node.is_global = False if self.current_function else True

    def visit_ParmDeclaration(self, node):
        # 1. Visit the typename and propagate types
        self.visit(node.typename)
        node.type = node.typename.type

    def visit_FunctionPrototype(self, node):
        # 1. Make sure the function name is not already defined
        # 2. Visit the parameters to make sure they contain valid types
        # 3. Make sure the function return type is a valid type
        # 4. Place the function prototype in the symbol table
        for parm in node.parameters:
            self.visit(parm)
        self.visit(node.typename)
        node.type = node.typename.type
        self.symtab_add(node.name, node)
    
    def visit_Typename(self, node):
        # 1. Make sure the typename is valid and that it's actually a type
        sym = self.symtab_lookup(node.name)
        if sym:
            if sym in builtin_types:
                node.type = sym
            else:
                error(node.lineno, '%s is not a type' % node.name)
                node.type = error_type
        else:
            error(node.lineno, '%s is not defined' % node.name)
            node.type = error_type

    def visit_LoadVariable(self, node):
        # 1. Make sure the location is a valid variable or constant value
        # 2. Assign the type of the location to the node
        sym = self.symtab_lookup(node.name)
        if sym:
            if isinstance(sym, (ConstDeclaration, VarDeclaration, ParmDeclaration)):
                node.type = sym.type
            else:
                error(node.lineno, '%s not a valid location' % node.name)
                node.type = error_type
        else:
            error(node.lineno, '%s undefined' % node.name)
            node.type = error_type
        # Attach the symbol to the node
        node.sym = sym

    def visit_StoreVariable(self, node):
        # 1. Make sure the location can be assigned
        # 2. Assign the appropriate type
        sym = self.symtab_lookup(node.name)
        if sym:
            if isinstance(sym, (VarDeclaration, ParmDeclaration)):
                node.type = sym.type
            elif isinstance(sym, ConstDeclaration):
                error(node.lineno, 'Type error. %s is constant' % node.name)
                node.type = sym.type
            else:
                error(node.lineno, '%s not a valid location' % node.name)
                node.type = error_type
        else:
            error(node.lineno, '%s undefined' % node.name)
            node.type = error_type
        node.sym = sym
        
    def visit_Literal(self, node):
        # Lookup the literal typename in the symbol table to get the type object
        # Note: the typename is set implicitly in the parser. 
        node.type = self.symtab_lookup(node.typename)

    # Support for conditionals and loops (Project 7)
    def visit_IfElseStatement(self, node):
        # 1. Check if the conditional expression evaluates to a boolean
        # 2. Check the if and else branches
        self.visit(node.condition)
        if node.condition.type != bool_type:
            error(node.lineno, 'Conditional expression must evaluate to bool')
        self.visit(node.if_statements)
        self.visit(node.else_statements)

    def visit_WhileStatement(self, node):
        # 1. Check if the conditional expression evaluates to a boolean
        # 2. Check the loop body
        self.visit(node.condition)
        if node.condition.type != bool_type:
            error(node.lineno, 'Conditional expression must evaluate to bool')
        self.visit(node.statements)

    # Function call support
    def visit_ReturnStatement(self, node):
        # 1. Check if we're actually inside a function
        # 2. Visit the expression value
        # 3. Make sure the expression type matches the return type
        if self.current_function is None:
            error(node.lineno, 'return used outside of a function')
        else:
            self.visit(node.expr)
            if node.expr.type != self.current_function.prototype.type:
                error(node.lineno, 'Type error in return.  %s != %s' % (
                        node.expr.type.name,
                        self.current_function.prototype.type.name
                        )
                      )

    # Function declaration
    def visit_FunctionDeclaration(self, node):
        # 1. Check to make sure not nested function
        # 2. Visit prototype to check for duplication/typenames
        # 3. Set up a new local scope
        # 4. Process function parameters and add symbols to symbol table
        # 5. Visit the body
        # 6. Pop the local scope
        if self.current_function:
            error(node.lineno, 'Nested functions not supported.')
        else:
            self.visit(node.prototype)
            self.local_symtab = SymbolTable()
            self.current_function = node

            # Process the function parameters
            for parm in node.prototype.parameters:
                self.symtab_add(parm.name, parm)

            self.visit(node.statements)
            self.local_symtab = None
            self.current_function = None

# ----------------------------------------------------------------------
#                       DO NOT MODIFY ANYTHING BELOW       
# ----------------------------------------------------------------------

def check_program(ast):
    '''
    Check the supplied program (in the form of an AST)
    '''
    checker = CheckProgramVisitor()
    checker.visit(ast)

def main():
    '''
    Main program. Used for testing
    '''
    import sys
    from .parser import parse

    if len(sys.argv) != 2:
        sys.stderr.write('Usage: python3 -m gone.checker filename\n')
        raise SystemExit(1)

    ast = parse(open(sys.argv[1]).read())
    check_program(ast)

if __name__ == '__main__':
    main()




