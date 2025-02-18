import ply.lex as lex

# Definición de tokens
tokens = ['NUMBER', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE']

# Expresiones regulares para tokens simples
t_PLUS = r'\+'
t_MINUS = r'\-'
t_TIMES = r'\*'
t_DIVIDE = r'\/'

# Expresión regular para reconocer números enteros
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Ignorar caracteres como espacios y saltos de línea
t_ignore = ' \n'

# Manejo de errores de token
def t_error(t):
    print("Carácter no válido: '%s'" % t.value[0])
    t.lexer.skip(1)

# Función para construir el analizador léxico
def construir_analizador():
    return lex.lex()

# Solo ejecuta el analizador si este archivo se ejecuta directamente
if __name__ == "__main__":
    lexer = construir_analizador()
    data = "3 + 4 * 2"
    lexer.input(data)

    while True:
        token = lexer.token()
        if not token:
            break
        print(token)