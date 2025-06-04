from enum import Enum
from collections import defaultdict

class StackMachine:
    """Máquina de pila para ejecutar cuádruplos generados"""
    
    def __init__(self, quadruples, function_directory):
        self.quadruples = quadruples
        self.function_directory = function_directory
        self.pc = 0  # Program Counter
        self.stack = []
        self.call_stack = []  # Para llamadas a funciones
        self.memory = defaultdict(dict)  # Memoria por ámbito
        self.temps = {}  # Variables temporales
        self.labels = {}  # Mapeo de etiquetas
        self.current_scope = "global"
        self.initialize_labels()
    
    def initialize_labels(self):
        """Preprocesa las etiquetas para saltos rápidos"""
        for idx, quad in enumerate(self.quadruples):
            if quad.op == Operation.LABEL:
                self.labels[quad.result] = idx
    
    def execute(self):
        """Ejecuta el programa completo"""
        print("\nIniciando ejecución en la máquina de pila...")
        while self.pc < len(self.quadruples):
            quad = self.quadruples[self.pc]
            self.execute_quad(quad)
            self.pc += 1
    
    def execute_quad(self, quad):
        """Ejecuta un cuádruplo individual"""
        op = quad.op
        
        # Operaciones aritméticas
        if op == Operation.ADD:
            self.handle_binary_op('+', quad)
        elif op == Operation.SUB:
            self.handle_binary_op('-', quad)
        elif op == Operation.MUL:
            self.handle_binary_op('*', quad)
        elif op == Operation.DIV:
            self.handle_binary_op('/', quad)
        elif op == Operation.MOD:
            self.handle_binary_op('%', quad)
            
        # Operaciones lógicas
        elif op == Operation.AND:
            self.handle_binary_op('and', quad)
        elif op == Operation.OR:
            self.handle_binary_op('or', quad)
        elif op == Operation.NOT:
            self.handle_unary_op('not', quad)
            
        # Comparaciones
        elif op == Operation.EQ:
            self.handle_binary_op('==', quad)
        elif op == Operation.NEQ:
            self.handle_binary_op('!=', quad)
        elif op == Operation.LT:
            self.handle_binary_op('<', quad)
        elif op == Operation.LTE:
            self.handle_binary_op('<=', quad)
        elif op == Operation.GT:
            self.handle_binary_op('>', quad)
        elif op == Operation.GTE:
            self.handle_binary_op('>=', quad)
            
        # Control de flujo
        elif op == Operation.GOTO:
            self.pc = self.labels[quad.result] - 1  # -1 por el incremento posterior
        elif op == Operation.GOTOF:
            condition = self.get_value(quad.arg1)
            if not condition:
                self.pc = self.labels[quad.result] - 1
        elif op == Operation.GOTOT:
            condition = self.get_value(quad.arg1)
            if condition:
                self.pc = self.labels[quad.result] - 1
                
        # Funciones
        elif op == Operation.CALL:
            self.handle_function_call(quad)
        elif op == Operation.PARAM:
            self.handle_parameter(quad)
        elif op == Operation.RETURN:
            self.handle_return(quad)
        elif op == Operation.ENDFUNC:
            self.handle_end_function()
            
        # Memoria
        elif op == Operation.ASSIGN:
            value = self.get_value(quad.arg1)
            self.set_value(quad.result, value)
            
        # Entrada/Salida
        elif op == Operation.PRINT:
            value = self.get_value(quad.arg1)
            print(f"Salida: {value}")
        elif op == Operation.READ:
            self.handle_read(quad)
            
        # Verificación
        elif op == Operation.VERIFY:
            self.handle_verify(quad)
    
    def handle_binary_op(self, operator, quad):
        """Maneja operaciones binarias"""
        left = self.get_value(quad.arg1)
        right = self.get_value(quad.arg2)
        
        if operator == '+': result = left + right
        elif operator == '-': result = left - right
        elif operator == '*': result = left * right
        elif operator == '/': result = left / right
        elif operator == '%': result = left % right
        elif operator == 'and': result = left and right
        elif operator == 'or': result = left or right
        elif operator == '==': result = left == right
        elif operator == '!=': result = left != right
        elif operator == '<': result = left < right
        elif operator == '<=': result = left <= right
        elif operator == '>': result = left > right
        elif operator == '>=': result = left >= right
        
        self.set_value(quad.result, result)
    
    def handle_unary_op(self, operator, quad):
        """Maneja operaciones unarias"""
        operand = self.get_value(quad.arg1)
        
        if operator == 'not': result = not operand
        elif operator == '-': result = -operand
        
        self.set_value(quad.result, result)
    
    def handle_function_call(self, quad):
        """Maneja llamadas a funciones"""
        func_name = quad.result
        func_info = self.function_directory[func_name]
        
        # Guardar estado actual
        self.call_stack.append({
            'return_pc': self.pc,
            'current_scope': self.current_scope,
            'local_memory': dict(self.memory[self.current_scope])
        })
        
        # Configurar nuevo ámbito
        self.current_scope = func_name
        self.memory[self.current_scope] = {}
        self.pc = func_info['start_quad']
    
    def handle_parameter(self, quad):
        """Pasa parámetros a una función"""
        param_value = self.get_value(quad.arg1)
        param_name = quad.result
        self.memory[self.current_scope][param_name] = param_value
    
    def handle_return(self, quad):
        """Maneja sentencias return"""
        if quad.result is not None:
            return_value = self.get_value(quad.result)
            self.stack.append(return_value)  # Guardar valor de retorno
    
    def handle_end_function(self):
        """Finaliza la ejecución de una función"""
        if not self.call_stack:
            return  # Función main terminando
            
        # Recuperar estado anterior
        context = self.call_stack.pop()
        self.pc = context['return_pc']
        self.current_scope = context['current_scope']
        self.memory[self.current_scope] = context['local_memory']
        
        # Si hay valor de retorno, guardarlo en el temporal result
        if self.stack:
            return_value = self.stack.pop()
            self.memory[self.current_scope][f"{self.current_scope}_result"] = return_value
    
    def handle_read(self, quad):
        """Maneja operaciones de lectura"""
        var_name = quad.result
        value = input(f"Ingrese valor para {var_name}: ")
        
        # Convertir al tipo adecuado
        var_info = self.get_symbol_info(var_name)
        if var_info.dtype == 'int':
            value = int(value)
        elif var_info.dtype == 'float':
            value = float(value)
        elif var_info.dtype == 'bool':
            value = bool(value)
            
        self.set_value(var_name, value)
    
    def handle_verify(self, quad):
        """Verifica límites de arreglos"""
        index = self.get_value(quad.arg1)
        limit = self.get_value(quad.arg2)
        
        if index < 0 or index >= limit:
            raise RuntimeError(f"Índice {index} fuera de límites [0, {limit-1}]")
    
    def get_value(self, source):
        """Obtiene un valor de una variable, constante o temporal"""
        if isinstance(source, (int, float, bool, str)):
            return source
            
        if isinstance(source, SymbolInfo):
            if source.is_temp:
                return self.temps.get(source.name, 0)
            return self.memory[self.current_scope].get(source.name, 0)
            
        if source in self.memory[self.current_scope]:
            return self.memory[self.current_scope][source]
            
        return 0  # Valor por defecto
    
    def set_value(self, target, value):
        """Asigna un valor a una variable o temporal"""
        if isinstance(target, SymbolInfo):
            if target.is_temp:
                self.temps[target.name] = value
            else:
                self.memory[self.current_scope][target.name] = value
        else:
            self.memory[self.current_scope][target] = value
    
    def get_symbol_info(self, symbol_name):
        """Obtiene información de un símbolo (simplificado)"""
        # En una implementación real, buscaríamos en la tabla de símbolos
        return SymbolInfo(symbol_name, 'int')  # Simplificación