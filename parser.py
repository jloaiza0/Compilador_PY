from lexer import TokenType, Token
from ASTnodes import *
from Error import ErrorHandler
from typing import List, Optional

class Parser:
    """Parser para el lenguaje GoX con manejo de errores robusto y recuperación"""
    
    def __init__(self, tokens: List[Token], error_handler: ErrorHandler):
        self.tokens = tokens
        self.error_handler = error_handler
        self.current_pos = 0
        self.current_token = tokens[0] if tokens else None
        self.loop_stack = []  # Para manejar break/continue en loops
        self.function_stack = []  # Para manejar returns en funciones
    
    @property
    def peek_token(self) -> Optional[Token]:
        """Obtiene el siguiente token sin consumirlo"""
        if self.current_pos + 1 < len(self.tokens):
            return self.tokens[self.current_pos + 1]
        return None
    
    def consume(self, expected_type: TokenType = None, err_msg: str = None) -> Token:
        """Consume el token actual y avanza al siguiente"""
        if expected_type and self.current_token.type != expected_type:
            self.error_handler.add_syntax_error(
                err_msg or f"Se esperaba {expected_type.name}, se encontró {self.current_token.type.name}",
                self.current_token.lineno
            )
            # Recuperación: busca el siguiente token del tipo esperado
            return self.sync_to(expected_type)
        
        token = self.current_token
        if self.current_pos + 1 < len(self.tokens):
            self.current_pos += 1
            self.current_token = self.tokens[self.current_pos]
        else:
            self.current_token = None
        return token
    
    def sync_to(self, target_type: TokenType) -> Token:
        """Recuperación de errores: avanza hasta encontrar el tipo de token objetivo"""
        while self.current_token and self.current_token.type != target_type:
            self.current_pos += 1
            if self.current_pos < len(self.tokens):
                self.current_token = self.tokens[self.current_pos]
            else:
                self.current_token = None
                break
        return self.current_token if self.current_token else None
    
    def parse(self) -> Program:
        """Analiza el programa completo y devuelve el AST"""
        statements = []
        while self.current_token and self.current_token.type != TokenType.EOF:
            try:
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
            except ParseError:
                # Recuperación: saltar al próximo punto seguro (; o })
                self.sync_to_statement_boundary()
        return Program(statements)
    
    def sync_to_statement_boundary(self):
        """Sincroniza a un límite seguro de declaración"""
        while self.current_token and self.current_token.type not in [
            TokenType.SEMI, TokenType.RBRACE, TokenType.VAR, TokenType.CONST,
            TokenType.FUNC, TokenType.IF, TokenType.WHILE, TokenType.FOR,
            TokenType.RETURN, TokenType.BREAK, TokenType.CONTINUE, TokenType.EOF
        ]:
            self.current_pos += 1
            if self.current_pos < len(self.tokens):
                self.current_token = self.tokens[self.current_pos]
            else:
                self.current_token = None
                break
        
        if self.current_token and self.current_token.type == TokenType.SEMI:
            self.consume(TokenType.SEMI)
    
    def parse_statement(self) -> Optional[ASTNode]:
        """Analiza una sentencia individual"""
        if not self.current_token or self.current_token.type == TokenType.EOF:
            return None
        
        try:
            token_type = self.current_token.type
            
            if token_type == TokenType.IMPORT:
                return self.parse_import()
            elif token_type in (TokenType.VAR, TokenType.CONST):
                return self.parse_declaration()
            elif token_type == TokenType.PRINT:
                return self.parse_print()
            elif token_type == TokenType.IF:
                return self.parse_if()
            elif token_type == TokenType.WHILE:
                return self.parse_while()
            elif token_type == TokenType.FOR:
                return self.parse_for()
            elif token_type == TokenType.FUNC:
                return self.parse_function()
            elif token_type == TokenType.RETURN:
                return self.parse_return()
            elif token_type == TokenType.BREAK:
                return self.parse_break()
            elif token_type == TokenType.CONTINUE:
                return self.parse_continue()
            elif token_type == TokenType.ID:
                # Distingue entre asignación y llamada a función
                if self.peek_token and self.peek_token.type == TokenType.LPAREN:
                    expr = self.parse_function_call()
                    self.consume(TokenType.SEMI, "Falta ';' después de la llamada a función")
                    return expr
                return self.parse_assignment()
            elif token_type == TokenType.LBRACE:
                return self.parse_block()
            else:
                # Intenta parsear como expresión
                expr = self.parse_expression()
                if expr:
                    self.consume(TokenType.SEMI, "Falta ';' después de la expresión")
                    return expr
                else:
                    self.error_handler.add_syntax_error(
                        f"Token inesperado: {token_type.name}",
                        self.current_token.lineno
                    )
                    return None
                    
        except ParseError as e:
            self.error_handler.add_error(str(e), self.current_token.lineno if self.current_token else 0)
            raise
    
    def parse_import(self) -> Import:
        """Analiza declaraciones de importación"""
        self.consume(TokenType.IMPORT)
        module_name = self.consume(TokenType.STRING, "Se esperaba nombre del módulo después de 'import'").value
        self.consume(TokenType.SEMI, "Falta ';' después de la declaración import")
        return Import(module_name.strip('"'))
    
    def parse_declaration(self) -> Declaration:
        """Analiza declaraciones de variables y constantes"""
        is_const = self.current_token.type == TokenType.CONST
        self.consume()  # Consume VAR o CONST
        
        name = self.consume(TokenType.ID, "Se esperaba nombre de variable").value
        
        var_type = None
        if self.current_token and self.current_token.type in [TokenType.INT, TokenType.FLOAT_TYPE, 
                                                               TokenType.BOOL, TokenType.CHAR_TYPE, 
                                                               TokenType.STRING_TYPE]:
            var_type = self.consume().value
        
        initial_value = None
        if self.current_token and self.current_token.type == TokenType.ASSIGN:
            self.consume(TokenType.ASSIGN)
            initial_value = self.parse_expression()
        
        self.consume(TokenType.SEMI, "Falta ';' después de la declaración")
        return Declaration(name, var_type, initial_value, is_const)
    
    def parse_assignment(self) -> Assignment:
        """Analiza asignaciones"""
        name = self.consume(TokenType.ID).value
        self.consume(TokenType.ASSIGN, "Se esperaba '=' en la asignación")
        value = self.parse_expression()
        self.consume(TokenType.SEMI, "Falta ';' después de la asignación")
        return Assignment(name, value)
    
    def parse_print(self) -> Print:
        """Analiza declaraciones print"""
        self.consume(TokenType.PRINT)
        expr = self.parse_expression()
        self.consume(TokenType.SEMI, "Falta ';' después de print")
        return Print(expr)
    
    def parse_if(self) -> If:
        """Analiza declaraciones if"""
        self.consume(TokenType.IF)
        self.consume(TokenType.LPAREN, "Falta '(' después de 'if'")
        condition = self.parse_expression()
        self.consume(TokenType.RPAREN, "Falta ')' después de la condición")
        
        then_stmt = self.parse_statement()
        
        else_stmt = None
        if self.current_token and self.current_token.type == TokenType.ELSE:
            self.consume(TokenType.ELSE)
            else_stmt = self.parse_statement()
        
        return If(condition, then_stmt, else_stmt)
    
    def parse_while(self) -> While:
        """Analiza loops while"""
        self.consume(TokenType.WHILE)
        self.consume(TokenType.LPAREN, "Falta '(' después de 'while'")
        condition = self.parse_expression()
        self.consume(TokenType.RPAREN, "Falta ')' después de la condición")
        
        self.loop_stack.append('while')
        body = self.parse_statement()
        self.loop_stack.pop()
        
        return While(condition, body)
    
    def parse_for(self) -> For:
        """Analiza loops for"""
        self.consume(TokenType.FOR)
        self.consume(TokenType.LPAREN, "Falta '(' después de 'for'")
        
        # Inicialización (opcional)
        init = None
        if self.current_token.type != TokenType.SEMI:
            if self.current_token.type in [TokenType.VAR, TokenType.CONST]:
                init = self.parse_declaration()
            else:
                init = self.parse_assignment()
        else:
            self.consume(TokenType.SEMI)
        
        # Condición (opcional)
        condition = None
        if self.current_token.type != TokenType.SEMI:
            condition = self.parse_expression()
        self.consume(TokenType.SEMI, "Falta ';' después de la condición del for")
        
        # Incremento (opcional)
        update = None
        if self.current_token.type != TokenType.RPAREN:
            if self.current_token.type == TokenType.ID and self.peek_token.type == TokenType.ASSIGN:
                # Es una asignación
                name = self.consume(TokenType.ID).value
                self.consume(TokenType.ASSIGN)
                value = self.parse_expression()
                update = Assignment(name, value)
            else:
                update = self.parse_expression()
        
        self.consume(TokenType.RPAREN, "Falta ')' para cerrar el for")
        
        self.loop_stack.append('for')
        body = self.parse_statement()
        self.loop_stack.pop()
        
        return For(init, condition, update, body)
    
    def parse_function(self) -> Function:
        """Analiza definiciones de funciones"""
        self.consume(TokenType.FUNC)
        name = self.consume(TokenType.ID, "Se esperaba nombre de función").value
        
        self.consume(TokenType.LPAREN, "Falta '(' después del nombre de función")
        
        # Parámetros
        params = []
        if self.current_token.type != TokenType.RPAREN:
            # Primer parámetro
            param_name = self.consume(TokenType.ID, "Se esperaba nombre de parámetro").value
            param_type = self.consume(TokenType.ID, "Se esperaba tipo de parámetro").value
            params.append((param_name, param_type))
            
            # Parámetros adicionales
            while self.current_token.type == TokenType.COMMA:
                self.consume(TokenType.COMMA)
                param_name = self.consume(TokenType.ID, "Se esperaba nombre de parámetro").value
                param_type = self.consume(TokenType.ID, "Se esperaba tipo de parámetro").value
                params.append((param_name, param_type))
        
        self.consume(TokenType.RPAREN, "Falta ')' después de los parámetros")
        
        # Tipo de retorno (opcional)
        return_type = None
        if self.current_token.type in [TokenType.INT, TokenType.FLOAT_TYPE, TokenType.BOOL, 
                                       TokenType.CHAR_TYPE, TokenType.STRING_TYPE]:
            return_type = self.consume().value
        
        self.function_stack.append(name)
        body = self.parse_statement()
        self.function_stack.pop()
        
        return Function(name, params, return_type, body)
    
    def parse_return(self) -> Return:
        """Analiza declaraciones return"""
        if not self.function_stack:
            self.error_handler.add_semantic_error("Return fuera de función", self.current_token.lineno)
        
        self.consume(TokenType.RETURN)
        
        value = None
        if self.current_token.type != TokenType.SEMI:
            value = self.parse_expression()
        
        self.consume(TokenType.SEMI, "Falta ';' después de return")
        return Return(value)
    
    def parse_break(self) -> Break:
        """Analiza declaraciones break"""
        if not self.loop_stack:
            self.error_handler.add_semantic_error("Break fuera de loop", self.current_token.lineno)
        
        self.consume(TokenType.BREAK)
        self.consume(TokenType.SEMI, "Falta ';' después de break")
        return Break()
    
    def parse_continue(self) -> Continue:
        """Analiza declaraciones continue"""
        if not self.loop_stack:
            self.error_handler.add_semantic_error("Continue fuera de loop", self.current_token.lineno)
        
        self.consume(TokenType.CONTINUE)
        self.consume(TokenType.SEMI, "Falta ';' después de continue")
        return Continue()
    
    def parse_block(self) -> Block:
        """Analiza un bloque de código entre llaves"""
        self.consume(TokenType.LBRACE, "Falta '{' para iniciar el bloque")
        statements = []
        
        while self.current_token and self.current_token.type != TokenType.RBRACE:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        self.consume(TokenType.RBRACE, "Falta '}' para cerrar el bloque")
        return Block(statements)
    
    def parse_expression(self, min_precedence: int = 0) -> Optional[Expression]:
        """Analiza expresiones con precedencia de operadores"""
        left = self.parse_unary()
        if not left:
            return None
        
        while self.current_token:
            op_info = self.get_operator_info()
            if not op_info or op_info.precedence < min_precedence:
                break
            
            op_token = self.consume()
            right_precedence = op_info.precedence + (0 if op_info.right_associative else 1)
            right = self.parse_expression(right_precedence)
            
            if not right:
                self.error_handler.add_error(
                    f"Falta expresión después del operador {op_token.value}",
                    op_token.lineno
                )
                return left
            
            left = BinOp(op_token.value, left, right)
        
        return left
    
    def get_operator_info(self) -> Optional['OperatorInfo']:
        """Obtiene información sobre el operador actual"""
        if not self.current_token:
            return None
        return OPERATOR_INFO.get(self.current_token.type)
    
    def parse_unary(self) -> Optional[Expression]:
        """Analiza operadores unarios y expresiones primarias"""
        if self.current_token.type in (TokenType.PLUS, TokenType.MINUS, TokenType.NOT, TokenType.DEREF):
            op = self.consume().value
            operand = self.parse_unary()
            return UnaryOp(op, operand) if operand else None
        return self.parse_primary()
    
    def parse_primary(self) -> Optional[Expression]:
        """Analiza expresiones primarias"""
        token = self.current_token
        if not token:
            return None
        
        if token.type == TokenType.INTEGER:
            self.consume()
            return Integer(int(token.value))
        elif token.type == TokenType.FLOAT:
            self.consume()
            return Float(float(token.value))
        elif token.type == TokenType.STRING:
            self.consume()
            return String(token.value.strip('"'))
        elif token.type == TokenType.CHAR:
            self.consume()
            return Char(token.value.strip("'"))
        elif token.type in (TokenType.TRUE, TokenType.FALSE):
            self.consume()
            return Boolean(token.type == TokenType.TRUE)
        elif token.type == TokenType.ID:
            return self.parse_id_expression()
        elif token.type == TokenType.LPAREN:
            self.consume()
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN, "Falta ')' para cerrar la expresión")
            return expr
        elif token.type == TokenType.LBRACKET:
            return self.parse_array_literal()
        else:
            self.error_handler.add_error(
                f"Token inesperado en expresión: {token.type.name}",
                token.lineno
            )
            return None
    
    def parse_id_expression(self) -> Expression:
        """Analiza expresiones que comienzan con un ID (variable, llamada a función)"""
        ident = self.consume(TokenType.ID).value
        
        if self.current_token and self.current_token.type == TokenType.LPAREN:
            # Llamada a función
            return self.parse_function_call_with_name(ident)
        
        # Variable simple
        return Location(ident)
    
    def parse_function_call(self) -> FunctionCall:
        """Analiza llamadas a función completas"""
        name = self.consume(TokenType.ID).value
        return self.parse_function_call_with_name(name)
    
    def parse_function_call_with_name(self, name: str) -> FunctionCall:
        """Analiza llamada a función con nombre dado"""
        self.consume(TokenType.LPAREN)
        args = []
        
        if self.current_token and self.current_token.type != TokenType.RPAREN:
            args.append(self.parse_expression())
            while self.current_token and self.current_token.type == TokenType.COMMA:
                self.consume(TokenType.COMMA)
                args.append(self.parse_expression())
        
        self.consume(TokenType.RPAREN, "Falta ')' después de los argumentos")
        return FunctionCall(name, args)
    
    def parse_array_literal(self) -> ArrayLiteral:
        """Analiza literales de array [1, 2, 3]"""
        self.consume(TokenType.LBRACKET)
        elements = []
        
        if self.current_token and self.current_token.type != TokenType.RBRACKET:
            elements.append(self.parse_expression())
            while self.current_token and self.current_token.type == TokenType.COMMA:
                self.consume(TokenType.COMMA)
                elements.append(self.parse_expression())
        
        self.consume(TokenType.RBRACKET, "Falta ']' para cerrar el array")
        return ArrayLiteral(elements)


class OperatorInfo:
    """Clase auxiliar para información de operadores"""
    __slots__ = ['precedence', 'right_associative']
    
    def __init__(self, precedence: int, right_associative: bool = False):
        self.precedence = precedence
        self.right_associative = right_associative


# Tabla de precedencia y asociatividad de operadores
OPERATOR_INFO = {
    TokenType.OR: OperatorInfo(1),
    TokenType.AND: OperatorInfo(2),
    TokenType.EQ: OperatorInfo(3), 
    TokenType.NE: OperatorInfo(3),
    TokenType.LT: OperatorInfo(4), 
    TokenType.LE: OperatorInfo(4),
    TokenType.GT: OperatorInfo(4), 
    TokenType.GE: OperatorInfo(4),
    TokenType.PLUS: OperatorInfo(5), 
    TokenType.MINUS: OperatorInfo(5),
    TokenType.TIMES: OperatorInfo(6), 
    TokenType.DIVIDE: OperatorInfo(6), 
    TokenType.MOD: OperatorInfo(6),
    TokenType.POWER: OperatorInfo(7, right_associative=True),
    TokenType.NOT: OperatorInfo(8, right_associative=True),
    TokenType.DEREF: OperatorInfo(8, right_associative=True),
}


class ParseError(Exception):
    """Excepción para errores de parsing con recuperación"""
    pass