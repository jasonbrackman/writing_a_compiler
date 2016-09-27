# gone/ircode.py
'''
Project 4
=========
Code generation for the Gone language.  In this project, you are going to turn
the AST into an intermediate machine code known as Single Static Assignment (SSA).
There are a few important parts you'll need to make this work.  Please read 
carefully before beginning:

Single Static Assignment
========================
The first problem is how to decompose complex expressions into
something that can be handled more simply.  One way to do this is
to decompose all expressions into a sequence of simple assignments
involving binary or unary operations.  

As an example, suppose you had a mathematical expression like this:

        2 + 3 * 4 - 5

Here is one possible way to decompose the expression into simple
operations:

        int_1 = 2
        int_2 = 3
        int_3 = 4
        int_4 = int_2 * int_3
        int_5 = int_1 + int_4
        int_6 = 5
        int_7 = int_5 - int_6

In this code, the int_n variables are temporaries used while
carrying out the calculation .  A critical feature of SSA is that such
temporary variables are only assigned once (single assignment) and
never reused.  Thus, if you were to evaluate another expression, you
would  keep incrementing the numbers. For example, if you were
to evaluate 10+20+30, you would have code like this:

        int_8 = 10
        int_9 = 20
        int_10 = int_8 + int_9
        int_11 = 30
        int_12 = int_11 + int_11

SSA is meant to mimic the low-level instructions one might carry out 
on a CPU.  For example, the above instructions might be translated to
low-level machine instructions (for a hypothetical CPU) like this:

        MOVI   #2, R1
        MOVI   #3, R2
        MOVI   #4, R3
        MUL    R2, R3, R4
        ADD    R4, R1, R5
        MOVI   #5, R6
        SUB    R5, R6, R7

Another benefit of SSA is that it is very easy to encode and
manipulate using simple data structures such as tuples. For example,
you could encode the above sequence of operations as a list like this:

       [ 
         ('movi', 2, 'int_1'),
         ('movi', 3, 'int_2'),
         ('movi', 4, 'int_3'),
         ('mul', 'int_2', 'int_3', 'int_4'),
         ('add', 'int_1', 'int_4', 'int_5'),
         ('movi', 5, 'int_6'),
         ('sub', 'int_5','int_6','int_7'),
       ]

Dealing with Variables
======================
In your program, you are probably going to have some variables that get
used and assigned different values.  For example:

       a = 10 + 20;
       b = 2 * a;
       a = a + 1;

In "pure SSA", all of your variables would actually be versioned just
like temporaries in the expressions above.  For example, you would
emit code like this:

       int_1 = 10
       int_2 = 20
       a_1 = int_1 + int_2
       int_3 = 2
       b_1 = int_3 * a_1
       int_4 = 1 
       a_2 = a_1 + int_4
       ...

For reasons that will simplify life later, we're going to treat declared
variables as memory locations and access them using load/store
instructions instead.  For example:

       int_1 = 10
       int_2 = 20
       int_3 = int_1 + int_2
       store(int_3, 'a')
       int_4 = 2
       int_5 = load('a')
       int_6 = int_4 * int_5
       store(int_6, 'b')
       int_7 = load('a')
       int_8 = 1
       int_9 = int_7 + int_8
       store(int_9, 'a')

A Word About Types
==================
At a low-level, CPUs can only operate a few different kinds of 
data such as ints and floats.  Because the semantics of the
low-level types might vary slightly, you'll need to take 
some steps to handle them separately.

In our intermediate code, we're going to tag temporary variable
names and instructions with an associated type low-level type.  For
example:

      2 + 3*4          (ints)
      2.0 + 3.0*4.0    (floats)

The generated intermediate code might look like this:

      ('literal_int', 2, 'int_1')
      ('literal_int', 3, 'int_2')
      ('literal_int', 4, 'int_3')
      ('mul_int', 'int_2', 'int_3', 'int_4')
      ('add_int', 'int_1', 'int_4', 'int_5')

      ('literal_float', 2.0, 'float_1')
      ('literal_float', 3.0, 'float_2')
      ('literal_float', 4.0, 'float_3')
      ('mul_float', 'float_2', 'float_3', 'float_4')
      ('add_float', 'float_1', 'float_4', 'float_5')

Note: These types may or may not correspond directly to the type names
used in the input program.  For example, during translation, higher
level data structures would be reduced to a low-level operations.

Your Task
=========
Your task is as follows: Write a AST Visitor() class that takes an
Expr program and flattens it to a single sequence of SSA code instructions
represented as tuples of the form 

       (operation, operands, ..., destination)

To start, your SSA code should only contain the following operators:

       ('alloc_type', varname)            # Allocate a variable of a given type
       ('literal_type', value, target)    # Load a literal value into target
       ('load_type', varname, target)     # Load the value of a variable into target
       ('store_type',source, varname)     # Store the value of source into varname
       ('add_type',left,right,target )    # target = left + right
       ('sub_type',left,right,target)     # target = left - right
       ('mul_type',left,right,target)     # target = left * right
       ('div_type',left,right,target)     # target = left / right  (integer truncation)
       ('uadd_type',source,target)        # target = +source
       ('uneg_type',source,target)        # target = -source
       ('print_type',source)              # Print value of source
       ('extern_func',name,*types)        # Extern function declaration
       ('call_func',name,*args,target)    # Function call

In this operators '_type' is replaced by the appropriate low-level type 
such as '_int' or '_float'.

Project 6 Additions:
====================
The following opcodes need to be added for Project 6:

       ('lt_type', left, right, target)   # target = left < right
       ('le_type', left, right, target)   # target = left <= right
       ('gt_type', left, right, target)   # target = left > right
       ('ge_type', left, right, target)   # target = left <= right
       ('eq_type', left, right, target)   # target = left == right
       ('ne_type', left, right, target)   # target = left != right
       ('and_bool', left, right, target)  # target = left && right
       ('or_bool', left, right, target)   # target = left || right
       ('not_bool', source, target)       # target = !source

Project 7 Additions:
====================
A distinction between local and global variables is made:

       ('global_type', name)              # Declare a global variable
       ('parm_type', name, pos)           # Declare a parameter of a given type (pos is arg #)
       ('alloc_type', name)               # Declare a local variable
       ('return_type', name)              # Return a value

Note: You may need to extend some of the existing op-codes to handle the new
bool type as well.
'''

from . import ast
from .bblock import *
from collections import defaultdict

class Function(object):
    '''
    Class to represent function objects.
    '''
    def __init__(self, name, return_type, parameters, start_block):
        self.name = name
        self.return_type = return_type
        self.parameters = parameters
        self.start_block = start_block

# STEP 1: Map map operator symbol names such as +, -, *, /
# to actual opcode names 'add','sub','mul','div' to be emitted in
# the SSA code.   This is easy to do using dictionaries:

binary_ops = {
    '+' : 'add',
    '-' : 'sub',
    '*' : 'mul',
    '/' : 'div',
    '<' : 'lt',
    '<=' : 'le',
    '>' : 'gt',
    '>=' : 'ge',
    '==' : 'eq',
    '!=' : 'ne',
    '&&' : 'and',
    '||' : 'or'
}

unary_ops = {
    '+' : 'uadd',
    '-' : 'usub',
    '!' : 'not'
}

# STEP 2: Implement the following Node Visitor class so that it creates
# a sequence of SSA instructions in the form of tuples.  Use the
# above description of the allowed op-codes as a guide.
class GenerateCode(ast.NodeVisitor):
    '''
    Node visitor class that creates 3-address encoded instruction sequences.
    '''
    def __init__(self):
        super(GenerateCode, self).__init__()

        # List of all functions generated
        self.functions = []

        # version dictionary for temporaries
        self.versions = defaultdict(int)

        # The generated code (a basic block)
        self.code = BasicBlock()
        self.start_block = self.code

        # Create the init function
        self.functions.append(Function('__init', 'void', [], self.start_block))

    def new_temp(self, typeobj):
         '''
         Create a new temporary variable of a given type.
         '''
         typename = str(typeobj)
         name = '__%s_%d' % (typename, self.versions[typename])
         self.versions[typename] += 1
         return name

    # You must implement visit_Nodename methods for all of the other
    # AST nodes.  In your code, you will need to make instructions
    # and append them to the self.code list.
    #
    # One sample method follows

    def visit_Program(self, node):
        self.visit(node.statements)
        
        # Append the final return statement onto the initial function
        self.code.append(('return_void',))

    def visit_LoadVariable(self, node):
        target = self.new_temp(node.type)
        inst = ('load_' + str(node.type), node.name, target)
        self.code.append(inst)
        node.gen_location = target

    def visit_Unaryop(self, node):
        self.visit(node.expr)
        target = self.new_temp(node.expr.type)
        opcode = unary_ops[node.op] + '_' + str(node.type)
        inst = (opcode, node.expr.gen_location, target)
        self.code.append(inst)
        node.gen_location = target

    def visit_Binop(self, node):
        self.visit(node.left)
        self.visit(node.right)
        target = self.new_temp(node.type)
        opcode = binary_ops[node.op] + '_' + str(node.left.type)
        inst = (opcode, node.left.gen_location, node.right.gen_location, target)
        self.code.append(inst)
        node.gen_location = target

    def visit_AssignmentStatement(self, node):
        self.visit(node.expr)
        self.visit(node.store_location)

    def visit_StoreVariable(self, node):
        inst = ('store_' + str(node.type), node.expr.gen_location, node.name)
        self.code.append(inst)

    def visit_PrintStatement(self, node):
        self.visit(node.expr)
        inst = ('print_' + str(node.expr.type) ,node.expr.gen_location)
        self.code.append(inst)

    def visit_VarDeclaration(self, node):
        if node.is_global:
            inst = ('global_' + str(node.type), node.name)
        else:
            inst = ('alloc_' + str(node.type), node.name)
        self.code.append(inst)
        if node.expr:
            self.visit(node.expr)
            inst = ('store_' + str(node.type), node.expr.gen_location, node.name)
            self.code.append(inst)

    def visit_ConstDeclaration(self, node):
        if node.is_global:
            inst = ('global_' + str(node.expr.type), node.name)
        else:
            inst = ('alloc_' + str(node.expr.type), node.name)
        self.code.append(inst)
        self.visit(node.expr)
        inst = ('store_' + str(node.expr.type), node.expr.gen_location, node.name)
        self.code.append(inst)

    def visit_ExternFunctionDeclaration(self, node):
        self.visit(node.prototype)
        inst = ('extern_func', node.prototype.name, str(node.prototype.type)) + \
            tuple(str(parm.type) for parm in node.prototype.parameters)
        self.code.append(inst)
        
    def visit_FunctionCall(self, node):
        args = []
        for arg in node.arglist:
            self.visit(arg)
            args.append(arg.gen_location)
        target = self.new_temp(node.type)
        inst = ('call_func', node.name) + tuple(args) + (target,)
        self.code.append(inst)
        node.gen_location = target

    def visit_Literal(self, node):
        target = self.new_temp(node.type)
        inst = ('literal_' + str(node.type), node.value, target)
        self.code.append(inst)
        # Save the name of the temporary variable where the value was placed 
        node.gen_location = target

    # Added control flow (Project 7)
    def visit_IfElseStatement(self, node):
         ifblock = IfBlock()
         self.code.next_block = ifblock
         self.code = ifblock
         # Evaluate the condition
         self.visit(node.condition)

         # Save the variable where the test value is stored
         ifblock.testvar = node.condition.gen_location

         # Traverse the if-branch
         ifblock.if_branch = BasicBlock()
         self.code = ifblock.if_branch
         self.visit(node.if_statements)
         
         # Traverse the else-branch
         if node.else_statements:
              ifblock.else_branch = BasicBlock()
              self.code = ifblock.else_branch
              self.visit(node.else_statements)
              
         # Create a new block to terminate the if
         self.code = BasicBlock()
         ifblock.next_block = self.code

    def visit_WhileStatement(self, node):
         whileblock = WhileBlock()
         self.code.next_block = whileblock
         self.code = whileblock
         # Evaluate the condition
         self.visit(node.condition)
         
         # Save the variable where the test value is stored
         whileblock.testvar = node.condition.gen_location

         # Traverse the body
         whileblock.body = BasicBlock()
         self.code = whileblock.body
         self.visit(node.statements)

         # Create the terminating block
         self.code = BasicBlock()
         whileblock.next_block = self.code

    def visit_ReturnStatement(self, node):
        # Evaluate the expression
        self.visit(node.expr)
        inst = ('return_' + str(node.expr.type), node.expr.gen_location)
        self.code.append(inst)

    def visit_FunctionDeclaration(self, node):
        # Save the current block
        saved_code = self.code

        self.code = BasicBlock()
        # Get the return type names and parameter type names
        rettypename = str(node.prototype.typename.type)
        parmtypenames = [ str(parm.type) for parm in node.prototype.parameters]

        self.functions.append(Function(node.prototype.name, 
                                       rettypename, 
                                       parmtypenames, 
                                       self.code))
        
        # Emit the function parameters
        for n, parm in enumerate(node.prototype.parameters):
            inst = ('parm_' + str(parm.type), parm.name, n)
            self.code.append(inst)

        # Visit the function body
        self.visit(node.statements)

        # Restore the last saved block
        self.code = saved_code

# STEP 3: Testing
# 
# Try running this program on the input file Project4/Tests/good.e and viewing
# the resulting SSA code sequence.
#
#     bash % python3 -m gone.ircode good.e
#     ... look at the output ...
#
# Sample output can be found in Project4/Tests/good.out.  While coding,
# you may want to break the code down into more manageable chunks.
# Think about unit testing.

# ----------------------------------------------------------------------
#                       DO NOT MODIFY ANYTHING BELOW       
# ----------------------------------------------------------------------

def compile_ircode(source):
    '''
    Generate intermediate code from source.
    '''
    from .parser import parse
    from .checker import check_program
    from .errors import errors_reported

    ast = parse(source)
    check_program(ast)

    # If no errors occurred, generate code
    if not errors_reported():
        gen = GenerateCode()
        gen.visit(ast)
        return gen.functions
    else:
        return []

def main():
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write('Usage: python3 -m gone.ircode filename\n')
        raise SystemExit(1)

    source = open(sys.argv[1]).read()
    functions = compile_ircode(source)
    for func in functions:
        print(':::::::::::::::: FUNCTION: %s %s %s' % (func.name,
                                                       func.return_type,
                                                       func.parameters))

        PrintBlocks().visit(func.start_block)
        print()

if __name__ == '__main__':
    main()
