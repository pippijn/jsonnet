import jsonnet_ast as ast
import error

def rename_local(ast_: ast.AST, name_env: dict):
    if isinstance(ast_, ast.Object):
        for _, field_value in ast_.fields.items():
            rename_local(field_value, name_env)

    elif isinstance(ast_, ast.Local):
        all_bind_names = {}
        for bind in ast_.binds:
            all_bind_names[bind.var] = 'local_' + rename(bind.var)
        for bind in ast_.binds:
            new_name_env = name_env.copy()
            key = bind.var
            temp_value = all_bind_names.pop(key)
            if key in name_env:
                all_bind_names[key] = name_env[key]
            new_name_env.update(all_bind_names)
            rename_local(bind.body, new_name_env)
            all_bind_names[key] = temp_value
            bind.var = temp_value

        new_name_env = name_env.copy()
        new_name_env.update(all_bind_names)
        rename_local(ast_.body, new_name_env)

    elif isinstance(ast_, ast.Apply):
        rename_local(ast_.fn, name_env)
        for arg in ast_.arguments:
            rename_local(arg.expr, name_env)

    elif isinstance(ast_, ast.Array):
        for el in ast_.elements:
            rename_local(el, name_env)

    elif isinstance(ast_, ast.BinaryOp):
        rename_local(ast_.left_arg, name_env)
        rename_local(ast_.right_arg, name_env)

    elif isinstance(ast_, ast.BuiltinFunction):
        raise Exception('Not renamed yet!\n')

    elif isinstance(ast_, ast.Conditional):
        rename_local(ast_.cond, name_env)
        rename_local(ast_.branchTrue, name_env)
        rename_local(ast_.branchFalse, name_env)

    elif isinstance(ast_, ast.Error):
        return

    elif isinstance(ast_, ast.Function):
        new_name_env = name_env.copy()
        for arg in ast_.arguments:
            new_name_env[arg.id] = arg.id
        rename_local(ast_.body, new_name_env)

    elif isinstance(ast_, ast.InSuper):
        return

    elif isinstance(ast_, ast.Index):
        return

    elif isinstance(ast_, ast.LiteralBoolean):
        return

    elif isinstance(ast_, ast.LiteralNumber):
        return

    elif isinstance(ast_, ast.LiteralString):
        return

    elif isinstance(ast_, ast.LiteralNull):
        return

    elif isinstance(ast_, ast.ObjectComprehension):
        raise Exception('Not renamed yet!\n')

    elif isinstance(ast_, ast.Self):
        return

    elif isinstance(ast_, ast.SuperIndex):
        return

    elif isinstance(ast_, ast.UnaryOp):
        rename_local(ast_.arg, name_env)

    elif isinstance(ast_, ast.Var):
        if ast_.id not in name_env:
            raise error.ParseError(f"Local variable `{ast_.id}` is not defined, {ast_.location}")
        ast_.id = name_env[ast_.id]

    else:
        raise Exception('Node {x} is not found in jsonnet_ast\n'.format(
            x=ast_.__class__))


def rename(name):
    return name.replace('_', 'U_')