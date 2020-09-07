import jsonnet_ast as ast
from lambda_ast import *
from lambda_types import TypeVariable, TypeRowOperator, Function


def translate_to_lambda_ast(ast_: ast.AST, my_env):
    if isinstance(ast_, ast.Object):
        record = build_record_type_constructor(ast_.fields)
        record_id = get_next_record_id(my_env)
        my_env[record_id] = record

        field_names = list(ast_.fields.keys())
        body = apply_record(field_names, record_id, my_env)
        return build_letrec_and(field_names, ast_.fields, body, my_env)

    elif isinstance(ast_, ast.Local):
        bind_dic = {}
        for bind in ast_.binds:
            translated_body = translate_to_lambda_ast(bind.body, my_env)
            bind_dic[bind.var] = translated_body
        body = translate_to_lambda_ast(ast_.body, my_env)
        if isinstance(body, LetrecAnd):
            body.bindings.update(bind_dic)
            return body
        else:
            return LetrecAnd(bind_dic, body)

    elif isinstance(ast_, ast.Apply):
        def build_apply(fn, args):
            if not args:
                return translate_to_lambda_ast(fn, my_env)
            translated_arg = translate_to_lambda_ast(args[-1].expr, my_env)
            return Apply(build_apply(fn, args[:-1]), translated_arg)
        return build_apply(ast_.fn, ast_.arguments)

    elif isinstance(ast_, ast.Array):
        raise Exception('Not translated yet!\n') 

    elif isinstance(ast_, ast.BinaryOp):
        raise Exception('Not translated yet!\n')

    elif isinstance(ast_, ast.BuiltinFunction):
        raise Exception('Not translated yet!\n')

    elif isinstance(ast_, ast.Conditional):
        raise Exception('Not translated yet!\n')

    elif isinstance(ast_, ast.Error):
        raise Exception('Not translated yet!\n')

    elif isinstance(ast_, ast.Function):
        def build_lambda(args, body):
            if not args:
                return translate_to_lambda_ast(body, my_env)
            return Lambda(args[0].id, build_lambda(args[1:], body))
        return build_lambda(ast_.arguments, ast_.body)

    elif isinstance(ast_, ast.InSuper):
        raise Exception('Not translated yet!\n')

    elif isinstance(ast_, ast.Index):
        if isinstance(ast_.target, ast.Self) and isinstance(ast_.index, ast.LiteralString):
            return Identifier(ast_.index.value)
        else:
            raise Exception('Not translated yet!\n')

    elif isinstance(ast_, ast.LiteralBoolean):
        return LiteralBoolean(ast_.value)

    elif isinstance(ast_, ast.LiteralNumber):
        return LiteralNumber(ast_.value)

    elif isinstance(ast_, ast.LiteralString):
        return LiteralString(ast_.value)

    elif isinstance(ast_, ast.LiteralNull):
        return LetrecAnd({"null": Identifier("null")}, Identifier("null"))

    elif isinstance(ast_, ast.ObjectComprehensionSimple):
        raise Exception('Not translated yet!\n')

    elif isinstance(ast_, ast.Self):
        return Identifier("self")

    elif isinstance(ast_, ast.SuperIndex):
        raise Exception('Not translated yet!\n')

    elif isinstance(ast_, ast.UnaryOp):
        raise Exception('Not translated yet!\n')

    elif isinstance(ast_, ast.Var):
        return Identifier(ast_.id)

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
        var = type_var[f'var{i}']
        if (i == n-1):
            return Function(var, record_type)
        return Function(var, rec_build(i+1, n, type_var, record_type))

    return rec_build(0, len(type_var), type_var, record_type)


def build_letrec_and(names, fields, body, env):
    translated_fields = {}
    for name in names:
        translated_id = translate_field_name(name)
        translated_body = translate_to_lambda_ast(fields[name], env)
        translated_fields[translated_id] = translated_body
    return LetrecAnd(translated_fields, body)


def build_let(names, fields, body, env):
    if not names:
        return body
    translated_body = translate_to_lambda_ast(fields[names[0]], env)
    translated_id = translate_field_name(names[0])
    return Let(translated_id, translated_body, build_let(names[1:], fields, body, env))


def get_next_record_id(env):
    record_id = "record_{n}".format(n=env["__record_count__"])
    env["__record_count__"] += 1
    return record_id


def apply_record(names, record_id, env):
    if not names:
        return Identifier(record_id)
    name = translate_field_name(names[-1])
    return Apply(apply_record(names[:-1], record_id, env), Identifier(name))


def translate_field_name(name):
    if isinstance(name, ast.LiteralString):
        return name.value
    else:
        raise Exception(
            f"Expected type LiteralString but got {name.__class__}")

