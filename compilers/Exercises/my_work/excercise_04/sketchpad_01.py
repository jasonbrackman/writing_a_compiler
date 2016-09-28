# coding=utf-8
#
# Filename: 
#
# Create Date: 2016-09-28
#
# ------------------------------------------------------------------


def look_at_machine_code():
    # Machine Code
    def foo():
        return a + 2 * b - 3 * c

    import dis
    dis.dis(foo)


def ast_into_machine_code():
    # Machine AST into Machine Code
    import ast
    top = ast.parse("a + 2*b - 3*c")
    print(ast.dump(top))

# Generate some code
import ast


class CodeGenerator(ast.NodeVisitor):
    def __init__(self):
        self.code = []

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        opname = node.op.__class__.__name__
        inst = ("BINARY_" + opname.upper(),)
        self.code.append(inst)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            inst = ('LOAD_GLOBAL', node.id)
        else:
            inst = ('Unimplemented',)
        self.code.append(inst)

    def visit_Num(self, node):
        inst = ('LOAD_CONST', node.n)
        self.code.append(inst)


def generate_machine_code():
    top = ast.parse("a + 2*b - 3*c")
    gen = CodeGenerator()
    gen.visit(top)
    # print(gen.code)
    for inst in gen.code:
        print(inst)


if __name__ == "__main__":
    #look_at_machine_code()
    #ast_into_machine_code()
    generate_machine_code()


