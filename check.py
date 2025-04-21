# check.py
from typing import Any, Optional
from goxLang_AST_nodes import *
from symtab import Symtab
from typesys import (
    check_binop, check_unaryop, can_assign,
    is_valid_type, get_type_info, TYPE_HIERARCHY
)
from gox_error_manager import ErrorManager

class TypeChecker:
    def __init__(self):
        self.error_manager = ErrorManager()
        self.current_function_return_type = None
        self.in_loop = False

    def check(self, node: Program) -> bool:
        """
        Realiza el análisis de tipos en el programa completo.
        
        Returns:
            bool: True si no hay errores de tipos, False si se encontraron errores
        """
        global_env = Symtab("global")
        node.accept(self, global_env)
        return not self.error_manager.has_errors()

    def visit_Program(self, node: Program, env: Symtab) -> None:
        for stmt in node.statements:
            stmt.accept(self, env)

    def visit_Print(self, node: Print, env: Symtab) -> None:
        node.expression.accept(self, env)
        node.dtype = node.expression.dtype

    def visit_If(self, node: If, env: Symtab) -> None:
        # Verificar condición
        node.condition.accept(self, env)
        if node.condition.dtype != 'bool':
            self.error_manager.add_error(
                f"Condition in if statement must be bool, got {node.condition.dtype}",
                getattr(node, 'lineno', None)
            )

        # Verificar bloque then
        then_env = Symtab("if_then", env)
        node.then_block.accept(self, then_env)

        # Verificar bloque else si existe
        if node.else_block:
            else_env = Symtab("if_else", env)
            node.else_block.accept(self, else_env)

        node.dtype = 'void'

    def visit_Block(self, node: Block, env: Symtab) -> None:
        block_env = Symtab("block", env)
        for stmt in node.statements:
            stmt.accept(self, block_env)
        node.dtype = 'void'

    def visit_IntLiteral(self, node: IntLiteral, env: Symtab) -> None:
        node.dtype = 'int'

    def visit_FloatLiteral(self, node: FloatLiteral, env: Symtab) -> None:
        node.dtype = 'float'

    def visit_StringLiteral(self, node: StringLiteral, env: Symtab) -> None:
        node.dtype = 'string'

    def visit_BoolLiteral(self, node: BoolLiteral, env: Symtab) -> None:
        node.dtype = 'bool'

    def visit_CharLiteral(self, node: CharLiteral, env: Symtab) -> None:
        node.dtype = 'char'

    def visit_Identifier(self, node: Identifier, env: Symtab) -> None:
        try:
            symbol = env.get(node.name)
            node.dtype = getattr(symbol, 'dtype', None)
            if node.dtype is None:
                self.error_manager.add_error(
                    f"Symbol '{node.name}' has no type information",
                    getattr(node, 'lineno', None)
                )
        except Symtab.SymbolNotFoundError:
            self.error_manager.add_error(
                f"Undefined variable '{node.name}'",
                getattr(node, 'lineno', None)
            )
            node.dtype = 'error'

    def visit_TypeCast(self, node: TypeCast, env: Symtab) -> None:
        node.expression.accept(self, env)
        if not is_valid_type(node.cast_type):
            self.error_manager.add_error(
                f"Invalid type in cast: '{node.cast_type}'",
                getattr(node, 'lineno', None)
            )
        node.dtype = node.cast_type

    def visit_MemoryAccess(self, node: MemoryAccess, env: Symtab) -> None:
        node.expression.accept(self, env)
        # Asumimos que es un puntero a int por defecto
        node.dtype = 'int'

    def visit_ImportFunctionDecl(self, node: ImportFunctionDecl, env: Symtab) -> None:
        if not is_valid_type(node.return_type):
            self.error_manager.add_error(
                f"Invalid return type '{node.return_type}' for function '{node.name}'",
                getattr(node, 'lineno', None)
            )

        try:
            env.add(node.name, node)
        except Symtab.SymbolDefinedError as e:
            self.error_manager.add_error(str(e), getattr(node, 'lineno', None))
        except Symtab.SymbolConflictError as e:
            self.error_manager.add_error(str(e), getattr(node, 'lineno', None))

        node.dtype = node.return_type

    def visit_ConstDecl(self, node: ConstDecl, env: Symtab) -> None:
        node.value.accept(self, env)
        node.dtype = node.value.dtype

        try:
            env.add(node.name, node)
        except Symtab.SymbolDefinedError as e:
            self.error_manager.add_error(str(e), getattr(node, 'lineno', None))
        except Symtab.SymbolConflictError as e:
            self.error_manager.add_error(str(e), getattr(node, 'lineno', None))

    def visit_VarDecl(self, node: VarDecl, env: Symtab) -> None:
        if not is_valid_type(node.var_type):
            self.error_manager.add_error(
                f"Invalid variable type '{node.var_type}' for '{node.name}'",
                getattr(node, 'lineno', None)
            )

        if node.value:
            node.value.accept(self, env)
            if not can_assign(node.var_type, node.value.dtype):
                self.error_manager.add_error(
                    f"Cannot assign {node.value.dtype} to variable '{node.name}' of type {node.var_type}",
                    getattr(node, 'lineno', None)
                )

        node.dtype = node.var_type

        try:
            env.add(node.name, node)
        except Symtab.SymbolDefinedError as e:
            self.error_manager.add_error(str(e), getattr(node, 'lineno', None))
        except Symtab.SymbolConflictError as e:
            self.error_manager.add_error(str(e), getattr(node, 'lineno', None))

    def visit_Assignment(self, node: Assignment, env: Symtab) -> None:
        node.value.accept(self, env)
        
        try:
            var_info = env.get(node.name)
            if not can_assign(var_info.dtype, node.value.dtype):
                self.error_manager.add_error(
                    f"Cannot assign {node.value.dtype} to variable '{node.name}' of type {var_info.dtype}",
                    getattr(node, 'lineno', None)
                )
            node.dtype = var_info.dtype
        except Symtab.SymbolNotFoundError:
            self.error_manager.add_error(
                f"Cannot assign to undeclared variable '{node.name}'",
                getattr(node, 'lineno', None)
            )
            node.dtype = 'error'

    def visit_FuncDecl(self, node: FuncDecl, env: Symtab) -> None:
        if not is_valid_type(node.return_type):
            self.error_manager.add_error(
                f"Invalid return type '{node.return_type}' for function '{node.name}'",
                getattr(node, 'lineno', None)
            )

        # Registrar la función en el ámbito actual
        try:
            env.add(node.name, node)
        except Symtab.SymbolDefinedError as e:
            self.error_manager.add_error(str(e), getattr(node, 'lineno', None))
        except Symtab.SymbolConflictError as e:
            self.error_manager.add_error(str(e), getattr(node, 'lineno', None))

        # Crear nuevo ámbito para los parámetros y cuerpo
        func_env = Symtab(f"func_{node.name}", env)
        
        # Registrar parámetros
        for param_name, param_type in node.params:
            if not is_valid_type(param_type):
                self.error_manager.add_error(
                    f"Invalid parameter type '{param_type}' in function '{node.name}'",
                    getattr(node, 'lineno', None)
                )
            param_node = VarDecl(param_name, param_type)
            func_env.add(param_name, param_node)

        # Verificar cuerpo de la función
        prev_return_type = self.current_function_return_type
        self.current_function_return_type = node.return_type
        
        node.body.accept(self, func_env)
        
        self.current_function_return_type = prev_return_type
        node.dtype = node.return_type

    def visit_Return(self, node: Return, env: Symtab) -> None:
        if node.value:
            node.value.accept(self, env)
            return_type = node.value.dtype
        else:
            return_type = 'void'

        if self.current_function_return_type is None:
            self.error_manager.add_error(
                "Return statement outside of function",
                getattr(node, 'lineno', None)
            )
        elif not can_assign(self.current_function_return_type, return_type):
            self.error_manager.add_error(
                f"Return type mismatch: expected {self.current_function_return_type}, got {return_type}",
                getattr(node, 'lineno', None)
            )

        node.dtype = return_type

    def visit_While(self, node: While, env: Symtab) -> None:
        node.condition.accept(self, env)
        if node.condition.dtype != 'bool':
            self.error_manager.add_error(
                "While condition must be a boolean expression",
                getattr(node, 'lineno', None)
            )

        prev_in_loop = self.in_loop
        self.in_loop = True
        
        loop_env = Symtab("while", env)
        node.body.accept(self, loop_env)
        
        self.in_loop = prev_in_loop
        node.dtype = 'void'

    def visit_BinaryOp(self, node: BinaryOp, env: Symtab) -> None:
        node.left.accept(self, env)
        node.right.accept(self, env)
        
        result_type = check_binop(
            node.operator,
            node.left.dtype,
            node.right.dtype,
            self.error_manager
        )
        
        if result_type is None:
            self.error_manager.add_error(
                f"Invalid operation: {node.left.dtype} {node.operator} {node.right.dtype}",
                getattr(node, 'lineno', None)
            )
            result_type = 'error'
        
        node.dtype = result_type

    def visit_FuncCall(self, node: FuncCall, env: Symtab) -> None:
        # Verificar que la función existe
        try:
            func_decl = env.get(node.name)
            node.dtype = func_decl.dtype
        except Symtab.SymbolNotFoundError:
            self.error_manager.add_error(
                f"Undefined function '{node.name}'",
                getattr(node, 'lineno', None)
            )
            node.dtype = 'error'
            return

        # Verificar argumentos
        if len(node.args) != len(func_decl.params):
            self.error_manager.add_error(
                f"Function '{node.name}' expects {len(func_decl.params)} arguments, got {len(node.args)}",
                getattr(node, 'lineno', None)
            )
        else:
            for arg, (param_name, param_type) in zip(node.args, func_decl.params):
                arg.accept(self, env)
                if not can_assign(param_type, arg.dtype):
                    self.error_manager.add_error(
                        f"Argument type mismatch in '{node.name}': expected {param_type}, got {arg.dtype}",
                        getattr(node, 'lineno', None)
                    )

    def visit_Break(self, node: Break, env: Symtab) -> None:
        if not self.in_loop:
            self.error_manager.add_error(
                "Break statement outside of loop",
                getattr(node, 'lineno', None)
            )
        node.dtype = 'void'

    def visit_Continue(self, node: Continue, env: Symtab) -> None:
        if not self.in_loop:
            self.error_manager.add_error(
                "Continue statement outside of loop",
                getattr(node, 'lineno', None)
            )
        node.dtype = 'void'

# Alias para compatibilidad
Checker = TypeChecker