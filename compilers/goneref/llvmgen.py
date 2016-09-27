# gone/llvmgen.py
'''
Project 5 : Generate LLVM
=========================
In this project, you're going to translate the SSA intermediate code
into LLVM IR.    Once you're done, your code will be runnable.  It
is strongly advised that you do *all* of the steps of Exercise 5
prior to starting this project.   Don't rush into it.

Further instructions are contained in the comments.
'''

from . import bblock

# LLVM imports. Don't change this.

from llvmlite.ir import (
    Module, IRBuilder, Function, IntType, DoubleType, VoidType, Constant, GlobalVariable,
    FunctionType
    )

# Declare the LLVM type objects that you want to use for the types
# in our intermediate code.  Basically, you're going to need to 
# declare your integer, float, and string types here.

int_type    = IntType(32)         # 32-bit integer
float_type  = DoubleType()        # 64-bit float
bool_type   = IntType(1)          # 1-bit integer (bool)
string_type = None                # Up to you (leave until the end)
void_type   = VoidType()

# A dictionary that maps the typenames used in IR to the corresponding
# LLVM types defined above.   This is mainly provided for convenience
# so you can quickly look up the type object given its type name.
typemap = {
    'int' : int_type,
    'float' : float_type,
    'bool' : bool_type,
    'string' : string_type,
    'void' : void_type
}

# The following class is going to generate the LLVM instruction stream.  
# The basic features of this class are going to mirror the experiments
# you tried in Exercise 5.  The execution module is very similar
# to the interpreter written in Project 4.  See specific comments 
# in the class. 

class GenerateLLVM(object):
    def __init__(self, name='module'):
        # Perform the basic LLVM initialization.  You need the following parts:
        #
        #    1.  A top-level Module object
        #    2.  A Function instance in which to insert code
        #    3.  A Builder instance to generate instructions
        #
        # Note: at this point in the project, we don't have any user-defined
        # functions so we're just going to emit all LLVM code into a top
        # level function void main() { ... }.   This will get changed later.

        self.module = Module(name=name)
        self.function = None
        self.block = None
        self.builder = None
        
        # Dictionary holding all global variable/function declarations
        self.globals = {}

        # Dictionary holding all local declarations
        self.locals = {}

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

        # Last block that performed an unconditional branch
        self.last_branch = None

    def start_function(self, name, rettypename, parmtypenames):
        rettype = typemap[rettypename]
        parmtypes = [typemap[pname] for pname in parmtypenames]
        func_type = FunctionType(rettype, parmtypes)   #  Type.function(rettype, parmtypes, False)

        # Create the function for which we're generating code
        self.function = Function(self.module, func_type, name=name)   #Function.new(self.module, func_type, name)

        # Make the builder and entry block
        self.block = self.function.append_basic_block('entry')
        self.builder = IRBuilder(self.block)

        # Make the exit block
        self.exit_block = self.function.append_basic_block('exit')

        # Clear the local vars and temps
        self.locals = {}
        self.temps = {}

        # Make the return variable
        if rettype is not void_type:
            self.locals['return'] = self.builder.alloca(rettype, name='return')

        # Put an entry in the globals
        self.globals[name] = self.function

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
                                                 name='_print_int')

        self.runtime['_print_float'] = Function(self.module,
                                                FunctionType(void_type, [float_type]),
                                                   name='_print_float')

        self.runtime['_print_bool'] = Function(self.module,
                                               FunctionType(void_type, [int_type]),
                                                   name='_print_bool')

    def generate_code(self, ircode):
        # Given a sequence of SSA intermediate code tuples, generate LLVM
        # instructions using the current builder (self.builder).  Each
        # opcode tuple (opcode, args) is dispatched to a method of the
        # form self.emit_opcode(args)
        for op in ircode:
            opcode = op[0]
            if hasattr(self, 'emit_'+opcode):
                getattr(self, 'emit_'+opcode)(*op[1:])
            else:
                print('Warning: No emit_'+opcode+'() method')

    def terminate(self):
        # Add a return statement. This connects the last block to the exit block.
        # The return statement is then emitted
        if self.last_branch != self.block:
            self.builder.branch(self.exit_block)
        self.builder.position_at_end(self.exit_block)
        
        if 'return' in self.locals:
            self.builder.ret(self.builder.load(self.locals['return']))
        else:
            self.builder.ret_void()

    # Project 7:  Extra methods to assist with the construction of
    # of basic blocks and branching between blocks
    def add_block(self, name):
        # Add a new block to the existing function
        return self.function.append_basic_block(name)
    
    def set_block(self, block):
        # Sets the current block for adding more code
        self.block = block
        self.builder.position_at_end(block)

    def cbranch(self, testvar, true_block, false_block):
        self.builder.cbranch(self.temps[testvar], true_block, false_block)

    def branch(self, next_block):
        if self.last_branch != self.block:
            self.builder.branch(next_block)
        self.last_branch = self.block

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

        
    # Allocation of variables.  Declare as local variables and set to
    # a sensible initial value.
    def emit_alloc_int(self, name):
        var = self.builder.alloca(int_type, name=name)
        self.builder.store(Constant(int_type, 0), var)
        self.locals[name] = var

    def emit_alloc_float(self, name):
        var = self.builder.alloca(float_type, name=name)
        self.builder.store(Constant(float_type, 0.0), var)
        self.locals[name] = var

    def emit_alloc_bool(self, name):
        var = self.builder.alloca(bool_type, name=name)
        var.builder.store(Constant(bool_type, 0), var)
        self.locals[name] = var

    # Global variables
    def emit_global_int(self, name):
        var = GlobalVariable(self.module, int_type, name=name)
        var.initializer = Constant(int_type, 0)
        self.globals[name] = var

    def emit_global_float(self, name):
        var = GlobalVariable(self.module, float_type, name=name)
        var.initializer = Constant(float_type, 0.0)
        self.globals[name] = var

    def emit_global_bool(self, name):
        var = GlobalVariable(self.module, bool_type, name=name)
        var.initializer = Constant(bool_type, 0)
        self.globals[name] = var

    # Load/store instructions for variables.  Load needs to pull a
    # value from a global variable and store in a temporary. Store
    # goes in the opposite direction.
    def lookup_var(self, name):
        if name in self.locals:
            return self.locals[name]
        else:
            return self.globals[name]

    def emit_load_int(self, name, target):
        self.temps[target] = self.builder.load(self.lookup_var(name), target)

    def emit_load_float(self, name, target):
        self.temps[target] = self.builder.load(self.lookup_var(name), target)

    def emit_load_bool(self, name, target):
        self.temps[target] = self.builder.load(self.lookup_var(name), target)

    def emit_store_int(self, source, target):
        self.builder.store(self.temps[source], self.lookup_var(target))

    def emit_store_float(self, source, target):
        self.builder.store(self.temps[source], self.lookup_var(target))

    def emit_store_bool(self, source, target):
        self.builder.store(self.temps[source], self.lookup_var(target))

    # Binary + operator
    def emit_add_int(self, left, right, target):
        self.temps[target] = self.builder.add(self.temps[left], self.temps[right], target)

    def emit_add_float(self, left, right, target):
        self.temps[target] = self.builder.fadd(self.temps[left], self.temps[right], target)

    # Binary - operator
    def emit_sub_int(self, left, right, target):
        self.temps[target] = self.builder.sub(self.temps[left], self.temps[right], target)

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
        self.temps[target] = self.temps[source]

    def emit_uadd_float(self, source, target):
        self.temps[target] = self.temps[source]

    # Unary - operator
    def emit_usub_int(self, source, target):
        self.temps[target] = self.builder.sub(
            Constant(int_type, 0),
            self.temps[source],
            target)

    def emit_usub_float(self, source, target):
        self.temps[target] = self.builder.fsub(
            Constant(float_type, 0.0),
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
        self.builder.call(self.runtime['_print_float'], [self.temps[source]])

    def emit_print_bool(self, source):
        tmp = self.builder.zext(self.temps[source], int_type)
        self.builder.call(self.runtime['_print_bool'], [tmp])

    # Extern function declaration.  
    def emit_extern_func(self, name, rettypename, *parmtypenames):
        rettype = typemap[rettypename]
        parmtypes = [typemap[pname] for pname in parmtypenames]
        func_type = FunctionType(rettype, parmtypes)
        self.globals[name] = Function(self.module, func_type, name=name)

    # Call an external function.
    def emit_call_func(self, funcname, *args):
        target = args[-1]
        func = self.globals[funcname]
        argvals = [self.temps[name] for name in args[:-1]]
        self.temps[target] = self.builder.call(func, argvals)

    # Return statements
    def emit_return_int(self, source):
        self.builder.store(self.temps[source], self.locals['return'])
        self.branch(self.exit_block)

    def emit_return_float(self, source):
        self.builder.store(self.temps[source], self.locals['return'])
        self.branch(self.exit_block)

    def emit_return_bool(self, source):
        self.builder.store(self.temps[source], self.locals['return'])
        self.branch(self.exit_block)

    def emit_return_void(self):
        self.branch(self.exit_block)

    # Function parameter declarations.  Must create as local variables
    def emit_parm_int(self, name, num):
        var = self.builder.alloca(int_type, name=name)
        self.builder.store(self.function.args[num], var)
        self.locals[name] = var

    def emit_parm_float(self, name, num):
        var = self.builder.alloca(float_type, name=name)
        self.builder.store(self.function.args[num], var)
        self.locals[name] = var

    def emit_parm_bool(self, name, num):
        var = self.builder.alloca(bool_type, name=name)
        self.builder.store(self.function.args[num], var)
        self.locals[name] = var

# This class walks the basic block structure of our intermediate code
# and turns it into LLVM blocks.   It uses a few methods added to the
# GenerateLLVM() class defined above.
class GenerateBlocksLLVM(bblock.BlockVisitor):
    def __init__(self, generator):
        self.generator = generator

    def generate_function(self, func):
        if func.name == 'main':
            name = '_gone_main'
        else:
            name = func.name

        self.generator.start_function(name, func.return_type, func.parameters)
        self.visit(func.start_block)
        self.generator.terminate()
        # return self.generator.function

    def visit_BasicBlock(self, block):
        # Generate the LLVM code for the block
        self.generator.generate_code(block)

    def visit_IfBlock(self, block):
        # Generate LLVM code for the test
        self.generator.generate_code(block)

        # Make basic blocks for the if-else and merge

        then_block = self.generator.add_block('then')
        else_block = self.generator.add_block('else')
        merge_block = self.generator.add_block('merge')

        # Conditional branch
        self.generator.cbranch(block.testvar, then_block, else_block)

        # Visit the then-branch
        self.generator.set_block(then_block)
        self.visit(block.if_branch)
        self.generator.branch(merge_block)

        # Visit the else-branch
        self.generator.set_block(else_block)
        self.visit(block.else_branch)
        self.generator.branch(merge_block)

        # Continue with the merge block
        self.generator.set_block(merge_block)

    def visit_WhileBlock(self, block):
        test_block = self.generator.add_block('whiletest')
        # Unconditionally branch to the new block
        self.generator.branch(test_block)
        self.generator.set_block(test_block)
        
        # Generate the LLVM code for the test
        self.generator.generate_code(block)

        # Make a block for the body and loop termination
        loop_block = self.generator.add_block('loop')
        after_loop = self.generator.add_block('afterloop')
        
        # Conditional branch
        self.generator.cbranch(block.testvar, loop_block, after_loop)

        # Emit the loop body
        self.generator.set_block(loop_block)
        self.visit(block.body)
        self.generator.branch(test_block)
        
        self.generator.set_block(after_loop)

#######################################################################
#                 DO NOT MODIFY ANYTHING BELOW HERE
#######################################################################

def compile_llvm(source):
    from .ircode import compile_ircode

    # Compile intermediate code and get the function list
    functions = compile_ircode(source)

    # Make the low-level code generator
    generator = GenerateLLVM()

    # Make the block generator
    blockgen = GenerateBlocksLLVM(generator)

    for func in functions:
        blockgen.generate_function(func)

    return str(generator.module)

def main():
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write('Usage: python3 -m gone.llvmgen filename\n')
        raise SystemExit(1)

    source = open(sys.argv[1]).read()
    llvm_code = compile_llvm(source)
    print(llvm_code)

if __name__ == '__main__':
    main()

        
        
        
