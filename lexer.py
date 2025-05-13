import re
import sys
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
    ('BLOCKCOMMENT', r'/\*[\s\S]*?\*/'),
    ('COMMENT', r'//.*'),
    ('FLOAT', r'-?\d+\.\d+'),
    ('NUMBER', r'-?\d+'),
    ('STRING', r'"(?:\\.|[^"\\])*"'),
    ('HEXCHAR', r"'\\x[0-9a-fA-F]{2}'"),  # Nueva regla para caracteres hexadecimales
    ('CHAR', r"'(?:\\.|[^'\\])'"),
    ('BACKTICK', r'`'),
    ('MEM_ACCESS', r'´[a-zA-Z_]\w*'),
    ('EQ', r'=='),
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
    ('ID', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('WHITESPACE', r'[ \t\r]+'),
    ('NEWLINE', r'\n'),
    ('MISMATCH', r'.')
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
            elif kind == 'HEXCHAR':
                # Procesar caracteres hexadecimales como '\xff'
                try:
                    hex_value = value[3:-1]  # Extraer 'ff' de '\xff'
                    value = int(hex_value, 16)
                    kind = 'CHAR'  # Lo tratamos como CHAR pero con valor numérico
                except ValueError:
                    errors.append(f"Secuencia hexadecimal inválida: {value} en línea {lineno}")
                    continue
            elif kind == 'CHAR':
                if len(value) < 3:
                    errors.append(f"Literal de carácter inválido {value} en línea {lineno}")
                    continue
                try:
                    if value.startswith("'\\") and value[2] != 'x':
                        # Secuencias de escape que no son hexadecimales
                        value = value[1:-1].encode('utf-8').decode('unicode-escape')
                except Exception:
                    errors.append(f"Literal de carácter inválido {value} en línea {lineno}")
                    continue
            
            tokens.append(Token(kind, value, lineno))
        
        tokens.append(Token('EOF', '', lineno))
        return tokens, errors

    def test_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                source_code = file.read()
            
            print(f"\n=== Analizando: {file_path} ===")
            
            tokens, errors = self.tokenize(source_code)
            
            print("\n=== Tokens generados ===")
            for i, token in enumerate(tokens):
                print(f"{i:3d}: {token.type:12} '{token.value}' (línea {token.lineno})")
            
            if errors:
                print("\n✗ Errores léxicos encontrados:")
                for error in errors:
                    print(f"  - {error}")
                return False
            else:
                print("\n✓ El archivo se tokenizó correctamente sin errores léxicos")
                return True
            
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {file_path}")
            return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python lexer.py archivo.gox")
        sys.exit(1)
    
    lexer = Lexer()
    file_path = sys.argv[1]
    
    if not file_path.endswith('.gox'):
        print("Advertencia: El archivo no tiene extensión .gox")
    
    success = lexer.test_file(file_path)
    sys.exit(0 if success else 1)