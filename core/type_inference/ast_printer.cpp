
// Sample output of print_ast function
// print_ast(desugar(parse(allocator, lex('if 2 == 3 then "hello" else 55'))))
// =>
// ast.Conditional(
// ast.BinaryOp("==", ast.Integer("2"), ast.Integer("3")),
// …,
// …) <-

#include <iostream>
#include <ostream>
#include <string>

#include "./ast.h"
#include "desugarer.h"
#include "lexer.h"
#include "parser.h"

// Overloading '<<' for AST and its nodes
std::ostream &operator<<(std::ostream &out, Apply *ast)
{
    out << "ast.Apply(";
    out << ast->target;
    for (ArgParam &arg : ast->args) {
        out << ", ";
        out << arg.expr;
    }
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, Array *ast)
{
    out << "ast.Array([";
    for (auto &el : ast->elements) {
        out << el.expr;
        out << ",";
    }
    out << "])";
    return out;
}

std::ostream &operator<<(std::ostream &out, Binary *ast)
{
    out << "ast.BinaryOp(";
    out << bop_string(ast->op);
    out << ",";
    out << ast->left;
    out << ",";
    out << ast->right;
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, BuiltinFunction *ast)
{
    out << "ast.BuiltInFunction(";
    out << ast->name;
    for (auto param : ast->params) {
        out << ",";
        out << param;
    }
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, Function *ast)
{
    out << "ast.Function(";
    for (auto arg_param : ast->params) {
        out << arg_param.id;
        out << " ";
        out << arg_param.expr;
        out << ",";
    }
    out << ")";
    out << ast->body;
    return out;
}

std::ostream &operator<<(std::ostream &out, Conditional *ast)
{
    out << "ast.Conditional(";
    out << ast->cond;
    out << ",";
    out << ast->branchTrue;
    out << ",";
    out << ast->branchFalse;
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, Error *ast)
{
    out << "ast.Error(";
    out << ast->expr;
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, Import *ast)
{
    out << "ast.Import(";
    out << ast->file;
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, Local *ast)
{
    // it should be changed most probably
    out << "ast.Local(";
    // out << ast->body;
    for (auto bind : ast->binds) {
        out << ',';
        out << bind.var;
        out << ": ";
        // out << bind.body;
    }
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, LiteralBoolean *ast)
{
    out << "ast.LiteralBoolean(";
    out << ast->value;
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, LiteralNumber *ast)
{
    out << "ast.LiteralNumber(";
    out << ast->value;
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, LiteralString *ast)
{
    out << "ast.LiteralString(";
    out << ast->value.c_str();
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, DesugaredObject *ast)
{
    // - maybe it is better to overload operator for Field structure
    // - maybe we will need hide field to kepp info about inheritance
    out << "ast.Object({";
    for (auto field : ast->fields) {
        out << field.name;
        out << ": ";
        out << field.body;
        out << ",";
    }
    out << "})";
    return out;
}

std::ostream &operator<<(std::ostream &out, Unary *ast)
{
    out << "ast.Unary(";
    out << uop_string(ast->op);
    out << ",";
    out << ast->expr;
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, Var *ast)
{
    out << "ast.Var(";
    out << ast->id;
    out << ")";
    return out;
}

// keep empty cases for desugared nodes or just delete them ?
std::ostream &operator<<(std::ostream &out, AST *ast_)
{
    out << ASTTypeToString(ast_->type) << " : ";
    if (auto *ast = dynamic_cast<Apply *>(ast_)) {
        out << ast;

    } else if (auto *ast = dynamic_cast<ApplyBrace *>(ast_)) {
        // nothing here

    } else if (auto *ast = dynamic_cast<Array *>(ast_)) {
        out << ast;

    } else if (auto *ast = dynamic_cast<ArrayComprehension *>(ast_)) {
        // ArrayComprehension is desugared and doesn't exist in core AST

    } else if (auto *ast = dynamic_cast<Assert *>(ast_)) {
    } else if (auto *ast = dynamic_cast<Binary *>(ast_)) {
        out << ast;

    } else if (auto *ast = dynamic_cast<const BuiltinFunction *>(ast_)) {
        out << ast;

    } else if (auto *ast = dynamic_cast<Conditional *>(ast_)) {
        out << ast;

    } else if (auto *ast = dynamic_cast<Dollar *>(ast_)) {
        // $ is desugared and is not a keyword in core AST
    } else if (auto *ast = dynamic_cast<Error *>(ast_)) {
        out << ast;

    } else if (auto *ast = dynamic_cast<Function *>(ast_)) {
        out << ast;
    } else if (auto *ast = dynamic_cast<Import *>(ast_)) {
        out << ast;

    } else if (auto *ast = dynamic_cast<Importstr *>(ast_)) {
        // not implemented

    } else if (auto *ast = dynamic_cast<InSuper *>(ast_)) {
        // not implemented

    } else if (auto *ast = dynamic_cast<Index *>(ast_)) {
        // slices are desugared, how to deal with other cases?
    } else if (auto *ast = dynamic_cast<Local *>(ast_)) {
        // object-level local is desugared;
        // the definition of Local is not completely clear for me: body vs binds?
        out << ast;

    } else if (auto *ast = dynamic_cast<const LiteralBoolean *>(ast_)) {
        out << ast;

    } else if (dynamic_cast<const LiteralNumber *>(ast_)) {
        out << ast;

    } else if (auto *ast = dynamic_cast<LiteralString *>(ast_)) {
        out << ast;

    } else if (dynamic_cast<const LiteralNull *>(ast_)) {
        out << "ast.Null";

    } else if (auto *ast = dynamic_cast<DesugaredObject *>(ast_)) {
        // object after desugaring that doesn't contain object-level locals, assert
        out << ast;

    } else if (dynamic_cast<Object *>(ast_)) {
        // desugared to DesugaredObject
    } else if (dynamic_cast<ObjectComprehension *>(ast_)) {
        // is desugared to simple ObjectComprehension
    } else if (auto *ast = dynamic_cast<ObjectComprehensionSimple *>(ast_)) {
        // not implemented yet
    } else if (dynamic_cast<Parens *>(ast_)) {
        // is desugared
    } else if (dynamic_cast<const Self *>(ast_)) {
        // Nothing to do.
    } else if (auto *ast = dynamic_cast<SuperIndex *>(ast_)) {
        // not implemented, but after desugaring id field will be set to nullptr
    } else if (auto *ast = dynamic_cast<Unary *>(ast_)) {
        out << ast;
    } else if (auto *ast = dynamic_cast<const Var *>(ast_)) {
        out << ast;
    } else {
        out << "INTERNAL ERROR: Unknown AST: " << std::endl;
        std::abort();
    }
    out << std::endl;
    return out;
}

int main(int argc, char const *argv[])
{
    const char *str = "{a: if true then 1 else 0,}"; // don't understand why AST for consitional is ast.Local ...

    Allocator *alloc = new Allocator();
    Tokens tokens = jsonnet_lex("add_op", str);
    
    // print lexer tokens
    std::cout << "Tokens:\n";
    for (auto t : tokens) {
      std::cout << t << ", ";
    }
    std::cout << std::endl;

    AST *ast = jsonnet_parse(alloc, tokens);
    // Allocator *alloc1 = new Allocator();
    jsonnet_desugar(alloc, ast, nullptr);

    // print AST
    std::cout << "AST nodes:\n";
    std::cout << ast;
    std::cout << std::endl;

    return 0;
}
