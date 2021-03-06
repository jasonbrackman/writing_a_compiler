# gone/llvmgen.py
"""
Project 5 : Generate LLVM
=========================
In this project, you're going to translate the SSA intermediate code
into LLVM IR.    Once you're done, your code will be runnable.  It
is strongly advised that you do *all* of the steps of Exercise 5
prior to starting this project.   Don't rush into it.

For Project 5, you are going to emit all of the LLVM instructions into
a single function main().  This is a temporary shim to get things to
work before we implement further support for user-defined functions in
Project 8.

Further instructions are contained in the comments below.
"""

# LLVM imports. Don't change this.

from llvmlite.ir import (
    Module, IRBuilder, Function, IntType, DoubleType, VoidType, Constant, GlobalVariable,
    FunctionType
)

# Declare the LLVM type objects that you want to use for the low-level
# in our intermediate code.  Basically, you're going to need to
# declare the integer, float, and string types here.  These correspond
# to the types being used the intermediate code being created by
# the ircode.py file.

int_type   = IntType(32)   # 32-bit integer
float_type = DoubleType()  # 64-bit float
bool_type  = IntType(1)    # 1-bit integer (bool)

string_type = None         # Up to you (leave until the end)

void_type = VoidType()  # Void type.  This is a special type
                        # used for internal functions returning
                        # no value

# A dictionary that maps the typenames used in IR to the corresponding
# LLVM types defined above.   This is mainly provided for convenience
# so you can quickly look up the type object given its type name.
typemap = {
    'int': int_type,
    'float': float_type,
    'string': string_type,
    'bool': bool_type
}


# The following class is going to generate the LLVM instruction stream.
# The basic features of this class are going to mirror the experiments
# you tried in Exercise 5.  The execution model is somewhat similar
# to the visitor class.
#
# Given a sequence of instruction tuples such as this:
#
#         code = [ 
#              ('literal_int', 1, '_int_1'),
#              ('literal_int', 2, '_int_2'),
#              ('add_int', '_int_1', '_int_2, '_int_3')
#              ('print_int', '_int_3')
#              ...
#         ]
#
#    The class executes methods self.emit_opcode(args).  For example:
#
#             self.emit_literal_int(1, '_int_1')
#             self.emit_literal_int(2, '_int_2')
#             self.emit_add_int('_int_1', '_int_2', '_int_3')
#             self.emit_print_int('_int_3')
#
#    Internally, you'll need to track variables, constants and other
#    objects being created.  Use a Python dictionary to emulate
#    storage. 

class GenerateLLVM(object):
    def __init__(self, name='module'):
        # Perform the basic LLVM initialization.  You need the following parts:
        #
        #    1.  A top-level Module object
        #    2.  A Function instance in which to insert code
        #    3.  A Builder instance to generate instructions
        #
        # Note: For project 5, we don't have any user-defined
        # functions so we're just going to emit all LLVM code into a top
        # level function void main() { ... }.   This will get changed later.

        self.module = Module(name)
        self.function = Function(self.module,
                                 FunctionType(void_type, []),
                                 name='main')

        self.block = self.function.append_basic_block('entry')
        self.builder = IRBuilder(self.block)

        # Dictionary that holds all of the global variable/function declarations.
        # Any declaration in the Gone source code is going to get an entry here
        self.vars = {}

        # Dictionary that holds all of the temporary variables created in
        # the intermediate code.   For example, if you had an expression
        # like this:
        #
        #      a = b + c*d
        #
        # The corresponding intermediate code might look like this:
        #
        #      ('load_int', 'b', 'int_1')
        #      ('load_int', 'c', 'int_2')
        #      ('load_int', 'd', 'int_3')
        #      ('mul_int', 'int_2','int_3','int_4')
        #      ('add_int', 'int_1','int_4','int_5')
        #      ('store_int', 'int_5', 'a')
        #
        # The self.temp dictionary below is used to map names such as 'int_1', 
        # 'int_2' to their corresponding LLVM values.  Essentially, every time
        # you make anything in LLVM, it gets stored here.
        self.temps = {}

        # Initialize the runtime library functions (see below)
        self.declare_runtime_library()

    def declare_runtime_library(self):
        # Certain functions such as I/O and string handling are often easier
        # to implement in an external C library.  This method should make
        # the LLVM declarations for any runtime functions to be used
        # during code generation.    Please note that runtime function
        # functions are implemented in C in a separate file gonert.c

        self.runtime = {}

        # Declare printing functions
        self.runtime['_print_int'] = Function(self.module,
                                              FunctionType(void_type, [int_type]),
                                              name="_print_int")

        self.runtime['_print_float'] = Function(self.module,
                                                FunctionType(void_type, [float_type]),
                                                name="_print_float")

        self.runtime['_print_bool'] = Function(self.module,
                                               FunctionType(void_type, [int_type]),
                                               name="_print_bool")


    def generate_code(self, ircode):
        # Given a sequence of SSA intermediate code tuples, generate LLVM
        # instructions using the current builder (self.builder).  Each
        # opcode tuple (opcode, args) is dispatched to a method of the
        # form self.emit_opcode(args)
        # Gather all of the block labels

        labels = [op[1] for op in ircode if op[0] == 'block']
        # Make a dict of LLVM block objects (in advance!!!)
        self.blocks = {label: self.function.append_basic_block(label)
                       for label in labels}

        for opcode, *args in ircode:
            if hasattr(self, 'emit_' + opcode):
                getattr(self, 'emit_' + opcode)(*args)
            else:
                print('Warning: No emit_' + opcode + '() method')

        # Add a return statement.  Note, at this point, we don't really have
        # user-defined functions so this is a bit of hack--it may be removed later.
        self.builder.ret_void()

    # ----------------------------------------------------------------------
    # Opcode implementation.   You must implement the opcodes.  A few
    # sample opcodes have been given to get you started.
    # ----------------------------------------------------------------------

    # Creation of literal values.  Simply define as LLVM constants.
    def emit_literal_int(self, value, target):
        self.temps[target] = Constant(int_type, value)

    def emit_literal_float(self, value, target):
        self.temps[target] = Constant(float_type, value)

    def emit_literal_bool(self, value, target):
        self.temps[target] = Constant(bool_type, value)

    # STRINGS BONUS: Nightmare scenarios :) --
    # def emit_literal_string(self, value, target):
    #     self.temps[target] = Constant(string_type, value)

    # Allocation of variables.  Declare as global variables and set to
    # a sensible initial value.
    def emit_alloc_int(self, name):
        var = GlobalVariable(self.module, int_type, name=name)
        var.initializer = Constant(int_type, 0)
        self.vars[name] = var

    def emit_alloc_float(self, name):
        var = GlobalVariable(self.module, float_type, name=name)
        var.initializer = Constant(float_type, 0)
        self.vars[name] = var

    def emit_alloc_bool(self, name):
        var = GlobalVariable(self.module, bool_type, name=name)
        var.initializer = Constant(bool_type, 0)
        self.vars[name] = var

    # Load/store instructions for variables.  Load needs to pull a
    # value from a global variable and store in a temporary. Store
    # goes in the opposite direction.
    def emit_load_int(self, name, target):
        self.temps[target] = self.builder.load(self.vars[name], target)

    def emit_load_float(self, name, target):
        self.temps[target] = self.builder.load(self.vars[name], target)

    def emit_load_bool(self, name, target):
        self.temps[target] = self.builder.load(self.vars[name], target)

    def emit_store_int(self, source, target):
        self.builder.store(self.temps[source], self.vars[target])

    def emit_store_float(self, source, target):
        self.builder.store(self.temps[source], self.vars[target])

    def emit_store_bool(self, source, target):
        self.builder.store(self.temps[source], self.vars[target])

    # Binary + operator
    def emit_add_int(self, left, right, target):
        self.temps[target] = self.builder.add(self.temps[left], self.temps[right], target)

    def emit_add_float(self, left, right, target):
        self.temps[target] = self.builder.fadd(self.temps[left], self.temps[right], target)

    # Binary - operator
    def emit_sub_int(self, left, right, target):
        self.temps[target] = self.builder.sub(self.temps[left], self.temps[right], target)  # You must implement

    def emit_sub_float(self, left, right, target):
        self.temps[target] = self.builder.fsub(self.temps[left], self.temps[right], target)

    # Binary * operator
    def emit_mul_int(self, left, right, target):
        self.temps[target] = self.builder.mul(self.temps[left], self.temps[right], target)

    def emit_mul_float(self, left, right, target):
        self.temps[target] = self.builder.fmul(self.temps[left], self.temps[right], target)

    # Binary / operator
    def emit_div_int(self, left, right, target):
        self.temps[target] = self.builder.sdiv(self.temps[left], self.temps[right], target)

    def emit_div_float(self, left, right, target):
        self.temps[target] = self.builder.fdiv(self.temps[left], self.temps[right], target)

    # Unary + operator
    def emit_uadd_int(self, source, target):
        self.temps[target] = self.builder.add(Constant(int_type, 0),
                                              self.temps[source],
                                              target)

    def emit_uadd_float(self, source, target):
        self.temps[target] = self.builder.fadd(Constant(float_type, 0),
                                               self.temps[source],
                                               target)

    # Unary - operator
    def emit_usub_int(self, source, target):
        self.temps[target] = self.builder.sub(Constant(int_type, 0),
                                              self.temps[source],
                                              target)

    def emit_usub_float(self, source, target):
        self.temps[target] = self.builder.fsub(Constant(float_type, 0),
                                               self.temps[source],
                                               target)

    # Binary < operator
    def emit_lt_int(self, left, right, target):
        self.temps[target] = self.builder.icmp_signed('<', self.temps[left], self.temps[right], target)

    def emit_lt_float(self, left, right, target):
        self.temps[target] = self.builder.fcmp_ordered('<', self.temps[left], self.temps[right], target)

    # Binary <= operator
    def emit_le_int(self, left, right, target):
        self.temps[target] = self.builder.icmp_signed('<=', self.temps[left], self.temps[right], target)

    def emit_le_float(self, left, right, target):
        self.temps[target] = self.builder.fcmp_ordered('<=', self.temps[left], self.temps[right], target)

    # Binary > operator
    def emit_gt_int(self, left, right, target):
        self.temps[target] = self.builder.icmp_signed('>', self.temps[left], self.temps[right], target)

    def emit_gt_float(self, left, right, target):
        self.temps[target] = self.builder.fcmp_ordered('>', self.temps[left], self.temps[right], target)

    # Binary >= operator
    def emit_ge_int(self, left, right, target):
        self.temps[target] = self.builder.icmp_signed('>=', self.temps[left], self.temps[right], target)

    def emit_ge_float(self, left, right, target):
        self.temps[target] = self.builder.fcmp_ordered('>=', self.temps[left], self.temps[right], target)

    # Binary == operator
    def emit_eq_int(self, left, right, target):
        self.temps[target] = self.builder.icmp_signed('==', self.temps[left], self.temps[right], target)

    def emit_eq_bool(self, left, right, target):
        self.temps[target] = self.builder.icmp_signed('==', self.temps[left], self.temps[right], target)

    def emit_eq_float(self, left, right, target):
        self.temps[target] = self.builder.fcmp_ordered('==', self.temps[left], self.temps[right], target)

    # Binary != operator
    def emit_ne_int(self, left, right, target):
        self.temps[target] = self.builder.icmp_signed('!=', self.temps[left], self.temps[right], target)

    def emit_ne_bool(self, left, right, target):
        self.temps[target] = self.builder.icmp_signed('!=', self.temps[left], self.temps[right], target)

    def emit_ne_float(self, left, right, target):
        self.temps[target] = self.builder.fcmp_ordered('!=', self.temps[left], self.temps[right], target)

    # Binary && operator
    def emit_and_bool(self, left, right, target):
        self.temps[target] = self.builder.and_(self.temps[left], self.temps[right], target)

    # Binary || operator
    def emit_or_bool(self, left, right, target):
        self.temps[target] = self.builder.or_(self.temps[left], self.temps[right], target)

    # Unary ! operator
    def emit_not_bool(self, source, target):
        self.temps[target] = self.builder.icmp_signed('==', self.temps[source], Constant(bool_type, 0), target)

    # Print statements
    def emit_print_int(self, source):
        self.builder.call(self.runtime['_print_int'], [self.temps[source]])

    def emit_print_float(self, source):
        try:
            self.builder.call(self.runtime['_print_float'], [self.temps[source]])
        except KeyError as e:
            print("Failed to print a float: {}".format(e))

    def emit_print_bool(self, source):
        tmp = self.builder.zext(self.temps[source], int_type)
        self.builder.call(self.runtime['_print_bool'], [tmp])


    # blocks
    def emit_block(self, label):
        self.builder.position_at_end(self.blocks[label])

    def emit_branch(self, label):
        self.builder.branch(self.blocks[label])

    def emit_cbranch(self, testvar, iflabel, elselabel):
        self.builder.cbranch(self.temps[testvar],
                             self.blocks[iflabel],
                             self.blocks[elselabel])

    # Extern function declaration.  
    def emit_extern_func(self, name, return_type, parameter_names):
        #print("emit_extern_func: ", name, return_type, parameter_names)
        rettype = typemap[return_type]
        parmtypes = [typemap[pname] for pname in parameter_names]
        func_type = FunctionType(rettype, parmtypes)
        self.vars[name] = Function(self.module, func_type, name=name)

    # Call an external function.
    def emit_call_func(self, name, args, target):

        #print("NOT IMPLEMENTED: emit_call_func: ", name, *args)
        func = self.vars[name]
        argvals = [self.temps[name] for name in args]
        #print('{}'.format(self.temps))
        self.temps[target] = self.builder.call(func, argvals)


#######################################################################
#                      TESTING/MAIN PROGRAM
#######################################################################

def compile_llvm(source):
    from .ircode import compile_ircode

    # Compile intermediate code 
    # !!! This needs to be changed in Project 7/8
    code = compile_ircode(source)

    # Make the low-level code generator
    generator = GenerateLLVM()

    # Generate low-level code
    # !!! This needs to be changed in Project 7/8
    generator.generate_code(code)

    return str(generator.module)


def main():
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 -m gone.llvmgen filename\n")
        raise SystemExit(1)

    source = open(sys.argv[1]).read()
    llvm_code = compile_llvm(source)
    print(llvm_code)


if __name__ == '__main__':
    main()
