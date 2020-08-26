
// Sample output of print_ast function
// print_ast(desugar(parse(allocator, lex('if 2 == 3 then "hello" else 55'))))
// =>
// ast.Conditional(
// ast.BinaryOp("==", ast.Integer("2"), ast.Integer("3")),
// …,

#include <fstream>
#include <iostream>
#include <ostream>
#include <string>

#include "./ast.h"
#include "desugarer.h"
#include "lexer.h"
#include "parser.h"

const bool test_mode = false;

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
        if (arg_param.id) {
            out << arg_param.id;  // can be nullptr
        }
        out << " ";
        if (arg_param.expr) {
            out << arg_param.expr;  // can be nullptr
        }

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

std::ostream &operator<<(std::ostream &out, const Local *ast)
{
    out << "ast.Local(";
    out << ast->body;
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
    for (const auto &c : ast->value) {
        char ch = static_cast<char>(c);
        if (ch == '\n') {
            out << R"(\n)";
        } else {
            out << ch;
        }
    }
    // out << encode_utf8(ast->value); // if multiline output string is ok
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

std::ostream &operator<<(std::ostream &out, const Unary *ast)
{
    out << "ast.Unary(";
    out << "\"" << uop_string(ast->op) << "\"";
    out << ",";
    out << ast->expr;
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const Var *ast)
{
    out << "ast.Var(";
    out << ast->id;
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const Index *ast)
{
    out << "ast.Index(";
    out << ast->target;
    out << ", ";
    out << ast->index;
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const SuperIndex *ast)
{
    out << "ast.Index(";
    out << "ast.Super()";
    out << ", ";
    out << ast->index;
    out << ")";
    return out;
}

std::ostream &operator<<(std::ostream &out, const InSuper *ast)
{
    out << "ast.InSuper(";
    out << ast->element;
    out << ")";
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

    } else if (dynamic_cast<const LiteralNull *>(ast_)) {
        out << "ast.LiteralNull()";

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

    } else if (dynamic_cast<const Self *>(ast_)) {
        out << "ast.Self()";

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

const char *examples(int example)
{
    const char *res = "";
    switch (example) {
        case 1: res = "if 2 == 6 then \"magic\" else 0"; break;
        case 2: res = "[1, 2, 3]"; break;
        case 3:
            res = R""""({ 
                person1: {
                    name: "Alice",
                    welcome: "Hello " + self.name + "!",
                },
                person2: self.person1 { name: "Bob" },
            })"""";
            break;
        case 4: res = "{local b = [1, 2, 3, 4, 5], b: b[1::2], s: self.b}"; break;
        case 5:
            res = R""""(
                local person(name) = {
                    name: name,
                    welcome: 'Hello ' + name + '!',
                }; 
                {}
            )"""";
            break;
        case 6:  // example that produces Index node
            res = R""""({ 
                local obj = self,
                person1: {
                    name: "Alice",
                    kind: "child",
                },
                person2: { 
                    name: "Bob",
                    kind: obj.person1.kind 
                },
            })"""";
            break;
        case 7:  // example that produces SuperIndex and InSuper nodes
            res = R""""({ 
                local person = {
                    name: "Alice",
                    age: 20,
                    country: "Wonderland"
                },
                student: person + { 
                    name: super.name,
                    age: super["age"],  
                    university: "MIT", 
                    has_country: "country" in super, 
                },
            })"""";
            break;
        case 8:  // example of array comprehension
            res = R""""({ 
                local person = {
                    friends: ["Martin", "Lu"]
                },
                student: person + { 
                    university: "MIT", 
                    contacts: [i + "_" + self.university for i in super.friends]  
                },
            })"""";
            break;
        case 9: res = "{b: 3, assert b > 2 : 'b must be bigger than 2'}"; break;
        case 10:  // text block will be printed in AST as multiline text
            res = R""""(
                {
                    text: |||  
                        text
                        block
                    |||
                }
            )"""";
        default: break;
    }
    return res;
}

int main(int argc, char const *argv[])
{
    const char *input = examples(10);
    Allocator *alloc = new Allocator();

    Tokens tokens = jsonnet_lex("file", input);
    AST *ast = jsonnet_parse(alloc, tokens);
    jsonnet_desugar(alloc, ast, nullptr);

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
