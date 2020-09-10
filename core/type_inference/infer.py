import subprocess

import hm_algo
import jsonnet_ast as ast
from lambda_types import TypeVariable
from translate_jsonnet_to_lambda import translate_to_lambda_ast
from rename import rename_local


def get_jsonnet_ast_str(jsonnet):
    command1 = ['bazel', 'build', '//core/type_inference:print_ast']
    subprocess.run(command1, check=True, text=True)

    command2 = ['bazel-bin/core/type_inference/print_ast', f'{jsonnet}']
    result = subprocess.run(
        command2, stdout=subprocess.PIPE, check=True, text=True)
    return result.stdout


def parse_ast(ast_str):
    return eval(ast_str)


def create_init_env():
    init_env = {}
    init_env["__record_count__"] = 0
    init_env["__plus_count__"] = 0
    init_env["None"] = TypeVariable()
    init_env["null"] = TypeVariable()
    init_env["self"] = TypeVariable()
    return init_env


def run(jsonnet_program):
    jsonnet_ast_str = get_jsonnet_ast_str(jsonnet_program)
    print(f"AST:\n{jsonnet_ast_str}")

    jsonnet_ast = parse_ast(jsonnet_ast_str)
    print(jsonnet_ast)

    name_env = {'std': 'std'}
    rename_local(jsonnet_ast, name_env)
    print(f"Renamed AST:\n{jsonnet_ast}")

    env = create_init_env()
    lambda_ast = translate_to_lambda_ast(jsonnet_ast, env)
    print(f"Lambda AST:\n{lambda_ast}")

    return hm_algo.try_exp(env, lambda_ast)


if __name__ == "__main__":
    jsonnet_program = "{a: 1}"
    run(jsonnet_program)
