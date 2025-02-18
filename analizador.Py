import ply.lex as lex

# Diccionario de palabras reservadas
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

# Definición de tokens
tokens = [
    'NUMBER', 'FLOAT', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'POW', 'MOD',
    'LPAR', 'RPAR', 'COMMA', 'SEMICOLON', 'COLON', 'DOT',
    'LBRACE', 'RBRACE', 'LSQUARE', 'RSQUARE', 'EQ', 'NEQ', 'GT', 'LT', 'GTE', 'LTE',
    'ASSIGN',
    'ID',
    'QUOTE', 'DQUOTE', 'STRING'
] + list(reserved.values())  # Agrega las palabras reservadas a los tokens

# Expresiones regulares para tokens de operadores matemáticos
t_PLUS = r'\+'
t_MINUS = r'\-'
t_TIMES = r'\*'
t_DIVIDE = r'\/'
t_POW = r'\^'
t_MOD = r'\%'

# Expresiones regulares para operadores de comparación
t_EQ = r'=='
t_NEQ = r'!='
t_GT = r'>'
t_LT = r'<'
t_GTE = r'>='
t_LTE = r'<='

# Expresión regular para asignación
t_ASSIGN = r'='

# Expresiones regulares para tokens de puntuación y símbolos
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

# Expresiones regulares para otros símbolos
t_QUOTE = r'\"'
t_DQUOTE = r'\''

# Expresión regular para reconocer cadenas
def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"|\'.*?\''
    t.value = t.value[1:-1]  # Remover las comillas
    return t

# Expresión regular para reconocer números flotantes
def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

# Expresión regular para reconocer números enteros
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Expresión regular para reconocer identificadores
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')  # Verificar si es una palabra reservada
    return t

# Ignorar caracteres como espacios y saltos de línea
t_ignore = ' \t\n'

# Manejo de comentarios de línea
def t_COMMENT(t):
    r'\#.*'
    pass  # Ignorar el comentario

# Manejo de comentarios de bloque
def t_BLOCKCOMMENT(t):
    r'/\*.*?\*/'
    pass  # Ignorar el comentario

# Manejo de errores de token
def t_error(t):
    print("Carácter no válido: '%s'" % t.value[0])
    t.lexer.skip(1)

# Función para construir el analizador léxico
def build_lexer():
    return lex.lex()

# Solo ejecutar el ejemplo si el archivo se ejecuta directamente
if __name__ == "__main__":
    lexer = build_lexer()
    data = 'var x = 3.12 and 4 * 2 # Esto es un comentario de línea\n "Esto es una cadena" /* Esto es un comentario de bloque */'
    lexer.input(data)

    while True:
        token = lexer.token()
        if not token:
            break
        print(token)
