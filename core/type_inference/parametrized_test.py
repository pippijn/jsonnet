import pytest
import infer

""" Module with parametrized integration tests.
To run tests from jsonnet folder, execute the following: 
pytest core/type_inference/parametrized_test.py 
"""

testdata = [
    (1, 2, '{x: number, y: number, sum: number}'),
    ('"lala"', '"lalala"', '{x: string, y: string, sum: string}'),
    (1, '"la"', 'Type mismatch: string != number, line 1')
]


@pytest.mark.parametrize("arg1, arg2, expected_type", testdata)
def test_plus_bop(arg1, arg2, expected_type):
    programm = '{' + f'x: {arg1}, y: {arg2}, sum: self.x + self.y' + '}'
    assert infer.run(programm) == expected_type
