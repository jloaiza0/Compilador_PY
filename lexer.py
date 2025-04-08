import re
from collections import namedtuple

Token = namedtuple('Token', ['type', 'value', 'lineno'])

reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'for': 'FOR',
    'while': 'WHILE',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    'return': 'RETURN',
    'fn': 'FUNCTION',
    'var': 'VAR',
    'true': 'TRUE',
    'false': 'FALSE',
    'null': 'NULL',
}

token_specification = [
    ('NUMBER',      r'\d+(\.\d*)?'),
    ('STRING',      r'"(\\.|[^"\\])*"'),
    ('CHAR',        r"'(\\.|[^'\\])'"),
    ('ASSIGN',      r'='),
    ('EQ',          r'=='),
    ('NE',          r'!='),
    ('LE',          r'<='),
    ('GE',          r'>='),
    ('LT',          r'<'),
    ('GT',          r'>'),
    ('PLUS',        r'\+'),
    ('MINUS',       r'-'),
    ('TIMES',       r'\*'),
    ('DIVIDE',      r'/'),
    ('MOD',         r'%'),
    ('LPAREN',      r'\('),
    ('RPAREN',      r'\)'),
    ('LBRACE',      r'\{'),
    ('RBRACE',      r'\}'),
    ('LBRACKET',    r'\['),
    ('RBRACKET',    r'\]'),
    ('COMMA',       r','),
    ('SEMI',        r';'),
    ('ID',          r'[A-Za-z_][A-Za-z0-9_]*'),
    ('COMMENT',     r'//.*'),
    ('BLOCKCOMMENT', r'/\*[\s\S]*?\*/'),
    ('WHITESPACE',  r'[ \t\r\n]+'),
    ('MISMATCH',    r'.'),
]

token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)

# --- FUNCION PRINCIPAL DE TOKENIZACIÓN ---

def tokenize(text):
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
        elif kind == 'CHAR':
            if len(value) < 3:
                errors.append(f"Línea {lineno}: Error - Literal de carácter inválido {value}")
                continue
            try:
                value = eval(value)  # convierte '\n' -> salto de línea, etc.
            except Exception:
                errors.append(f"Línea {lineno}: Error - Literal de carácter inválido {value}")
                continue

        tokens.append(Token(kind, value, lineno))

    return tokens, errors

# --- CLASE WRAPPER DEL LEXER ---

class GoxLangLexer:
    def tokenize(self, source_code):
        return tokenize(source_code)  # retorna tokens, errores




