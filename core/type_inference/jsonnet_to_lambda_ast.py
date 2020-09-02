import jsonnet_ast as ast
from lambda_ast import *
from lambda_types import *

import hm_algo


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


def get_next_record_id(env):
    record_id = "record_{n}".format(n=env["__record_count__"])
    env["__record_count__"] += 1
    return record_id


def apply_record(keys, record_id, env):
    if not keys:
        return Identifier(record_id)
    key = translate_to_lambda_ast(keys[-1], env, only_str=True)
    return Apply(apply_record(keys[:-1], record_id, env), Identifier(key))

# create LetrecAnd object
def build_letrec_and(keys, fields, body, env):
    translated_fields = {}
    for key in keys:
        translated_id = translate_to_lambda_ast(key, env, only_str=True)
        translated_body = translate_to_lambda_ast(fields[key], env)
        translated_fields[translated_id] = translated_body
    return LetrecAnd(translated_fields, body)

# create Let object
def build_let(keys, fields, body, env):
    if not keys:
        return body
    translated_body = translate_to_lambda_ast(fields[keys[0]], env)
    translated_id = translate_to_lambda_ast(keys[0], env, only_str=True)
    return Let(translated_id, translated_body, build_let(keys[1:], fields, body, env))


def translate_to_lambda_ast(ast_: ast.AST, my_env, **kwargs):
    if isinstance(ast_, ast.Object):
        record = build_record_type_constructor(ast_.fields)
        record_id = get_next_record_id(my_env)
        my_env[record_id] = record

        field_keys = list(ast_.fields.keys())
        let_body = apply_record(field_keys, record_id, my_env)
        res = build_letrec_and(field_keys, ast_.fields, let_body, my_env)
        return res

    elif isinstance(ast_, ast.Local):
        def process_binds(binds, body):
            if not binds:
                return body
            translated_body = translate_to_lambda_ast(binds[0].body, my_env)
            return Let(binds[0].var, translated_body, process_binds(binds[1:], body))
        body = translate_to_lambda_ast(ast_.body, my_env)
        return process_binds(ast_.binds, body)

    elif isinstance(ast_, ast.Apply):
        return Apply(ast_.fn, ast_.argv)

    elif isinstance(ast_, ast.Array):
        raise Exception('Not translated yet!\n')  # add to lambda AST

    elif isinstance(ast_, ast.BinaryOp):
        raise Exception('Not translated yet!\n')

    elif isinstance(ast_, ast.BuiltinFunction):
        raise Exception('Not translated yet!\n')

    elif isinstance(ast_, ast.Conditional):
        raise Exception('Not translated yet!\n')

    elif isinstance(ast_, ast.Error):
        raise Exception('Not translated yet!\n')

    elif isinstance(ast_, ast.Function):
        raise Exception('Not translated yet!\n')

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
        if 'only_str' in kwargs and kwargs.get('only_str'):
            return ast_.value
        return LiteralString(ast_.value)

    elif isinstance(ast_, ast.LiteralNull):
        return Letrec("null", Identifier("null"), Identifier("null"))

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


def read_ast(filename):
    f = open(filename, 'r')
    ast = f.read()
    return ast


def parse_ast(ast_str):
    return eval(ast_str)


def create_init_env():
    init_env = {}
    init_env["__record_count__"] = 0
    init_env["None"] = TypeVariable 
    init_env["self"] = TypeVariable
    return init_env


if __name__ == "__main__":
    ast_str = read_ast("core/type_inference/ast_string.txt")
    print(f"AST: {ast_str}")
    ast_ = parse_ast(ast_str)
    print(ast_)

    env = create_init_env()
    res = translate_to_lambda_ast(ast_, env)
    print(res)
    hm_algo.try_exp(env, res)
