import sys

class ErrorType:
    # Tipos de error posibles
    LEXICAL       = 'LEXICAL'
    SYNTAX        = 'SYNTAX'
    SEMANTIC      = 'SEMANTIC'
    INTERPRETATION= 'INTERPRETATION'
    GENERAL       = 'GENERAL'

    @classmethod
    def normalize(cls, t):
        # Normaliza el tipo de error para que siempre sea uno de los tipos definidos
        t = t.upper() if isinstance(t, str) else str(t).upper()
        return t if t in {
            cls.LEXICAL, cls.SYNTAX, cls.SEMANTIC,
            cls.INTERPRETATION, cls.GENERAL
        } else cls.GENERAL

class ErrorEntry:
    def __init__(self, message, lineno, colno, type):
        # Representa una entrada de error con mensaje, línea, columna y tipo
        self.message = message
        self.lineno = lineno
        self.colno = colno
        self.type = type

class CompilerError(Exception):
    """Excepción base para las fases del compilador."""
    def __init__(self, message, lineno=None, colno=None):
        super().__init__(message)
        self.message = message
        self.lineno = lineno
        self.colno = colno

# Definición de errores específicos para cada fase
class LexicalError(CompilerError):       pass
class SyntaxError(CompilerError):        pass
class SemanticError(CompilerError):      pass
class InterpretationError(CompilerError): pass

class ErrorHandler:
    def __init__(self):
        # Inicializa una lista vacía de errores
        self.errors = []

    def add_error(self, message, lineno=None, colno=None, error_type=ErrorType.GENERAL):
        # Registra un error en cualquier fase del compilador
        et = ErrorType.normalize(error_type)
        entry = ErrorEntry(message, lineno or 0, colno, et)
        self.errors.append(entry)

    def add_lexical_error(self, message, lineno, colno=None):
        # Agrega un error léxico
        self.add_error(message, lineno, colno, ErrorType.LEXICAL)

    def add_syntax_error(self, message, lineno, colno=None):
        # Agrega un error sintáctico
        self.add_error(message, lineno, colno, ErrorType.SYNTAX)

    def add_semantic_error(self, message, lineno, colno=None):
        # Agrega un error semántico
        self.add_error(message, lineno, colno, ErrorType.SEMANTIC)

    def add_interpretation_error(self, message, lineno, colno=None):
        # Agrega un error de interpretación
        self.add_error(message, lineno, colno, ErrorType.INTERPRETATION)

    def has_errors(self):
        # Retorna True si hay errores registrados
        return bool(self.errors)

    def report_errors(self):
        # Imprime todos los errores ordenados por ubicación (línea y columna)
        for err in sorted(self.errors, key=lambda e: (e.lineno, e.colno or 0)):
            loc = f"Línea {err.lineno}"
            if err.colno is not None:
                loc += f":{err.colno}"
            print(f"{loc} [{err.type}] {err.message}")

    def exit_if_errors(self, exit_code=1):
        # Informa los errores y termina la ejecución si hay errores registrados
        if self.has_errors():
            self.report_errors()
            sys.exit(exit_code)

    def clear_errors(self):
        # Limpia todos los errores registrados
        self.errors.clear()

# Ejemplo de uso
if __name__ == "__main__":
    eh = ErrorHandler()
    eh.add_lexical_error("Token inesperado", 3, 5)
    eh.add_syntax_error("Falta ';'", 4)
    eh.add_semantic_error("Incompatibilidad de tipos", 7, 12)
    eh.add_interpretation_error("División por cero", 15, 2)
    if eh.has_errors():
        eh.report_errors()
