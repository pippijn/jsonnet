# =======================================================#
# Types and type constructors
import copy

class TypeVariable(object):
    """A type variable standing for an arbitrary type.

    All type variables have a unique id, but names are only assigned lazily,
    when required.
    """

    next_variable_id = 0

    def __init__(self):
        self.id = TypeVariable.next_variable_id
        TypeVariable.next_variable_id += 1
        self.instance = None
        self.__name = None

    next_variable_name = 'a'

    @property
    def name(self):
        """Names are allocated to TypeVariables lazily, so that only TypeVariables
        present after analysis consume names.
        """
        if self.__name is None:
            self.__name = TypeVariable.next_variable_name
            TypeVariable.next_variable_name = chr(
                ord(TypeVariable.next_variable_name) + 1)
        return self.__name

    def __str__(self):
        if self.instance is not None:
            return str(self.instance)
        else:
            return self.name

    def __repr__(self):
        return "TypeVariable(id = {0})".format(self.id)
    
    def type_deepcopy(self):
        new_instance = TypeVariable()
        new_instance.__dict__.update(self.__dict__)
        new_instance.id = self.id
        new_instance.instance = copy.deepcopy(self.instance)
        new_instance.__name = self.__name
        return new_instance


class TypeRowOperator(object):
    """An n-ary type constructor which builds a new type from old"""

    def __init__(self, fields):
        self.fields = fields

    def __str__(self):
        num_types = len(self.fields)

        if num_types == 0:
            return '{}'

        name_type_pairs = [f"{x[0]}: {x[1]}" for x in self.fields.items()]

        return "{{{0}}}".format(', '.join(name_type_pairs))
    
    def type_deepcopy(self):
        new_instance = TypeRowOperator(self.fields)
        new_instance.__dict__.update(self.__dict__)
        new_instance.fields = copy.deepcopy(self.fields)
        return new_instance


class TypeOperator(object):
    """An n-ary type constructor which builds a new type from old"""

    def __init__(self, name, types):
        self.name = name
        self.types = types

    def __str__(self):
        num_types = len(self.types)
        if num_types == 0:
            return self.name
        elif num_types == 2:
            return "({0} {1} {2})".format(str(self.types[0]), self.name, str(self.types[1]))
        else:
            return "{0} {1}" .format(self.name, ' '.join(self.types))
    
    def type_deepcopy(self):
        new_instance = TypeOperator(self.name, self.types)
        new_instance.__dict__.update(self.__dict__)
        new_instance.types = copy.deepcopy(self.types)
        return new_instance


class Function(TypeOperator):
    """A binary type constructor which builds function types"""

    def __init__(self, from_type, to_type):
        super(Function, self).__init__("->", [from_type, to_type])


# =============================================================#
# Basic types, constructed with a nullary type constructor

Number = TypeOperator("number", [])  # Basic number: int, float
Bool = TypeOperator("boolean", [])  # Basic boolean
String = TypeOperator("string", [])  # string
