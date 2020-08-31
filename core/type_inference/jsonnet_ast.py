class AST(object):
    def __init__(self, location):
        self.location = location


class Object(AST):
    def __init__(self, location, fields):
        super().__init__(location)
        self.fields = fields

    def __str__(self):
        obj_str = '{'
        for field in self.fields:
            obj_str += f'{str(field)}: {str(self.fields[field])}, '
        obj_str += '}'
        return obj_str


class Local(AST):
    def __init__(self, location, body, *binds):
        super().__init__(location)
        self.body = body
        self.binds = binds

    def __str__(self):
        local_str = f'{str(self.body)}, '
        for bind in self.binds:
            local_str += f'local {str(bind.var)} = {str(bind.body)};'
        return local_str


class Var(AST):
    def __init__(self, location, id):
        super().__init__(location)
        self.id = id
    
    def __str__(self):
        var_str = f'Var({self.id})'
        return var_str

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
    
    def __str__(self):
        return f'{self.value}'


class LiteralNumber(AST):
    def __init__(self, location, value):
        super().__init__(location)
        self.value = value
    
    def __str__(self):
        return f'{self.value}'


class LiteralNull(AST):
    def __init__(self, location):
        super().__init__(location)


class LiteralString(AST):
    def __init__(self, location, value):
        super().__init__(location)
        self.value = value
    
    def __str__(self):
        return self.value


class Array(AST):
    def __init__(self, location, elements):
        super().__init__(location)
        self.elements = elements
    
    def __str__(self):
        arr_str = '['
        for e in self.elements:
            arr_str += f'{str(e)}, '
        arr_str += ']'
        return arr_str


class Apply(AST):
    def __init__(self, location, fn, *argv):
        super().__init__(location)
        self.fn = fn
        self.arguments = argv
    
    def __str__(self):
        arr_str = f'Apply({self.fn}'
        for arg in self.arguments:
            arr_str += f', {str(arg)}'
        arr_str += ')'
        return arr_str


class Function(AST):
    def __init__(self, location, body, *argv):
        super().__init__(location)
        self.body = body
        self.arguments = argv


class BuiltinFunction(AST):
    def __init__(self, location, name, *params):
        self.location = location
        self.name = name
        self.params = params


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
    
    def __str__(self):
        return 'self'


class Super(AST):
    def __init__(self, location):
        super().__init__(location)
    
    def __str__(self):
        return 'super'


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

    def __str__(self):
        arg_str = ''
        delim = ''
        if self.id:
            arg_str += self.id
            delim = '='
        if self.expr:
            arg_str += f'{delim}{str(self.expr)}'
        return arg_str

class Bind:
    def __init__(self, var, body):
        self.var = var
        self.body = body
    
    def __str__(self):
        bind_str = f'Bind({self.var}, {str(self.body)})' 
        return bind_str


class Location:
    def __init__(self, location):
        # string with structure <line>:<column>
        self.begin, self.end = location.split(',')
    
    def __str__(self):
        loc_str = f'Location({self.begin}, {str(self.end)})' 
        return loc_str
