import subprocess

import hm_algo
import jsonnet_ast as ast
from lambda_types import TypeVariable
from translate_jsonnet_to_lambda import translate_to_lambda_ast
from rename import rename_local


def get_jsonnet_ast_str(jsonnet):
    command = f'bazel build //core/type_inference:print_ast && bazel-bin/core/type_inference/print_ast "{jsonnet}"'
    # maybe delete shell=True in future to make program more safe but it requires special form of command
    result = subprocess.run(command, stdout=subprocess.PIPE,
                            check=True, text=True, shell=True)
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


if __name__ == "__main__":
    jsonnet_program = "{a: 1}"
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

    hm_algo.try_exp(env, lambda_ast)
