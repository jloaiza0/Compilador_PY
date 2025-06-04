# ASTnodes.py
from Types import Types
from SymbolInfo import SymbolInfo, SymbolFactory

class ASTNode:
    """Clase base para todos los nodos del AST con capacidades extendidas"""
    def __init__(self):
        self.symbol = None       # Referencia al símbolo asociado en la tabla
        self.type = None         # Tipo inferido del nodo (para análisis semántico)
        self.temp_var = None     # Variable temporal asociada (para código intermedio)
        self.quad = None         # Cuádruplo inicial asociado (para generación de código)
        
    def accept(self, visitor):
        """Método para implementar el patrón Visitor"""
        method_name = f'visit_{self.__class__.__name__}'
        visitor_method = getattr(visitor, method_name, None)
        if visitor_method:
            return visitor_method(self)
        raise NotImplementedError(f"No visitor method for {self.__class__.__name__}")

# ---------------------------------------------------------------------
# Expresiones
# ---------------------------------------------------------------------

class Expression(ASTNode):
    """Clase base para todas las expresiones"""
    pass

class LiteralNode(Expression):
    """Clase base para literales"""
    def __init__(self, value):
        super().__init__()
        self.value = value

class Integer(LiteralNode):
    """Representa un literal entero (ej. 42)"""
    def __init__(self, value):
        super().__init__(value)
        self.type = 'int'
        
    def __repr__(self):
        return f"Integer({self.value})"

class Float(LiteralNode):
    """Representa un literal float (ej. 3.14)"""
    def __init__(self, value):
        super().__init__(value)
        self.type = 'float'
        
    def __repr__(self):
        return f"Float({self.value})"

class Boolean(LiteralNode):
    """Representa un literal booleano (true/false)"""
    def __init__(self, value):
        super().__init__(value)
        self.type = 'bool'
        
    def __repr__(self):
        return f"Boolean({self.value})"

class String(LiteralNode):
    """Representa un literal string"""
    def __init__(self, value):
        super().__init__(value)
        self.type = 'string'
        
    def __repr__(self):
        return f"String({self.value})"

class Char(LiteralNode):
    """Representa un literal char"""
    def __init__(self, value):
        super().__init__(value)
        self.type = 'char'
        
    def __repr__(self):
        return f"Char({self.value})"

class ArrayLiteral(LiteralNode):
    """Representa un literal de array (ej. [1, 2, 3])"""
    def __init__(self, elements):
        super().__init__(elements)
        self.elements = elements
        self.type = 'array'
        
    def __repr__(self):
        return f"ArrayLiteral({self.elements})"

class BinOp(Expression):
    """Operación binaria con verificación de tipos"""
    def __init__(self, op, left, right):
        super().__init__()
        self.op = op
        self.left = left
        self.right = right
        
    def __repr__(self):
        return f"BinOp({self.op}, {self.left}, {self.right})"
    
    def infer_type(self):
        """Infiere el tipo resultante de la operación"""
        if not self.left.type or not self.right.type:
            return None
            
        return Types.check_binop(self.op, self.left.type, self.right.type)

class CompareOp(Expression):
    """Operación de comparación (==, !=, <, >, <=, >=)"""
    def __init__(self, op, left, right):
        super().__init__()
        self.op = op
        self.left = left
        self.right = right
        self.type = 'bool'  # Las comparaciones siempre devuelven booleano
        
    def __repr__(self):
        return f"CompareOp({self.op}, {self.left}, {self.right})"
    
    def infer_type(self):
        """Infiere el tipo resultante de la comparación"""
        return 'bool'  # Siempre devuelve booleano

class LogicalOp(Expression):
    """Operación lógica (and, or)"""
    def __init__(self, op, left, right):
        super().__init__()
        self.op = op
        self.left = left
        self.right = right
        self.type = 'bool'
        
    def __repr__(self):
        return f"LogicalOp({self.op}, {self.left}, {self.right})"

class UnaryOp(Expression):
    """Operación unaria con verificación de tipos"""
    def __init__(self, op, operand):
        super().__init__()
        self.op = op
        self.operand = operand
        
    def __repr__(self):
        return f"UnaryOp({self.op}, {self.operand})"
    
    def infer_type(self):
        """Infiere el tipo resultante de la operación"""
        if not self.operand.type:
            return None
            
        return Types.check_unaryop(self.op, self.operand.type)

class Location(Expression):
    """Ubicación con referencia a símbolo"""
    def __init__(self, name):
        super().__init__()
        self.name = name
        
    def __repr__(self):
        return f"Location({self.name})"
    
    def resolve_symbol(self, symbol_table):
        """Resuelve la referencia al símbolo en la tabla"""
        self.symbol = symbol_table.get(self.name)
        if self.symbol:
            self.type = self.symbol.dtype
        return self.symbol is not None

class Dereference(Expression):
    """Desreferenciación de puntero"""
    def __init__(self, location):
        super().__init__()
        self.location = location
        
    def __repr__(self):
        return f"Dereference({self.location})"

class FunctionCall(Expression):
    """Llamada a función"""
    def __init__(self, name, args):
        super().__init__()
        self.name = name
        self.args = args
        
    def __repr__(self):
        return f"FunctionCall({self.name}, {self.args})"

class ArrayAccess(Expression):
    """Acceso a elemento de array"""
    def __init__(self, array, index):
        super().__init__()
        self.array = array
        self.index = index
        
    def __repr__(self):
        return f"ArrayAccess({self.array}, {self.index})"

# ---------------------------------------------------------------------
# Declaraciones
# ---------------------------------------------------------------------

class Declaration(ASTNode):
    """Clase base para declaraciones"""
    pass

class VariableDecl(Declaration):
    """Declaración de variable con soporte para símbolos"""
    def __init__(self, name, var_type, value=None):
        super().__init__()
        self.name = name
        self.var_type = var_type
        self.value = value
        self.type = var_type
        
    def __repr__(self):
        return f"VariableDecl({self.name}, {self.var_type}, {self.value})"
    
    def create_symbol(self):
        """Crea el símbolo asociado a esta declaración"""
        return SymbolFactory.create('var', 
                                 name=self.name,
                                 dtype=self.var_type,
                                 value=self.value.value if self.value else None)

class ConstantDecl(Declaration):
    """Declaración de constante"""
    def __init__(self, name, value):
        super().__init__()
        self.name = name
        self.value = value
        self.type = value.type if hasattr(value, 'type') else None
        
    def __repr__(self):
        return f"ConstantDecl({self.name}, {self.value})"
    
    def create_symbol(self):
        """Crea el símbolo asociado a esta declaración"""
        return SymbolFactory.create('const', 
                                 name=self.name,
                                 dtype=self.type,
                                 value=self.value.value if hasattr(self.value, 'value') else self.value)

class FunctionDecl(Declaration):
    """Declaración de función con tabla de símbolos propia"""
    def __init__(self, name, params, return_type, body):
        super().__init__()
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body
        self.type = return_type
        self.local_scope = None  # Se establecerá durante el análisis semántico
        
    def __repr__(self):
        return f"FunctionDecl({self.name}, {self.params}, {self.return_type}, {self.body})"
    
    def create_symbol(self):
        """Crea el símbolo de función con sus parámetros"""
        func_symbol = SymbolFactory.create('func',
                                         name=self.name,
                                         return_type=self.return_type)
        
        for param in self.params:
            func_symbol.add_param(param.name, param.param_type)
            
        return func_symbol

# Alias para Function - para compatibilidad con el parser
Function = FunctionDecl

class Parameter(ASTNode):
    """Parámetro de función"""
    def __init__(self, name, param_type):
        super().__init__()
        self.name = name
        self.param_type = param_type
        self.type = param_type
        
    def __repr__(self):
        return f"Parameter({self.name}, {self.param_type})"

class ImportDecl(Declaration):
    """Declaración de importación"""
    def __init__(self, module_name):
        super().__init__()
        self.module_name = module_name
        
    def __repr__(self):
        return f"ImportDecl({self.module_name})"

# Alias para Import - para compatibilidad con el parser
Import = ImportDecl

class FunctionImportDecl(Declaration):
    """Declaración de importación de función"""
    def __init__(self, module_name, params, return_type):
        super().__init__()
        self.module_name = module_name
        self.params = params
        self.return_type = return_type
        
    def __repr__(self):
        return f"FunctionImportDecl({self.module_name}, {self.params}, {self.return_type})"

class ArrayDecl(Declaration):
    """Declaración de array"""
    def __init__(self, name, element_type, size=None, values=None):
        super().__init__()
        self.name = name
        self.element_type = element_type
        self.size = size
        self.values = values
        self.type = f"array[{element_type}]"
        
    def __repr__(self):
        return f"ArrayDecl({self.name}, {self.element_type}, {self.size}, {self.values})"

# ---------------------------------------------------------------------
# Sentencias
# ---------------------------------------------------------------------

class Statement(ASTNode):
    """Clase base para sentencias"""
    pass

class Assignment(Statement):
    """Asignación con verificación de tipos"""
    def __init__(self, location, expr):
        super().__init__()
        self.location = location
        self.expr = expr
        
    def __repr__(self):
        return f"Assignment({self.location}, {self.expr})"
    
    def check_types(self):
        """Verifica compatibilidad de tipos en asignación"""
        if not self.location.type or not self.expr.type:
            return False
            
        # Permite asignación si los tipos son iguales o hay conversión implícita
        return (self.location.type == self.expr.type or 
                Types.get_wider_type(self.location.type, self.expr.type))

class Print(Statement):
    """Sentencia print"""
    def __init__(self, expr):
        super().__init__()
        self.expr = expr
        
    def __repr__(self):
        return f"Print({self.expr})"

class If(Statement):
    """Sentencia if con ámbito de bloque"""
    def __init__(self, test, consequence, alternative=None):
        super().__init__()
        self.test = test
        self.consequence = consequence
        self.alternative = alternative
        
    def __repr__(self):
        return f"If({self.test}, {self.consequence}, {self.alternative})"

class While(Statement):
    """Sentencia while"""
    def __init__(self, test, body):
        super().__init__()
        self.test = test
        self.body = body
        
    def __repr__(self):
        return f"While({self.test}, {self.body})"

class Break(Statement):
    """Sentencia break"""
    def __init__(self):
        super().__init__()
        
    def __repr__(self):
        return "Break()"

class Continue(Statement):
    """Sentencia continue"""
    def __init__(self):
        super().__init__()
        
    def __repr__(self):
        return "Continue()"

class Return(Statement):
    """Sentencia return"""
    def __init__(self, expr=None):
        super().__init__()
        self.expr = expr
        
    def __repr__(self):
        return f"Return({self.expr})"

class For(Statement):
    """Sentencia for"""
    def __init__(self, init, condition, update, body):
        super().__init__()
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body
        
    def __repr__(self):
        return f"For({self.init}, {self.condition}, {self.update}, {self.body})"

class Block(Statement):
    """Bloque de sentencias"""
    def __init__(self, statements):
        super().__init__()
        self.statements = statements
        
    def __repr__(self):
        return f"Block({self.statements})"

class ExpressionStatement(Statement):
    """Sentencia que contiene una expresión"""
    def __init__(self, expr):
        super().__init__()
        self.expr = expr
        
    def __repr__(self):
        return f"ExpressionStatement({self.expr})"

# ---------------------------------------------------------------------
# Programa
# ---------------------------------------------------------------------

class Program(ASTNode):
    """Nodo raíz del programa con tabla de símbolos global"""
    def __init__(self, statements):
        super().__init__()
        self.statements = statements
        self.global_scope = None  # Se establecerá durante el análisis semántico
        
    def __repr__(self):
        return f"Program({self.statements})"

# ---------------------------------------------------------------------
# Visitor para recorrido del AST
# ---------------------------------------------------------------------

class ASTVisitor:
    """Clase base para visitantes del AST"""
    def visit(self, node):
        return node.accept(self)