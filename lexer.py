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

# Definición de tokens
TOKEN_SPEC = [(name, rf'\b{kw}\b') for kw, name in reserved.items()] + [
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
    ('BLOCKCOMMENT', r'/\*[\s\S]*?\*/'),  # Acepta múltiples líneas
    ('WHITESPACE', r'\s+'),
    ('MISMATCH', r'.')
]

# Crear expresión regular combinada
token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC)

@dataclass
class Token:
    type: str
    value: str
    lineno: int

def tokenize(text):
    """
    Analiza el texto fuente y retorna una lista de tokens válidos.
    Reporta errores para caracteres ilegales.
    """
    tokens = []
    errors = []
    lineno = 1

    for match in re.finditer(token_regex, text, re.DOTALL):
        kind = match.lastgroup
        value = match.group()

        if kind == 'WHITESPACE':
            lineno += value.count('\n')
            continue
        elif kind in ['COMMENT', 'BLOCKCOMMENT']:
            lineno += value.count('\n')
            continue
        elif kind == 'MISMATCH':
            errors.append(f"Línea {lineno}: Error - Caracter ilegal '{value}'")
            continue
        elif kind == 'ID' and value in reserved:
            kind = reserved[value]

        tokens.append(Token(kind, value, lineno))

    for error in errors:
        print(error)

    return tokens

# Clase adaptadora para usar el lexer desde el parser
class GoxLangLexer:
    def tokenize(self, source_code):
        return tokenize(source_code)

# Prueba si se ejecuta directamente
if __name__ == "__main__":
    test_code = '''
    var x = 3.12 and 4 * 2 # Comentario simple
    /* Comentario
       de bloque */
    if (x > 2) {
        print(x);
    }
    $  # Caracter ilegal para test
    '''

    for tok in tokenize(test_code):
        print(tok)

