class AST(object):
    def __init__(self, location):
        self.location = location


class Object(AST):
    def __init__(self, location, fields):
        super().__init__(location)
        self.fields = fields


class Local(AST):
    def __init__(self, location, body, *binds):
        super().__init__(location)
        self.body = body
        self.binds = binds


class Var(AST):
    def __init__(self, location, id):
        super().__init__(location)
        self.id = id


class Conditional(AST):
    def __init__(self, location, cond, branchTrue: AST, branchFalse: AST):
        super().__init__(location)
        self.cond = cond
        self.branchTrue = branchTrue
        self.branchFalse = branchFalse


class BinaryOp(AST):
    def __init__(self, location, op, left_arg: AST, right_arg: AST):
        super().__init__(location)
        self.op = op
        self.left_arg = left_arg
        self.right_arg = right_arg


class UnaryOp(AST):
    def __init__(self, location, op, arg: AST):
        super().__init__(location)
        self.op = op
        self.arg = arg


class LiteralBoolean(AST):
    def __init__(self, location, value):
        super().__init__(location)
        self.value = value


class LiteralNumber(AST):
    def __init__(self, location, value):
        super().__init__(location)
        self.value = value


class LiteralNull(AST):
    def __init__(self, location):
        super().__init__(location)


class LiteralString(AST):
    def __init__(self, location, value):
        super().__init__(location)
        self.value = value


class Array(AST):
    def __init__(self, location, elements):
        super().__init__(location)
        self.elements = elements


class Apply(AST):
    def __init__(self, location, func, *argv):
        super().__init__(location)
        self.func = func
        self.arguments = argv


class Function(AST):
    def __init__(self, location, body, *argv):
        super().__init__(location)
        self.body = body
        self.arguments = argv


class Error(AST):
    def __init__(self, location, msg):
        super().__init__(location)
        self.msg = msg


class Index(AST):
    def __init__(self, location, target, index):
        super().__init__(location)
        self.target = target
        self.index = index


class Self(AST):
    def __init__(self, location):
        super().__init__(location)


class Super(AST):
    def __init__(self, location):
        super().__init__(location)


class InSuper(AST):
    def __init__(self, location, elem):
        super().__init__(location)
        self.element = elem


class Identifier:
    def __init__(self, name):
        self.name = name


class ArgParam:
    def __init__(self, id=None, expr=None):
        self.id = id
        self.expr = expr


class Bind:
    def __init__(self, var, body):
        self.var = var
        self.body = body


class Location:
    def __init__(self, location):
        self.begin, self.end = location.split(',') # string with structure <line>:<column>
