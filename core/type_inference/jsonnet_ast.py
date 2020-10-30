class AST(object):
    def __init__(self, location):
        if location:
            self.location = location


class Object(AST):
    def __init__(self, location, fields):
        super().__init__(location)
        self.fields = fields

    def __str__(self):
        obj_str = 'Object({'
        for field in self.fields:
            obj_str += f'{str(field)}: {str(self.fields[field])}, '
        obj_str += '})'
        return obj_str


class Local(AST):
    def __init__(self, location, body, *binds):
        super().__init__(location)
        self.body = body
        self.binds = binds

    def __str__(self):
        local_str = 'Local('
        for bind in self.binds:
            local_str += f'{bind.var}={bind.body}, '
        local_str += f'in {self.body})'
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
    
    def __str__(self):
        cond_str = f'if ({self.cond}) then ({self.branchTrue}) else ({self.branchFalse})'
        return cond_str


class BinaryOp(AST):
    def __init__(self, location, op, left_arg: AST, right_arg: AST):
        super().__init__(location)
        self.op = op
        self.left_arg = left_arg
        self.right_arg = right_arg
    
    def __str__(self):
        bop_str = f'({self.left_arg} {self.op} {self.right_arg})'
        return bop_str


class UnaryOp(AST):
    def __init__(self, location, op, arg: AST):
        super().__init__(location)
        self.op = op
        self.arg = arg
    
    def __str__(self):
        uop_str = f'({self.op}{self.arg})'
        return uop_str


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
    def __init__(self, location=None):
        super().__init__(location)
    
    def __str__(self):
        return 'None'


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
        apply_str = f'Apply({self.fn}'
        for arg in self.arguments:
            apply_str += f', {str(arg)}'
        apply_str += ')'
        return apply_str


class Function(AST):
    def __init__(self, location, body, *argv):
        super().__init__(location)
        self.body = body
        self.arguments = argv
    
    def __str__(self):
        func_str = f'Function('
        for arg in self.arguments:
            func_str += f'{str(arg)}, '
        func_str += f'=> {str(self.body)})'
        return func_str


class BuiltinFunction(AST):
    def __init__(self, location, name, *params):
        self.location = location
        self.name = name
        self.params = params


class Error(AST):
    def __init__(self, location, msg):
        super().__init__(location)
        self.msg = msg
    
    def __str__(self):
        return f'Error("{self.msg}")'


class Index(AST):
    def __init__(self, location, target, index):
        super().__init__(location)
        self.target = target
        self.index = index

    def __str__(self):
        return f'{self.target}.{self.index}'


class Self(AST):
    def __init__(self, location):
        super().__init__(location)

    def __str__(self):
        return 'self'


class SuperIndex(AST):
    def __init__(self, location, index):
        super().__init__(location)
        self.index = index

    def __str__(self):
        return f'super.{str(self.index)}'


class InSuper(AST):
    def __init__(self, location, elem):
        super().__init__(location)
        self.element = elem
    
    def __str__(self):
        return f'{self.element} in super'


class Identifier:
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return self.name


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
            arg_str += f'{delim}{self.expr}'
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
        self.begin, self.end = location.split(',')

    def __str__(self):
        loc_str = f'Location({self.begin}, {str(self.end)})'
        return loc_str


class ObjectComprehension(AST):
    def __init__(self, location, id_, field, value, array):
        super().__init__(location)
        self.id = id_
        self.field = field
        self.value = value
        self.array = array

    def __str__(self):
        obj_comp_str = 'ObjectComprehension({id_}, {field}, {val}, {arr})'.format(
            id_ = self.id,
            field = self.field,
            val = self.value,
            arr = self.array
        )
        return obj_comp_str
