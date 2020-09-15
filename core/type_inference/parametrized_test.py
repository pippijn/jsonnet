import pytest
import infer

testdata = [
    (1, 2, '{x: number, y: number, sum: number}'),
    ('"lala"', '"lalala"', '{x: string, y: string, sum: string}'),
    (1, '"la"', 'Type mismatch: string != number')    
]


@pytest.mark.parametrize("arg1, arg2, expected_type", testdata)
def test_plus_bop(arg1, arg2, expected_type):
    programm = '{' + f'x: {arg1}, y: {arg2}, sum: self.x + self.y' + '}'
    assert infer.run(programm) == expected_type
