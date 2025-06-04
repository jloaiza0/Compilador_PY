from lexer import TokenType
from ASTnodes import *
from Error import ErrorHandler
from typing import List, Optional

class Parser:
    """Parser para el lenguaje GoX con manejo de errores robusto y recuperación"""
    
    def __init__(self, tokens: List['Token'], error_handler: ErrorHandler):
        self.tokens = tokens
        self.error_handler = error_handler
        self.current_pos = 0
        self.current_token = tokens[0] if tokens else None
        self.loop_stack = []  # Para manejar break/continue en loops
        self.function_stack = []  # Para manejar returns en funciones

    @property
    def peek_token(self) -> Optional['Token']:
        """Obtiene el siguiente token sin consumirlo"""
        if self.current_pos + 1 < len(self.tokens):
            return self.tokens[self.current_pos + 1]
        return None

    def consume(self, expected_type: TokenType = None, err_msg: str = None) -> 'Token':
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

    def sync_to(self, target_type: TokenType) -> 'Token':
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
        while self.current_token:
            try:
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
            except ParseError:
                # Recuperación: saltar al próximo punto seguro (; o })
                self.sync_to(TokenType.SEMI)
                self.consume(TokenType.SEMI)
        
        return Program(statements)

    def parse_statement(self) -> Optional[ASTNode]:
        """Analiza una sentencia individual"""
        if not self.current_token:
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
                    return self.parse_function_call()
                return self.parse_assignment()
            elif token_type == TokenType.LBRACE:
                return self.parse_block()
            else:
                # Intenta parsear como expresión
                expr = self.parse_expression()
                self.consume(TokenType.SEMI, "Falta ';' después de la expresión")
                return expr
                
        except ParseError as e:
            self.error_handler.add_error(str(e), self.current_token.lineno)
            raise

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
            right = self.parse_expression(op_info.precedence + (1 if op_info.right_associative else 0))
            
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
            return String(token.value)
        elif token.type == TokenType.CHAR:
            self.consume()
            return Char(token.value)
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
            self.consume()
            args = []
            
            if self.current_token and self.current_token.type != TokenType.RPAREN:
                args.append(self.parse_expression())
                while self.current_token and self.current_token.type == TokenType.COMMA:
                    self.consume()
                    args.append(self.parse_expression())
            
            self.consume(TokenType.RPAREN, "Falta ')' después de los argumentos")
            return FunctionCall(ident, args)
        
        # Variable simple
        return Location(ident)

    # Resto de métodos de parseo (parse_if, parse_while, parse_function, etc.)
    # ... (implementaciones similares a las originales pero con mejor manejo de errores)

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
    TokenType.EQ: OperatorInfo(3), TokenType.NE: OperatorInfo(3),
    TokenType.LT: OperatorInfo(4), TokenType.LE: OperatorInfo(4),
    TokenType.GT: OperatorInfo(4), TokenType.GE: OperatorInfo(4),
    TokenType.PLUS: OperatorInfo(5), TokenType.MINUS: OperatorInfo(5),
    TokenType.TIMES: OperatorInfo(6), TokenType.DIVIDE: OperatorInfo(6), TokenType.MOD: OperatorInfo(6),
    TokenType.NOT: OperatorInfo(7, right_associative=True),
    TokenType.MINUS: OperatorInfo(7, right_associative=True),  # Unario
    TokenType.PLUS: OperatorInfo(7, right_associative=True),   # Unario
}

class ParseError(Exception):
    """Excepción para errores de parsing con recuperación"""
    pass