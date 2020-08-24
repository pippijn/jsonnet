
# ast.Conditional(ast.BinaryOp(==,ast.LiteralNumber(2),ast.LiteralNumber(3)), ast.LiteralString(magic), ast.LiteralNumber(0))


class AST(object):
    def __init__(self):
        pass


class Object(AST):
    def __init__(self, fields):
        self.fields = fields


class Local(AST):
    def __init__(self, body, binds):
        self.body = body
        self.binds = binds


class Var(AST):
    def __init__(self, id):
        self.id = id


class Identifier:
    def __init__(self, name):
        self.name = name


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


class UnaryOp(AST):
    def __init__(self, op, arg: AST):
        self.op = op
        self.arg = arg


class LiteralBoolean(AST):
    def __init__(self, value):
        self.value = value


class LiteralNumber(AST):
    def __init__(self, value):
        self.value = value


class LiteralNull(AST):
    def __init__(self):
        pass


class LiteralString(AST):
    def __init__(self, value):
        self.value = value


class Array(AST):
    def __init__(self, elements):
        self.elements = elements


class Apply(AST):
    def __init__(self, func, *argv):
        self.func = func
        self.arguments = argv


class Function(AST):
    def __init__(self, id, arguments, body):
        self.arguments = arguments
        self.body = body


class Error(AST):
    def __init__(self, msg):
        self.msg = msg
