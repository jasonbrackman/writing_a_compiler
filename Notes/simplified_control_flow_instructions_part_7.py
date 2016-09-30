"""
Control Flow in 30 Minutes (or less) - Maybe
============================================

Note; This needs to be tested.  I'm about 99% sure it's going to
work though.... - Dave

Prerequisites:
--------------

- You need support for booleans (Project 6)
- Your parse tree must have conditionals in it
  (if statement, while statement, etc.)

Approach:
---------
Forget all of that BasicBlock, BlockVisitor stuff. No.

In ircode.py, give your code generator class a new
method to create unique block names:
"""


class GenerateCode(NodeVisitor):
    def __init__(self):
        self._blocknum = 0

    def new_block(self):
        self._blocknum += 1
        return '.L%d' % self._blocknum

#Now, introduce three new intermediate instructions

    ('block', label)                               # Start a new block
    ('branch', label)                              # Branch to a block
    ('cbranch', testvar, true_label, false_label)  # Conditional branch

# Define the handling of an if-statement like this:

   def visit_IfStatement(self, node):
       # Make block labels for the merge, if, and else branches.
       # Do this in advance!
       merge_block = self.new_block()
       if_block = self.new_block()
       if node.else_branch:
           else_block = self.new_block()
       else:
           else_block = merge_block

       # Visit the expression for the test (if (expr) { ... )
       self.visit(node.expr)

       # Conditionally branch based on result
       self.code.append(('cbranch', node.expr.gen_location, if_block, else_block))

       # Visit the if-branch
       self.code.append(('block', if_block))
       self.visit(node.if_branch)
       self.code.append(('branch', merge_block))

       # Visit the else-branch (if any)
       if node.else_branch:
           self.code.append(('block', else_block))
           self.visit(node.else_branch)
           self.code.append(('branch', merge_block))

       # Emit the merge block label
       self.code.append(('block', merge_block))

#Now, in the llvmgen.py file, you're going to do a few things.
#In the generate_code() method, create all of the LLVM blocks
#in advance from the block labels in the ircode!

    def generate_code(self, ircode):
        # Gather all of the block labels
        labels = [ op[1] for op in ircode if op[0] == 'block']

        # Make a dict of LLVM block objects (in advance!!!)
        self.blocks = { label: self.function.append_basic_block(label)
	                for label in labels }
 
        ...

#Now, write instructions for 'block', 'branch', 'cbranch' like this

     def emit_block(self, label):
         self.builder.position_at_end(self.blocks[label])

     def emit_branch(self, label):
         self.builder.branch(self.blocks[label])

     def emit_cbranch(self, testvar, iflabel, elselabel):
         self.builder.cbranch(self.temps[testvar],
	                            self.blocks[iflabel],
                              self.blocks[elselabel])

#That's it!   Control flow for if-statements might work.  Try it!
#while statements will be very similar.  You won't need to modify
#anything in the LLVM code if you do it right in ircode.py
