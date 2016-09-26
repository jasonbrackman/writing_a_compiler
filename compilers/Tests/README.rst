Testing Guide
=============

Project1:  Lexing
-----------------
python3 -m gone.tokenizer Tests/testlex1.g       # Tests valid tokens
python3 -m gone.tokenizer Tests/testlex2.g       # Tests bad input

Project2: Parsing
-----------------
There are a series of tests that progressively build up more and more
advanced parts of the language. Work them in order.

python3 -m gone.parser Tests/parsetest0.g      
python3 -m gone.parser Tests/parsetest1.g
python3 -m gone.parser Tests/parsetest2.g
python3 -m gone.parser Tests/parsetest3.g
python3 -m gone.parser Tests/parsetest4.g
python3 -m gone.parser Tests/parsetest5.g
python3 -m gone.parser Tests/parsetest6.g

When you are done, you should be able to run this final test:

python3 -m gone.parser Tests/good.g

Project 3: Type Checking
------------------------
You should be able to typecheck both a good and a bad program::

python3 -m gone.checker Tests/good.g      # No errors should be reported
python3 -m gone.checker Tests/errors.g    # Many errors reported

Project 4: Intermediate Code
----------------------------
Try running the following tests to test basic code generation::

python3 -m gone.ircode Tests/gen_int.g    # Integer operations
python3 -m gone.ircode Tests/gen_float.g  # Float operations
python3 -m gone.ircode Tests/gen_func.g   # Function calls

You can also run the following test::

python3 -m gone.ircode Tests/good.g

Project 5: LLVM Code Generation
-------------------------------
Run the same tests as project 4::

python3 -m gone.llvmgen Tests/gen_int.g
python3 -m gone.llvmgen Tests/gen_float.g
python3 -m gone.llvmgen Tests/gen_func.g

You should be able to compile this code.  Run a.out after each
command::

python3 -m gone.compile Tests/gen_int.g
python3 -m gone.compile Tests/gen_float.g
python3 -m gone.compile Tests/gen_func.g

You can als try running the code in a JIT::

python3 -m gone.run Tests/gen_int.g
python3 -m gone.run Tests/gen_float.g
python3 -m gone.run Tests/gen_func.g

Project 6 : Comparisons and Boolean Operators
---------------------------------------------
Run the following tests on comparison operators::

python3 -m gone.run Tests/testrel_int.g
python3 -m gone.run Tests/testrel_float.g

Note: You might need to run other kinds of more preliminary tests
during development.

The following tests checks some bad comparisons:

python3 -m gone.run Tests/testrel_bad.g

Project 7: Control Flow
-----------------------
The following test files involve control flow features::

python3 -m gone.run Tests/cond.g
python3 -m gone.run Tests/nestedcond.g
python3 -m gone.run Tests/fact.g
python3 -m gone.run Tests/fib.g
python3 -m gone.run Tests/nestedwhile.g

This tests some bad control flow::

python3 -m gone.run Tests/badcontrol.g

Project 8: Functions
--------------------

python3 -m gone.run Tests/func.g
python3 -m gone.run Tests/funcret.g    # Errors involving return statements
python3 -m gone.run Tests/funcerrors.g # Various function related errors
python3 -m gone.run Tests/mandel.g     # Mandelbrot set

For project 8, you can also start running code in the Programs/ directoy.

