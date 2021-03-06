# gone/run.py
#
# Project 5:
# ----------
# Runs a Gone program in a LLVM JIT.   This requires that the
# Gone runtime support library (gonert.c) be compiled into a shared
# object and placed in the same directory as this file.
#
# Note:  This project will require minor modification in Project 8

import os.path
import ctypes
import llvmlite.binding as llvm

_path = os.path.dirname(__file__)

def run(llvm_ir):
    # Load the runtime
    ctypes._dlopen(os.path.join(_path, 'gonert.so'), ctypes.RTLD_GLOBAL)

    # Initialize LLVM
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    target = llvm.Target.from_default_triple()
    target_machine = target.create_target_machine()
    mod = llvm.parse_assembly(llvm_ir)
    mod.verify()

    engine = llvm.create_mcjit_compiler(mod, target_machine)

    # Execute the main() function
    #
    # !!! Note: Requires modification in Project 8 (see below)
    main_ptr = engine.get_function_address('main')
    main_func = ctypes.CFUNCTYPE(None)(main_ptr)
    main_func()

    # Project 8:  Modify the above code to execute the Gone __init()
    # function that initializes global variables.  Then add code below
    # that executes the Gone main() function.

def tests():
    from gone.errors import errors_reported
    from gone.llvmgen import compile_llvm
    import os
    import sys
    root = r'/Users/jasonbrackman/PycharmProjects/writing_a_compiler/compilers/Tests'
    files = [os.path.join(root, file) for file in os.listdir(root) if file.endswith('.g')]
    for file in files:
        try:
            sys.argv = ['', file]

            if len(sys.argv) != 2:
                sys.stderr.write("Usage: python3 -m gone.run filename\n")
                raise SystemExit(1)

            source = open(sys.argv[1]).read()
            llvm_code = compile_llvm(source)
            if not errors_reported():
                run(llvm_code)

            print("Testing: {}".format(file))
        except Exception as e:
            print("Testing Failed: {}".format(file))

def main():
    from gone.errors import errors_reported
    from gone.llvmgen import compile_llvm

    import sys
    sys.argv = ['',
                r'/Users/jasonbrackman/PycharmProjects/writing_a_compiler/compilers/Tests/mandel_simple.g']

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 -m gone.run filename\n")
        raise SystemExit(1)

    source = open(sys.argv[1]).read()
    llvm_code = compile_llvm(source)
    if not errors_reported():
        run(llvm_code)

if __name__ == '__main__':
    main()
    #tests()
