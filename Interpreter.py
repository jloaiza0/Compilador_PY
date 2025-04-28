from ASTnodes import *
from Symboltab import SimbolTab
from Types import typenames

class Interpreter:
    def __init__(self):
        # Diccionario para almacenar variables globales
        self.globals = {}             
        # Memoria simulada (1MB) para operaciones de bajo nivel
        self.memory = bytearray(1<<20)  
        # Tabla de símbolos global
        self.symtab = SimbolTab("global")

    def visit_Program(self, node):
        """
        Visita el nodo raíz del programa.
        Procesa todas las declaraciones y ejecuta main() si existe.
        """
        # Procesa todas las declaraciones (constantes, variables, funciones)
        for d in node.decls:
            self.visit(d)
        
        # Si existe una función main, la ejecuta
        if "main" in self.symtab:
            return self.call_func("main", [])
    
    def visit_VarDecl(self, node):
        """
        Procesa declaración de variable.
        Si tiene valor inicial lo evalúa, sino asigna valor por defecto.
        """
        value = self.visit(node.init) if node.init else self.default_value(node.vtype)
        self.globals[node.name] = value  # Almacena en variables globales
        self.symtab.add(node.name, node)  # Registra en tabla de símbolos

    def visit_ConstDecl(self, node):
        """Procesa declaración de constante y almacena su valor."""
        value = self.visit(node.value)
        self.globals[node.name] = value
        self.symtab.add(node.name, node)

    def visit_FuncDecl(self, node):
        """Registra la función en la tabla de símbolos."""
        self.symtab.add(node.name, node)

    def call_func(self, name, args):
        """
        Ejecuta una función con los argumentos proporcionados.
        
        Args:
            name: Nombre de la función
            args: Lista de argumentos
            
        Returns:
            El valor de retorno de la función (None si no retorna nada)
        """
        f = self.symtab.get(name)  # Obtiene la definición de la función
        frame = {}  # Nuevo ámbito para los parámetros y variables locales
        
        # Asigna los valores de los parámetros
        for (p, _), a in zip(f.params, args):
            frame[p] = a
            
        # Ejecuta el cuerpo de la función
        try:
            return self._exec_block(f.body, frame)
        except ReturnException as ret:
            return ret.value  # Captura el valor de retorno

    def _exec_block(self, stmts, frame):
        """
        Ejecuta un bloque de instrucciones en un nuevo ámbito.
        
        Args:
            stmts: Lista de instrucciones del bloque
            frame: Diccionario con variables locales
        """
        old = self.globals
        # Combina globales con el nuevo ámbito (las locales sobrescriben)
        self.globals = {**old, **frame}  
        
        # Ejecuta cada instrucción del bloque
        for s in stmts:
            self.visit(s)
            
        # Restaura el ámbito anterior
        self.globals = old  

    def visit_Return(self, node):
        """Procesa una sentencia return lanzando una excepción especial."""
        val = self.visit(node.value)
        raise ReturnException(val)  # Usamos excepción para propagar el valor

    def visit_If(self, node):
        """Ejecuta condicional if-else."""
        cond = self.visit(node.cond)
        if cond:
            self._exec_block(node.then_block, {})
        elif node.else_block:
            self._exec_block(node.else_block, {})

    def visit_While(self, node):
        """Ejecuta bucle while."""
        while self.visit(node.cond):
            self.visit_Block(node.body)

    def visit_Assign(self, node):
        """Procesa asignación a variable o memoria."""
        val = self.visit(node.value)
        if node.target.is_memory:
            # Asignación a dirección de memoria
            addr = self.visit(node.target.addr)
            self._write_mem(addr, val)
        else:
            # Asignación a variable
            self.globals[node.target.name] = val

    def visit_MemRead(self, node):
        """Lee un valor de la memoria simulada."""
        addr = self.visit(node.addr)
        return self._read_mem(addr)

    def visit_BinOp(self, node):
        """Evalúa una operación binaria."""
        l = self.visit(node.left)
        r = self.visit(node.right)
        return _eval_binop(node.op, l, r)

    def visit_UnaryOp(self, node):
        """Evalúa una operación unaria."""
        v = self.visit(node.operand)
        return _eval_unary(node.op, v)

    def visit_Literal(self, node):
        """Devuelve el valor de un literal."""
        return node.value

    def visit_Ident(self, node):
        """Obtiene el valor de un identificador (variable/constante)."""
        return self.globals[node.name]

    def visit_Print(self, node):
        """Evalúa e imprime una expresión."""
        v = self.visit(node.expr)
        print(v)

    def _read_mem(self, addr):
        """Lee 4 bytes de la memoria simulada (little endian)."""
        return int.from_bytes(self.memory[addr:addr+4], 'little')

    def _write_mem(self, addr, val):
        """Escribe 4 bytes en la memoria simulada (little endian)."""
        self.memory[addr:addr+4] = int(val).to_bytes(4, 'little')

class ReturnException(Exception):
    """Excepción especial para manejar sentencias return."""
    def __init__(self, value):
        self.value = value

# Funciones auxiliares para operaciones
def _eval_binop(op, a, b):
    """Evalúa operaciones binarias."""
    return {
      '+': a+b, '-': a-b, '*': a*b, 
      '/': a//b if isinstance(a,int) else a/b,  # División entera o flotante
      '<': a<b, '<=': a<=b, '>': a>b, '>=': a>=b, 
      '==': a==b, '!=': a!=b,
      '&&': a and b, '||': a or b
    }[op]

def _eval_unary(op, a):
    """Evalúa operaciones unarias."""
    return {
      '+': +a, '-': -a, '!': not a
    }[op]