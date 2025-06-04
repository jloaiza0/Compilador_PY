# IntermediateCode.py
from ASTnodes import *
from SymbolInfo import SymbolFactory
from enum import Enum, auto

class Operation(Enum):
    """Operaciones soportadas en cuádruplos"""
    ASSIGN = auto()
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()
    NEG = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    EQ = auto()
    NEQ = auto()
    LT = auto()
    LTE = auto()
    GT = auto()
    GTE = auto()
    GOTO = auto()
    GOTOF = auto()
    GOTOT = auto()
    PARAM = auto()
    CALL = auto()
    RETURN = auto()
    PRINT = auto()
    READ = auto()
    VERIFY = auto()  # Para verificación de límites de arreglos
    LABEL = auto()   # Para etiquetas
    ENDFUNC = auto() # Para marcar fin de función
    END = auto()     # Para marcar fin de programa

class Quadruple:
    """Representación de un cuádruplo (operación, op1, op2, resultado)"""
    def __init__(self, op, arg1=None, arg2=None, result=None):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result
    
    def __repr__(self):
        return f"{self.op.name.ljust(8)} {str(self.arg1).ljust(10)} {str(self.arg2).ljust(10)} -> {self.result}"

class IntermediateCodeGenerator:
    """Visitor para generar código intermedio (cuádruplos)"""
    def __init__(self):
        self.quadruples = []
        self.temp_counter = 0
        self.label_counter = 0
        self.function_directory = {}
        self.current_function = None
        self.param_counter = 0
        self.call_stack = []
    
    def generate_temp(self, dtype):
        """Genera una variable temporal"""
        self.temp_counter += 1
        return SymbolFactory.create_temp(f"t{self.temp_counter}", dtype)
    
    def new_label(self):
        """Genera una nueva etiqueta"""
        self.label_counter += 1
        return f"L{self.label_counter}"
    
    def add_quadruple(self, op, arg1=None, arg2=None, result=None):
        """Añade un cuádruplo a la lista"""
        self.quadruples.append(Quadruple(op, arg1, arg2, result))
    
    def visit_Program(self, node):
        # Procesar todas las declaraciones globales
        for stmt in node.statements:
            stmt.accept(self)
        
        # Asegurar que hay una función main
        if 'main' not in self.function_directory:
            raise Exception("Función 'main' no definida")
        
        # Generar llamada a main al final
        self.add_quadruple(Operation.CALL, None, None, 'main')
        self.add_quadruple(Operation.END)
    
    def visit_FunctionDecl(self, node):
        # Registrar función en el directorio
        func_entry = {
            'start_quad': len(self.quadruples),
            'params': [(p.name, getattr(p, 'param_type', getattr(p, 'type', 'int'))) for p in node.params],
            'return_type': getattr(node, 'return_type', 'void'),
            'local_vars': {},
            'temp_vars': {}
        }
        self.function_directory[node.name] = func_entry
        self.current_function = node.name
        
        # Generar cuádruplo de inicio de función
        start_index = len(self.quadruples)
        self.add_quadruple(Operation.ENDFUNC, None, None, node.name)
        func_entry['start_quad'] = start_index
        
        # Procesar parámetros y cuerpo
        for param in node.params:
            param_type = getattr(param, 'param_type', getattr(param, 'type', 'int'))
            func_entry['local_vars'][param.name] = param_type
        
        if hasattr(node, 'body') and node.body:
            node.body.accept(self)
        
        # Si no hay return explícito, añadir uno para funciones void
        if (getattr(node, 'return_type', 'void') == 'void' and 
            (not self.quadruples or self.quadruples[-1].op != Operation.RETURN)):
            self.add_quadruple(Operation.RETURN, None, None, None)
    
    def visit_BinOp(self, node):
        # Procesar operandos
        if hasattr(node, 'left') and node.left:
            node.left.accept(self)
        if hasattr(node, 'right') and node.right:
            node.right.accept(self)
        
        # Mapear operador a operación
        op_mapping = {
            '+': Operation.ADD,
            '-': Operation.SUB,
            '*': Operation.MUL,
            '/': Operation.DIV,
            '%': Operation.MOD,
            '&&': Operation.AND,
            '||': Operation.OR,
            '==': Operation.EQ,
            '!=': Operation.NEQ,
            '<': Operation.LT,
            '<=': Operation.LTE,
            '>': Operation.GT,
            '>=': Operation.GTE
        }
        
        if node.op not in op_mapping:
            raise Exception(f"Operador '{node.op}' no soportado")
        
        # Determinar tipo del resultado
        result_type = getattr(node, 'type', 'int')
        
        # Generar temporal para resultado
        temp = self.generate_temp(result_type)
        if self.current_function:
            self.function_directory[self.current_function]['temp_vars'][temp.name] = temp.dtype
        
        # Obtener temporales de los operandos
        left_temp = getattr(node.left, 'temp_var', node.left) if hasattr(node, 'left') else None
        right_temp = getattr(node.right, 'temp_var', node.right) if hasattr(node, 'right') else None
        
        # Generar cuádruplo
        self.add_quadruple(op_mapping[node.op], left_temp, right_temp, temp)
        node.temp_var = temp
    
    def visit_Assignment(self, node):
        # Procesar expresión
        if hasattr(node, 'expr') and node.expr:
            node.expr.accept(self)
        
        # Verificar que la ubicación existe
        if hasattr(node, 'location') and not getattr(node.location, 'symbol', None):
            raise Exception(f"Variable '{getattr(node.location, 'name', 'unknown')}' no declarada")
        
        # Generar cuádruplo de asignación
        expr_temp = getattr(node.expr, 'temp_var', node.expr) if hasattr(node, 'expr') else None
        location_symbol = getattr(node.location, 'symbol', node.location) if hasattr(node, 'location') else None
        
        self.add_quadruple(Operation.ASSIGN, expr_temp, None, location_symbol)
    
    def visit_If(self, node):
        # Procesar condición
        if hasattr(node, 'test') and node.test:
            node.test.accept(self)
        
        # Generar etiquetas
        false_label = self.new_label()
        end_label = self.new_label()
        
        # Cuádruplo condicional
        test_temp = getattr(node.test, 'temp_var', node.test) if hasattr(node, 'test') else None
        self.add_quadruple(Operation.GOTOF, test_temp, None, false_label)
        
        # Bloque then
        if hasattr(node, 'consequence') and node.consequence:
            node.consequence.accept(self)
        self.add_quadruple(Operation.GOTO, None, None, end_label)
        
        # Bloque else (si existe)
        self.add_quadruple(Operation.LABEL, None, None, false_label)
        if hasattr(node, 'alternative') and node.alternative:
            node.alternative.accept(self)
        
        # Fin de la estructura
        self.add_quadruple(Operation.LABEL, None, None, end_label)
    
    def visit_While(self, node):
        # Generar etiquetas
        start_label = self.new_label()
        end_label = self.new_label()
        
        # Guardar etiquetas para break/continue
        node.start_label = start_label
        node.end_label = end_label
        
        # Etiqueta de inicio
        self.add_quadruple(Operation.LABEL, None, None, start_label)
        
        # Procesar condición
        if hasattr(node, 'test') and node.test:
            node.test.accept(self)
        
        test_temp = getattr(node.test, 'temp_var', node.test) if hasattr(node, 'test') else None
        self.add_quadruple(Operation.GOTOF, test_temp, None, end_label)
        
        # Bloque del cuerpo
        if hasattr(node, 'body') and node.body:
            node.body.accept(self)
        
        # Volver al inicio
        self.add_quadruple(Operation.GOTO, None, None, start_label)
        
        # Etiqueta de fin
        self.add_quadruple(Operation.LABEL, None, None, end_label)
    
    def visit_Return(self, node):
        if hasattr(node, 'expr') and node.expr:
            node.expr.accept(self)
            expr_temp = getattr(node.expr, 'temp_var', node.expr)
            self.add_quadruple(Operation.RETURN, None, None, expr_temp)
        else:
            self.add_quadruple(Operation.RETURN, None, None, None)
    
    def visit_FunctionCall(self, node):
        # Procesar argumentos
        if hasattr(node, 'args'):
            for arg in node.args:
                arg.accept(self)
                arg_temp = getattr(arg, 'temp_var', arg)
                self.add_quadruple(Operation.PARAM, arg_temp, None, f"param{self.param_counter}")
                self.param_counter += 1
        
        # Generar temporal para el resultado (si no es void)
        func_info = self.function_directory.get(node.name)
        if not func_info:
            raise Exception(f"Función '{node.name}' no definida")
        
        if func_info['return_type'] != 'void':
            temp = self.generate_temp(func_info['return_type'])
            if self.current_function:
                self.function_directory[self.current_function]['temp_vars'][temp.name] = temp.dtype
            node.temp_var = temp
        else:
            node.temp_var = None
        
        # Generar llamada
        self.add_quadruple(Operation.CALL, None, None, node.name)
        
        # Guardar resultado si es necesario
        if node.temp_var:
            self.add_quadruple(Operation.ASSIGN, f"{node.name}_result", None, node.temp_var)
        
        self.param_counter = 0
    
    def visit_Integer(self, node):
        temp = self.generate_temp('int')
        if self.current_function:
            self.function_directory[self.current_function]['temp_vars'][temp.name] = temp.dtype
        
        value = getattr(node, 'value', 0)
        self.add_quadruple(Operation.ASSIGN, value, None, temp)
        node.temp_var = temp
    
    def visit_Float(self, node):
        temp = self.generate_temp('float')
        if self.current_function:
            self.function_directory[self.current_function]['temp_vars'][temp.name] = temp.dtype
        
        value = getattr(node, 'value', 0.0)
        self.add_quadruple(Operation.ASSIGN, value, None, temp)
        node.temp_var = temp
    
    def visit_Location(self, node):
        if not getattr(node, 'symbol', None):
            raise Exception(f"Variable '{getattr(node, 'name', 'unknown')}' no declarada")
        node.temp_var = node.symbol
    
    def visit_Block(self, node):
        """Visita un bloque de declaraciones"""
        if hasattr(node, 'statements'):
            for stmt in node.statements:
                if stmt:
                    stmt.accept(self)
    
    def visit_VarDecl(self, node):
        """Visita una declaración de variable"""
        # Las declaraciones de variables se manejan en el análisis semántico
        # Aquí solo necesitamos registrarlas si tienen inicialización
        if hasattr(node, 'init') and node.init:
            node.init.accept(self)
            # Crear asignación implícita
            init_temp = getattr(node.init, 'temp_var', node.init)
            var_symbol = getattr(node, 'symbol', node.name)
            self.add_quadruple(Operation.ASSIGN, init_temp, None, var_symbol)
    
    def print_quads(self):
        """Imprime todos los cuádruplos generados"""
        print("\nCódigo Intermedio (Cuádruplos):")
        print("-" * 50)
        for i, quad in enumerate(self.quadruples):
            print(f"{i:4d} | {quad}")
    
    def get_function_directory(self):
        """Retorna el directorio de funciones"""
        return self.function_directory