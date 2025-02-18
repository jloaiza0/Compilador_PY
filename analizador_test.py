import unittest
from analizador import build_lexer

class TestAnalizadorLexico(unittest.TestCase):

    def setUp(self):
        #Crear una instancia del analizador antes de cada prueba
        self.lexer = build_lexer()

    def test_operadores_matematicos(self):
        # Prueba para todos los operadores matemáticos
        self.lexer.input("3 + 4 * 2 - 1 / 5")
        tokens = [tok for tok in self.lexer]
        tipos_esperados = ['NUMBER', 'PLUS', 'NUMBER', 'TIMES', 'NUMBER', 'MINUS', 'NUMBER', 'DIVIDE', 'NUMBER']
        valores_esperados = [3, '+', 4, '*', 2, '-', 1, '/', 5]

        self.assertEqual([t.type for t in tokens], tipos_esperados)
        self.assertEqual([str(t.value) for t in tokens], [str(v) for v in valores_esperados])

    def test_operadores_comparacion(self):
        # Prueba para todos los operadores de comparación
        self.lexer.input("== != > < >= <=")
        tokens = [tok for tok in self.lexer]
        tipos_esperados = ['EQ', 'NEQ', 'GT', 'LT', 'GTE', 'LTE']
        valores_esperados = ['==', '!=', '>', '<', '>=', '<=']

        self.assertEqual([t.type for t in tokens], tipos_esperados)
        self.assertEqual([str(t.value) for t in tokens], valores_esperados)

    def test_operadores_logicos(self):
        # Prueba para operadores lógicos
        self.lexer.input("and or not")
        tokens = [tok for tok in self.lexer]
        tipos_esperados = ['AND', 'OR', 'NOT']
        valores_esperados = ['and', 'or', 'not']

        self.assertEqual([t.type for t in tokens], tipos_esperados)
        self.assertEqual([str(t.value) for t in tokens], valores_esperados)

    def test_puntuacion_y_simbolos(self):
        # Prueba para puntuación y símbolos
        self.lexer.input("() , ; : . { } [ ]")
        tokens = [tok for tok in self.lexer]
        tipos_esperados = ['LPAR', 'RPAR', 'COMMA', 'SEMICOLON', 'COLON', 'DOT', 'LBRACE', 'RBRACE', 'LSQUARE', 'RSQUARE']
        valores_esperados = ['(', ')', ',', ';', ':', '.', '{', '}', '[', ']']

        self.assertEqual([t.type for t in tokens], tipos_esperados)
        self.assertEqual([str(t.value) for t in tokens], valores_esperados)

    def test_palabras_reservadas(self):
        # Prueba para palabras reservadas
        self.lexer.input("const var print if else while for function return true false null break import from")
        tokens = [tok for tok in self.lexer]
        tipos_esperados = [
            'CONSTANT', 'VAR', 'PRINT', 'IF', 'ELSE', 'WHILE', 'FOR', 'FUNCTION', 'RETURN', 'TRUE', 'FALSE', 'NULL', 'BREAK', 'IMPORT', 'FROM'
        ]
        valores_esperados = ['const', 'var', 'print', 'if', 'else', 'while', 'for', 'function', 'return', 'true', 'false', 'null', 'break', 'import', 'from']

        self.assertEqual([t.type for t in tokens], tipos_esperados)
        self.assertEqual([str(t.value) for t in tokens], valores_esperados)

    def test_cadenas(self):
        # Prueba para cadenas
        self.lexer.input('"Hola, mundo!" \'Texto de prueba\'')
        tokens = [tok for tok in self.lexer]
        tipos_esperados = ['STRING', 'STRING']
        valores_esperados = ['Hola, mundo!', 'Texto de prueba']

        self.assertEqual([t.type for t in tokens], tipos_esperados)
        self.assertEqual([str(t.value) for t in tokens], valores_esperados)

    def test_identificadores(self):
        # Prueba para identificadores
        self.lexer.input("abc var")
        tokens = [tok for tok in self.lexer]
        tipos_esperados = ['ID', 'VAR']
        valores_esperados = ['abc', 'var']

        self.assertEqual([t.type for t in tokens], tipos_esperados)
        self.assertEqual([str(t.value) for t in tokens], valores_esperados)

    def test_string(self):
        # Prueba para el token STRING
        self.lexer.input('"Hola Mundo!"')
        tokens = [tok for tok in self.lexer]
        tipos_esperados = ['STRING']
        valores_esperados = ['Hola Mundo!']

        self.assertEqual([t.type for t in tokens], tipos_esperados)
        self.assertEqual([str(t.value) for t in tokens], [str(v) for v in valores_esperados])

    def test_float(self):
        # Prueba para el token FLOAT
        self.lexer.input('3.14')
        tokens = [tok for tok in self.lexer]
        tipos_esperados = ['FLOAT']  # El token de flotante se debe clasificar como 'NUMBER'
        valores_esperados = [3.14]

        self.assertEqual([t.type for t in tokens], tipos_esperados)
        self.assertEqual([str(t.value) for t in tokens], [str(v) for v in valores_esperados])

    def test_todos_los_tipos(self):
        # Prueba final que cubre todos los tipos de tokens
        self.lexer.input("const x = 10.2 + 20 * 30 and if (x > 10) print 'Hola, Mundo!'")
        tokens = [tok for tok in self.lexer]
        tipos_esperados = [
            'CONSTANT', 'ID', 'ASSIGN', 'FLOAT', 'PLUS', 'NUMBER', 'TIMES', 'NUMBER', 'AND', 'IF', 'LPAR', 'ID', 'GT', 'NUMBER', 'RPAR', 'PRINT', 'STRING'
        ]
        valores_esperados = ['const', 'x', '=', 10.2, '+', 20, '*', 30, 'and', 'if', '(', 'x', '>', 10, ')', 'print', 'Hola, Mundo!']

        self.assertEqual([t.type for t in tokens], tipos_esperados)
        self.assertEqual([str(t.value) for t in tokens], [str(v) for v in valores_esperados])

if __name__ == "__main__":
    unittest.main()

