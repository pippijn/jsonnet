import jsonnet_ast as ast
from lambda_ast import *
from lambda_types import *

import hm_algo


def build_record(fields):
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


def get_record_id_in_env(env):
    # if "record" not in env:
    #     env["record"] = {}
    # record_id = "record{n}".format(n=len(env["record"]))
    return "record0"


def build_let_body(keys, record_id, env):
    if not keys:
        return Identifier(record_id)
    key = translate_to_lambda_ast(keys[0], env)
    return Apply(build_let_body(keys[1:], record_id, env), Identifier(key)) 


def translate_to_lambda_ast(ast_: ast.AST, my_env):
    if isinstance(ast_, ast.Object):
        record = build_record(ast_.fields)
        record_id = get_record_id_in_env(my_env)
        my_env[record_id] = record

        # create let object
        def process_fields(keys, fields, body):
            if not keys:
                return body
            translated_body = translate_to_lambda_ast(fields[keys[0]], my_env)
            translated_id = translate_to_lambda_ast(keys[0], my_env)
            return Let(translated_id, translated_body, process_fields(keys[1:], fields, body))

        field_keys = list(ast_.fields.keys())
        let_body = build_let_body(field_keys, record_id, my_env)
        res = process_fields(field_keys, ast_.fields, let_body)
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
        pass  # add to lambda AST

    # elif isinstance(ast_, ast.Binary):
    #     pass

    # elif isinstance(ast_, ast.BuiltInFunction):
    #     pass

    elif isinstance(ast_, ast.Conditional):
        pass

    elif isinstance(ast_, ast.Error):
        pass

    elif isinstance(ast_, ast.Function):
        pass

    elif isinstance(ast_, ast.InSuper):
        pass

    elif isinstance(ast_, ast.Index):
        pass

    elif isinstance(ast_, ast.LiteralBoolean):
        return ast_.value

    elif isinstance(ast_, ast.LiteralNumber):
        return ast_.value

    elif isinstance(ast_, ast.LiteralString):
        return ast_.value

    elif isinstance(ast_, ast.LiteralNull):
        return Letrec("null", Identifier("null"), Identifier("null"))

    # elif isinstance(ast_, ast.ObjectComprehensionSimple):
    #     pass

    elif isinstance(ast_, ast.Self):
        pass

    # elif isinstance(ast_, ast.SuperIndex):
    #     pass

    # elif isinstance(ast_, ast.Unary):
    #     pass

    elif isinstance(ast_, ast.Var):
        return Identifier(ast_.id)

    else:
        pass


def read_ast(filename):
    f = open(filename, 'r')
    ast = f.read()
    return ast


def parse_ast(ast_str):
    return eval(ast_str)


if __name__ == "__main__":
    ast_str = read_ast("core/type_inference/ast_string.txt")
    print(f"AST: {ast_str}")
    ast_ = parse_ast(ast_str)
    print(ast_)
    env = {"None": TypeVariable()}
    res = translate_to_lambda_ast(ast_, env)
    print(res)
    print("env", env)
    hm_algo.try_exp(env, res)


