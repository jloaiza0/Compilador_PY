import re
from collections import namedtuple

Token = namedtuple('Token', ['type', 'value', 'lineno'])

reserved = {
    'if': 'IF',
    'import': 'IMPORT',
    'func': 'FUNC',
    'else': 'ELSE',
    'for': 'FOR',
    'while': 'WHILE',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    'return': 'RETURN',
    'var': 'VAR',
    'true': 'TRUE',
    'false': 'FALSE',
    'int': 'TYPE', #tipo de dato entero
    'bool': 'TYPE', #tipo de dato booleano
    'float': 'TYPE', #tipo de dato flotante
    'char': 'TYPE', #tipo de dato caracter
    'string': 'TYPE', #tipo de dato cadena
    'void': 'TYPE', #tipo de dato vacio
    'null': 'NULL',
}

token_specification = [
    ('FLOAT', r'-?(\d+\.\d*|\.\d+)'),
    ('NUMBER', r'-?\d+'),
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
    ('POW',         r'\^'),
    ('LPAREN',      r'\('),
    ('RPAREN',      r'\)'),
    ('LBRACE',      r'\{'),
    ('RBRACE',      r'\}'),
    ('LBRACKET',    r'\['),
    ('RBRACKET',    r'\]'),
    ('COMMA',       r','),
    ('SEMICOLON',   r';'),
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




