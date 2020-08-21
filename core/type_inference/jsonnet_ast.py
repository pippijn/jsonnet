
# ast.Conditional(ast.BinaryOp(==,ast.LiteralNumber(2),ast.LiteralNumber(3)), ast.LiteralString(magic), ast.LiteralNumber(0))

class AST(object):
    def __init__(self):
        pass


class Conditional(AST):
    def __init__(self, cond, branchTrue: AST, branchFalse: AST):
        self.cond = cond
        self.branchTrue = branchTrue
        self.branchFalse = branchFalse


class BinaryOp(AST):
    def __init__(self, op, left_arg: AST, right_arg: AST):
        self.op = op
        self.left_arg = left_arg
        self.right_arg = right_arg


class LiteralBoolean(AST):
    def __init__(self, value):
        self.value = value


class LiteralNumber(AST):
    def __init__(self, value):
        self.value = value


class LiteralNull(AST):
    def __init__(self, value):
        self.value = None


class LiteralString(AST):
    def __init__(self, value):
        self.value = value
