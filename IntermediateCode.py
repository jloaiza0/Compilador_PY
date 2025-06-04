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
        return SymbolFactory.create_temp(dtype)
    
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
            'params': [(p.name, p.param_type) for p in node.params],
            'return_type': node.return_type,
            'local_vars': {},
            'temp_vars': {}
        }
        self.function_directory[node.name] = func_entry
        self.current_function = node.name
        
        # Generar cuádruplo de inicio de función
        self.add_quadruple(Operation.ENDFUNC)  # Marcador de posición
        
        # Procesar parámetros y cuerpo
        for param in node.params:
            func_entry['local_vars'][param.name] = param.param_type
        
        node.body.accept(self)
        
        # Si no hay return explícito, añadir uno para funciones void
        if node.return_type == 'void' and (not self.quadruples or self.quadruples[-1].op != Operation.RETURN):
            self.add_quadruple(Operation.RETURN, None, None, None)
        
        # Actualizar marcador de posición con el índice correcto
        start_quad = func_entry['start_quad']
        self.quadruples[start_quad] = Quadruple(Operation.ENDFUNC, None, None, node.name)
    
    def visit_BinOp(self, node):
        # Procesar operandos
        node.left.accept(self)
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
        
        # Generar temporal para resultado
        temp = self.generate_temp(node.type)
        self.function_directory[self.current_function]['temp_vars'][temp.name] = temp.dtype
        
        # Generar cuádruplo
        self.add_quadruple(op_mapping[node.op], node.left.temp_var, node.right.temp_var, temp)
        node.temp_var = temp
    
    def visit_Assignment(self, node):
        # Procesar expresión
        node.expr.accept(self)
        
        # Verificar que la ubicación existe
        if not node.location.symbol:
            raise Exception(f"Variable '{node.location.name}' no declarada")
        
        # Generar cuádruplo de asignación
        self.add_quadruple(Operation.ASSIGN, node.expr.temp_var, None, node.location.symbol)
    
    def visit_If(self, node):
        # Procesar condición
        node.test.accept(self)
        
        # Generar etiquetas
        false_label = self.new_label()
        end_label = self.new_label()
        
        # Cuádruplo condicional
        self.add_quadruple(Operation.GOTOF, node.test.temp_var, None, false_label)
        
        # Bloque then
        node.consequence.accept(self)
        self.add_quadruple(Operation.GOTO, None, None, end_label)
        
        # Bloque else (si existe)
        self.add_quadruple(Operation.LABEL, None, None, false_label)
        if node.alternative:
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
        node.test.accept(self)
        self.add_quadruple(Operation.GOTOF, node.test.temp_var, None, end_label)
        
        # Bloque del cuerpo
        node.body.accept(self)
        
        # Volver al inicio
        self.add_quadruple(Operation.GOTO, None, None, start_label)
        
        # Etiqueta de fin
        self.add_quadruple(Operation.LABEL, None, None, end_label)
    
    def visit_Return(self, node):
        if node.expr:
            node.expr.accept(self)
            self.add_quadruple(Operation.RETURN, None, None, node.expr.temp_var)
        else:
            self.add_quadruple(Operation.RETURN, None, None, None)
    
    def visit_FunctionCall(self, node):
        # Procesar argumentos
        for arg in node.args:
            arg.accept(self)
            self.add_quadruple(Operation.PARAM, arg.temp_var, None, f"param{self.param_counter}")
            self.param_counter += 1
        
        # Generar temporal para el resultado (si no es void)
        func_info = self.function_directory.get(node.name)
        if not func_info:
            raise Exception(f"Función '{node.name}' no definida")
        
        if func_info['return_type'] != 'void':
            temp = self.generate_temp(func_info['return_type'])
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
        self.add_quadruple(Operation.ASSIGN, node.value, None, temp)
        node.temp_var = temp
    
    def visit_Float(self, node):
        temp = self.generate_temp('float')
        self.add_quadruple(Operation.ASSIGN, node.value, None, temp)
        node.temp_var = temp
    
    def visit_Location(self, node):
        if not node.symbol:
            raise Exception(f"Variable '{node.name}' no declarada")
        node.temp_var = node.symbol
    
    def print_quads(self):
        """Imprime todos los cuádruplos generados"""
        print("\nCódigo Intermedio (Cuádruplos):")
        print("-" * 50)
        for i, quad in enumerate(self.quadruples):
            print(f"{i:4d} | {quad}")