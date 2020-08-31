class Lambda(object):
    """Lambda abstraction"""

    def __init__(self, v, body):
        self.v = v
        self.body = body

    def __str__(self):
        return "(fn {v} => {body})".format(v=self.v, body=self.body)


class Identifier(object):
    """Identifier"""

    def __init__(self, name):
        assert(isinstance(name, str))
        self.name = name

    def __str__(self):
        return self.name


class Apply(object):
    """Function application"""

    def __init__(self, fn, arg):
        self.fn = fn
        self.arg = arg

    def __str__(self):
        return "({fn} {arg})".format(fn=self.fn, arg=self.arg)


class Let(object):
    """Let binding"""

    def __init__(self, v, defn, body):
        self.v = v
        self.defn = defn
        self.body = body

    def __str__(self):
        return "(let {v} = {defn} in {body})".format(v=self.v, defn=self.defn, body=self.body)


class Letrec(object):
    """Letrec binding"""

    def __init__(self, v, defn, body):
        self.v = v
        self.defn = defn
        self.body = body

    def __str__(self):
        return "(letrec {v} = {defn} in {body})".format(v=self.v, defn=self.defn, body=self.body)


class LiteralNumber(object):
    """LiteralNumber"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class LiteralString(object):
    """LiteralString"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class LiteralBoolean(object):
    """LiteralBoolean"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
