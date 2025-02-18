import ply.lex as lex

# Definición de tokens
tokens = [
    'NUMBER', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'POW', 'MOD',
    'LPAR', 'RPAR', 'COMMA', 'SEMICOLON', 'COLON', 'DOT',
    'LBRACE', 'RBRACE', 'LSQUARE', 'RSQUARE', 'EQ', 'NEQ', 'GT', 'LT', 'GTE', 'LTE',
    'AND', 'OR', 'NOT', 'ASSIGN',
    'CONSTANT', 'VAR', 'PRINT', 'IF', 'ELSE', 'WHILE', 'FOR', 'FUNCTION', 'RETURN',
    'TRUE', 'FALSE', 'NULL', 'BREAK', 'IMPORT', 'FROM',
    'QUOTE', 'DQUOTE'
]

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

# Expresiones regulares para operadores lógicos
t_AND = r'\band\b'
t_OR = r'\bor\b'
t_NOT = r'\bnot\b'

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

# Expresiones regulares para palabras reservadas
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

# Expresiones regulares para otros símbolos
t_quote = r'\"'
t_dquote = r'\''

# Expresión regular para reconocer números enteros
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

#Ignorar caracteres como espacios y saltos de línea
t_ignore = ' \n'

#Manejo de errores de token
def t_error(t):
    print("Carácter no válido: '%s'" % t.value[0])
    t.lexer.skip(1)

#Función para construir el analizador léxico
def build_lexer():
    return lex.lex()

#Solo ejecutar el ejemplo si el archivo se ejecuta directamente
if name == "main":
    lexer = build_lexer()
    data = "3 + 4 * 2"
    lexer.input(data)

    while True:
        token = lexer.token()
        if not token:
            break
        print(token)