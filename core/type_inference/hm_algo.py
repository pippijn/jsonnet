""" An implementation of the Hindley Milner type checking algorithm
    based on implementation of Robert Smallshire. The algorithm was modified 
    to process additionaly introduced AST nodes and types. 
    Source code: https://github.com/rob-smallshire/hindley-milner-python
"""
from __future__ import print_function
import lambda_ast as l_ast
import lambda_types as l_type

# ----------------------------------------------------------------
# Exception types

class InferenceError(Exception):
    """Raised if the type inference algorithm cannot infer types successfully"""

    def __init__(self, message):
        self.__message = message

    message = property(lambda self: self.__message)

    def __str__(self):
        return str(self.message)


class ParseError(Exception):
    """Raised if the type environment supplied for is incomplete"""

    def __init__(self, message):
        self.__message = message

    message = property(lambda self: self.__message)

    def __str__(self):
        return str(self.message)

# ----------------------------------------------------------------
# Type inference machinery

def analyse(node, env, non_generic=None):
    """Computes the type of the expression given by node.

    The type of the node is computed in the context of the
    supplied type environment env. Data types can be introduced into the
    language simply by having a predefined set of identifiers in the initial
    environment. environment; this way there is no need to change the syntax or, more
    importantly, the type-checking program when extending the language.

    Args:
        node: The root of the abstract syntax tree.
        env: The type environment is a mapping of expression identifier names
            to type assignments.
        non_generic: A set of non-generic variables, or None

    Returns:
        The computed type of the expression.

    Raises:
        InferenceError: The type of the expression could not be inferred, for example
            if it is not possible to unify two types such as Number and Bool
        ParseError: The abstract syntax tree rooted at node could not be parsed
    """

    if non_generic is None:
        non_generic = set()

    if isinstance(node, l_ast.Identifier):
        result_type = get_type(node.name, env, non_generic, node.location)
        return result_type
    elif isinstance(node, l_ast.LiteralNumber):
        result_type = l_type.Number
        return result_type
    elif isinstance(node, l_ast.LiteralBoolean):
        result_type = l_type.Bool
        return result_type
    elif isinstance(node, l_ast.LiteralString):
        result_type = l_type.String
        return result_type
    elif isinstance(node, l_ast.Apply):
        fun_type = analyse(node.fn, env, non_generic)
        arg_type = analyse(node.arg, env, non_generic)
        result_type = l_type.TypeVariable()
        unify(l_type.Function(arg_type, result_type), fun_type, node.location)
        return result_type
    elif isinstance(node, l_ast.Lambda):
        arg_type = l_type.TypeVariable()
        new_env = env.copy()
        new_env[node.v] = arg_type
        new_non_generic = non_generic.copy()
        new_non_generic.add(arg_type)
        result_type = analyse(node.body, new_env, new_non_generic)
        return l_type.Function(arg_type, result_type)
    elif isinstance(node, l_ast.Let):
        defn_type = analyse(node.defn, env, non_generic)
        new_env = env.copy()
        new_env[node.v] = defn_type
        return analyse(node.body, new_env, non_generic)
    elif isinstance(node, l_ast.Letrec):
        new_type = l_type.TypeVariable()
        new_env = env.copy()
        new_env[node.v] = new_type
        new_non_generic = non_generic.copy()
        new_non_generic.add(new_type)
        defn_type = analyse(node.defn, new_env, new_non_generic)
        unify(new_type, defn_type, node.location)
        return analyse(node.body, new_env, non_generic)
    elif isinstance(node, l_ast.LetrecAnd):
        new_env = env.copy()
        new_non_generic = non_generic.copy()
        for v in node.bindings:
            new_type = l_type.TypeVariable()
            new_env[v] = new_type
            new_non_generic.add(new_type)
        for v, (defn, loc) in node.bindings.items():
            v_type = new_env[v]
            defn_type = analyse(defn, new_env, new_non_generic)
            unify(v_type, defn_type, loc, v)
        return analyse(node.body, new_env, new_non_generic)
    elif isinstance(node, l_ast.Inherit):
        left_row = analyse(node.base, env, non_generic)
        new_env = env.copy()
        update_env_with_obj_type_info(node.base, new_env)
        right_row = analyse(node.child, new_env, non_generic)

        result_type = l_type.TypeVariable()
        """
        type_copy is used as a temporary solution for not exatly correct implementation 
        of rows unification. It prevents update of the base object's type with the 
        fields of child object. 
        But the side-effect of the type_copy is too harmful. Since we work with copy of
        base object, we lose connection between the type of inheritance result and
        the type of base object. 
        """
        left_row_copy = type_copy(left_row)
        unify(left_row_copy, result_type, node.location)
        unify(right_row, result_type, node.location)
        return result_type
    assert 0, "Unhandled syntax node {0}".format(type(node))


def get_type(name, env, non_generic, location):
    """Get the type of identifier name from the type environment env.

    Args:
        name: The identifier name
        env: The type environment mapping from identifier names to types
        non_generic: A set of non-generic TypeVariables

    Raises:
        ParseError: Raised if name is undefined in the type environment.
    """
    if name in env:
        return fresh(env[name], non_generic)
    else:
        raise ParseError("Undefined name `{name}`, {loc}".format(
            name = name, 
            loc = location)
        )


def fresh(t, non_generic):
    """Makes a copy of a type expression.

    The type t is copied. The the generic variables are duplicated and the
    non_generic variables are shared.

    Args:
        t: A type to be copied.
        non_generic: A set of non-generic TypeVariables
    """
    mappings = {}  # A mapping of TypeVariables to TypeVariables

    def freshrec(tp):
        p = prune(tp)
        if isinstance(p, l_type.TypeVariable):
            if is_generic(p, non_generic):
                if p not in mappings:
                    mappings[p] = l_type.TypeVariable()
                return mappings[p]
            else:
                return p
        elif isinstance(p, l_type.TypeOperator):
            return l_type.TypeOperator(p.name, [freshrec(x) for x in p.types])
        elif isinstance(p, l_type.TypeRowOperator):
            return l_type.TypeRowOperator({k: freshrec(v) for k, v in p.fields.items()})

    return freshrec(t)


def type_copy(t):
    if isinstance(t, l_type.TypeVariable):
        new_instance = l_type.TypeVariable()
        new_instance.id = t.id
        if t.instance:
            new_instance.instance = type_copy(t.instance)
            new_instance.__name = t.name
    elif isinstance(t, l_type.TypeOperator):
        new_instance = l_type.TypeOperator(
            t.name, [type_copy(x) for x in t.types])
    elif isinstance(t, l_type.TypeRowOperator):
        new_instance = l_type.TypeRowOperator(
            {k: type_copy(v) for k, v in t.fields.items()})
    return new_instance


def unify(t1, t2, loc=None, field_name=None):
    """Unify the two types t1 and t2.

    Makes the types t1 and t2 the same.

    Args:
        t1: The first type to be made equivalent
        t2: The second type to be be equivalent

    Returns:
        None

    Raises:
        InferenceError: Raised if the types cannot be unified.
    """
    a = prune(t1)
    b = prune(t2)
    if isinstance(a, l_type.TypeVariable):
        if a != b:
            if occurs_in_type(a, b):
                raise InferenceError("recursive unification")
            a.instance = b
    elif (isinstance(a, l_type.TypeOperator) or isinstance(a, l_type.TypeRowOperator)) and isinstance(b, l_type.TypeVariable):
        unify(b, a, loc)
    elif isinstance(a, l_type.TypeOperator) and isinstance(b, l_type.TypeOperator):
        if a.name != b.name or len(a.types) != len(b.types):
            err_msg = "Type mismatch: {0} != {1}, {2}".format(
                str(a), str(b), loc)
            if field_name:
                err_msg += f", field '{field_name}'"
            raise InferenceError(err_msg)
        for p, q in zip(a.types, b.types):
            unify(p, q, loc)
    elif isinstance(a, l_type.TypeRowOperator) and isinstance(b, l_type.TypeRowOperator):
        for k in a.fields:
            if k in b.fields:
                unify(a.fields[k], b.fields[k], loc, k)
        unified_fields = a.fields.copy()
        unified_fields.update(b.fields)
        b.fields = unified_fields
    else:
        assert 0, "{a} and {b} are not unified".format(
            a=a.__class__.__name__, b=b.__class__.__name__
        )


def prune(t):
    """Returns the currently defining instance of t.

    As a side effect, collapses the list of type instances. The function Prune
    is used whenever a type expression has to be inspected: it will always
    return a type expression which is either an uninstantiated type variable or
    a type operator; i.e. it will skip instantiated variables, and will
    actually prune them from expressions to remove long chains of instantiated
    variables.

    Args:
        t: The type to be pruned

    Returns:
        An uninstantiated TypeVariable or a TypeOperator
    """
    if isinstance(t, l_type.TypeVariable):
        if t.instance is not None:
            t.instance = prune(t.instance)
            return t.instance
    return t


def is_generic(v, non_generic):
    """Checks whether a given variable occurs in a list of non-generic variables

    Note that a variables in such a list may be instantiated to a type term,
    in which case the variables contained in the type term are considered
    non-generic.

    Note: Must be called with v pre-pruned

    Args:
        v: The TypeVariable to be tested for genericity
        non_generic: A set of non-generic TypeVariables

    Returns:
        True if v is a generic variable, otherwise False
    """
    return not occurs_in(v, non_generic)


def occurs_in_type(v, type2):
    """Checks whether a type variable occurs in a type expression.

    Note: Must be called with v pre-pruned

    Args:
        v:  The TypeVariable to be tested for
        type2: The type in which to search

    Returns:
        True if v occurs in type2, otherwise False
    """
    pruned_type2 = prune(type2)
    if pruned_type2 == v:
        return True
    elif isinstance(pruned_type2, l_type.TypeOperator):
        return occurs_in(v, pruned_type2.types)
    elif isinstance(pruned_type2, l_type.TypeRowOperator):
        return occurs_in(v, pruned_type2.fields.values())
    return False


def occurs_in(t, types):
    """Checks whether a types variable occurs in any other types.

    Args:
        t:  The TypeVariable to be tested for
        types: The sequence of types in which to search

    Returns:
        True if t occurs in any of types, otherwise False
    """
    return any(occurs_in_type(t, t2) for t2 in types)


def update_env_with_obj_type_info(base_obj, env):
    """ 
    This function is used during inheritance to update type env with fields of base 
    object before child object will be analysed. It was a naive solution to cope 
    with undefined_but_used fields (marked as '!') inside object. In particular, 
    it works when type of base object is know during inheritance but some fields 
    of child object are supposed to be defined in the base object (and they are). 
    See `test_unrecognized_base_field` and `test_unrecognized_base_func_field` in 
    type_inference_test.py.
    
    An alternative (and more universal solution) to this problem is to define
    those undefined_but_used fields as `null` inside object. Then, we avoid 
    'Undefined <field_name>' error.
    """
    if isinstance(base_obj, l_ast.Identifier):
        if base_obj.name not in env:
            return
        base_obj_type = prune(env[base_obj.name])
        if isinstance(base_obj_type, l_type.TypeRowOperator):
            fields = base_obj_type.fields
            for v, tp in fields.items():
                env[v] = tp
    elif isinstance(base_obj, l_ast.Apply):
        if base_obj.fn.name not in env:
            return
        base_obj_type = prune(env[base_obj.fn.name])
        if isinstance(base_obj_type, l_type.Function):
            return_type = prune(base_obj_type.types[1])
            if isinstance(return_type, l_type.TypeRowOperator):
                fields = return_type.fields
                for v, tp in fields.items():
                    env[v] = tp
    else:
        raise Exception(f'Unexpected type of base: {base_obj.__class__.__name__}')


def try_exp(env, node):
    """Try to evaluate a type printing the result or reporting errors.

    Args:
        env: The type environment in which to evaluate the expression.
        node: The root node of the abstract syntax tree of the expression.

    Returns:
        None
    """
    try:
        with l_type.context():
            t = analyse(node, env)
            print(str(t))
            return str(t)
    except (ParseError, InferenceError) as e:
        print(e)
        return str(e)
