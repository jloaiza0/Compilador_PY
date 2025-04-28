import re
# Definición de tokens con orden de precedencia (los más específicos primero)
TOKEN_SPEC = [
    # Palabras reservadas del lenguaje
    ('CONST', r'\bconst\b'),
    ('VAR', r'\bvar\b'),
    ('PRINT', r'\bprint\b'),
    ('RETURN', r'\breturn\b'),
    ('BREAK', r'\bbreak\b'),
    ('CONTINUE', r'\bcontinue\b'),
    ('IF', r'\bif\b'),
    ('ELSE', r'\belse\b'),
    ('WHILE', r'\bwhile\b'),
    ('FUNC', r'\bfunc\b'),
    ('IMPORT', r'\bimport\b'),
    ('TRUE', r'\btrue\b'),
    ('FALSE', r'\bfalse\b'),
    ('INPUT', r'\binput\b'),

    # Tipos de datos
    ('INT', r'\bint\b'),
    ('FLOAT_TYPE', r'\bfloat\b'),
    ('BOOL', r'\bbool\b'),
    ('STRING_TYPE', r'\bstring\b'),
    ('CHAR_TYPE', r'\bchar\b'),

    # Literales numéricos
    ('HEX', r'0[xX][0-9a-fA-F]+'),       # Números hexadecimales
    ('BINARY', r'0[bB][01]+'),           # Números binarios
    ('FLOAT', r'\d+\.\d*|\.\d+'),        # Números decimales
    ('INTEGER', r'\d+'),                 # Números enteros

    # Literales de caracteres y strings
    ('CHAR', r"'([^\\]|\\.)'"),          # Caracteres individuales
    ('STRING', r'"([^\\"]|\\.)*"'),      # Cadenas de texto

    # Identificadores (nombres de variables/funciones)
    ('ID', r'[a-zA-Z_][a-zA-Z_0-9]*'),

    # Operadores compuestos (deben ir antes que los simples)
    ('INT_DIV', r'(?<!/)//(?=\s*\d)'),  # División entera (//)
    ('POWER', r'\*\*'),                  # Potenciación (**)

    # Comentarios (el patrón se maneja aparte)
    ('COMMENT', None),                   # Marcador para comentarios

    # Operadores de comparación y lógicos
    ('LE', r'<='), ('GE', r'>='),        # Menor/mayor o igual
    ('EQ', r'=='), ('NE', r'!='),        # Igualdad/desigualdad
    ('LAND', r'&&'), ('LOR', r'\|\|'),   # AND/OR lógico

    # Operadores de incremento y asignación compuesta
    ('INC', r'\+\+'), ('DEC', r'--'),    # Incremento/decremento
    ('PLUS_ASSIGN', r'\+='), ('MINUS_ASSIGN', r'-='),
    ('TIMES_ASSIGN', r'\*='), ('DIV_ASSIGN', r'/='),
    ('MOD_ASSIGN', r'%='), ('POW_ASSIGN', r'\^='),

    # Operadores de un solo carácter
    ('LT', r'<'), ('GT', r'>'),          # Menor/mayor que
    ('PLUS', r'\+'), ('MINUS', r'-'),    # Suma/resta
    ('TIMES', r'\*'), ('DIVIDE', r'/'),  # Multiplicación/división
    ('MOD', r'%'), ('GROW', r'\^'),      # Módulo, operador especial
    ('ASSIGN', r'='),                    # Asignación simple

    # Símbolos y delimitadores
    ('SEMI', r';'),                      # Punto y coma
    ('LPAREN', r'\('), ('RPAREN', r'\)'),  # Paréntesis
    ('LBRACE', r'\{'), ('RBRACE', r'\}'),  # Llaves
    ('LBRACKET', r'\['), ('RBRACKET', r'\]'), # Corchetes
    ('COMMA', r','), ('DOT', r'\.'),     # Coma, punto
    ('COLON', r':'), ('DEREF', r'`'),    # Dos puntos, operador de dereferencia

    # Espacios en blanco (se ignoran)
    ('WHITESPACE', r'\s+'),

    # Cualquier otro carácter no reconocido
    ('MISMATCH', r'.')
]

# Compilar una expresión regular combinada para todos los tokens
token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC if pattern)

class Token:
    """Clase que representa un token con tipo, valor y número de línea"""
    def __init__(self, type: str, value: str, lineno: int):
        self.type = type   # Tipo de token (ej. 'ID', 'INTEGER')
        self.value = value # Valor literal del token
        self.lineno = lineno # Línea donde aparece el token

    def __repr__(self):
        return f"Token(type='{self.type}', value='{self.value}', lineno={self.lineno})"

def tokenize(text, error_handler):
    """
    Función principal del lexer que convierte texto fuente en una lista de tokens.
    
    Args:
        text: Código fuente a analizar
        error_handler: Manejador de errores para reportar problemas
        
    Returns:
        Lista de objetos Token
    """
    tokens = []
    lineno = 1  # Contador de líneas
    pos = 0     # Posición actual en el texto
    
    while pos < len(text):
        # Manejo de comentarios de una línea (// ...)
        if text[pos:pos+2] == '//':
            end = text.find('\n', pos)
            if end == -1:  # Si no hay salto de línea, llega al final
                end = len(text)
            value = text[pos:end]
            lineno += value.count('\n')  # Actualiza contador de líneas
            pos = end
            continue

        # Manejo de comentarios de bloque (/* ... */) con anidamiento
        if text[pos:pos+2] == '/*':
            depth = 1  # Contador de anidamiento
            i = pos + 2
            while i < len(text) and depth > 0:
                if text[i:i+2] == '/*':
                    depth += 1
                    i += 2
                elif text[i:i+2] == '*/':
                    depth -= 1
                    i += 2
                else:
                    if text[i] == '\n':
                        lineno += 1
                    i += 1
            if depth > 0:  # Comentario no cerrado
                error_handler.add_error("Comentario de bloque sin cerrar", lineno)
                pos = i
            else:
                pos = i
            continue

        # Procesamiento de tokens regulares
        match = re.match(token_regex, text[pos:], re.DOTALL)
        if not match:
            error_handler.add_error(f"Carácter ilegal '{text[pos]}'", lineno)
            pos += 1
            continue
            
        kind = match.lastgroup  # Tipo de token encontrado
        value = match.group()   # Valor del token
        
        # Ignorar espacios en blanco (pero contar líneas)
        if kind == 'WHITESPACE':
            lineno += value.count('\n')
            pos += len(value)
            continue
        # Manejar caracteres no reconocidos
        elif kind == 'MISMATCH':
            error_handler.add_error(f"Carácter ilegal '{value}'", lineno)
            pos += len(value)
            continue
            
        # Crear y almacenar el token válido
        tokens.append(Token(kind, value, lineno))
        pos += len(value)
    
    return tokens

# Ejemplo de uso del lexer (solo se ejecuta si es el módulo principal)
if __name__ == "__main__":
    from Error import ErrorHandler
    
    # Código de prueba para el lexer
    test_code = """
/* ******************************************************************* *
 *                                                                     *
 * factorize.gox  (compilador gox)                                     *
 *                                                                     *
 * Dado un numero N, lo descompone en sus factores primos.             *
 * Ejemplo: 21 = 3x7                                                   *
 *                                                                     *
 ********************************************************************* *
 */

func mod(x int, y int) int {
	return x - (x/y) * y;
}

func isprime(n int) bool {
    if n < 2 {
        return false;
    }
    var i int = 2;
    while i * i <= n {
        if mod(n, i) == 0 {
            return false;
        }
        i = i + 1;
    }
    return true;
}

func factorize(n int) int {
    var factor int = 2;
    // print "factores primos de " + n + ": ";

    while n > 1 {
        while mod(n, factor) == 0 {
            print factor;
            n = n / factor;
        }
        factor = factor + 1;
    }
}

var num int = 21;
print factorize(num);

"""
    error_handler = ErrorHandler()
    tokens = tokenize(test_code, error_handler)
    
    # Imprimir todos los tokens encontrados
    for tok in tokens:
        print(tok)
    
    # Reportar errores si los hay
    if error_handler.has_errors():
        print("--- Errores encontrados ---")
        error_handler.report_errors()