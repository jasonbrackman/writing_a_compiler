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
from collections import defaultdict

# STEP 1: Map map operator symbol names such as +, -, *, /
# to actual opcode names 'add','sub','mul','div' to be emitted in
# the SSA code.   This is easy to do using dictionaries:

binary_ops = {
    '+' : 'add',
    '-' : 'sub',
    '*' : 'mul',
    '/' : 'div',
}

unary_ops = {
    '+' : 'uadd',
    '-' : 'usub',
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

        # version dictionary for temporaries
        self.versions = defaultdict(int)

        # The generated code (list of tuples)
        self.code = []

        # A list of external declarations (and types)
        self.externs = []

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
    # A few sample methods follow.  You may have to adjust depending
    # on the names and structure of your AST nodes.

    def visit_Literal(self, node):
        target = self.new_temp(node.type)
        inst = ('literal_' + str(node.type), node.value, target)
        self.code.append(inst)
        # Save the name of the temporary variable where the value was placed 
        node.gen_location = target

    def visit_Binop(self, node):
        self.visit(node.left)
        self.visit(node.right)
        target = self.new_temp(node.type)
        opcode = binary_ops[node.op] + '_' + str(node.left.type)
        inst = (opcode, node.left.gen_location, node.right.gen_location, target)
        self.code.append(inst)
        node.gen_location = target

    def visit_PrintStatement(self, node):
        self.visit(node.expr)
        inst = ('print_' + str(node.expr.type) ,node.expr.gen_location)
        self.code.append(inst)

# Project 6 - Comparisons/Booleans
# --------------------------------
# You will need to extend this code to support comparisons and boolean
# operators.  This will mostly involve the addition of new opcodes
#
# Project 7 - Control Flow
# ------------------------
# You will extend this code to emit code in basic blocks that are linked
# together.  Most of the underlying code will remain unchanged except that 
# instructions will be append to a block.  You'll also need to add support
# for if/else statements and while loops.
#
# Project 8 - Functions
# ---------------------
# You will extend this code to organize the emitted code into a functions.
# Each function will consist of a name and a starting block.   Any code
# emitted outside of a function needs to be placed into a default function
# called __init(). 

# ----------------------------------------------------------------------
#                          TESTING/MAIN PROGRAM
#
# Note: Some changes will be required in later projects.
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

        # !!!  This part will need to be changed slightly in Projects 7/8
        return gen.code    
    else:
        return []

def main():
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 -m gone.ircode filename\n")
        raise SystemExit(1)

    source = open(sys.argv[1]).read()
    code = compile_ircode(source)

    # !!! This part will need to be changed slightly in Projects 7/8
    for instr in code:
        print(code)

if __name__ == '__main__':
    main()
