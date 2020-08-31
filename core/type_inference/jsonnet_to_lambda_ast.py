import jsonnet_ast as ast
from lambda_ast import *
from lambda_types import *


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
    if "record" not in env:
        env["record"] = {}
    record_id = "record{n}".format(n=len(env["record"]))
    return record_id


def build_let_body(keys, record_id):
    if not keys:
        return Identifier(record_id)
    return Apply(build_let_body(keys[1:], record_id), Identifier(keys[0]))


def translate_to_lambda_ast(ast: ast.AST, my_env):
    if isinstance(ast, ast.Object):
        record = build_record(ast.fields)
        record_id = get_record_id_in_env(my_env)
        my_env["record"][record_id] = record

        # create let object
        def process_fields(keys, fields, body):
            if not keys:
                return body
            translated_body = translate_to_lambda_ast(fields[keys[0]], my_env)
            translated_id = translate_to_lambda_ast(keys[0], my_env)
            return Let(translated_id, translated_body, process_fields(keys[1:], fields, body))

        field_keys = list(ast.fields.keys())
        let_body = build_let_body(field_keys, record_id)
        res = process_fields(field_keys, ast.fields, let_body)
        return res

    elif isinstance(ast, ast.Local):
        def process_binds(binds, body):
            if not binds:
                return body
            translated_body = translate_to_lambda_ast(binds[0].body, my_env)
            return Let(binds[0].var, translated_body, process_binds(binds[1:], body))
        body = translate_to_lambda_ast(ast.body, my_env)
        return process_binds(ast.binds, body)

    elif isinstance(ast, ast.Apply):
        return Apply(ast.fn, ast.argv)

    elif isinstance(ast, ast.Array):
        pass  # add to lambda AST

    elif isinstance(ast, ast.Binary):
        pass

    elif isinstance(ast, ast.BuiltInFunction):
        pass

    elif isinstance(ast, ast.Conditional):
        pass

    elif isinstance(ast, ast.Error):
        pass

    elif isinstance(ast, ast.Function):
        pass

    elif isinstance(ast, ast.InSuper):
        pass

    elif isinstance(ast, ast.Index):
        pass

    elif isinstance(ast, ast.LiteralBoolean):
        return ast.value

    elif isinstance(ast, ast.LiteralNumber):
        return ast.value

    elif isinstance(ast, ast.LiteralString):
        return ast.value

    elif isinstance(ast, ast.LiteralNull):
        return Letrec("null", Identifier("null"), Identifier("null"))

    elif isinstance(ast, ast.ObjectComprehensionSimple):
        pass

    elif isinstance(ast, ast.Self):
        pass

    elif isinstance(ast, ast.SuperIndex):
        pass

    elif isinstance(ast, ast.Unary):
        pass

    elif isinstance(ast, ast.Var):
        return Identifier(ast.id)

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
    ast = parse_ast(ast_str)
    print(ast)
