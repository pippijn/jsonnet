import unittest
import infer
import hm_algo


class TestTypeInference(unittest.TestCase):

    def test_number(self):
        self.assertEqual(infer.run("{x: 1}"), "{x: number}")

    def test_boolean(self):
        self.assertEqual(infer.run("{x: true}"), "{x: boolean}")

    def test_string(self):
        self.assertEqual(infer.run("{x: 'a'}"), "{x: string}")

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
        inferred_type = "{student: {name: string, age: number, best_friend: {age: number, has_friend: boolean, name: string}}}"
        self.assertEqual(infer.run(example), inferred_type)

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
        error_msg = "Type mismatch: string != number"
        self.assertEqual(infer.run(example), error_msg)

    def test_mutual_rec(self):
        example = """(
            {
                euro: self.dol,
                dol: self.euro,
            }
        )"""
        inferred_type = "{euro: a, dol: a}"
        self.assertEqual(infer.run(example), inferred_type)

    def test_local_field_rec(self):
        example = """(
            {
                local x = y, 
                local y = self.z, 
                z: 2,
                t: x 
            }
        )"""
        inferred_type = "{z: number, t: number}"
        self.assertEqual(infer.run(example), inferred_type)
    
    def test_binary_plus(self):
        example = """(
            {
                x: 1,
                y: 2,
                z: self.x + self.y
            }
        )"""
        inferred_type = "{x: number, y: number, z: number}"
        self.assertEqual(infer.run(example), inferred_type)
    
    def test_binary_plus_type_error(self):
        example = """(
            {
                x: 1,
                y: true,
                z: self.x + self.y
            }
        )"""
        error_msg = "Type mismatch: boolean != number"
        self.assertEqual(infer.run(example), error_msg)


if __name__ == '__main__':
    unittest.main()
