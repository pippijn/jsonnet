import hm_algo
import jsonnet_ast as ast
from lambda_types import TypeVariable
from translate_jsonnet_to_lambda import translate_to_lambda_ast
from rename import rename_local


def read_ast(filename):
    f = open(filename, 'r')
    ast = f.read()
    return ast


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
    ast_str = read_ast("core/type_inference/ast_string.txt")
    print(f"AST:\n{ast_str}")
    
    ast_ = parse_ast(ast_str)
    print(ast_)

    name_env = {'std': 'std'}
    rename_local(ast_, name_env)
    print(f"Renamed AST:\n{ast_}")

    env = create_init_env()
    lambda_ast = translate_to_lambda_ast(ast_, env)
    print(f"Lambda AST:\n{lambda_ast}")
    
    hm_algo.try_exp(env, lambda_ast)
