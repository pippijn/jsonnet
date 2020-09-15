import jsonnet_ast as j_ast
import lambda_ast as lam_ast
from lambda_types import TypeVariable, TypeRowOperator, Function, TypeOperator


def translate_to_lambda_ast(ast_: j_ast.AST, my_env):
    if isinstance(ast_, j_ast.Object):
        ast_.fields = {translate_field_name(
            name): val for name, val in ast_.fields.items()}
        record = build_record_type_constructor(ast_.fields)
        record_id = get_next_record_id(my_env)
        my_env[record_id] = record

        field_names = list(ast_.fields.keys())
        body = apply_record(field_names, record_id, my_env)
        return build_letrec_and(field_names, ast_.fields, body, my_env)

    elif isinstance(ast_, j_ast.Local):
        bind_dic = {}
        for bind in ast_.binds:
            translated_body = translate_to_lambda_ast(bind.body, my_env)
            bind_dic[bind.var] = translated_body
        body = translate_to_lambda_ast(ast_.body, my_env)
        if isinstance(body, lam_ast.LetrecAnd):
            body.bindings.update(bind_dic)
            return body
        else:
            return lam_ast.LetrecAnd(bind_dic, body)

    elif isinstance(ast_, j_ast.Apply):
        def build_apply(fn, args):
            if not args:
                return translate_to_lambda_ast(fn, my_env)
            translated_arg = translate_to_lambda_ast(args[-1].expr, my_env)
            return lam_ast.Apply(build_apply(fn, args[:-1]), translated_arg)
        return build_apply(ast_.fn, ast_.arguments)

    elif isinstance(ast_, j_ast.Array):
        raise Exception('Not translated yet!\n')

    elif isinstance(ast_, j_ast.BinaryOp):
        if ast_.op == '+':
            return build_plus_op(ast_.left_arg, ast_.right_arg, my_env)
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
        if isinstance(ast_.target, j_ast.Self) and isinstance(ast_.index, j_ast.LiteralString):
            return lam_ast.Identifier(ast_.index.value)
        else:
            raise Exception('Not translated yet!\n')

    elif isinstance(ast_, j_ast.LiteralBoolean):
        return lam_ast.LiteralBoolean(ast_.value)

    elif isinstance(ast_, j_ast.LiteralNumber):
        return lam_ast.LiteralNumber(ast_.value)

    elif isinstance(ast_, j_ast.LiteralString):
        return lam_ast.LiteralString(ast_.value)

    elif isinstance(ast_, j_ast.LiteralNull):
        return lam_ast.Identifier("null")

    elif isinstance(ast_, j_ast.ObjectComprehensionSimple):
        raise Exception('Not translated yet!\n')

    elif isinstance(ast_, j_ast.Self):
        return lam_ast.Identifier("self")

    elif isinstance(ast_, j_ast.SuperIndex):
        return lam_ast.Identifier(ast_.index.value)

    elif isinstance(ast_, j_ast.UnaryOp):
        raise Exception('Not translated yet!\n')

    elif isinstance(ast_, j_ast.Var):
        return lam_ast.Identifier(ast_.id)

    else:
        print(ast_.__class__)
        raise Exception('Node is not found in jsonnet_ast\n')


def build_record_type_constructor(fields):
    type_var = {}
    field_type = {}
    for i, field in enumerate(fields):
        var = f'var{i}'
        type_var[var] = TypeVariable()
        field_type[field] = type_var[var]
    record_type = TypeRowOperator(field_type)

    def rec_build(i, n, type_var, record_type):
        if n == 0:
            return record_type
        var = type_var[f'var{i}']
        if (i == n-1):
            return Function(var, record_type)
        return Function(var, rec_build(i+1, n, type_var, record_type))

    return rec_build(0, len(type_var), type_var, record_type)


def build_letrec_and(names, fields, body, env):
    translated_fields = {}
    for name in names:
        translated_body = translate_to_lambda_ast(fields[name], env)
        translated_fields[name] = translated_body
    return lam_ast.LetrecAnd(translated_fields, body)


def build_let(names, fields, body, env):
    if not names:
        return body
    translated_body = translate_to_lambda_ast(fields[names[0]], env)
    return lam_ast.Let(names[0], translated_body, build_let(names[1:], fields, body, env))


def get_next_record_id(env):
    record_id = "record_{n}".format(n=env["__record_count__"])
    env["__record_count__"] += 1
    return record_id


def get_next_plus_id(env):
    plus_id = "plus_{n}".format(n=env["__plus_count__"])
    env["__plus_count__"] += 1
    return plus_id


def apply_record(names, record_id, env):
    if not names:
        return lam_ast.Identifier(record_id)
    return lam_ast.Apply(apply_record(names[:-1], record_id, env), lam_ast.Identifier(names[-1]))


def translate_field_name(name):
    if isinstance(name, j_ast.LiteralString):
        return name.value
    else:
        raise Exception(f"Expected LiteralString but got {name.__class__}")


def build_plus_op(left_arg, right_arg, env):
    if isinstance(right_arg, j_ast.Object):
        base_obj = translate_to_lambda_ast(left_arg, env)
        child_obj = translate_to_lambda_ast(right_arg, env)
        return lam_ast.Inherit(base_obj, child_obj)
    else:
        var = TypeVariable()
        plus_id = get_next_plus_id(env)
        env[plus_id] = Function(var, Function(var, var))
        return lam_ast.Apply(lam_ast.Apply(lam_ast.Identifier(plus_id),
                           translate_to_lambda_ast(left_arg, env)),
                     translate_to_lambda_ast(right_arg, env))
