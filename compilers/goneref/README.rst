This directory contains a very basic reference implementation of Gone.
It implements all phases of the project and can run simple programs.
Look at it for implementation hints and other details.

This implementation does NOT include all possible Gone features. 
Here are notable omissions:

- No support for strings or arrays.
- A variety of subtle evil corner cases are not addressed.
- Bonus/Challenge problems are not solved.
- No sophisticated testing/debugging has been added.

The compiler includes various stages that can execute independently.

Tokenizing:
-----------
python3 -m goneref.tokenize filename.g  

Parsing
-------
python3 -m goneref.parser filename.g

Type Checking
-------------
python3 -m goneref.checker filename.g

Intermediate code generation
----------------------------
python3 -m goneref.ircode filename.g

LLVM Code generation
--------------------
python3 -m goneref.llvmgen filename.g

IR Code Interpreter
-------------------
python3 -m goneref.interp filename.g

LLVM Just in Time Compilation
-----------------------------
python3 -m goneref.run filename.g

Stand-alone Compilation
-----------------------
python3 -m goneref.compile filename.g
