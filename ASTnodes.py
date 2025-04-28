class ASTNode:
    """Clase base para todos los nodos del AST."""
    pass

# ---------------------------------------------------------------------
# Expresiones
# ---------------------------------------------------------------------

class Integer(ASTNode):
    """Representa un literal entero (ej. 42)."""
    def __init__(self, value):
        self.value = value  # Valor numérico del entero

    def __repr__(self):
        return f"Integer({self.value})"

class Float(ASTNode):
    """Representa un literal de punto flotante (ej. 3.14)."""
    def __init__(self, value):
        self.value = value  # Valor numérico del float

    def __repr__(self):
        return f"Float({self.value})"

class BinOp(ASTNode):
    """Representa una operación binaria (ej. 2 + 3)."""
    def __init__(self, op, left, right):
        self.op = op     # Operador (+, -, *, /, etc.)
        self.left = left  # Subexpresión izquierda
        self.right = right  # Subexpresión derecha

    def __repr__(self):
        return f"BinOp({self.op}, {self.left}, {self.right})"

class UnaryOp(ASTNode):
    """Representa una operación unaria (ej. -5, !true)."""
    def __init__(self, op, operand):
        self.op = op      # Operador (+, -, !)
        self.operand = operand  # Subexpresión

    def __repr__(self):
        return f"UnaryOp({self.op}, {self.operand})"

class Location(ASTNode):
    """Representa una ubicación (variable o dirección de memoria)."""
    def __init__(self, name):
        self.name = name  # Nombre de la variable

    def __repr__(self):
        return f"Location({self.name})"

class FunctionCall(ASTNode):
    """Representa una llamada a función (ej. suma(2,3))."""
    def __init__(self, name, args):
        self.name = name  # Nombre de la función
        self.args = args  # Lista de argumentos

    def __repr__(self):
        return f"FunctionCall({self.name}, {self.args})"

class TypeCast(ASTNode):
    """Representa una conversión de tipo (ej. int(3.14))."""
    def __init__(self, target_type, expr):
        self.target_type = target_type  # Tipo objetivo
        self.expr = expr  # Expresión a convertir

    def __repr__(self):
        return f"TypeCast({self.target_type}, {self.expr})"

# ---------------------------------------------------------------------
# Expresiones Adicionales
# ---------------------------------------------------------------------

class String(ASTNode):
    """Representa un literal de cadena (ej. "hola")."""
    def __init__(self, value):
        self.value = value  # Valor del string

    def __repr__(self):
        return f"String('{self.value}')"

class Boolean(ASTNode):
    """Representa un literal booleano (true/false)."""
    def __init__(self, value):
        self.value = value  # Valor (True/False)

    def __repr__(self):
        return f"Boolean({self.value})"

class CompareOp(ASTNode):
    """Representa una comparación (ej. x > y)."""
    def __init__(self, op, left, right):
        self.op = op     # Operador (>, <, ==, etc.)
        self.left = left  # Lado izquierdo
        self.right = right  # Lado derecho

    def __repr__(self):
        return f"CompareOp({self.op}, {self.left}, {self.right})"

class LogicalOp(ASTNode):
    """Representa una operación lógica (ej. x && y)."""
    def __init__(self, op, left, right):
        self.op = op     # Operador (&&, ||)
        self.left = left  # Operando izquierdo
        self.right = right  # Operando derecho

    def __repr__(self):
        return f"LogicalOp({self.op}, {self.left}, {self.right})"

class ArrayLiteral(ASTNode):
    """Representa un arreglo literal (ej. [1, 2, 3])."""
    def __init__(self, elements):
        self.elements = elements  # Lista de elementos

    def __repr__(self):
        return f"ArrayLiteral({self.elements})"

class IndexAccess(ASTNode):
    """Representa acceso por índice (ej. arr[i])."""
    def __init__(self, array, index):
        self.array = array  # Expresión del arreglo
        self.index = index  # Expresión del índice

    def __repr__(self):
        return f"IndexAccess({self.array}, {self.index})"

class Char(ASTNode):
    """Representa un literal de carácter (ej. 'a')."""
    def __init__(self, value):
        self.value = value  # Carácter

    def __repr__(self):
        return f"Char({self.value})"

class Dereference(ASTNode):
    """Representa una operación de desreferencia (ej. *ptr)."""
    def __init__(self, location):
        self.location = location  # Ubicación a desreferenciar

    def __repr__(self):
        return f"Dereference({self.location})"

# ---------------------------------------------------------------------
# Declaraciones
# ---------------------------------------------------------------------

class VariableDecl(ASTNode):
    """Representa una declaración de variable (ej. var x int = 5)."""
    def __init__(self, name, var_type, value=None):
        self.name = name      # Nombre de la variable
        self.var_type = var_type  # Tipo de dato
        self.value = value    # Valor inicial (opcional)

    def __repr__(self):
        return f"VariableDecl({self.name}, {self.var_type}, {self.value})"

class ConstantDecl(ASTNode):
    """Representa una declaración de constante (ej. const PI = 3.14)."""
    def __init__(self, name, value):
        self.name = name   # Nombre de la constante
        self.value = value  # Valor (requerido)

    def __repr__(self):
        return f"ConstantDecl({self.name}, {self.value})"

class FunctionDecl(ASTNode):
    """Representa una declaración de función."""
    def __init__(self, name, params, return_type, body):
        self.name = name        # Nombre de la función
        self.params = params    # Lista de parámetros
        self.return_type = return_type  # Tipo de retorno
        self.body = body        # Cuerpo de la función (lista de statements)

    def __repr__(self):
        return f"FunctionDecl({self.name}, {self.params}, {self.return_type}, {self.body})"

# ---------------------------------------------------------------------
# Sentencias
# ---------------------------------------------------------------------

class Assignment(ASTNode):
    """Representa una asignación (ej. x = 10)."""
    def __init__(self, location, expr):
        self.location = location  # Lado izquierdo (ubicación)
        self.expr = expr         # Lado derecho (expresión)

    def __repr__(self):
        return f"Assignment({self.location}, {self.expr})"

class Print(ASTNode):
    """Representa una sentencia print (ej. print "hola")."""
    def __init__(self, expr):
        self.expr = expr  # Expresión a imprimir

    def __repr__(self):
        return f"Print({self.expr})"

class If(ASTNode):
    """Representa una sentencia if/else."""
    def __init__(self, test, consequence, alternative=None):
        self.test = test          # Condición
        self.consequence = consequence  # Bloque if
        self.alternative = alternative  # Bloque else (opcional)

    def __repr__(self):
        return f"If({self.test}, {self.consequence}, {self.alternative})"

class While(ASTNode):
    """Representa un bucle while."""
    def __init__(self, test, body):
        self.test = test  # Condición
        self.body = body   # Cuerpo del bucle

    def __repr__(self):
        return f"While({self.test}, {self.body})"

class Return(ASTNode):
    """Representa una sentencia return (ej. return x)."""
    def __init__(self, expr):
        self.expr = expr  # Expresión a retornar

    def __repr__(self):
        return f"Return({self.expr})"

# ---------------------------------------------------------------------
# Sentencias Adicionales
# ---------------------------------------------------------------------

class For(ASTNode):
    """Representa un bucle for."""
    def __init__(self, init, test, update, body):
        self.init = init    # Inicialización
        self.test = test    # Condición
        self.update = update  # Actualización
        self.body = body    # Cuerpo

    def __repr__(self):
        return f"For({self.init}, {self.test}, {self.update}, {self.body})"

class Block(ASTNode):
    """Representa un bloque de sentencias (entre llaves {})."""
    def __init__(self, statements):
        self.statements = statements  # Lista de sentencias

    def __repr__(self):
        return f"Block({self.statements})"

class Break(ASTNode):
    """Representa una sentencia break."""
    def __repr__(self):
        return "Break()"

class Continue(ASTNode):
    """Representa una sentencia continue."""
    def __repr__(self):
        return "Continue()"

# ---------------------------------------------------------------------
# Otros
# ---------------------------------------------------------------------

class SymbolTable:
    """Maneja tablas de símbolos para variables y funciones."""
    def __init__(self):
        self.scopes = [{}]  # Pila de ámbitos (scopes)

    def declare_variable(self, name, var_type, value=None):
        """Declara una variable en el ámbito actual."""
        self.scopes[-1][name] = {'type': var_type, 'value': value}

    def declare_constant(self, name, value):
        """Declara una constante en el ámbito actual."""
        self.scopes[-1][name] = {'type': type(value).__name__, 'value': value}

    def lookup(self, name):
        """Busca un símbolo en los ámbitos (del más interno al más externo)."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

class Parameter(ASTNode):
    """Representa un parámetro de función."""
    def __init__(self, name, param_type):
        self.name = name        # Nombre del parámetro
        self.param_type = param_type  # Tipo del parámetro

    def __repr__(self):
        return f"Parameter({self.name}, {self.param_type})"

class Program(ASTNode):
    """Nodo raíz que representa un programa completo."""
    def __init__(self, statements):
        self.statements = statements  # Lista de sentencias

    def __repr__(self):
        return f"Program({self.statements})"

class ImportDecl(ASTNode):
    """Representa una declaración de importación (ej. import miModulo;)."""
    def __init__(self, module_name):
        self.module_name = module_name  # Nombre del módulo

    def __repr__(self):
        return f"ImportDecl({self.module_name})"

class FunctionImportDecl(ASTNode):
    """Representa la importación de una función con su firma."""
    def __init__(self, module_name, params, return_type):
        self.module_name = module_name  # Nombre del módulo
        self.params = params           # Parámetros
        self.return_type = return_type  # Tipo de retorno

    def __repr__(self):
        return f"FunctionImportDecl({self.module_name}, {self.params}, {self.return_type})"