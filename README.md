# Analizador lexico
Este documento detalla el proceso para crear un analizador lexico usando la libreria `ply` y la libreria `unittest` para las pruebas unitarias, para esto tendremos que instalar la libreria `ply` de la siguiente forma:
```c
pip install ply
```
### Integrantes del grupo
- Juan Loaiza
- Javier Parra
- Estiven Munoz
---
# Construccion del analizador lexico usando ply
### Tokens asignados:
```c
tokens = [
    'NUMBER', 'FLOAT', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'POW', 'MOD',
    'LPAR', 'RPAR', 'COMMA', 'SEMICOLON', 'COLON', 'DOT',
    'LBRACE', 'RBRACE', 'LSQUARE', 'RSQUARE', 'EQ', 'NEQ', 'GT', 'LT', 'GTE', 'LTE',
    'ASSIGN',
    'ID',
    'QUOTE', 'DQUOTE', 'STRING', 'COMMENT', 'BLOCKCOMMENT'
] + list(reserved.values())
```
### Palabras reservadas
```c
reserved = {
    'const': 'CONSTANT',
    'var': 'VAR',
    'print': 'PRINT',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'function': 'FUNCTION',
    'return': 'RETURN',
    'true': 'TRUE',
    'false': 'FALSE',
    'null': 'NULL',
    'break': 'BREAK',
    'import': 'IMPORT',
    'from': 'FROM',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT'
}
```
En esta sección del código se inicializan los tokens y palabras reservadas que se usarán posteriormente
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
t_LSQUARE = r'\['
t_RSQUARE = r'\]'
```
### Expresiones regulares para otros símbolos
```c
t_QUOTE = r'\"'
t_DQUOTE = r'\''
```
### Expresión regular para reconocer cadenas
```c
def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"|\'.*?\''
    t.value = t.value[1:-1]  # Remover las comillas
    return t
```
### Expresión regular para reconocer números flotantes
```c
def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t
```
### Expresión regular para reconocer números enteros
```c
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t
```
### Expresión regular para reconocer identificadores
```c
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')  # Verificar si es una palabra reservada
    return t
```
### Ignorar caracteres como espacios y saltos de línea
```c
t_ignore = ' \t\n'
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
Posteriormente creamos el constructor para el analizador lexico
```c
def build_lexer():
    return lex.lex()
```
### Se define el main
```c
if __name__ == "__main__":
    lexer = build_lexer()
    data = 'var x = 3.12 and 4 * 2 # Esto es un comentario de línea\n "Esto es una cadena" /* Esto es un comentario de bloque */'
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
Hicimos pruebas unitarias para cada caso y al final una sola prueba que reune todos los casos:
```c
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
```
Dando como resultado 10 pruebas unitaras con resultados satisfactorios.
---
# Errores cometidos
- Tuvimos un problema al asignar las palabras reservadas ya que intentamos asignarlas como tokens y en realidad se asiganan como un diccionaro, para luego concatenarla con los tokens cambiando `AND`, `OR` y `NOR` incluyendolas en las palabras reservadas.
- Tuvimos un puqueño error al asignar `t_QUOTE = r'\"'` y `t_DQUOTE = r'\''` ya que lo hicimos de la siguiente forma:
```c
t_quote = r'\"'
t_dquote = r'\''
```
y en el token original estaban definidas como `'QUOTE', 'DQUOTE'`
- Tuvimos que agregar primero la expresion regular del numero flotante antes que la del numero entero ya que se estaba reconociendo como numero entero y no como flotante.
---
# UNIVERSIDAD TECNOLOGICA DE PERERIA 2025
# COMPILADORES GRUPO 2
# DOCENTE: ANGEL AUGUSTO AGUDELO