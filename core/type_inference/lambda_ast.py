class Lambda(object):
    """Lambda abstraction"""

    def __init__(self, v, body, location=None):
        self.v = v
        self.body = body
        self.location = location

    def __str__(self):
        return "(fn {v} => {body})".format(v=self.v, body=self.body)


class Identifier(object):
    """Identifier"""

    def __init__(self, name, location=None):
        self.name = name
        self.location = location

    def __str__(self):
        return "Identifier({name})".format(name=self.name)


class Apply(object):
    """Function application"""

    def __init__(self, fn, arg, location=None):
        self.fn = fn
        self.arg = arg
        self.location = location

    def __str__(self):
        return "({fn} {arg})".format(fn=self.fn, arg=self.arg)


class Let(object):
    """Let binding"""

    def __init__(self, v, defn, body, location=None):
        self.v = v
        self.defn = defn
        self.body = body
        self.location = location

    def __str__(self):
        return "(let {v} = {defn} in {body})".format(v=self.v, defn=self.defn, body=self.body)


class Letrec(object):
    """Letrec binding"""

    def __init__(self, v, defn, body, location=None):
        self.v = v
        self.defn = defn
        self.body = body
        self.location = location

    def __str__(self):
        return "(letrec {v} = {defn} in {body})".format(v=self.v, defn=self.defn, body=self.body)


class LetrecAnd(object):
    """LetrecAnd binding"""

    def __init__(self, bindings, body, location=None):
        self.bindings = bindings
        self.body = body
        self.location = location

    def __str__(self):
        str_view = "letrec_and(bindings = {"
        bindings = [f"{v}: ({loc}, {defn})" for v, (defn, loc) in self.bindings.items()]
        bindings_str = ', '.join(bindings)
        str_view += f"{bindings_str}}}, body = {self.body})"
        return str_view


class LiteralNumber(object):
    """LiteralNumber"""

    def __init__(self, value, location=None):
        self.value = value
        self.location = location

    def __str__(self):
        return str(self.value)


class LiteralString(object):
    """LiteralString"""

    def __init__(self, value, location=None):
        self.value = value
        self.location = location

    def __str__(self):
        return "LiteralString({v})".format(v=self.value)


class LiteralBoolean(object):
    """LiteralBoolean"""

    def __init__(self, value, location=None):
        self.value = value
        self.location = location

    def __str__(self):
        return str(self.value)


class Inherit(object):
    """Inheritance representation"""
    
    def __init__(self, base, child, location=None):
        self.base = base
        self.child = child
        self.location = location

    def __str__(self):
        return "({child} inherits {base})".format(base=self.base, child=self.child)


class Location(object):
    """Location in the source code"""
    def __init__(self, begin, end):
        self.line1, self.col1 = begin.split(':')
        self.line2, self.col2 = end.split(':')

    def __str__(self):
        str_view = ""
        if self.line1 == self.line2:
            str_view += f"line {self.line1}"
        else:
            str_view += f"lines {self.line1}-{self.line2}"
        return str_view