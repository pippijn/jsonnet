#include <fstream>
#include <iostream>
#include <ostream>
#include <string>

#include "./ast.h"
#include "desugarer.h"
#include "lexer.h"
#include "parser.h"


std::ostream &operator<<(std::ostream &out, const LocationRange *lr);

std::ostream &operator<<(std::ostream &out, const AST *ast);

std::ostream &operator<<(std::ostream &out, const ArgParam arg_param)
{
    out << "ast.ArgParam(";
    if (arg_param.id) {
        out << "id=\"";
        out << arg_param.id;  
        out << "\", ";
    }
    if (arg_param.expr) {
        out << "expr=";
        out << arg_param.expr; 
    }
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const Local::Bind& bind)
{
    UString std = decode_utf8("std");
    if (bind.var->name == std) {
        out << "ast.Bind(\"std\", ast.LiteralNull())";
        return out;
    }
    out << "ast.Bind(";
    out << "var=\"";
    out << bind.var;
    out << "\", ";
    out << "body=";
    out << bind.body;
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const Apply *ast)
{
    out << "ast.Apply(";
    out << &ast->location;
    out << ",";
    out << ast->target;
    for (ArgParam arg : ast->args) {
        out << ", ";
        out << arg;
    }
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const Array *ast)
{
    out << &ast->location;
    out << ",";
    out << "ast.Array([";
    for (const auto &el : ast->elements) {
        out << el.expr;
        out << ",";
    }
    out << "])";
    return out;
}

std::ostream &operator<<(std::ostream &out, const Binary *ast)
{
    out << "ast.BinaryOp(";
    out << &ast->location;
    out << ",";
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
    out << "ast.BuiltinFunction(";
    out << &ast->location;
    out << ",";
    out << ast->name;
    for (const auto &param : ast->params) {
        out << ",";
        out << "\"";
        out << param;
        out << "\"";
    }
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const Function *ast)
{
    out << "ast.Function(";
    out << &ast->location;
    out << ",";
    out << ast->body;
    for (const auto &arg_param : ast->params) {
        out << ",";
        out << arg_param;
    }
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const Conditional *ast)
{
    out << "ast.Conditional(";
    out << &ast->location;
    out << ",";
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
    out << &ast->location;
    out << ",";
    out << ast->expr;
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const Local *ast)
{
    out << "ast.Local(";
    out << &ast->location;
    out << ",";
    out << ast->body;
    for (const Local::Bind &bind : ast->binds) {
        out << ",";
        out << bind;
    }
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const LiteralNumber *ast)
{
    out << "ast.LiteralNumber(";
    out << &ast->location;
    out << ",";
    out << ast->value;
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const LiteralBoolean *ast)
{
    out << "ast.LiteralBoolean(";
    out << &ast->location;
    out << ",";
    out << ast->value;
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const LiteralNull *ast)
{
    out << "ast.LiteralNull(";
    out << &ast->location;
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const LiteralString *ast)
{
    out << "ast.LiteralString(";
    out << &ast->location;
    out << ",";
    out << "\"";
    for (const auto &c : ast->value) {
        char ch = static_cast<char>(c);
        if (ch == '\n') {
            out << R"(\n)";
        } else {
            out << ch;
        }
    }
    out << "\")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const DesugaredObject *ast)
{
    // - maybe it is better to overload operator << for Field structure
    // - maybe we will need hide field to keep info about inheritance
    out << "ast.Object(";
    out << &ast->location;
    out << ",";
    out << "{";
    for (auto field : ast->fields) {
        out << field.name;
        out << ": ";
        out << field.body;
        out << ",";
    }
    out << "})";
    return out;
}

std::ostream &operator<<(std::ostream &out, const Unary *ast)
{
    out << "ast.Unary(";
    out << &ast->location;
    out << ",";
    out << "\"" << uop_string(ast->op) << "\"";
    out << ",";
    out << ast->expr;
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const Var *ast)
{
    out << "ast.Var(";
    out << &ast->location;
    out << ",";
    out << "\"";
    out << ast->id;
    out << "\")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const Index *ast)
{
    out << "ast.Index(";
    out << &ast->location;
    out << ", ";
    out << ast->target;
    out << ", ";
    out << ast->index;
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const Self *ast)
{
    out << "ast.Self(";
    out << &ast->location;
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const SuperIndex *ast)
{
    out << "ast.SuperIndex(";
    out << &ast->location;
    out << ",";
    out << ast->index;
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const InSuper *ast)
{
    out << "ast.InSuper(";
    out << &ast->location;
    out << ",";
    out << ast->element;
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const LocationRange *lr)
{
    out << "ast.Location(\"";
    out << lr->begin;
    out << ",";
    out << lr->end;
    out << "\")";
    return out;
}

// keep empty cases for desugared nodes or just delete them ?
std::ostream &operator<<(std::ostream &out, const AST *ast_)
{
    if (auto *ast = dynamic_cast<const Apply *>(ast_)) {
        out << ast;

    } else if (dynamic_cast<const ApplyBrace *>(ast_)) {
        // nothing here

    } else if (auto *ast = dynamic_cast<const Array *>(ast_)) {
        out << ast;

    } else if (dynamic_cast<const ArrayComprehension *>(ast_)) {
        // ArrayComprehension is desugared and doesn't exist in core AST

    } else if (dynamic_cast<const Assert *>(ast_)) {
        // object- and extression-level asserts are removed --> maybe nothing to do here

    } else if (auto *ast = dynamic_cast<const Binary *>(ast_)) {
        out << ast;

    } else if (auto *ast = dynamic_cast<const BuiltinFunction *>(ast_)) {
        out << ast;

    } else if (auto *ast = dynamic_cast<const Conditional *>(ast_)) {
        out << ast;

    } else if (dynamic_cast<const Dollar *>(ast_)) {
        // $ is desugared and is not a keyword in core AST

    } else if (auto *ast = dynamic_cast<const Error *>(ast_)) {
        out << ast;

    } else if (auto *ast = dynamic_cast<const Function *>(ast_)) {
        out << ast;

    } else if (dynamic_cast<const Import *>(ast_)) {
        // desugared: substituted with file content or error

    } else if (dynamic_cast<const Importstr *>(ast_)) {
        // desugared: substituted with file content or error

    } else if (auto *ast = dynamic_cast<const InSuper *>(ast_)) {
        // example: {base: {...}, a: base + {is_field_in_super: "some_field" in super}} -->
        //          is_field_in_super will be true or false
        // it doesn't matter for type inference because type of is_field_in_super is always bool
        out << ast;

    } else if (auto *ast = dynamic_cast<const Index *>(ast_)) {
        out << ast;

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

    } else if (auto *ast = dynamic_cast<const LiteralNull *>(ast_)) {
        out << ast;

    } else if (auto *ast = dynamic_cast<const DesugaredObject *>(ast_)) {
        // object after desugaring that doesn't contain object-level locals, assert
        out << ast;

    } else if (dynamic_cast<const Object *>(ast_)) {
        // desugared to DesugaredObject

    } else if (dynamic_cast<const ObjectComprehension *>(ast_)) {
        // desugared to simple ObjectComprehension

    } else if (dynamic_cast<const ObjectComprehensionSimple *>(ast_)) {
        // not implemented yet

    } else if (dynamic_cast<const Parens *>(ast_)) {
        // desugared

    } else if (auto *ast = dynamic_cast<const Self *>(ast_)) {
        out << ast;

    } else if (auto *ast = dynamic_cast<const SuperIndex *>(ast_)) {
        out << ast;

    } else if (auto *ast = dynamic_cast<const Unary *>(ast_)) {
        out << ast;

    } else if (auto *ast = dynamic_cast<const Var *>(ast_)) {
        out << ast;

    } else {
        // do we need abort here?
        std::cerr << "INTERNAL ERROR: Unknown AST: " << std::endl;
    }
    return out;
}

int main(int argc, char const *argv[])
{
    const char *input;
    if (argc < 2) {
        std::cerr << "No jsonnet example to execute " << std::endl;
    } else if (argc > 2) {
        std::cerr << "Too many cmd arguments " << std::endl;
    } else {
        input = argv[1];
    }

    Allocator *alloc = new Allocator();
    Tokens tokens = jsonnet_lex("", input);
    AST *ast = jsonnet_parse(alloc, tokens);
    jsonnet_desugar(alloc, ast, nullptr);
    
    std::cout << ast;
    return 0;
}
