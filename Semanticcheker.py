from Types import typenames, check_binop, check_unaryop
from ASTnodes import *
from Symboltab import SymbolTab
from Error import ErrorHandler

class Checker:
    def __init__(self):
        # Tabla de símbolos global para almacenar variables, constantes y funciones
        self.env = SymbolTab("global")
        # Manejador de errores semánticos
        self.errors = ErrorHandler()
        # Pila para llevar control de los tipos de retorno en funciones anidadas
        self.return_types: list[str | None] = []
        # Contador de niveles de anidamiento de bucles (para break/continue)
        self.loop_level = 0

    def check(self, prog: Program):
        """Método principal que inicia el análisis semántico del programa"""
        prog.accept(self, self.env)
        return self.errors

    # Visita el nodo Program (raíz del AST)
    def visit_Program(self, node: Program, env: SymbolTab):
        # Visita cada una de las declaraciones/instrucciones del programa
        for stmt in node.statements:
            stmt.accept(self, env)

    # Declaraciones
    def visit_VariableDecl(self, node: VariableDecl, env: SymbolTab):
        # Verifica si la variable ya fue declarada
        if node.name in env.entries:
            self.errors.add_semantic_error(f"Variable '{node.name}' redeclarada",
                                          getattr(node, 'lineno', None))
            return
        
        # Si tiene valor inicial, verifica que el tipo coincida
        if node.value:
            vtype = node.value.accept(self, env)
            if vtype != node.var_type:
                self.errors.add_semantic_error(
                    f"Inicializador de tipo '{vtype}' no coincide con declarado '{node.var_type}'",
                    getattr(node, 'lineno', None))
        # Registra la variable en la tabla de símbolos
        env.add(node.name, node)

    def visit_ConstantDecl(self, node: ConstantDecl, env: SymbolTab):
        # Verifica si la constante ya fue declarada
        if node.name in env.entries:
            self.errors.add_semantic_error(f"Constante '{node.name}' redeclarada",
                                          getattr(node, 'lineno', None))
            return
        # Obtiene el tipo del valor de la constante
        ctype = node.value.accept(self, env)
        # Registra la constante en la tabla de símbolos
        env.add(node.name, node)

    def visit_FunctionDecl(self, node: FunctionDecl, env: SymbolTab):
        # Verifica si la función ya fue declarada
        if node.name in env.entries:
            self.errors.add_semantic_error(f"Función '{node.name}' redeclarada",
                                          getattr(node, 'lineno', None))
            return
        # Registra la función en la tabla de símbolos
        env.add(node.name, node)
        # Crea un nuevo ámbito para los parámetros y variables locales
        fn_env = SymbolTab(node.name, parent=env)
        
        # Registra los parámetros en el nuevo ámbito
        for p in node.params:
            if p.name in fn_env.entries:
                self.errors.add_semantic_error(f"Parámetro '{p.name}' redeclarado",
                                              getattr(node, 'lineno', None))
            else:
                fn_env.add(p.name, p)
        
        # Apila el tipo de retorno de la función
        self.return_types.append(node.return_type)
        # Analiza el cuerpo de la función
        for stmt in node.body.statements:
            stmt.accept(self, fn_env)
        # Desapila el tipo de retorno
        self.return_types.pop()

    def visit_Parameter(self, node: Parameter, env: SymbolTab):
        # Simplemente retorna el tipo del parámetro (ya registrado en visit_FunctionDecl)
        return node.param_type

    # Instrucciones (statements)
    def visit_Assignment(self, node: Assignment, env: SymbolTab):
        # Verifica si la variable está declarada
        if not env.get(node.location.name):
            self.errors.add_semantic_error(
                f"Asignación a no declarada '{node.location.name}'",
                getattr(node, 'lineno', None))
            return None
        
        # Obtiene el tipo esperado (de la declaración)
        expected = None
        sym = env.get(node.location.name)
        if isinstance(sym, VariableDecl):
            expected = sym.var_type
        elif isinstance(sym, ConstantDecl):
            expected = sym.value.accept(self, env)
        
        # Obtiene el tipo de la expresión asignada
        actual = node.expr.accept(self, env)
        
        # Verifica compatibilidad de tipos
        if expected and actual != expected:
            self.errors.add_semantic_error(
                f"No se puede asignar '{actual}' a '{expected}'",
                getattr(node, 'lineno', None))
        return expected

    def visit_Print(self, node: Print, env: SymbolTab):
        # Simplemente visita la expresión a imprimir
        node.expr.accept(self, env)

    def visit_If(self, node: If, env: SymbolTab):
        # Verifica que la condición sea de tipo booleano
        cond = node.test.accept(self, env)
        if cond != 'bool':
            self.errors.add_semantic_error(
                f"Condición de if debe ser 'bool', no '{cond}'",
                getattr(node, 'lineno', None))
        
        # Visita el bloque 'then'
        for stmt in node.consequence.statements:
            stmt.accept(self, env)
        
        # Visita el bloque 'else' si existe
        if node.alternative:
            for stmt in node.alternative.statements:
                stmt.accept(self, env)

    def visit_While(self, node: While, env: SymbolTab):
        # Verifica que la condición sea booleana
        cond = node.test.accept(self, env)
        if cond != 'bool':
            self.errors.add_semantic_error(
                f"Condición de while debe ser 'bool', no '{cond}'",
                getattr(node, 'lineno', None))
        
        # Incrementa el nivel de anidamiento de bucles
        self.loop_level += 1
        # Visita el cuerpo del bucle
        for stmt in node.body.statements:
            stmt.accept(self, env)
        # Decrementa el nivel al salir
        self.loop_level -= 1

    def visit_Break(self, node: Break, env: SymbolTab):
        # Verifica que el break esté dentro de un bucle
        if self.loop_level == 0:
            self.errors.add_semantic_error("Break fuera de bucle",
                                          getattr(node, 'lineno', None))

    def visit_Continue(self, node: Continue, env: SymbolTab):
        # Verifica que el continue esté dentro de un bucle
        if self.loop_level == 0:
            self.errors.add_semantic_error("Continue fuera de bucle",
                                          getattr(node, 'lineno', None))

    def visit_Return(self, node: Return, env: SymbolTab):
        # Obtiene el tipo de la expresión de retorno
        actual = node.expr.accept(self, env)
        # Obtiene el tipo esperado (de la declaración de función)
        expected = self.return_types[-1] if self.return_types else None
        
        # Verifica compatibilidad de tipos
        if expected and actual != expected:
            self.errors.add_semantic_error(
                f"Return de tipo '{actual}' no coincide con '{expected}'",
                getattr(node, 'lineno', None))

    # Expresiones
    def visit_Integer(self, node: Integer, env: SymbolTab):
        return 'int'

    def visit_Float(self, node: Float, env: SymbolTab):
        return 'float'

    def visit_String(self, node: String, env: SymbolTab):
        return 'string'

    def visit_Char(self, node: Char, env: SymbolTab):
        return 'char'

    def visit_Boolean(self, node: Boolean, env: SymbolTab):
        return 'bool'

    def visit_BinOp(self, node: BinOp, env: SymbolTab):
        # Obtiene tipos de los operandos
        l = node.left.accept(self, env)
        r = node.right.accept(self, env)
        # Verifica si la operación es válida para estos tipos
        res = check_binop(node.op, l, r)
        if res is None:
            self.errors.add_semantic_error(
                f"Operación binaria inválida: {l} {node.op} {r}",
                getattr(node, 'lineno', None))
        return res

    def visit_UnaryOp(self, node: UnaryOp, env: SymbolTab):
        # Obtiene tipo del operando
        v = node.operand.accept(self, env)
        # Verifica si la operación unaria es válida para este tipo
        res = check_unaryop(node.op, v)
        if res is None:
            self.errors.add_semantic_error(
                f"Operación unaria inválida: {node.op}{v}",
                getattr(node, 'lineno', None))
        return res

    def visit_TypeCast(self, node: TypeCast, env: SymbolTab):
        # Verifica que el tipo destino sea válido
        if node.target_type not in typenames:
            self.errors.add_semantic_error(
                f"Casteo a tipo desconocido '{node.target_type}'",
                getattr(node, 'lineno', None))
        return node.target_type

    def visit_FunctionCall(self, node: FunctionCall, env: SymbolTab):
        # Busca la función en la tabla de símbolos
        fn = env.get(node.name)
        if not fn or not isinstance(fn, FunctionDecl):
            self.errors.add_semantic_error(
                f"Llamada a función no definida '{node.name}'",
                getattr(node, 'lineno', None))
            return None
        
        # Verifica que el número de argumentos coincida con los parámetros
        if len(node.args) != len(fn.params):
            self.errors.add_semantic_error(
                f"Aridad incorrecta en '{node.name}' ({len(node.args)} vs {len(fn.params)})",
                getattr(node, 'lineno', None))
        
        # Verifica compatibilidad de tipos entre argumentos y parámetros
        for arg, param in zip(node.args, fn.params):
            at = arg.accept(self, env)
            if at != param.param_type:
                self.errors.add_semantic_error(
                    f"Arg '{param.name}' en '{node.name}' espera '{param.param_type}', recibe '{at}'",
                    getattr(node, 'lineno', None))
        return fn.return_type

    def visit_Location(self, node: Location, env: SymbolTab):
        # Busca el símbolo (variable/constante) en la tabla
        sym = env.get(node.name)
        if not sym:
            self.errors.add_semantic_error(
                f"Uso de variable no declarada '{node.name}'",
                getattr(node, 'lineno', None))
            return None
        
        # Retorna el tipo según sea variable o constante
        if isinstance(sym, VariableDecl):
            return sym.var_type
        if isinstance(sym, ConstantDecl):
            return sym.value.accept(self, env)
        return None

    # Método por defecto para nodos sin acción semántica específica
    def generic_visit(self, node, env):
        return None