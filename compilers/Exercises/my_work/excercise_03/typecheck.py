def visit_BinOp(self, node):
    self.visit(node.left)
    self.visit(node.right)
    left_type = getattr(node.left, 'type', None)
    right_type = getattr(node.right, 'type', None)
    if left_type != right_type:
        print('Error: Type error.  %s %s %s' % (left_type, type(node.op).__name__, right_type))
        node.type = 'error'
    else:
        node.type = left_type