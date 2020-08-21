import jsonnet_ast as ast


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

