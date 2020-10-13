# Type inference for Jsonnet

This is a prototype of the static type inference framework for Jsonnet. 

## Running the program

Make sure that your working directory is the root of jsonnet repository (jsonnet folder).

Then, run the following command: 

```bash
python3 core/type_inference/infer.py --file_path core/type_inference/examples/ex1.jsonnet --rebuild
```

The flag '--rebuild' causes rebuilding of print_ast.cpp. If you don't make any changes in print_ast.cpp, run the program without '--rebuild'.

## Examples

Some examples with expected types or type errors can be found in `/jsonnet/core/type_inference/type_inference_test.py`