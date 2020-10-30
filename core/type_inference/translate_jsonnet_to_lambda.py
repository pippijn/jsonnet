import jsonnet_ast as j_ast
import lambda_ast as lam_ast
from lambda_types import TypeVariable, TypeRowOperator, Function, TypeOperator


def translate_to_lambda_ast(ast_: j_ast.AST, my_env):
    """ Recursively translates Jsonnet AST to Lambda AST"""

    if isinstance(ast_, j_ast.Object):
        location = translate_location(ast_.location)
        ast_.fields = {
            translate_field_name(name): val for name, val in ast_.fields.items()
        }
        record = build_record_type_constructor(ast_.fields)
        record_id = get_next_record_id(my_env)
        my_env[record_id] = record

        field_keys = list(ast_.fields.keys())
        body = apply_record(field_keys, record_id, my_env, location)
        return build_letrec_and(field_keys, ast_.fields, body, my_env, location)

    elif isinstance(ast_, j_ast.Local):
        location = translate_location(ast_.location)
        bind_dic = {}
        for bind in ast_.binds:
            translated_body = translate_to_lambda_ast(bind.body, my_env)
            bind_dic[bind.var] = (translated_body, None)
        body = translate_to_lambda_ast(ast_.body, my_env)
        if isinstance(body, lam_ast.LetrecAnd):
            body.bindings.update(bind_dic)
            return body
        else:
            return lam_ast.LetrecAnd(bind_dic, body, location)

    elif isinstance(ast_, j_ast.Apply):
        location = translate_location(ast_.location)
        def build_apply(fn, args, location):
            if not args:
                return translate_to_lambda_ast(fn, my_env)
            translated_arg = translate_to_lambda_ast(args[-1].expr, my_env)
            return lam_ast.Apply(build_apply(fn, args[:-1], location), 
                                 translated_arg, 
                                 location)
        return build_apply(ast_.fn, ast_.arguments, location)

    elif isinstance(ast_, j_ast.Array):
        raise Exception('Not translated yet!\n')

    elif isinstance(ast_, j_ast.BinaryOp):
        location = translate_location(ast_.location)
        if ast_.op == '+':
            return build_plus_op(ast_.left_arg, ast_.right_arg, my_env, location)
        else:
            raise Exception('Not translated yet!\n')

    elif isinstance(ast_, j_ast.BuiltinFunction):
        raise Exception('Not translated yet!\n')

    elif isinstance(ast_, j_ast.Conditional):
        raise Exception('Not translated yet!\n')

    elif isinstance(ast_, j_ast.Error):
        raise Exception('Not translated yet!\n')

    elif isinstance(ast_, j_ast.Function):
        def build_lambda(args, body):
            if not args:
                return translate_to_lambda_ast(body, my_env)
            return lam_ast.Lambda(args[0].id, build_lambda(args[1:], body))
        return build_lambda(ast_.arguments, ast_.body)

    elif isinstance(ast_, j_ast.InSuper):
        raise Exception('Not translated yet!\n')

    elif isinstance(ast_, j_ast.Index):
        location = translate_location(ast_.location)
        if isinstance(ast_.target, j_ast.Self) and isinstance(ast_.index, j_ast.LiteralString):
            return lam_ast.Identifier(ast_.index.value, location)
        else:
            raise Exception('Not translated yet!\n')

    elif isinstance(ast_, j_ast.LiteralBoolean):
        location = translate_location(ast_.location)
        return lam_ast.LiteralBoolean(ast_.value, location)

    elif isinstance(ast_, j_ast.LiteralNumber):
        location = translate_location(ast_.location)
        return lam_ast.LiteralNumber(ast_.value, location)

    elif isinstance(ast_, j_ast.LiteralString):
        location = translate_location(ast_.location)
        return lam_ast.LiteralString(ast_.value, location)

    elif isinstance(ast_, j_ast.LiteralNull):
        return lam_ast.Identifier("null")

    elif isinstance(ast_, j_ast.ObjectComprehension):
        raise Exception('Not translated yet!\n')

    elif isinstance(ast_, j_ast.Self):
        return lam_ast.Identifier("self")

    elif isinstance(ast_, j_ast.SuperIndex):
        return lam_ast.Identifier(ast_.index.value)

    elif isinstance(ast_, j_ast.UnaryOp):
        raise Exception('Not translated yet!\n')

    elif isinstance(ast_, j_ast.Var):
        location = translate_location(ast_.location)
        return lam_ast.Identifier(ast_.id, location)

    else:
        print(ast_.__class__)
        raise Exception('Node is not found in jsonnet_ast\n')


def build_record_type_constructor(fields):
    """ Recursively builds constructor of TypeRowOperator by applying
    one field after another.

    Parameters:
        fields (dict): object's fields 
    """

    var_type = {}
    name_type = {}
    for i, field in enumerate(fields):
        name, _ = field
        var = f'var{i}'
        var_type[var] = TypeVariable()
        name_type[name] = var_type[var]
    record_type = TypeRowOperator(name_type)

    def rec_build(i, n, var_type, record_type):
        if n == 0:
            return record_type
        var = var_type[f'var{i}']
        if (i == n-1):
            return Function(var, record_type)
        return Function(var, rec_build(i+1, n, var_type, record_type))

    return rec_build(0, len(var_type), var_type, record_type)


def build_letrec_and(field_keys, fields, body, env, location):
    """ Builds LetrecAnd node. 
    
    Parameters:
        field_keys (list): list of keys which consist of field_name and location;
        fields (dict): dictionary which maps (field_name, field_location) to field_body;
        body (object): body of LetrecAnd wich consist of record application to its fields;
        env (dict): type environment;
        location (object): location of the corresponding object
    """

    translated_fields = {}
    for key in field_keys:
        translated_body = translate_to_lambda_ast(fields[key], env)
        name, loc = key
        translated_fields[name] = (translated_body, loc)
    return lam_ast.LetrecAnd(translated_fields, body, location)


def get_next_record_id(env):
    """ Returns new record id which can be used to store new record in env."""

    record_id = "record_{n}".format(n=env["__record_count__"])
    env["__record_count__"] += 1
    return record_id


def apply_record(field_keys, record_id, env, location):
    """ Recursively applies record to each field of object. 
    
    Parameters:
        field_keys (list): list of keys which consist of field_name and location;
        record_id (object): name of record constructor in type env;
        env (dict): type environment;
        location (object): location of the corresponding
    """

    if not field_keys:
        return lam_ast.Identifier(record_id)
    name, loc = field_keys[-1]
    return lam_ast.Apply(apply_record(field_keys[:-1], record_id, env, location),
                         lam_ast.Identifier(name, loc),
                         location)


def translate_field_name(name):
    """ If `name` is an instance of LiteralString then it is
    translated into tuple (name.value: str, location: Location).
    Otherwise, exception is thrown.

    Parameters:
        name (object): it corresponds to the name for field
    """

    location = translate_location(name.location)
    if isinstance(name, j_ast.LiteralString):
        return (name.value, location)
    else:
        raise Exception(f"Expected LiteralString but got {name.__class__}")


def build_plus_op(left_arg, right_arg, env, location):
    """ Represents Jsonnet AST node BinaryOp in terms of Lambda AST.
    Depending on the right_arg, binary_op is considered either as inheritance 
    or usual '+' operator between operands with the same types. 
    
    Remark:
    This function doesn't process all cases.
    For example, '+' is allowed in Jsonnet between string and any other type 
    but we don't allow this with current implementation.
    In addition, the problematic case is '+' between two objects when right_arg 
    is, for exmaple, an instance of Var. In this case, the type of left_arg doesn't 
    have to be equal to the type of right_arg but we require it now. 

    Parameters:
        left_arg (object): left operand;
        right_arg (object): right operand;
        env (dict): type environment;
        location (object): location of BinaryOp

    """

    if isinstance(right_arg, j_ast.Object):
        base_obj = translate_to_lambda_ast(left_arg, env)
        child_obj = translate_to_lambda_ast(right_arg, env)
        return lam_ast.Inherit(base_obj, child_obj, location)
    else:
        return lam_ast.Apply(lam_ast.Apply(lam_ast.Identifier("+"),
                                           translate_to_lambda_ast(
                                               left_arg, env),
                                           location),
                             translate_to_lambda_ast(right_arg, env),
                             location)

def translate_location(location):
    """ Translates location to the corresponding Location object in
    Lambda AST.
    """

    return lam_ast.Location(location.begin, location.end)