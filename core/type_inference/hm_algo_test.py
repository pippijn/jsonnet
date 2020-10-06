import unittest
import hm_algo
from lambda_types import (TypeVariable, Function, TypeOperator,
    TypeRowOperator, Number, Bool, String)
from lambda_ast import (LiteralBoolean, LiteralNumber, LiteralString,
    Let, Letrec, LetrecAnd, Inherit, Apply, Identifier, Location
)

EL = Location('0:0', '0:0') # empty location


class TestTypeInference(unittest.TestCase):

    def test_null(self):
        var1 = TypeVariable()
        record_type = TypeRowOperator({'x': var1})
        
        env = {
            "null": TypeVariable(),
            "record": Function(var1, record_type),
        }
        
        example = LetrecAnd(
            {
                "x": (Identifier("null"), EL)
            },
            Apply(
                Identifier("record"),
                Identifier("x")
            ),
        )
        
        inferred_type = "{x: a}"
        self.assertEqual(hm_algo.try_exp(env, example), inferred_type)

    def test_mutual_rec(self):
        var1 = TypeVariable()
        var2 = TypeVariable()
        record_type = TypeRowOperator({'x': var1, 'y': var2})
        
        env = {
            "record": Function(var1, Function(var2, record_type)),
        }
        
        example = LetrecAnd(
            {
                "x": (Identifier("y"), EL),
                "y": (Identifier("x"), EL),
            },
            Apply(
                Apply(
                    Identifier("record"),
                    Identifier("x")
                ),
                Identifier("y")
            )
        )
        
        inferred_type = "{x: a, y: a}"
        self.assertEqual(hm_algo.try_exp(env, example), inferred_type)


if __name__ == '__main__':
    unittest.main()

