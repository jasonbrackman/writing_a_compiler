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
You're going to use the NodeVisitor class defined in gone/_ast.py to
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

from gone.errors import error
from gone._ast import *
from gone.typesys import check_binop, check_unaryop, builtin_types


class SymbolTable(object):
    """
    Class representing a symbol table.   To start, it should provide
    functionality for adding and looking up objects associated with
    identifiers.   Think Python dictionaries.  You might want to add
    extra functionality later so it's probably better to make it
    a separate class as opposed to using a dict directly.
    """
    def __init__(self):
        self.symbols = {}

    def add(self, name, node):
        if name not in self.symbols:
            self.symbols[name] = node
        else:
            error(node.lineno, "{} already exists".format(name))

    def is_symbol(self, name):
        return True if name in self.symbols else False

    def get_type(self, name):
        _type = None
        if self.is_symbol(name):
            _type = self.symbols[name].type
        return _type


    def print(self):
        for k, v in self.symbols.items():
            print(k, getattr(v, 'type', v))

class CheckProgramVisitor(NodeVisitor):
    '''
    Program checking class.   This class uses the visitor pattern as described
    in _ast.py.   You need to define methods of the form visit_NodeName()
    for each kind of AST node that you want to process.  You may need to
    adjust the method names here if you've picked different AST node names.
    '''
    def __init__(self):
        self.global_symtab = SymbolTable()
        self.local_symtab = None
        self.current_function = None

        # Add built-in type names to the symbol table
        for item in builtin_types:
            self.symtab_add(item, item)

    # Method for adding a symbol to the appropriate symbol table
    def symtab_add(self, name, node):
        if self.local_symtab:
            self.local_symtab.add(name, node)
        else:
            self.global_symtab.add(name, node)

    def visit_UnaryOp(self, node):
        # 1. Make sure that the operation is supported by the type
        # 2. Set the result type 
        #
        # Hint: Use the check_unaryop() function in typesys.py
        self.visit(node.right)
        node.type = check_unaryop(node.op, node.right.type)

        if node.type is None:
            error(node.lineno, 'Type error: %s %s' % (node.op, node.right.type))

        # print("visit_unaryop", node, node.type)

    def visit_BinOp(self, node):
        # 1. Make sure left and right operands have the same type
        # 2. Make sure the operation is supported
        # 3. Assign the result type
        #
        # Hint: Use the check_binop() function in typesys.py

        self.visit(node.left)
        self.visit(node.right)

        node.type = check_binop(node.left.type, node.op, node.right.type)
        if node.type is None:
            error(node.lineno, 'BinOp Type error: %s %s %s' % (node.left.type, node.op, node.right.type))

        #print('visit_Binop', node, node.type)

    def visit_AssignmentStatement(self, node):
        # 1. Make sure the location of the assignment is defined
        # 2. Visit the expression on the right hand side
        # 3. Check that the types match
        self.visit(node.location)
        self.visit(node.value)

        if not hasattr(node.location, 'type') or not hasattr(node.value, 'type'):
            error(node.lineno, "Assignment is not recognized as valid: {}".format(node))

        # print("visit_assignmentStatement", node)

    def visit_ConstDeclaration(self, node):
        # 1. Check that the constant name is not already defined
        # 2. Add an entry to the symbol table
        self.visit(node.expr)
        node.type = node.expr.type

        if self.global_symtab.is_symbol(node.name):
            error(node.lineno, '{} is already defined'.format(node.name))
        self.global_symtab.add(node.name, node)

        #print('visit_ConstDeclaration')

    def visit_VarDeclaration(self, node):
        # 1. Check that the variable name is not already defined
        # 2. Add an entry to the symbol table
        # 3. Check that the type of the expression (if any) is the same
        # 4. If there is no expression, set an initial value for the value

        node.type = node.typename
        if node.expr:

            self.visit(node.expr)

            if hasattr(node.expr, 'typename') and node.expr.typename is not None:
                node.expr.type = node.expr.typename
                if node.typename != node.expr.typename:
                    error(node.lineno, 'Type error %s = %s' % (node.type, node.expr.type))

        self.symtab_add(node.name, node)

        #print('visit_VarDeclaration:', node.name, node.type)

    def visit_VarLocation(self, node):
        if self.global_symtab.get_type(node.name):
            node.type = self.global_symtab.get_type(node.name)
        else:
            node.type = None
        #print('visit_VarLocation', node)

    def visit_Typename(self, node):
        # 1. Make sure the typename is valid and that it's actually a type
        print('visit_Typename:', node)
        print(node.typename)

    def visit_LoadVariable(self, node):
        # 1. Make sure the location is a valid variable or constant value
        # 2. Assign the type of the variable to the node
        print('visit_LoadVariable:', node)

    def visit_StoreVariable(self, node):
        # 1. Make sure the location can be assigned
        # 2. Assign the appropriate type
        if self.global_symtab.is_symbol(node.name):
            node.type = self.global_symtab.get_type(node.name)
        else:
            error(node.lineno, "Requested storage of variable does not exist: {}".format(node.name))
        # print('visit_StoreVariable:', node)

    def visit_Literal(self, node):
        # 1. Attach an appropriate type to the literal

        node.type = node.typename

    def visit_ReadLocation(self, node):
        if self.global_symtab.is_symbol(node.location.name):
            node.type = self.global_symtab.get_type(node.location.name)
        else:
            error(node.lineno, "ReadLocation error: {}".format(node))

    def visit_FunctionCall(self, node):
        func_type = self.global_symtab.get_type(node.name)

        if func_type is None:
            error(node.lineno, '{} is not defined.'.format(node.name))
        else:
            for argument in node.arguments:
                self.visit(argument)
            node.type = func_type

        # print('visit_FunctionCall', node, node.type)

    def visit_FunctionPrototype(self, node):
        # 1. Make sure the function name is not already defined

        if self.global_symtab.is_symbol(node.name):
            error(node.lineno, '%r already defined.' % node.name)
        else:
            # 2. Visit the parameters to make sure they contain valid types
            for parm in node.parameters:
                parm.type = parm.typename

            # 3. Make sure the function return type is a valid type
            node.type = node.typename

            # 4. Place the function prototype in the symbol table
            self.global_symtab.add(node.name, node)

    def visit_ExternFunction(self, node):
        # print('checker_visit_ExternDeclaration', node)

        self.visit(node.prototype)
        # 1. Visit the external prototype to add a type

        # if self.global_symtab.is_symbol(node.prototype.name):
        #     error(node.lineno, '%r already defined.' % node.name)
        # else:
        #     node.type = node.prototype.typename
        #     self.global_symtab.add(node.prototype.name, node)


    # You will need to add more methods here in Projects 5-8.
# ----------------------------------------------------------------------
#                       DO NOT MODIFY ANYTHING BELOW       
# ----------------------------------------------------------------------

def check_program(ast):
    '''
    Check the supplied program (in the form of an AST)
    '''
    checker = CheckProgramVisitor()
    checker.visit(ast)
    # checker.global_symtab.print()

def main():
    '''
    Main program. Used for testing
    '''
    import sys
    from gone.parser import parse

    sys.argv = ['', r'/Users/jasonbrackman/PycharmProjects/writing_a_compiler/compilers/Tests/jason_simple_compile_01.g']

    if len(sys.argv) != 2:
        sys.stderr.write('Usage: python3 -m gone.checker filename\n')
        raise SystemExit(1)

    ast = parse(open(sys.argv[1]).read())
    check_program(ast)

if __name__ == '__main__':
    main()



