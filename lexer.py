import re
from collections import namedtuple

Token = namedtuple('Token', ['type', 'value', 'lineno'])

class LexerError(Exception):
    """Excepción para errores del lexer"""
    def __init__(self, message, lineno):
        self.message = message
        self.lineno = lineno
        super().__init__(f"Línea {lineno}: {message}")

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
    'const': 'CONST',
    'true': 'TRUE',
    'false': 'FALSE',
    'int': 'TYPE',
    'bool': 'TYPE',
    'float': 'TYPE',
    'char': 'TYPE',
    'string': 'TYPE',
    'void': 'TYPE',
    'null': 'NULL',
    'print': 'PRINT'
}

token_specification = [
    # El orden es importante - los más específicos primero
    ('BLOCKCOMMENT', r'/\*[\s\S]*?\*/'),  # Comentarios multilínea
    ('COMMENT', r'//.*'),  # Comentarios de línea
    ('FLOAT', r'-?\d+\.\d+'),  # Números con punto decimal
    ('NUMBER', r'-?\d+'),  # Enteros
    ('STRING', r'"(?:\\.|[^"\\])*"'),  # Strings con escape
    ('CHAR', r"'(?:\\.|[^'\\])'"),  # Caracteres
    ('EQ', r'=='),  # Operadores compuestos primero
    ('NE', r'!='),
    ('LE', r'<='),
    ('GE', r'>='),
    ('LT', r'<'),
    ('GT', r'>'),
    ('ASSIGN', r'='),
    ('PLUS', r'\+'),
    ('MINUS', r'-'),
    ('TIMES', r'\*'),
    ('DIVIDE', r'/'),
    ('MOD', r'%'),
    ('POW', r'\^'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('LBRACKET', r'\['),
    ('RBRACKET', r'\]'),
    ('COMMA', r','),
    ('SEMICOLON', r';'),
    ('ID', r'[A-Za-z_][A-Za-z0-9_]*'),
    ('WHITESPACE', r'[ \t\r]+'),  # Espacios y tabs
    ('NEWLINE', r'\n'),  # Manejo explícito de nuevas líneas
    ('MISMATCH', r'.'),  # Cualquier otro carácter
]

class Lexer:
    def __init__(self):
        self.token_regex = re.compile(
            '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification),
            re.DOTALL
        )
    
    def tokenize(self, source_code):
        tokens = []
        errors = []
        lineno = 1
        pos = 0
        
        while pos < len(source_code):
            match = self.token_regex.match(source_code, pos)
            if not match:
                errors.append(f"Carácter inesperado: '{source_code[pos]}' en línea {lineno}")
                break
            
            kind = match.lastgroup
            value = match.group()
            pos = match.end()
            
            if kind == 'NEWLINE':
                lineno += 1
                continue
            elif kind in ['WHITESPACE', 'COMMENT', 'BLOCKCOMMENT']:
                if kind == 'BLOCKCOMMENT':
                    lineno += value.count('\n')
                continue
            elif kind == 'MISMATCH':
                errors.append(f"Carácter ilegal '{value}' en línea {lineno}")
                continue
            elif kind == 'ID' and value in reserved:
                kind = reserved[value]
            elif kind == 'CHAR':
                if len(value) < 3:
                    errors.append(f"Literal de carácter inválido {value} en línea {lineno}")
                    continue
                try:
                    value = eval(value)  # Convierte escapes
                except Exception:
                    errors.append(f"Literal de carácter inválido {value} en línea {lineno}")
                    continue
            
            tokens.append(Token(kind, value, lineno))
        
        # Añadir token EOF al final
        tokens.append(Token('EOF', '', lineno))
        return tokens, errors