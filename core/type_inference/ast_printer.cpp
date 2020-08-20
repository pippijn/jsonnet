
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

std::ostream &operator<<(std::ostream &out, Conditional *ast) {
  out << "ast.Conditional(";
  out << ast->cond;
  out << ",";
  out << ast->branchTrue;
  out << ",";
  out << ast->branchFalse;
  out << ")";
  return out;
}

std::ostream &operator<<(std::ostream &out, Apply *ast) {
  out << "ast.Apply(";
  out << ast->target;
  for (ArgParam &arg : ast->args) {
    out << ", ";
    out << arg.expr;
  }
  out << ")";
  return out;
}

std::ostream &operator<<(std::ostream &out, Array *ast) {
  out << "ast.Array(";
  for (auto &el : ast->elements) {
    out << el.expr;
    out << ",";
  }
  out << ")";
  return out;
}

std::ostream &operator<<(std::ostream &out, Binary *ast) {
  out << "ast.BinaryOp(";
  out << bop_string(ast->op);
  out << ",";
  out << ast->left;
  out << ",";
  out << ast->right;
  out << ")";
  return out;
}

std::ostream &operator<<(std::ostream &out, AST *ast_) {
  if (auto *ast = dynamic_cast<Apply *>(ast_)) {
    out << ast;

  } else if (auto *ast = dynamic_cast<ApplyBrace *>(ast_)) {
    // nothing here
  } else if (auto *ast = dynamic_cast<Array *>(ast_)) {
    out << ast;

  } else if (auto *ast = dynamic_cast<ArrayComprehension *>(ast_)) {
    // ArrayComprehension is desugared and doesn't exist in core AST

  } else if (auto *ast = dynamic_cast<Assert *>(ast_)) {
    //   } else if (auto *ast = dynamic_cast<Binary *>(ast_)) {
    //     out << ast;

    //   } else if (dynamic_cast<const BuiltinFunction *>(ast_)) {
    //     // Nothing to do.

    //   } else if (auto *ast = dynamic_cast<Conditional *>(ast_)) {
    //       out << ast;

    //   } else if (auto *ast = dynamic_cast<Dollar *>(ast_)) {
    //     if (obj_level == 0) {
    //       throw StaticError(ast->location, "No top-level object found.");
    //     }
    //     ast_ = var(id(U"$"));

    //   } else if (auto *ast = dynamic_cast<Error *>(ast_)) {
    //     desugar(ast->expr, obj_level);

    //   } else if (auto *ast = dynamic_cast<Function *>(ast_)) {
    //     desugar(ast->body, obj_level);
    //     desugarParams(ast->params, obj_level);

    //   } else if (auto *ast = dynamic_cast<Import *>(ast_)) {
    //     // TODO(dcunnin): Abstract this into a template function if it
    //     becomes more
    //     // common.
    //     AST *file = ast->file;
    //     desugar(file, obj_level);
    //     ast->file = dynamic_cast<LiteralString *>(file);

    //   } else if (auto *ast = dynamic_cast<Importstr *>(ast_)) {
    //     // TODO(dcunnin): Abstract this into a template function if it
    //     becomes more
    //     // common.
    //     AST *file = ast->file;
    //     desugar(file, obj_level);
    //     ast->file = dynamic_cast<LiteralString *>(file);

    //   } else if (auto *ast = dynamic_cast<InSuper *>(ast_)) {
    //     desugar(ast->element, obj_level);

    //   } else if (auto *ast = dynamic_cast<Index *>(ast_)) {
    //     desugar(ast->target, obj_level);
    //     if (ast->isSlice) {
    //       if (ast->index == nullptr) ast->index = null();
    //       desugar(ast->index, obj_level);

    //       if (ast->end == nullptr) ast->end = null();
    //       desugar(ast->end, obj_level);

    //       if (ast->step == nullptr) ast->step = null();
    //       desugar(ast->step, obj_level);

    //       ast_ = make<Apply>(ast->location, EF,
    //                          make<Index>(E, EF, std(), EF, false,
    //                          str(U"slice"), EF,
    //                                      nullptr, EF, nullptr, EF),
    //                          EF,
    //                          ArgParams{
    //                              {ast->target, EF},
    //                              {ast->index, EF},
    //                              {ast->end, EF},
    //                              {ast->step, EF},
    //                          },
    //                          false,  // trailing comma
    //                          EF, EF,
    //                          false  // tailstrict
    //       );
    //     } else {
    //       if (ast->id != nullptr) {
    //         assert(ast->index == nullptr);
    //         ast->index = str(ast->id->name);
    //         ast->id = nullptr;
    //       }
    //       desugar(ast->index, obj_level);
    //     }

    //   } else if (auto *ast = dynamic_cast<Local *>(ast_)) {
    //     for (auto &bind : ast->binds) desugar(bind.body, obj_level);
    //     desugar(ast->body, obj_level);

    //     for (auto &bind : ast->binds) {
    //       if (bind.functionSugar) {
    //         desugarParams(bind.params, obj_level);
    //         bind.body = make<Function>(ast->location, ast->openFodder,
    //                                    bind.parenLeftFodder, bind.params,
    //                                    false, bind.parenRightFodder,
    //                                    bind.body);
    //         bind.functionSugar = false;
    //         bind.params.clear();
    //       }
    //     }

  } else if (auto *ast = dynamic_cast<const LiteralBoolean *>(ast_)) {
    out << ast->value;

  } else if (dynamic_cast<const LiteralNumber *>(ast_)) {
    out << ast->value;

  } else if (auto *ast = dynamic_cast<LiteralString *>(ast_)) {
    // if ((ast->tokenKind != LiteralString::BLOCK) &&
    //     (ast->tokenKind != LiteralString::VERBATIM_DOUBLE) &&
    //     (ast->tokenKind != LiteralString::VERBATIM_SINGLE)) {
    //   ast->value = jsonnet_string_unescape(ast->location, ast->value);
    // }
    // ast->tokenKind = LiteralString::DOUBLE;
    // ast->blockIndent.clear();

  } else if (auto *ast = dynamic_cast<const LiteralNull *>(ast_)) {
    out << "ast.Null";

    //   } else if (auto *ast = dynamic_cast<DesugaredObject *>(ast_)) {
    //     for (auto &field : ast->fields) {
    //       desugar(field.name, obj_level);
    //       desugar(field.body, obj_level + 1);
    //     }
    //     for (AST *assert : ast->asserts) {
    //       desugar(assert, obj_level + 1);
    //     }

    //   } else if (auto *ast = dynamic_cast<Object *>(ast_)) {
    //     ast_ = makeObject(ast, obj_level);

    //   } else if (auto *ast = dynamic_cast<ObjectComprehension *>(ast_)) {
    //     ast_ = makeObjectComprehension(ast, obj_level);

    //   } else if (auto *ast = dynamic_cast<ObjectComprehensionSimple *>(ast_))
    //   {
    //     desugar(ast->field, obj_level);
    //     desugar(ast->value, obj_level + 1);
    //     desugar(ast->array, obj_level);

    //   } else if (auto *ast = dynamic_cast<Parens *>(ast_)) {
    //     // Strip parens.
    //     desugar(ast->expr, obj_level);
    //     ast_ = ast->expr;

    //   } else if (dynamic_cast<const Self *>(ast_)) {
    //     // Nothing to do.

    //   } else if (auto *ast = dynamic_cast<SuperIndex *>(ast_)) {
    //     if (ast->id != nullptr) {
    //       assert(ast->index == nullptr);
    //       ast->index = str(ast->id->name);
    //       ast->id = nullptr;
    //     }
    //     desugar(ast->index, obj_level);

  } else if (auto *ast = dynamic_cast<Unary *>(ast_)) {
    // desugar(ast->expr, obj_level);

  } else if (auto *ast = dynamic_cast<const Var *>(ast_)) {
    out << "Var(";
    out << ast->id;
    out << ")";

  } else {
    out << "INTERNAL ERROR: Unknown AST: " << std::endl;
    std::abort();
  }
  return out;
}

int main(int argc, char const *argv[]) {
  const char *str = "2+3";

  Allocator *alloc = new Allocator();
  Tokens tokens = jsonnet_lex("add_op", str);
  AST *ast = jsonnet_parse(alloc, tokens);

  Allocator *alloc1 = new Allocator();
  jsonnet_desugar(alloc1, ast, nullptr);
  std::cout << ast;
  return 0;
}
