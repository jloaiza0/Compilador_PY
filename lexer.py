# lexer.py
import re
from enum import Enum, auto
from typing import List, NamedTuple, Optional, Pattern # Pattern not used directly by user, but by re.compile
from dataclasses import dataclass

# Considerar importar ErrorHandler y ErrorType de Error.py si se quiere integrar el reporte
# from Error import ErrorHandler, ErrorType # Ejemplo

class TokenType(Enum):
    """Tipos de tokens soportados por el lenguaje"""
    # Palabras reservadas
    CONST = auto()
    VAR = auto()
    PRINT = auto()
    RETURN = auto()
    BREAK = auto()
    CONTINUE = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FUNC = auto()
    IMPORT = auto()  # No en el ejemplo GoX, pero plausible
    TRUE = auto()
    FALSE = auto()
    INPUT = auto()   # No en el ejemplo GoX, pero plausible
    
    # Tipos de datos como palabras clave
    INT = auto()         # Para la palabra clave 'int'
    FLOAT_TYPE = auto()  # Para la palabra clave 'float'
    BOOL = auto()        # Para la palabra clave 'bool'
    STRING_TYPE = auto() # Para la palabra clave 'string'
    CHAR_TYPE = auto()   # Para la palabra clave 'char'
    
    # Literales
    HEX = auto()
    BINARY = auto()
    FLOAT = auto()       # Para el valor literal flotante, ej: 3.14
    INTEGER = auto()     # Para el valor literal entero, ej: 123
    CHAR = auto()        # Para el valor literal char, ej: 'a'
    STRING = auto()      # Para el valor literal string, ej: "hello"
    
    # Identificadores
    ID = auto()
    
    # Operadores
    INT_DIV = auto()      # //
    POWER = auto()        # **
    LE = auto()           # <=
    GE = auto()           # >=
    EQ = auto()           # ==
    NE = auto()           # !=
    LAND = auto()         # &&
    LOR = auto()          # ||
    INC = auto()          # ++
    DEC = auto()          # --
    PLUS_ASSIGN = auto()  # +=
    MINUS_ASSIGN = auto() # -=
    TIMES_ASSIGN = auto() # *=
    DIV_ASSIGN = auto()   # /=
    MOD_ASSIGN = auto()   # %=
    POW_ASSIGN = auto()   # ^= (si ^ es para potencia) o diferente si ^ es otro op
    
    LT = auto()           # <
    GT = auto()           # >
    PLUS = auto()         # +
    MINUS = auto()        # -
    TIMES = auto()        # *
    DIVIDE = auto()       # /
    MOD = auto()          # %
    GROW = auto()         # ^ (en GoX ejemplo: memsize = ^1000)
    ASSIGN = auto()       # =
    NOT = auto()          # !
    
    # Delimitadores
    SEMI = auto()         # ;
    LPAREN = auto()       # (
    RPAREN = auto()       # )
    LBRACE = auto()       # {
    RBRACE = auto()       # }
    LBRACKET = auto()     # [
    RBRACKET = auto()     # ]
    COMMA = auto()        # ,
    DOT = auto()          # .
    COLON = auto()        # :
    DEREF = auto()        # ` (backtick)
    
    # Especiales (TokenType.COMMENT no se generará como token, se omite)
    # TokenType.COMMENT = auto() # Eliminado de aquí si _try_match_comment lo maneja todo
    WHITESPACE = auto()   # Se omite, pero necesita ser reconocido
    MISMATCH = auto()     # Para cualquier carácter no reconocido
    EOF = auto()          # Fin de archivo

@dataclass
class TokenInfo:
    """Información sobre un tipo de token incluyendo su expresión regular"""
    type: TokenType
    pattern: str
    # precedence es útil si se construye una única regex muy compleja y el orden importa críticamente.
    # Con el enfoque actual (TOKEN_SPEC ordenado y _try_match_comment separado), es menos crítico.
    precedence: int = 0

class Token(NamedTuple):
    """Representación de un token con tipo, valor y ubicación"""
    type: TokenType
    value: str
    lineno: int
    column: int

    def __repr__(self):
        return f"Token(type={self.type.name}, value='{self.value}', line={self.lineno}, col={self.column})"

class LexerError(Exception):
    """Excepción para errores léxicos"""
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"Error léxico en línea {line}, columna {column}: {message}")
        self.line = line
        self.column = column

class Lexer:
    """Analizador léxico para el lenguaje GoX"""
    
    TOKEN_SPEC = [
        # Literales (los más específicos o complejos primero)
        TokenInfo(TokenType.HEX, r'0[xX][0-9a-fA-F]+'),
        TokenInfo(TokenType.BINARY, r'0[bB][01]+'),
        # Float regex corregida:
        TokenInfo(TokenType.FLOAT, r'(?:\d+\.\d*|\.\d+)(?:[eE][+-]?\d+)?|\d+[eE][+-]?\d+'),
        TokenInfo(TokenType.INTEGER, r'\d+'), # Debe ir después de FLOAT
        TokenInfo(TokenType.CHAR, r"'([^\\']|\\.)'"), # 'c', '\n', etc.
        TokenInfo(TokenType.STRING, r'"([^\\"]|\\.)*"'), # "string"
        
        # Palabras reservadas (usar \b para asegurar que sean palabras completas)
        # Tipos como palabras clave
        TokenInfo(TokenType.INT, r'\bint\b'),
        TokenInfo(TokenType.FLOAT_TYPE, r'\bfloat\b'), # Renombrado de FLOAT a FLOAT_TYPE en TokenType
        TokenInfo(TokenType.BOOL, r'\bbool\b'),
        TokenInfo(TokenType.STRING_TYPE, r'\bstring\b'),
        TokenInfo(TokenType.CHAR_TYPE, r'\bchar\b'),
        # Otras palabras clave
        TokenInfo(TokenType.CONST, r'\bconst\b'),
        TokenInfo(TokenType.VAR, r'\bvar\b'),
        TokenInfo(TokenType.PRINT, r'\bprint\b'),
        TokenInfo(TokenType.RETURN, r'\breturn\b'),
        TokenInfo(TokenType.BREAK, r'\bbreak\b'),
        TokenInfo(TokenType.CONTINUE, r'\bcontinue\b'),
        TokenInfo(TokenType.IF, r'\bif\b'),
        TokenInfo(TokenType.ELSE, r'\belse\b'),
        TokenInfo(TokenType.WHILE, r'\bwhile\b'),
        TokenInfo(TokenType.FUNC, r'\bfunc\b'),
        TokenInfo(TokenType.IMPORT, r'\bimport\b'),
        TokenInfo(TokenType.TRUE, r'\btrue\b'),
        TokenInfo(TokenType.FALSE, r'\bfalse\b'),
        TokenInfo(TokenType.INPUT, r'\binput\b'),
        
        # Identificadores (después de palabras reservadas)
        TokenInfo(TokenType.ID, r'[a-zA-Z_][a-zA-Z0-9_]*'),
        
        # Operadores compuestos (antes de los simples para correcta coincidencia)
        TokenInfo(TokenType.INT_DIV, r'//'),
        TokenInfo(TokenType.POWER, r'\*\*'),
        TokenInfo(TokenType.LE, r'<='),
        TokenInfo(TokenType.GE, r'>='),
        TokenInfo(TokenType.EQ, r'=='),
        TokenInfo(TokenType.NE, r'!='),
        TokenInfo(TokenType.LAND, r'&&'),
        TokenInfo(TokenType.LOR, r'\|\|'), # \| necesita escape en Python string literal -> \\|
        TokenInfo(TokenType.INC, r'\+\+'),
        TokenInfo(TokenType.DEC, r'--'),
        TokenInfo(TokenType.PLUS_ASSIGN, r'\+='),
        TokenInfo(TokenType.MINUS_ASSIGN, r'-='),
        TokenInfo(TokenType.TIMES_ASSIGN, r'\*='),
        TokenInfo(TokenType.DIV_ASSIGN, r'/='),
        TokenInfo(TokenType.MOD_ASSIGN, r'%='),
        TokenInfo(TokenType.POW_ASSIGN, r'\^='), # Asumiendo que esto es lo que quieres para ^=
        
        # Operadores simples
        TokenInfo(TokenType.LT, r'<'),
        TokenInfo(TokenType.GT, r'>'),
        TokenInfo(TokenType.PLUS, r'\+'),
        TokenInfo(TokenType.MINUS, r'-'),
        TokenInfo(TokenType.TIMES, r'\*'),
        TokenInfo(TokenType.DIVIDE, r'/'),
        TokenInfo(TokenType.MOD, r'%'),
        TokenInfo(TokenType.GROW, r'\^'), # Para el ^ de memsize = ^1000
        TokenInfo(TokenType.ASSIGN, r'='),
        TokenInfo(TokenType.NOT, r'!'),
        
        # Delimitadores
        TokenInfo(TokenType.SEMI, r';'),
        TokenInfo(TokenType.LPAREN, r'\('),
        TokenInfo(TokenType.RPAREN, r'\)'),
        TokenInfo(TokenType.LBRACE, r'\{'),
        TokenInfo(TokenType.RBRACE, r'\}'),
        TokenInfo(TokenType.LBRACKET, r'\['),
        TokenInfo(TokenType.RBRACKET, r'\]'),
        TokenInfo(TokenType.COMMA, r','),
        TokenInfo(TokenType.DOT, r'\.'),
        TokenInfo(TokenType.COLON, r':'),
        TokenInfo(TokenType.DEREF, r'`'),
        
        # Espacios en blanco (se ignoran, pero deben ser reconocidos)
        TokenInfo(TokenType.WHITESPACE, r'\s+'),
        
        # Cualquier otro carácter es un error
        TokenInfo(TokenType.MISMATCH, r'.'),
    ]

    # No es necesario incluir COMMENT aquí si _try_match_comment lo maneja.
    # TokenInfo(TokenType.COMMENT, r'//.*?$|/\*.*?\*/', precedence=100), -> Eliminado

    def __init__(self, source: str): # Podría añadir error_handler: ErrorHandler como parámetro
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        # self.error_handler = error_handler # Si se usa ErrorHandler centralizado
        
        self.token_regex = self._compile_token_regex()

    def _compile_token_regex(self) -> Pattern:
        # El orden en TOKEN_SPEC es crucial. Python re.match prueba alternativas de izq a der.
        # La ordenación por `precedence` aquí es menos útil si todas las precedencias son 0.
        # Lo importante es el orden en que se listan en TOKEN_SPEC.
        # No obstante, la lógica de ordenación no hace daño.
        sorted_tokens = sorted(self.TOKEN_SPEC, key=lambda x: -x.precedence)
        patterns = [f'(?P<{token.type.name}>{token.pattern})' for token in sorted_tokens]
        # re.DOTALL hace que '.' coincida también con saltos de línea.
        # Esto es importante para MISMATCH si un carácter inesperado es un salto de línea
        # que no forma parte de un WHITESPACE más grande.
        return re.compile('|'.join(patterns), re.DOTALL)

    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            # Primero, intentar consumir comentarios (que son ignorados)
            if self._try_match_comment():
                continue
            
            # Luego, intentar encontrar el siguiente token regular
            if not self._try_match_regular_token(): # Renombrado para claridad
                # Si _try_match_regular_token devuelve False, es un MISMATCH no manejado o fin de regex
                # La regex compilada ya incluye MISMATCH (r'.') al final de las alternativas.
                # Si se llega aquí, es un error lógico o un carácter que ni siquiera MISMATCH capturó
                # (lo cual es improbable con r'.').
                # Lo más probable es que MISMATCH haya sido reconocido por _try_match_regular_token
                # y este haya devuelto False, lo cual es manejado por el raise LexerError.
                # La condición de error real es si self.token_regex.match falla y no es WHITESPACE.
                # El raise LexerError ya está dentro de _try_match_regular_token para MISMATCH.
                # Esta parte del código podría simplificarse.
                # Si _try_match_regular_token devuelve False, significa que no hubo match o fue mismatch
                # El error por mismatch ya es manejado en _try_match_regular_token

                # Si _try_match_regular_token devuelve False (por ej. mismatch),
                # el error ya se levanta allí. Si devuelve False porque no hubo match en absoluto
                # (ni siquiera mismatch), entonces este es el lugar del error.
                # Sin embargo, con r'.' como última alternativa, siempre debería haber un match.
                 raise LexerError(
                     f"Carácter inesperado o no reconocido: '{self.source[self.pos]}'",
                     self.line,
                     self.column
                 )
        
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens

    def _try_match_comment(self) -> bool:
        # Comentarios de línea (// ...)
        if self.source.startswith('//', self.pos):
            end_line = self.source.find('\n', self.pos)
            length = (end_line - self.pos) if end_line != -1 else (len(self.source) - self.pos)
            self._advance(length) # Avanza hasta el fin de la línea o del fuente
            return True
            
        # Comentarios de bloque (/* ... */) con anidamiento
        if self.source.startswith('/*', self.pos):
            start_line, start_col = self.line, self.column # Guardar pos inicial del comentario
            depth = 1
            current_pos_in_comment = self.pos + 2 # Empezar a buscar después del '/*' inicial
            
            while current_pos_in_comment < len(self.source) and depth > 0:
                if self.source.startswith('/*', current_pos_in_comment):
                    depth += 1
                    current_pos_in_comment += 2
                elif self.source.startswith('*/', current_pos_in_comment):
                    depth -= 1
                    current_pos_in_comment += 2
                else:
                    # Actualizar línea y columna manualmente dentro del comentario
                    # ya que _advance se llamará una sola vez al final del comentario.
                    if self.source[current_pos_in_comment] == '\n':
                        self.line += 1
                        self.column = 1
                    else:
                        self.column += 1
                    current_pos_in_comment += 1
            
            if depth > 0:
                # Error de comentario no cerrado, reportar en la línea/col donde empezó
                raise LexerError("Comentario de bloque /* ... */ sin cerrar", start_line, start_col)
                # O usar self.error_handler.add_lexical_error(...) si se integra
            
            # Avanzar la posición global del lexer más allá del comentario consumido
            self.pos = current_pos_in_comment 
            # self.column ya fue actualizado al final del comentario por el bucle interno.
            return True
            
        return False

    def _try_match_regular_token(self) -> bool: # Renombrado desde _try_match_token
        match = self.token_regex.match(self.source, self.pos)
        if not match:
            # Esto no debería ocurrir si MISMATCH (r'.') está en TOKEN_SPEC y es la última opción.
            return False 
            
        kind_name = match.lastgroup # Nombre del grupo (ej. "INTEGER", "ID")
        value = match.group()
        token_type = TokenType[kind_name]
        
        current_line, current_column = self.line, self.column # Guardar pos antes de avanzar

        if token_type == TokenType.WHITESPACE:
            self._advance(len(value))
            return True
            
        if token_type == TokenType.MISMATCH:
            # Si se integra ErrorHandler:
            # self.error_handler.add_lexical_error(f"Carácter inesperado: '{value}'", current_line, current_column)
            # self._advance(len(value)) # Consumir el carácter erróneo
            # return True # Indicar que se "manejó" (aunque sea un error)
            # O lanzar excepción como está ahora:
            raise LexerError(f"Carácter inesperado: '{value}'", current_line, current_column)
            
        token = Token(
            type=token_type,
            value=value,
            lineno=current_line,
            column=current_column
        )
        self.tokens.append(token)
        
        self._advance(len(value))
        return True

    def _advance(self, length: int):
        # Solo actualiza self.pos, self.line, self.column.
        # En _try_match_comment, line/col se actualizan dentro del bucle de comentario,
        # y self.pos se actualiza al final.
        # Para tokens regulares y whitespace, este _advance es el que actualiza line/col.
        text_processed = self.source[self.pos : self.pos + length]
        num_newlines = text_processed.count('\n')
        
        if num_newlines > 0:
            self.line += num_newlines
            # La columna es la longitud desde el último \n en el texto procesado
            self.column = length - text_processed.rfind('\n')
        else:
            self.column += length
            
        self.pos += length

if __name__ == "__main__":
    test_code = """
    /* Ejemplo de código GoX 
       con comentario anidado /* wow */
    */
    func factorial(n int) int {
        if n <= 1 { // Comentario de línea
            return 1;
        }
        // Otro comentario
        return n * factorial(n - 1); /* fin de func */
    }
    
    const MAX = 10; // Constante
    var result float = 0.0;
    // result = factorial(MAX); // Comentado
    result = 123.45e-2;
    print "Factorial de ", MAX, " es ", result, '\\n';
    var err_char = `$`; // Error léxico esperado si `$` no es un token.
                       // Con MISMATCH r'.', `$` será un token MISMATCH.
    """
    
    print(f"Probando código:\n{test_code}\n")
    
    try:
        lexer = Lexer(test_code)
        tokens = lexer.tokenize()
        
        print("Tokens encontrados:")
        for token in tokens:
            print(token)
            
    except LexerError as e:
        print(f"Error Léxico: {e}")