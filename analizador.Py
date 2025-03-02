import re
from dataclasses import dataclass

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

# Definición de tokens con orden adecuado
TOKEN_SPEC = [
    ('CONSTANT', r'\bconst\b'),
    ('VAR', r'\bvar\b'),
    ('PRINT', r'\bprint\b'),
    ('RETURN', r'\breturn\b'),
    ('BREAK', r'\bbreak\b'),
    ('IF', r'\bif\b'),
    ('ELSE', r'\belse\b'),
    ('WHILE', r'\bwhile\b'),
    ('FOR', r'\bfor\b'),
    ('FUNCTION', r'\bfunction\b'),
    ('IMPORT', r'\bimport\b'),
    ('TRUE', r'\btrue\b'),
    ('FALSE', r'\bfalse\b'),
    ('NULL', r'\bnull\b'),
    ('FROM', r'\bfrom\b'),
    ('AND', r'\band\b'),
    ('OR', r'\bor\b'),
    ('NOT', r'\bnot\b'),
    ('FLOAT', r'\d+\.\d*|\.\d+'),
    ('NUMBER', r'\d+'),
    ('ID', r'[a-zA-Z_][a-zA-Z_0-9]*'),
    ('LTE', r'<='), ('GTE', r'>='), ('EQ', r'=='), ('NEQ', r'!='),
    ('LT', r'<'), ('GT', r'>'), ('PLUS', r'\+'), ('MINUS', r'-'),
    ('MULTIPLY', r'\*'), ('DIVIDE', r'/'), ('POW', r'\^'), ('MOD', r'%'),
    ('ASSIGN', r'='),
    ('LPAR', r'\('), ('RPAR', r'\)'), ('COMMA', r','), ('SEMICOLON', r';'),
    ('COLON', r':'), ('DOT', r'\.'), ('LBRACE', r'\{'), ('RBRACE', r'\}'),
    ('LSQUARE', r'\['), ('RSQUARE', r'\]'),
    ('COMMENT', r'\#.*'),
    ('BLOCKCOMMENT', r'/\*.*?\*/'),
    ('WHITESPACE', r'\s+'),
    ('MISMATCH', r'.')
]

# Crear la expresión regular combinada a partir de los tokens
token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC)

@dataclass
class Token:
    type: str   # Tipo del token (por ejemplo, VAR, ID, ASSIGN, etc.)
    value: str  # Cadena que coincide (lexema)
    lineno: int # Número de línea donde se encontró el token

def tokenize(text):
    """
    Función que recibe un código fuente y retorna una lista de tokens.
    Los tokens se generan utilizando la expresión regular compuesta.
    """
    tokens = []
    lineno = 1
    for match in re.finditer(token_regex, text, re.DOTALL):
        kind = match.lastgroup  # Nombre del token
        value = match.group()   # Lexema encontrado
        if kind == 'WHITESPACE':
            lineno += value.count('\n')
            continue
        elif kind == 'COMMENT' or kind == 'BLOCKCOMMENT':
            lineno += value.count('\n')
            continue
        elif kind == 'MISMATCH':
            print(f"Línea {lineno}: Error - Caracter ilegal '{value}'")
            continue
        if kind == 'ID' and value in reserved:
            kind = reserved[value]
        tokens.append(Token(kind, value, lineno))
    return tokens

# Solo ejecutar el ejemplo si el archivo se ejecuta directamente
if __name__ == "__main__":
    test_code = 'var x = 3.12 and 4 * 2 # Esto es un comentario de línea\n/* Esto es un comentario de bloque */'
    for tok in tokenize(test_code):
        print(tok)
