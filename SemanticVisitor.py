# SemanticVisitor.py (versión corregida)
from SymbolInfo import *
from Types import Types
from ASTnodes import *
from Symboltab import *

class SemanticVisitor(ASTVisitor):
    """Visitor para análisis semántico: construcción de tabla de símbolos y verificación de tipos"""
    
    def __init__(self):
        super().__init__()
        self.current_scope = None
        self.errors = []
        self.warnings = []
    
    def visit(self, node, *args, **kwargs):
        """Método dispatcher principal mejorado"""
        try:
            if node is None:
                return None
            return super().visit(node, *args, **kwargs)
        except NotImplementedError as e:
            self.errors.append(str(e))
            return False
    
    def generic_visit(self, node, *args, **kwargs):
        """Método por defecto si no se encuentra un visitor específico"""
        node_name = type(node).__name__
        error_msg = f"Error semántico: No hay visitor implementado para {node_name}"
        self.errors.append(error_msg)
        return False
    
    def visit_Program(self, node, *args, **kwargs):
        # Ámbito global
        global_scope = SymbolTab("global", None)
        self.current_scope = global_scope
        node.global_scope = global_scope
        
        # Procesar todas las declaraciones globales
        for stmt in node.statements:
            self.visit(stmt)
        
        # Verificar que exista una función main
        main_symbol = global_scope.get('main')
        if not main_symbol or not isinstance(main_symbol, FunctionSymbol):
            has_functions = any(isinstance(stmt, FunctionDecl) for stmt in node.statements)
            if has_functions:
                self.warnings.append("Advertencia: función 'main' no definida")
        
        node.symbol = global_scope
        return len(self.errors) == 0
    
    def visit_FunctionDecl(self, node, *args, **kwargs):
        # Crear símbolo de la función
        func_symbol = node.create_symbol()
        
        try:
            self.current_scope.add(node.name, func_symbol)
            node.symbol = func_symbol
        except SymbolTab.SymbolDefinedError:
            self.errors.append(f"Función '{node.name}' ya está definida")
            return False
        
        # Crear nuevo ámbito para la función
        function_scope = SymbolTab(node.name, self.current_scope, "function")
        self.current_scope = function_scope
        func_symbol.local_symbols = function_scope
        node.local_scope = function_scope
        
        # Registrar parámetros
        for param in node.params:
            param_symbol = SymbolFactory.create('var', 
                                             name=param.name,
                                             dtype=param.param_type,
                                             is_param=True)
            function_scope.add(param.name, param_symbol)
            param.symbol = param_symbol
        
        # Procesar cuerpo de la función
        for stmt in node.body:
            self.visit(stmt)
        
        # Verificar tipo de retorno
        if node.return_type != 'void':
            last_stmt = node.body[-1] if node.body else None
            if not isinstance(last_stmt, Return):
                self.errors.append(f"Función '{node.name}' debe retornar un valor")
        
        # Volver al ámbito padre
        self.current_scope = function_scope.parent
        return len(self.errors) == 0
    
    def visit_VariableDecl(self, node, *args, **kwargs):
        # Verificar tipo válido
        if not Types.is_valid_type(node.var_type):
            self.errors.append(f"Tipo inválido '{node.var_type}' en declaración de '{node.name}'")
            return False
        
        # Crear símbolo
        var_symbol = node.create_symbol()
        
        try:
            self.current_scope.add(node.name, var_symbol)
            node.symbol = var_symbol
        except SymbolTab.SymbolDefinedError:
            self.errors.append(f"Variable '{node.name}' ya está definida")
            return False
        except SymbolTab.SymbolConflictError:
            self.errors.append(f"Conflicto de tipos para variable '{node.name}'")
            return False
        
        # Verificar inicialización
        if node.value:
            self.visit(node.value)
            if node.value.type and not Types.get_wider_type(node.var_type, node.value.type):
                self.errors.append(
                    f"Tipo incompatible en inicialización de '{node.name}': " +
                    f"esperado {node.var_type}, encontrado {node.value.type}")
        
        return True
    
    def visit_BinOp(self, node):
        # Procesar operandos
        self.visit(node.left)   # Cambiar a visit()
        self.visit(node.right)  # Cambiar a visit()
        
        # Verificar tipos
        result_type = Types.check_binop(node.op, node.left.type, node.right.type)
        if not result_type:
            self.errors.append(
                f"Operación binaria inválida: {node.left.type} {node.op} {node.right.type}")
            return False
        
        node.type = result_type
        return True
    
    def visit_Print(self, node, *args, **kwargs):
        """Visitor para la sentencia print"""
        if node.expr:
            # Visitar la expresión que se va a imprimir
            self.visit(node.expr)
            
            # Verificar que sea un tipo imprimible
            if hasattr(node.expr, 'type'):
                if node.expr.type not in ['int', 'float', 'string', 'char', 'bool']:
                    self.errors.append(
                        f"No se puede imprimir valor de tipo '{node.expr.type}'"
                    )
                    return False
        return True
    def visit_While(self, node, *args, **kwargs):
        """Visitor para la sentencia while"""
        # Verificar la condición
        self.visit(node.test)
        if hasattr(node.test, 'type') and node.test.type != 'bool':
            self.errors.append("La condición del while debe ser booleana")
        
        # Nuevo ámbito para el cuerpo del while
        while_scope = SymbolTab("while_block", self.current_scope)
        self.current_scope = while_scope
        
        # Visitar el cuerpo
        self.visit(node.body)
        
        # Volver al ámbito padre
        self.current_scope = while_scope.parent
        return True
    def visit_RelOp(self, node):
        """Visitor para operadores relacionales (<, <=, >, >=, ==, !=)"""
        self.visit(node.left)
        self.visit(node.right)
        
        # Los operadores relacionales requieren tipos compatibles
        left_type = getattr(node.left, 'type', None)
        right_type = getattr(node.right, 'type', None)
        
        if not left_type or not right_type:
            self.errors.append("Tipos no definidos en operación relacional")
            return False
            
        # Verificar compatibilidad de tipos para operadores relacionales
        compatible_types = [
            ('int', 'int'), ('float', 'float'), ('int', 'float'), ('float', 'int'),
            ('char', 'char'), ('string', 'string'), ('bool', 'bool')
        ]
        
        if (left_type, right_type) not in compatible_types and (right_type, left_type) not in compatible_types:
            self.errors.append(
                f"Tipos incompatibles en operación relacional: {left_type} {node.op} {right_type}")
            return False
        
        # Los operadores relacionales siempre devuelven bool
        node.type = 'bool'
        return True
    
    def visit_CompareOp(self, node):
        """Visitor para operadores de comparación - alias de RelOp"""
        self.visit(node.left)
        self.visit(node.right)
        
        # Los operadores relacionales requieren tipos compatibles
        left_type = getattr(node.left, 'type', None)
        right_type = getattr(node.right, 'type', None)
        
        if not left_type or not right_type:
            self.errors.append("Tipos no definidos en operación de comparación")
            return False
            
        # Verificar compatibilidad de tipos para operadores relacionales
        # Permitir comparaciones entre tipos compatibles
        op = getattr(node, 'op', getattr(node, 'operator', '?'))
        
        if left_type == right_type:
            # Mismo tipo siempre es compatible
            compatible = True
        elif left_type in ['int', 'float'] and right_type in ['int', 'float']:
            # int y float son compatibles entre sí
            compatible = True
        else:
            compatible = False
            
        if not compatible:
            self.errors.append(
                f"Tipos incompatibles en operación de comparación: {left_type} {op} {right_type}")
            return False
        
        # Los operadores de comparación siempre devuelven bool
        node.type = 'bool'
        return True
    
    # Nuevo: Visitor para operadores lógicos con short-circuit
    def visit_LogicalOr(self, node):
        """Visitor para operador OR lógico (||) con evaluación de cortocircuito"""
        self.visit(node.left)
        
        # Verificar que el operando izquierdo sea booleano
        if hasattr(node.left, 'type') and node.left.type != 'bool':
            self.errors.append(f"Operando izquierdo de || debe ser booleano, encontrado {node.left.type}")
        
        # Para short-circuit, el operando derecho solo se evalúa si es necesario
        # Pero para análisis semántico, debemos procesarlo para verificar tipos
        self.visit(node.right)
        
        if hasattr(node.right, 'type') and node.right.type != 'bool':
            self.errors.append(f"Operando derecho de || debe ser booleano, encontrado {node.right.type}")
        
        node.type = 'bool'
        return True
    
    def visit_LogicalAnd(self, node):
        """Visitor para operador AND lógico (&&) con evaluación de cortocircuito"""
        self.visit(node.left)
        
        # Verificar que el operando izquierdo sea booleano
        if hasattr(node.left, 'type') and node.left.type != 'bool':
            self.errors.append(f"Operando izquierdo de && debe ser booleano, encontrado {node.left.type}")
        
        # Para short-circuit, el operando derecho solo se evalúa si es necesario
        # Pero para análisis semántico, debemos procesarlo para verificar tipos
        self.visit(node.right)
        
        if hasattr(node.right, 'type') and node.right.type != 'bool':
            self.errors.append(f"Operando derecho de && debe ser booleano, encontrado {node.right.type}")
        
        node.type = 'bool'
        return True
    
    # NUEVO: Visitor para LogicalOp genérico
    def visit_LogicalOp(self, node):
        """Visitor para operadores lógicos genéricos (&&, ||)"""
        self.visit(node.left)
        self.visit(node.right)
        
        # Verificar que ambos operandos sean booleanos
        left_type = getattr(node.left, 'type', None)
        right_type = getattr(node.right, 'type', None)
        
        if left_type != 'bool':
            self.errors.append(f"Operando izquierdo de {node.op} debe ser booleano, encontrado {left_type}")
        
        if right_type != 'bool':
            self.errors.append(f"Operando derecho de {node.op} debe ser booleano, encontrado {right_type}")
        
        # Los operadores lógicos siempre devuelven bool
        node.type = 'bool'
        return True
    
    # NUEVO: Visitor para UnaryOp
    def visit_UnaryOp(self, node):
        """Visitor para operadores unarios (+, -, !, *)"""
        self.visit(node.operand)
        
        operand_type = getattr(node.operand, 'type', None)
        
        if node.op == '!':
            # NOT lógico requiere operando booleano
            if operand_type != 'bool':
                self.errors.append(f"Operador ! requiere operando booleano, encontrado {operand_type}")
                return False
            node.type = 'bool'
        elif node.op in ['+', '-']:
            # Más y menos unario requieren operandos numéricos
            if operand_type not in ['int', 'float']:
                self.errors.append(f"Operador {node.op} requiere operando numérico, encontrado {operand_type}")
                return False
            node.type = operand_type  # Mismo tipo que el operando
        elif node.op == '*':
            # Desreferenciación de puntero (si se soporta)
            # Por ahora asumimos que es válido
            node.type = operand_type
        else:
            self.errors.append(f"Operador unario desconocido: {node.op}")
            return False
        
        return True
    
    # NUEVO: Visitor para Float (literal)
    def visit_Float(self, node):
        """Visitor para literales de punto flotante"""
        node.type = 'float'
        return True
    
    # NUEVO: Visitor para Boolean (literal)
    def visit_Boolean(self, node):
        """Visitor para literales booleanos"""
        node.type = 'bool'
        return True
    
    # NUEVO: Visitor para Integer (literal)
    def visit_Integer(self, node):
        """Visitor para literales enteros"""
        node.type = 'int'
        return True
    
    # NUEVO: Visitor para String (literal)
    def visit_String(self, node):
        """Visitor para literales de cadena"""
        node.type = 'string'
        return True
    
    def visit_Literal(self, node):
        """Visitor para literales (números, strings, booleanos)"""
        # El tipo ya debería estar asignado por el parser
        if not hasattr(node, 'type'):
            if isinstance(node.value, bool):
                node.type = 'bool'
            elif isinstance(node.value, int):
                node.type = 'int'
            elif isinstance(node.value, float):
                node.type = 'float'
            elif isinstance(node.value, str):
                node.type = 'string'
        return True
    
    def visit_Char(self, node):
        """Visitor para literales de caracteres"""
        node.type = 'char'
        return True
    
    def visit_CharLiteral(self, node):
        """Visitor alternativo para literales de caracteres"""
        node.type = 'char'
        return True
    
    def visit_Assignment(self, node):
        # Verificar que el lado izquierdo sea una ubicación válida
        if not isinstance(node.location, Location):
            self.errors.append("Lado izquierdo de asignación debe ser una ubicación")
            return False
        
        self.visit(node.location)  # Cambiar a visit()
        self.visit(node.expr)      # Cambiar a visit()
        
        # Verificar tipos compatibles
        if not node.location.type:
            self.errors.append(f"Variable '{node.location.name}' no declarada")
            return False
        
        if not Types.get_wider_type(node.location.type, node.expr.type):
            self.errors.append(
                f"Tipos incompatibles en asignación: " +
                f"{node.location.type} = {node.expr.type}")
            return False
        
        return True
    
    def visit_Location(self, node):
        # Resolver símbolo
        if not node.resolve_symbol(self.current_scope):
            self.errors.append(f"Variable '{node.name}' no declarada")
            return False
        return True
    
    def visit_If(self, node, *args, **kwargs):
        # Verificar condición
        self.visit(node.test)
        if hasattr(node.test, 'type') and node.test.type != 'bool':
            self.errors.append("La condición del if debe ser booleana")
        
        # Nuevo ámbito para el bloque then
        then_scope = SymbolTab("if_block", self.current_scope)
        self.current_scope = then_scope
        self.visit(node.consequence)
        self.current_scope = then_scope.parent
        
        # Bloque else si existe
        if node.alternative:
            else_scope = SymbolTab("else_block", self.current_scope)
            self.current_scope = else_scope
            self.visit(node.alternative)
            self.current_scope = else_scope.parent
        
        return True
    
    def visit_Block(self, node, *args, **kwargs):
        # Nuevo ámbito para el bloque
        block_scope = SymbolTab("block", self.current_scope)
        self.current_scope = block_scope
        
        for stmt in node.statements:
            self.visit(stmt)
        
        self.current_scope = block_scope.parent
        return True

    def print_errors(self):
        """Imprime todos los errores encontrados"""
        if not self.errors:
            print("Análisis semántico completado sin errores")
            return
        
        print("\nErrores semánticos encontrados:")
        for error in self.errors:
            print(f"- {error}")
        
        if self.warnings:
            print("\nAdvertencias:")
            for warning in self.warnings:
                print(f"- {warning}")