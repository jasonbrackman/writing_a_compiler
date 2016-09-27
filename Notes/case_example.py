# coding=utf-8
#
# Filename: 
#
# Create Date: 2016-09-27
#
# ------------------------------------------------------------------


class NodeProcessor(object):

    def process(self, node):
        meth_name = 'process_' + type(node).__name__
        getattr(self, meth_name)

    def process_VarDeclaration(self, node):
        pass

    def process_constDeclaratio(self, node):
        pass

    def process_BinOp(self, node):
        pass