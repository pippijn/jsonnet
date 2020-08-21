
// Sample output of print_ast function
// print_ast(desugar(parse(allocator, lex('if 2 == 3 then "hello" else 55'))))
// =>
// ast.Conditional(
// ast.BinaryOp("==", ast.Integer("2"), ast.Integer("3")),
// …,

#include <iostream>
#include <ostream>
#include <fstream>
#include <string>

#include "./ast.h"
#include "desugarer.h"
#include "lexer.h"
#include "parser.h"

const bool test_mode = true;

std::ostream &operator<<(std::ostream &out, const AST *ast_);

std::ostream &operator<<(std::ostream &out, const LiteralNumber *ast)
{
    out << "ast.LiteralNumber(";
    out << ast->value;
    out << ")";
    return out;
}
// Overloading '<<' for AST and its nodes
std::ostream &operator<<(std::ostream &out, const Apply *ast)
{
    out << "ast.Apply(";
    out << ast->target;
    for (ArgParam arg : ast->args) {
        out << ", ";
        out << arg.expr;
    }
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const Array *ast)
{
    out << "ast.Array([";
    for (auto &el : ast->elements) {
        out << el.expr;
        out << ",";
    }
    out << "])";
    return out;
}

std::ostream &operator<<(std::ostream &out, const Binary *ast)
{
    out << "ast.BinaryOp(";
    out << "\"" << bop_string(ast->op) << "\"";  // maybe overload for each binary op.
    out << ",";
    out << ast->left;
    out << ",";
    out << ast->right;
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const BuiltinFunction *ast)
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

std::ostream &operator<<(std::ostream &out, const Function *ast)
{
    out << "ast.Function(";
    for (auto arg_param : ast->params) {
        out << arg_param.id;
        out << " ";
        out << arg_param.expr;  // after desugaring this part is unrecognized AST
        out << ",";
    }
    out << ")";
    out << ast->body;
    return out;
}

std::ostream &operator<<(std::ostream &out, const Conditional *ast)
{
    out << "ast.Conditional(";
    out << ast->cond;
    out << ", ";
    out << ast->branchTrue;
    out << ", ";
    out << ast->branchFalse;
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const Error *ast)
{
    out << "ast.Error(";
    out << ast->expr;
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const Import *ast)
{
    out << "ast.Import(";
    out << ast->file;
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const Local *ast)
{
    // it should be changed most probably
    out << "ast.Local(";
    out << ast->body;
    for (auto bind : ast->binds) {
        out << ',';
        out << bind.var;
        out << ": ";
        out << bind.body;
    }
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const LiteralBoolean *ast)
{
    out << "ast.LiteralBoolean(";
    out << ast->value;
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const LiteralString *ast)
{
    out << "ast.LiteralString(\"";
    // TODO: find a better way to print UString
    for (const auto &c : ast->value)
        out << static_cast<char>(c); // check what if we have multi-line string
    out << "\")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const DesugaredObject *ast)
{
    // - maybe it is better to overload operator << for Field structure
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
    out << "\"" << uop_string(ast->op) << "\"";
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
std::ostream &operator<<(std::ostream &out, const AST *ast_)
{
    if (auto *ast = dynamic_cast<const Apply *>(ast_)) {
        out << ast;

    } else if (auto *ast = dynamic_cast<const ApplyBrace *>(ast_)) {
        // nothing here

    } else if (auto *ast = dynamic_cast<const Array *>(ast_)) {
        out << ast;

    } else if (auto *ast = dynamic_cast<const ArrayComprehension *>(ast_)) {
        // ArrayComprehension is desugared and doesn't exist in core AST

    } else if (auto *ast = dynamic_cast<const Assert *>(ast_)) {
    } else if (auto *ast = dynamic_cast<const Binary *>(ast_)) {
        out << ast;

    } else if (auto *ast = dynamic_cast<const BuiltinFunction *>(ast_)) {
        out << ast;

    } else if (auto *ast = dynamic_cast<const Conditional *>(ast_)) {
        out << ast;

    } else if (auto *ast = dynamic_cast<const Dollar *>(ast_)) {
        // $ is desugared and is not a keyword in core AST
    } else if (auto *ast = dynamic_cast<const Error *>(ast_)) {
        out << ast;

    } else if (auto *ast = dynamic_cast<const Function *>(ast_)) {
        out << ast;

    } else if (auto *ast = dynamic_cast<const Import *>(ast_)) {
        out << ast;

    } else if (auto *ast = dynamic_cast<const Importstr *>(ast_)) {
        // not implemented

    } else if (auto *ast = dynamic_cast<const InSuper *>(ast_)) {
        // not implemented

    } else if (auto *ast = dynamic_cast<const Index *>(ast_)) {
        // slices are desugared, how to deal with other cases?
    } else if (auto *ast = dynamic_cast<const Local *>(ast_)) {
        // object-level local is desugared;
        // the definition of Local is not completely clear for me: body vs binds?
        out << ast;

    } else if (auto *ast = dynamic_cast<const LiteralBoolean *>(ast_)) {
        out << ast;

    } else if (auto *ast = dynamic_cast<const LiteralNumber *>(ast_)) {
        out << ast;

    } else if (auto *ast = dynamic_cast<const LiteralString *>(ast_)) {
        out << ast;

    } else if (dynamic_cast<const LiteralNull *>(ast_)) {
        out << "ast.Null";

    } else if (auto *ast = dynamic_cast<const DesugaredObject *>(ast_)) {
        // object after desugaring that doesn't contain object-level locals, assert
        out << ast;

    } else if (dynamic_cast<const Object *>(ast_)) {
        // desugared to DesugaredObject
    } else if (dynamic_cast<const ObjectComprehension *>(ast_)) {
        // is desugared to simple ObjectComprehension
    } else if (auto *ast = dynamic_cast<const ObjectComprehensionSimple *>(ast_)) {
        // not implemented yet
    } else if (dynamic_cast<const Parens *>(ast_)) {
        // is desugared
    } else if (dynamic_cast<const Self *>(ast_)) {
        // Nothing to do.
    } else if (auto *ast = dynamic_cast<const SuperIndex *>(ast_)) {
        // not implemented, but after desugaring id field will be set to nullptr
    } else if (auto *ast = dynamic_cast<const Unary *>(ast_)) {
        out << ast;

    } else if (auto *ast = dynamic_cast<const Var *>(ast_)) {
        out << ast;

    } else {
        out << "INTERNAL ERROR: Unknown AST: " << std::endl;
        std::abort();
    }
    return out;
}

void print_tokens(Tokens tokens)
{
    std::cout << "Tokens:\n";
    for (auto t : tokens) {
        std::cout << t << ", ";
    }
    std::cout << std::endl;
}

void write_to_file(std::string filename, AST *ast)
{
    std::ofstream myfile;
    myfile.open(filename);
    myfile << ast;
    myfile.close();
}

int main(int argc, char const *argv[])
{
    const char *str = "if 2 == 6 then \"magic\" else 0";

    Allocator *alloc = new Allocator();
    Tokens tokens = jsonnet_lex("file", str);

    AST *ast = jsonnet_parse(alloc, tokens);

    // doesn't work properly with desugaring
    // jsonnet_desugar(alloc, ast, nullptr);

    // print AST
    if (test_mode) {
      std::cout << "AST nodes:\n";
      std::cout << ast;
      std::cout << std::endl;
    }
    // TODO: pass the name of file as commmand line arg
    write_to_file("core/type_inference/ast_string.txt", ast);

    return 0;
}
