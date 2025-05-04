#!/usr/bin/env python3
import sys
from typing import *
from symtab import Symtab
from typesys import *
from gox_error_manager import *
from goxLang_AST_nodes import *
from parser import Parser
from lexer import Lexer

class TypeChecker:
    def __init__(self):
        self.error_manager = ErrorManager()
        self.current_function_return_type: Optional[str] = None
        self.in_loop: bool = False
        self.current_symtab: Optional[Symtab] = None
        self.show_symbol_table = True  # Control para mostrar tabla de símbolos

    def check(self, node) -> bool:
        """
        Realiza el análisis de tipos en el programa completo.
        
        Returns:
            bool: True si no hay errores de tipos, False si se encontraron errores
        """
        global_env = Symtab("global")
        self.current_symtab = global_env
        node.accept(self, global_env)
        
        # Mostrar tabla de símbolos si está habilitado
        if self.show_symbol_table:
            print("\n=== Tabla de Símbolos ===")
            global_env.print(show_all_scopes=True)
            
        return not self.error_manager.has_errors()

    def visit_Program(self, node, env):
        for stmt in node.statements:
            stmt.accept(self, env)
        return None

    def visit_VarDecl(self, node, env):
        try:
            env.add(node.name, node)
            if node.value:
                node.value.accept(self, env)
                if node.value.dtype is None:
                    self.error_manager.add_error(
                        f"Invalid initializer for variable '{node.name}'",
                        getattr(node, 'lineno', None))
                elif node.var_type == 'int' and node.value.dtype == 'float':
                    # Conversión explícita de float a int
                    node.value = TypeCast('int', node.value)
                elif not can_assign(node.var_type, node.value.dtype):
                    self.error_manager.add_error(
                        f"Cannot initialize {node.var_type} variable with {node.value.dtype} value",
                        getattr(node, 'lineno', None))
        except Symtab.SymbolDefinedError as e:
            self.error_manager.add_error(str(e), getattr(node, 'lineno', None))
        return None

    def visit_ConstDecl(self, node, env):
        try:
            node.value.accept(self, env)
            node.dtype = node.value.dtype
            env.add(node.name, node)
        except Symtab.SymbolDefinedError as e:
            self.error_manager.add_error(str(e), getattr(node, 'lineno', None))
        return None

    def visit_Assignment(self, node, env):
        # Verificar que la variable existe
        try:
            var_info = env.get(node.name)
            node.value.accept(self, env)
            
            # Verificar compatibilidad de tipos
            if not can_assign(var_info.dtype, node.value.dtype):
                self.error_manager.add_error(
                    f"Cannot assign {node.value.dtype} to {var_info.dtype} variable '{node.name}'",
                    getattr(node, 'lineno', None))
            
            node.dtype = var_info.dtype
        except Symtab.SymbolNotFoundError as e:
            self.error_manager.add_error(str(e), getattr(node, 'lineno', None))
        return None

    def visit_BinaryOp(self, node, env):
        node.left.accept(self, env)
        node.right.accept(self, env)
        
        # Conversión implícita de int a float si es necesario
        if node.operator in ['TIMES', 'PLUS', 'MINUS', 'DIVIDE']:
            if node.left.dtype == 'int' and node.right.dtype == 'float':
                node.left = TypeCast('float', node.left)
            elif node.left.dtype == 'float' and node.right.dtype == 'int':
                node.right = TypeCast('float', node.right)
        
        result_type = check_binop(
            node.operator,
            getattr(node.left, 'dtype', None),
            getattr(node.right, 'dtype', None),
            self.error_manager,
            getattr(node, 'lineno', None)
        )
        
        node.dtype = result_type
        return None

    def visit_UnaryOp(self, node, env):
        node.right.accept(self, env)
        
        result_type = check_unaryop(
            node.operator,
            node.right.dtype,
            self.error_manager
        )
        
        node.dtype = result_type
        return None

    def visit_IntLiteral(self, node, env):
        node.dtype = 'int'
        return None

    def visit_FloatLiteral(self, node, env):
        node.dtype = 'float'
        return None

    def visit_BoolLiteral(self, node, env):
        node.dtype = 'bool'
        return None

    def visit_StringLiteral(self, node, env):
        node.dtype = 'string'
        return None

    def visit_CharLiteral(self, node, env):
        node.dtype = 'char'
        return None

    def visit_Identifier(self, node, env):
        try:
            symbol = env.get(node.name)
            node.dtype = symbol.dtype
        except Symtab.SymbolNotFoundError as e:
            self.error_manager.add_error(str(e), getattr(node, 'lineno', None))
            node.dtype = 'unknown'
        return None

    def visit_If(self, node, env):
        node.condition.accept(self, env)
        if node.condition.dtype != 'bool':
            self.error_manager.add_error(
                "If condition must be boolean",
                getattr(node, 'lineno', None))
        
        # Verificar el bloque then
        then_env = Symtab("if_then", parent=env)
        node.then_block.accept(self, then_env)
        
        # Verificar el bloque else si existe
        if node.else_block:
            else_env = Symtab("if_else", parent=env)
            node.else_block.accept(self, else_env)
        
        return None

    def visit_While(self, node, env):
        node.condition.accept(self, env)
        if node.condition.dtype != 'bool':
            self.error_manager.add_error(
                "While condition must be boolean",
                getattr(node, 'lineno', None))
        
        # Crear nuevo ámbito para el cuerpo del while
        loop_env = Symtab("while_body", parent=env)
        self.in_loop = True
        node.body.accept(self, loop_env)
        self.in_loop = False
        
        return None

    def visit_Block(self, node, env):
        block_env = Symtab("block", parent=env)
        for stmt in node.statements:
            stmt.accept(self, block_env)
        return None

    def visit_Print(self, node, env):
        node.expression.accept(self, env)
        return None

    def visit_FuncDecl(self, node, env):
        try:
            # Registrar la función en el ámbito actual
            env.add(node.name, node)
            
            # Crear nuevo ámbito para los parámetros y cuerpo
            func_env = Symtab(node.name, parent=env)
            
            # Registrar parámetros
            for param_name, param_type in node.params:
                param_node = VarDecl(param_name, param_type)
                func_env.add(param_name, param_node)
            
            # Verificar el cuerpo de la función
            self.current_function_return_type = node.return_type
            node.body.accept(self, func_env)
            self.current_function_return_type = None
            
        except Symtab.SymbolDefinedError as e:
            self.error_manager.add_error(str(e), getattr(node, 'lineno', None))
        return None

    def visit_Return(self, node, env):
        if node.value:
            node.value.accept(self, env)
            if not can_assign(self.current_function_return_type, node.value.dtype):
                self.error_manager.add_error(
                    f"Return type mismatch: expected {self.current_function_return_type}, got {node.value.dtype}",
                    getattr(node, 'lineno', None))
        elif self.current_function_return_type != 'void':
            self.error_manager.add_error(
                f"Non-void function must return a value",
                getattr(node, 'lineno', None))
        return None

    def visit_FuncCall(self, node, env):
        try:
            func_info = env.get(node.name)
            
            # Verificar argumentos
            for arg in node.args:
                arg.accept(self, env)
            
            # TODO: Verificar coincidencia de parámetros y argumentos
            node.dtype = func_info.return_type
        except Symtab.SymbolNotFoundError as e:
            self.error_manager.add_error(str(e), getattr(node, 'lineno', None))
            node.dtype = 'unknown'
        return None

    def visit_Break(self, node, env):
        if not self.in_loop:
            self.error_manager.add_error(
                "Break statement outside loop",
                getattr(node, 'lineno', None))
        return None

    def visit_Continue(self, node, env):
        if not self.in_loop:
            self.error_manager.add_error(
                "Continue statement outside loop",
                getattr(node, 'lineno', None))
        return None

    def visit_TypeCast(self, node, env):
        node.expression.accept(self, env)
        # TODO: Verificar que el cast es válido
        node.dtype = node.cast_type
        return None

    def visit_MemoryAccess(self, node, env):
        node.expression.accept(self, env)
        # TODO: Determinar tipo de acceso a memoria
        return None

def print_errors(title, errors):
    """Imprime errores con formato consistente"""
    if errors:
        print(f"\n✗ {title}:")
        for error in errors:
            print(f"  - {error}")

def print_success(message):
    """Imprime mensaje de éxito con formato"""
    print(f"\n✓ {message}")

def main():
    if len(sys.argv) != 2:
        print("Uso: python check.py archivo.gox")
        sys.exit(1)

    filename = sys.argv[1]
    
    try:
        # Leer código fuente
        with open(filename, 'r') as file:
            source_code = file.read()
        
        print(f"\nAnalizando: {filename}")
        
        # Análisis léxico
        lexer = Lexer()
        tokens, lex_errors = lexer.tokenize(source_code)
        print_errors("Errores léxicos encontrados", lex_errors)
        if lex_errors:
            sys.exit(1)

        # Análisis sintáctico
        parser = Parser(tokens)
        ast = parser.parse()
        print_errors("Errores de sintaxis encontrados", parser.error_manager.get_all())
        if ast is None:
            sys.exit(1)

        # Análisis semántico
        checker = TypeChecker()
        is_valid = checker.check(ast)
        
        if is_valid:
            print_success("Programa válido semánticamente")
            sys.exit(0)
        else:
            print_errors("Errores semánticos encontrados", checker.error_manager.get_all())
            sys.exit(1)
            
    except FileNotFoundError:
        print(f"\nError: No se encontró el archivo {filename}")
        sys.exit(1)
    except Exception as e:
        print(f"\nError inesperado: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()