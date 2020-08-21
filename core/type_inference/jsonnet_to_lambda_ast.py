import jsonnet_ast as ast


def read_ast(filename):
    f = open(filename, 'r')
    ast = f.read()
    return ast


def parse_ast(ast):
    return eval(ast)


if __name__ == "__main__":
    ast = read_ast("core/type_inference/ast_string.txt")
    print(ast)
    ast = parse_ast(ast)
    print(ast)

