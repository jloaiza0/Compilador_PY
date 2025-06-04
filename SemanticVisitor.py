from SymbolInfo import *
from Types import Types
from ASTnodes import *
from Symboltab import *
from parser import *

class SemanticVisitor:
    """Visitor para análisis semántico: construcción de tabla de símbolos y verificación de tipos"""
    
    def __init__(self):
        self.current_scope = None
        self.errors = []
        self.warnings = []
    
    def visit_Program(self, node):
        # Ámbito global
        global_scope = SymbolTab("global", None)
        self.current_scope = global_scope
        node.global_scope = global_scope
        
        # Procesar todas las declaraciones globales
        for stmt in node.statements:
            if isinstance(stmt, (FunctionDecl, VariableDecl, ConstantDecl)):
                stmt.accept(self)
        
        # Verificar que exista una función main
        main_symbol = global_scope.get('main')
        if not main_symbol or not isinstance(main_symbol, FunctionSymbol):
            self.errors.append("Error: función 'main' no definida")
        
        node.symbol = global_scope
        return len(self.errors) == 0
    
    def visit_FunctionDecl(self, node):
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
            stmt.accept(self)
        
        # Verificar tipo de retorno
        if node.return_type != 'void':
            last_stmt = node.body[-1] if node.body else None
            if not isinstance(last_stmt, Return):
                self.errors.append(f"Función '{node.name}' debe retornar un valor")
        
        # Volver al ámbito padre
        self.current_scope = function_scope.parent
        return len(self.errors) == 0
    
    def visit_VariableDecl(self, node):
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
            node.value.accept(self)
            if not Types.get_wider_type(node.var_type, node.value.type):
                self.errors.append(
                    f"Tipo incompatible en inicialización de '{node.name}': " +
                    f"esperado {node.var_type}, encontrado {node.value.type}")
        
        return True
    
    def visit_BinOp(self, node):
        # Procesar operandos
        node.left.accept(self)
        node.right.accept(self)
        
        # Verificar tipos
        result_type = Types.check_binop(node.op, node.left.type, node.right.type)
        if not result_type:
            self.errors.append(
                f"Operación binaria inválida: {node.left.type} {node.op} {node.right.type}")
            return False
        
        node.type = result_type
        return True
    
    def visit_Assignment(self, node):
        # Verificar que el lado izquierdo sea una ubicación válida
        if not isinstance(node.location, Location):
            self.errors.append("Lado izquierdo de asignación debe ser una ubicación")
            return False
        
        node.location.accept(self)
        node.expr.accept(self)
        
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
    
    def visit_If(self, node):
        # Verificar condición
        node.test.accept(self)
        if node.test.type != 'bool':
            self.errors.append("La condición del if debe ser booleana")
        
        # Nuevo ámbito para el bloque then
        then_scope = SymbolTab("if_block", self.current_scope)
        self.current_scope = then_scope
        node.consequence.accept(self)
        self.current_scope = then_scope.parent
        
        # Bloque else si existe
        if node.alternative:
            else_scope = SymbolTab("else_block", self.current_scope)
            self.current_scope = else_scope
            node.alternative.accept(self)
            self.current_scope = else_scope.parent
        
        return True
    
    def visit_Block(self, node):
        # Nuevo ámbito para el bloque
        block_scope = SymbolTab("block", self.current_scope)
        self.current_scope = block_scope
        
        for stmt in node.statements:
            stmt.accept(self)
        
        self.current_scope = block_scope.parent
        return True
    
    def visit_Return(self, node):
        # Verificar compatibilidad con tipo de retorno de la función
        current_function = self._get_current_function()
        if not current_function:
            self.errors.append("Return fuera de función")
            return False
        
        node.expr.accept(self)
        
        if current_function.return_type == 'void' and node.expr:
            self.errors.append("Función void no debe retornar valor")
        elif current_function.return_type != 'void':
            if not node.expr:
                self.errors.append("Se esperaba valor de retorno")
            elif not Types.get_wider_type(current_function.return_type, node.expr.type):
                self.errors.append(
                    f"Tipo de retorno incompatible: " +
                    f"esperado {current_function.return_type}, " +
                    f"obtenido {node.expr.type}")
        
        return True
    
    def _get_current_function(self):
        """Obtiene la función actual basada en el ámbito"""
        scope = self.current_scope
        while scope:
            if scope.scope_type == "function":
                return scope.get(scope.name)
            scope = scope.parent
        return None

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