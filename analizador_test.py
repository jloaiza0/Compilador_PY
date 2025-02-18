import unittest
from analizador import construir_analizador

class TestAnalizadorLexico(unittest.TestCase):

    def setUp(self):
        #Crear una instancia del analizador antes de cada prueba
        self.lexer = construir_analizador()

    def test_numeros(self):
        #Prueba si el analizador reconoce números correctamente
        self.lexer.input("123 456 789")
        tokens = [tok for tok in self.lexer]
        tipos_esperados = ['NUMBER', 'NUMBER', 'NUMBER']
        valores_esperados = [123, 456, 789]

        self.assertEqual([t.type for t in tokens], tipos_esperados)
        self.assertEqual([t.value for t in tokens], valores_esperados)

    def test_operadores(self):
        #Prueba si el analizador reconoce operadores correctamente
        self.lexer.input("+ - * /")
        tokens = [tok for tok in self.lexer]
        tipos_esperados = ['PLUS', 'MINUS', 'TIMES', 'DIVIDE']

        self.assertEqual([t.type for t in tokens], tipos_esperados)

    def test_expresion_mixta(self):
        #Prueba una expresión matemática completa
        self.lexer.input("3 + 4 * 2 - 1 / 5")
        tokens = [tok for tok in self.lexer]
        tipos_esperados = ['NUMBER', 'PLUS', 'NUMBER', 'TIMES', 'NUMBER', 'MINUS', 'NUMBER', 'DIVIDE', 'NUMBER']
        valores_esperados = [3, '+', 4, '*', 2, '-', 1, '/', 5]

        self.assertEqual([t.type for t in tokens], tipos_esperados)
        self.assertEqual([str(t.value) for t in tokens], [str(v) for v in valores_esperados])

    def test_caracter_invalido(self):
        #Prueba la detección de caracteres no válidos
        self.lexer.input("3 + 4")
        tokens = [tok for tok in self.lexer]
        tipos_esperados = ['NUMBER', 'PLUS', 'NUMBER']

        self.assertEqual([t.type for t in tokens], tipos_esperados)

if __name__ == "__main__":
    unittest.main()
