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

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        target = self.new_temp(node.type)
        opcode = binary_ops[node.op] + '_' + str(node.left.type)
        inst = (opcode, node.left.gen_location, node.right.gen_location, target)
        self.code.append(inst)
        node.gen_location = target

    def visit_UnaryOp(self, node):
        self.visit(node.value)
        target = self.new_temp(node.type)
        opcode = unary_ops[node.op] + '_' + str(node.type)
        inst = (opcode, node.value.gen_location, target)
        self.code.append(inst)
        node.gen_location = target

    def visit_PrintStatement(self, node):
        self.visit(node.expr)
        inst = ('print_' + str(node.expr.type) ,node.expr.gen_location)
        self.code.append(inst)

    def visit_VarDeclaration(self, node):
        # Allocate storage for the value
        inst = ('alloc_' + str(node.type), node.name)
        self.code.append(inst)

        # Evaluate the right hand side
        if node.value:
            self.visit(node.value)

            # Store the value in the allocated space
            inst = ('store_' + str(node.type), node.value.gen_location, node.name)
            self.code.append(inst)

    visit_ConstDeclaration = visit_VarDeclaration

    def visit_VarLocation(self, node):
        # Either reads or stores a variable depending on usage
        if node.usage == 'load':
            node.gen_location = self.new_temp(node.type)
            inst = ('load_' + str(node.type), node.name, node.gen_location)
        elif node.usage == 'store':
            # Assume that the gen_location was attached to this node.
            # Tricky bit: In order for this to work, the value being
            # stored needs to be visited FIRST.  Once it has been visited,
            # the generated location (gen_location) needs to be copied
            # from the result over to the location node (myself).  Then,
            # you visit the location node.  I'll look at gen_location
            # to figure where the value is located in order to store it.
            #
            # See the code in visit_AssignStatement to see the other part
            # of this.
            inst = ('store_' + str(node.type), node.gen_location, node.name)
        self.code.append(inst)

    def visit_ExternFunction(self, node):
        # Declares a function as external to gone.
        inst = ('extern_func',
                node.prototype.name,
                *(parm.type for parm in node.prototype.parmlist),
                node.prototype.type)
        self.code.append(inst)

    def visit_AssignStatement(self, node):
        # Visit the right hand side.  This evaluates the value
        # that's going to be stored.
        self.visit(node.value)

        # Attach the generated value as the 'gen_location' attribute
        # of the location.   Then visit the location.  See the
        # note in visit_VarLocation().
        node.location.gen_location = node.value.gen_location
        self.visit(node.location)

    def visit_FunctionCall(self, node):
        # Visit each of the function arguments, one by one
        # This will evaluate each one and store the gen_location on them
        for arg in node.args:
            self.visit(arg)

        # Make a location for the result (the return type)
        node.gen_location = self.new_temp(node.type)

        inst = ('call_func', node.name, *(arg.gen_location for arg in node.args), node.gen_location)
        self.code.append(inst)