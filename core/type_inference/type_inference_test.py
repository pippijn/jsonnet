import unittest
import infer
import hm_algo


class TestTypeInference(unittest.TestCase):

    def test_number(self):
        self.assertEqual(infer.run("{a: 1}"), "{a: number}")

    def test_boolean(self):
        self.assertEqual(infer.run("{a: true}"), "{a: boolean}")

    def test_string(self):
        self.assertEqual(infer.run("{a: 'a'}"), "{a: string}")

    def test_inheritance(self):
        example = """(
            {
                local person = {
                    name: '',
                },
                student: person { 
                    name: 'Ali', 
                    age: 19,
                    best_friend: person {
                        age: 18,
                        has_friend: true
                    }  
                },
            }
        )"""
        infered_type = "{student: {name: string, age: number, best_friend: {name: string, age: number, has_friend: boolean}}}"
        self.assertEqual(infer.run(example), infered_type)

    def test_type_mismatch_error(self):
        example = """(
            {
                local person = {
                    name: 0,
                },
                student: person { 
                    name: 'Ali', 
                },
            }
        )"""
        error_msg = "Type mismatch: number != string"
        self.assertEqual(infer.run(example), error_msg)


if __name__ == '__main__':
    unittest.main()
