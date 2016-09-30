def visit_WhileStatement(self, node):
    # Make the labels for the different parts of the loop
    test_label = self.new_block()
    exit_label = self.new_block()
    body_label = self.new_block()

    # Tricky: Branch to the start of the test block
    self.code.append(('branch', test_label))

    # Evaluate the loop test
    self.code.append(('block', test_label))
    self.visit(node.expr)

    # Branch into the loop body or exit on result
    self.code.append(('cbranch', node.expr.gen_location,
                      body_label, exit_label))

    # Loop body
    self.code.append(('block', body_label))
    self.visit(node.body)

    # Go back and re-evaluate the test
    self.code.append(('branch', test_label))

    # Loop exit
    self.code.append(('block', exit_label))