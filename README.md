# Analizador lexico
Este documento detalla el proceso para crear un analizador lexico usando la libreria `ply` y la libreria `unittest` para las pruebas unitarias, para esto tendremos que instalar la lipreria `ply` de la siguiente forma:
```c
pip install ply
```
### Integrantes del grupo
- Juan Loaiza
- Javier Parra
- Estiven Munoz
---
# Contruccion del analizador lexico usando ply
### Tokens asignados:
```c
tokens = [
    'NUMBER', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'POW', 'MOD',
    'LPAR', 'RPAR', 'COMMA', 'SEMICOLON', 'COLON', 'DOT',
    'LBRACE', 'RBRACE', 'EQ', 'NEQ', 'GT', 'LT', 'GTE', 'LTE',
    'AND', 'OR', 'NOT', 'ASSIGN',
    'CONSTANT', 'VAR', 'PRINT', 'IF', 'ELSE', 'WHILE', 'FOR', 'FUNCTION', 'RETURN',
    'TRUE', 'FALSE', 'NULL', 'BREAK', 'IMPORT', 'FROM'
]
```
En esta sección del código se inicializan los tokens que se usarán posteriormente
---
# Expresiones regulares
En esta sección se asignan los simbolos a cada token
### Expresiones regulares para tokens de operadores matemáticos
```c
t_PLUS = r'\+'
t_MINUS = r'\-'
t_TIMES = r'\*'
t_DIVIDE = r'\/'
t_POW = r'\^'
t_MOD = r'\%'
```
### Expresiones regulares para operadores de comparación
```c
t_EQ = r'=='
t_NEQ = r'!='
t_GT = r'>'
t_LT = r'<'
t_GTE = r'>='
t_LTE = r'<='
```
### Expresiones regulares para operadores lógicos
```c
t_AND = r'\band\b'
t_OR = r'\bor\b'
t_NOT = r'\bnot\b'
```
### Expresión regular para asignación
```c
t_ASSIGN = r'='
```
### Expresiones regulares para tokens de puntuación y símbolos
```c
t_LPAR = r'\('
t_RPAR = r'\)'
t_COMMA = r'\,'
t_SEMICOLON = r'\;'
t_COLON = r'\:'
t_DOT = r'\.'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
```
### Expresiones regulares para palabras reservadas
```c
t_CONSTANT = r'\bconst\b'
t_VAR = r'\bvar\b'
t_PRINT = r'\bprint\b'
t_IF = r'\bif\b'
t_ELSE = r'\belse\b'
t_WHILE = r'\bwhile\b'
t_FOR = r'\bfor\b'
t_FUNCTION = r'\bfunction\b'
t_RETURN = r'\breturn\b'
t_TRUE = r'\btrue\b'
t_FALSE = r'\bfalse\b'
t_NULL = r'\bnull\b'
t_BREAK = r'\bbreak\b'
t_IMPORT = r'\bimport\b'
t_FROM = r'\bfrom\b'
```
### Expresión regular para reconocer números enteros
```c
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t
```
### Ingorar
```c
t_ignore = ' \n'
```
---
# Funciones necesarias
### Manejo de errores
Para manejar errores debemos mostrar el valor del token especifico en el que se encontro el error, mostrandolo en un `print("")`, para posteriormente saltar al siguiente usando `t.lexer.skip(1)` de la siguiente forma:
```c
def t_error(t):
    print("Carácter no válido: '%s'" % t.value[0])
    t.lexer.skip(1)
```
Posteriormente creamos el contructor para el analizador lexico
```c
def build_lexer():
    return lex.lex()
```
### Se define el main
```c
if __name__ == "__main__":
    lexer = build_lexer()
    data = "3 + 4 * 2"
    lexer.input(data)
    
    while True:
        token = lexer.token()
        if not token:
            break
        print(token)

```
---
# Pruebas unitarias
Para las pruebas unitarias se usó las libreria `unittest` e importando el contructor del analizador, de la siguiente forma:
```c
import unittest
from analizador import build_lexer
```
Ejemplo de las pruebas unitarias:
```c
def test_expresion_mixta(self):
        #Prueba una expresión matemática completa
        self.lexer.input("3 + 4 * 2 - 1 / 5")
        tokens = [tok for tok in self.lexer]
        tipos_esperados = ['NUMBER', 'PLUS', 'NUMBER', 'TIMES', 'NUMBER', 'MINUS', 'NUMBER', 'DIVIDE', 'NUMBER']
        valores_esperados = [3, '+', 4, '*', 2, '-', 1, '/', 5]

        self.assertEqual([t.type for t in tokens], tipos_esperados)
        self.assertEqual([str(t.value) for t in tokens], [str(v) for v in valores_esperados])
```
---
#Errores cometidos
- Tuvimos un problema al asignar las palabras reservadas ya que intentamos asignarlas como tokens y en realidad se asiganan como
- Tuvimos un puqueño error al asignar `t_QUOTE = r'\"'` y `t_DQUOTE = r'\''` ya que lo hicimos de la siguiente forma:
```c
t_quote = r'\"'
t_dquote = r'\''
```
y el token originar estaban definidas como `'QUOTE', 'DQUOTE'`
