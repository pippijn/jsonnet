# Type inference for Jsonnet

This is a prototype of the static type inference framework for Jsonnet. 

## Running the program

```bash
bazel build //core/type_inference:print_ast
python3 core/type_inference/infer.py --file_path core/type_inference/examples/ex1.jsonnet
```

The first command is not necessary if you don't change print_ast.cpp.

## Examples

Some examples with expected output of type inference (e.g. inferred types or type errors)
can be found in core/type_inference/type_inference_test.py