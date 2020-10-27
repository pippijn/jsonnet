import subprocess
import argparse

import hm_algo
import jsonnet_ast as ast
from lambda_types import TypeVariable, Function
from translate_jsonnet_to_lambda import translate_to_lambda_ast
from rename import rename_local


def get_jsonnet_ast_str(jsonnet, rebuild):
    if rebuild:
        command1 = ['bazel', 'build', '//core/type_inference:print_ast']
        subprocess.run(command1, check=True, text=True)

    command2 = ['bazel-bin/core/type_inference/print_ast', f'{jsonnet}']
    result = subprocess.run(command2, stdout=subprocess.PIPE, 
                            check=True, text=True, shell=False)
    return result.stdout


def parse_ast(ast_str):
    return eval(ast_str)


def create_init_env():
    init_env = {}
    init_env["__record_count__"] = 0
    tv = TypeVariable()
    init_env["+"] = Function(tv, Function(tv, tv))
    init_env["null"] = TypeVariable()
    init_env["self"] = TypeVariable()
    return init_env


def run(jsonnet_program, rebuild=False):
    print(jsonnet_program)

    jsonnet_ast_str = get_jsonnet_ast_str(jsonnet_program, rebuild)
    print(f"\nAST:\n{jsonnet_ast_str}")

    jsonnet_ast = parse_ast(jsonnet_ast_str)
    print(jsonnet_ast)

    name_env = {'std': 'std'}
    rename_local(jsonnet_ast, name_env)
    print(f"\nRenamed AST:\n{jsonnet_ast}")

    env = create_init_env()
    lambda_ast = translate_to_lambda_ast(jsonnet_ast, env)
    print(f"\nLambda AST:\n{lambda_ast}")

    return hm_algo.try_exp(env, lambda_ast)


def read_file(file_name):
    f = open(file_name, "r")
    return f.read()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run type inference.')
    parser.add_argument('--file_path', type=str, required=True,
                        help='path to file with jsonnet program')
    parser.add_argument('--rebuild', action='store_true', default=False,
                        help='add this flag to rebuild print_ast.cpp')
    args = parser.parse_args()
    
    jsonnet_program = read_file(args.file_path)
    run(jsonnet_program, args.rebuild)
