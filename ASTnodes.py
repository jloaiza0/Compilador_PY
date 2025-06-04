#ASTnodes.py
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

class LiteralNode(ASTNode):
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

class BinOp(ASTNode):
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

class UnaryOp(ASTNode):
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

class Location(ASTNode):
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

class If(Statement):
    """Sentencia if con ámbito de bloque"""
    def __init__(self, test, consequence, alternative=None):
        super().__init__()
        self.test = test
        self.consequence = consequence
        self.alternative = alternative
        
    def __repr__(self):
        return f"If({self.test}, {self.consequence}, {self.alternative})"

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