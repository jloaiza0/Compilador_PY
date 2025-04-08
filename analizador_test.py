import unittest
from lexer import tokenize, Token

class TestAnalizadorLexico(unittest.TestCase):

    def test_operadores_matematicos(self):
        code = "3 + 4 * 2 - 1 / 5"
        tokens = tokenize(code)
        expected = [
            Token("NUMBER", "3", 1),
            Token("PLUS", "+", 1),
            Token("NUMBER", "4", 1),
            Token("MULTIPLY", "*", 1),
            Token("NUMBER", "2", 1),
            Token("MINUS", "-", 1),
            Token("NUMBER", "1", 1),
            Token("DIVIDE", "/", 1),
            Token("NUMBER", "5", 1)
        ]
        self.assertEqual(tokens, expected)

    def test_operadores_comparacion(self):
        code = "== != > < >= <="
        tokens = tokenize(code)
        expected = [
            Token("EQ", "==", 1),
            Token("NEQ", "!=", 1),
            Token("GT", ">", 1),
            Token("LT", "<", 1),
            Token("GTE", ">=", 1),
            Token("LTE", "<=", 1)
        ]
        self.assertEqual(tokens, expected)

    def test_operadores_logicos(self):
        code = "and or not"
        tokens = tokenize(code)
        expected = [
            Token("AND", "and", 1),
            Token("OR", "or", 1),
            Token("NOT", "not", 1)
        ]
        self.assertEqual(tokens, expected)

    def test_puntuacion_y_simbolos(self):
        code = "() , ; : . { } [ ]"
        tokens = tokenize(code)
        expected = [
            Token("LPAR", "(", 1),
            Token("RPAR", ")", 1),
            Token("COMMA", ",", 1),
            Token("SEMICOLON", ";", 1),
            Token("COLON", ":", 1),
            Token("DOT", ".", 1),
            Token("LBRACE", "{", 1),
            Token("RBRACE", "}", 1),
            Token("LSQUARE", "[", 1),
            Token("RSQUARE", "]", 1)
        ]
        self.assertEqual(tokens, expected)

    def test_palabras_reservadas(self):
        code = "const var print if else while for function return true false null break import from"
        tokens = tokenize(code)
        expected = [
            Token("CONSTANT", "const", 1),
            Token("VAR", "var", 1),
            Token("PRINT", "print", 1),
            Token("IF", "if", 1),
            Token("ELSE", "else", 1),
            Token("WHILE", "while", 1),
            Token("FOR", "for", 1),
            Token("FUNCTION", "function", 1),
            Token("RETURN", "return", 1),
            Token("TRUE", "true", 1),
            Token("FALSE", "false", 1),
            Token("NULL", "null", 1),
            Token("BREAK", "break", 1),
            Token("IMPORT", "import", 1),
            Token("FROM", "from", 1)
        ]
        self.assertEqual(tokens, expected)


    def test_identificadores(self):
        code = "abc var"
        tokens = tokenize(code)
        expected = [
            Token("ID", "abc", 1),
            Token("VAR", "var", 1)
        ]
        self.assertEqual(tokens, expected)

    def test_float(self):
        code = '3.14'
        tokens = tokenize(code)
        expected = [
            Token("FLOAT", "3.14", 1)
        ]
        self.assertEqual(tokens, expected)


if __name__ == "__main__":
    unittest.main()

