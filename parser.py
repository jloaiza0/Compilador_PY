import os
import json
from goxLang_AST_nodes import *
from lexer import Lexer, Token
from gox_error_manager import ErrorManager

class Parser:
    def __init__(self, tokens=None):
        self.lexer = Lexer()
        self.tokens = tokens or []
        self.current = 0
        self.error_manager = ErrorManager()

    def add_error(self, message, lineno=None, col=None):
        """Registra un error con información de posición"""
        self.error_manager.add_error(message, lineno, col)

    def check_next(self, token_type):
        """Verifica el tipo del siguiente token sin consumirlo"""
        if self.current + 1 >= len(self.tokens):
            return False
        return self.tokens[self.current + 1].type == token_type

    def tokenize(self, source_code):
        """Convierte el código fuente en tokens"""
        tokens, lex_errors = self.lexer.tokenize(source_code)
        for err in lex_errors:
            self.error_manager.add_error(err)
        return tokens, lex_errors

    def parse(self):
        """Analiza los tokens y retorna el AST o None si hay errores"""
        # Debug: Mostrar todos los tokens
        print("\n=== TOKEN STREAM ===")
        for i, token in enumerate(self.tokens):
            print(f"{i}: {token.type} '{token.value}' (line {token.lineno})")

        if not self.tokens:
            self.add_error("No hay tokens para analizar")
            return None

        # Asegurar token EOF
        if self.tokens[-1].type != "EOF":
            last_line = self.tokens[-1].lineno if self.tokens else 1
            self.tokens.append(Token("EOF", "", last_line))
        
        self.current = 0
        
        try:
            program_node = self.parse_program()
            self._generate_debug_files(program_node)
            return program_node
        except Exception as e:
            current_token = self.peek()
            lineno = current_token.lineno if hasattr(current_token, 'lineno') else None
            self.add_error(f"Error durante el parsing: {str(e)}", lineno)
            return None

    def _generate_debug_files(self, program_node):
        """Genera archivos JSON con el AST y errores"""
        os.makedirs("temp", exist_ok=True)
        if program_node:
            with open("temp/ast_output.json", "w") as f:
                json.dump(program_node.to_dict(), f, indent=4)
        
        with open("temp/error_log.txt", "w") as f:
            for error in self.error_manager.get_all():
                f.write(error + "\n")

    def parse_program(self):
        """Program ::= Statement*"""
        statements = []
        while not self.is_at_end():
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return Program(statements)

    def parse_statement(self):
        """Statement ::= PrintStmt | IfStmt | WhileStmt | ReturnStmt 
                       | VarDecl | ConstDecl | FuncDecl | ImportDecl
                       | Assignment | ExprStmt | Block | Break | Continue"""
        current_token = self.peek()
        
        if self.match("PRINT"):
            return self.parse_print()
        elif self.match("IF"):
            return self.parse_if()
        elif self.match("IMPORT"):
            return self.parse_import_func()
        elif self.match("FUNC"):
            return self.parse_func_decl()
        elif self.match("VAR"):
            return self.parse_var_decl()
        elif self.match("CONST"):
            return self.parse_const_decl()
        elif self.match("WHILE"):
            return self.parse_while()
        elif self.match("LBRACE"):
            return self.parse_block()
        elif self.match("RETURN"):
            return self.parse_return()
        elif self.match("BREAK"):
            if not self.match("SEMICOLON"):
                self.add_error("Expected ';' after break statement", current_token.lineno)
            return Break()
        elif self.match("CONTINUE"):
            if not self.match("SEMICOLON"):
                self.add_error("Expected ';' after continue statement", current_token.lineno)
            return Continue()
        else:
            return self.parse_expression_statement()

    def parse_expression_statement(self):
        """ExprStmt ::= Expression (';' | Assignment | FuncCall)"""
        current_token = self.peek()
        
        # Caso especial para asignaciones
        if self.check("ID") and self.check_next("ASSIGN"):
            name_token = self.advance()  # Consume el ID
            self.advance()  # Consume el ASSIGN
            value = self.parse_expression()
            if not self.match("SEMICOLON"):
                self.add_error("Expected ';' after assignment", current_token.lineno)
            return Assignment(name_token.value, value)
        
        # Intenta parsear una expresión normal
        expr = self.parse_expression()
        if not expr:
            return None
            
        # Verificar si es una llamada a función
        if isinstance(expr, Identifier) and self.match("LPAREN"):
            args = self.parse_argument_list()
            if not self.match("SEMICOLON"):
                self.add_error("Expected ';' after function call", current_token.lineno)
            return FuncCall(expr.name, args)
            
        if self.match("SEMICOLON"):
            return expr
            
        self.add_error("Expected ';' after expression", current_token.lineno)
        return expr

    def parse_argument_list(self):
        """ArgumentList ::= '(' (Expression (',' Expression)*)? ')'"""
        args = []
        current_token = self.peek()
        
        while not self.check("RPAREN") and not self.is_at_end():
            arg = self.parse_expression()
            args.append(arg)
            if not self.match("COMMA"):
                break
                
        if not self.match("RPAREN"):
            self.add_error("Expected ')' after arguments", current_token.lineno)
        return args

    def parse_print(self):
        """PrintStmt ::= 'print' Expression ';'"""
        current_token = self.peek()
        expr = self.parse_expression()
        if not self.match("SEMICOLON"):
            self.add_error("Expected ';' after print statement", current_token.lineno)
        return Print(expr)

    def parse_if(self):
        """IfStmt ::= 'if' Expression Block ('else' Block)?"""
        current_token = self.peek()
        condition = self.parse_expression()
        
        if condition.dtype != 'bool':
            self.add_error("Condition must be a boolean expression", current_token.lineno)
            
        then_block = self.parse_block()
        else_block = None
        
        if self.match("ELSE"):
            else_block = self.parse_block()
            
        return If(condition, then_block, else_block)

    def parse_while(self):
        """WhileStmt ::= 'while' Expression Block"""
        while_token = self.advance()  # Consume 'while'
        
        condition = self.parse_expression()
        if not condition:
            self.add_error("Expected condition after 'while'", while_token.lineno)
            return None

        # No debe haber ; después de la condición
        if self.match('SEMICOLON'):
            self.add_error("Unexpected ';' after while condition", while_token.lineno)

        body = self.parse_block()
        if not body:
            self.add_error("Expected block after while condition", while_token.lineno)
            return None

        return While(condition, body, while_token.lineno)

    def parse_return(self):
        """ReturnStmt ::= 'return' Expression? ';'"""
        current_token = self.peek()
        expr = None
        
        if not self.check("SEMICOLON"):
            expr = self.parse_expression()
            
        if not self.match("SEMICOLON"):
            self.add_error("Expected ';' after return statement", current_token.lineno)
            
        return Return(expr)

    def parse_import_func(self):
        """ImportDecl ::= 'import' 'func' ID '(' ParamList ')' Type ';'"""
        current_token = self.peek()
        
        if not self.match("FUNC"):
            self.add_error("Expected 'func' after 'import'", current_token.lineno)
            return None
            
        return self._parse_func_signature(imported=True)

    def parse_func_decl(self):
        """FuncDecl ::= 'func' ID '(' ParamList ')' Type Block"""
        return self._parse_func_signature(imported=False)

    def _parse_func_signature(self, imported):
        """Helper para analizar firmas de funciones"""
        current_token = self.peek()
        
        if not self.check("ID"):
            self.add_error("Expected function name", current_token.lineno)
            return None
            
        name = self.advance().value

        if not self.match("LPAREN"):
            self.add_error("Expected '(' after function name", current_token.lineno)
            return None

        params = self.parse_parameter_list()

        if not self.check("TYPE"):
            self.add_error("Expected return type", current_token.lineno)
            return None
            
        return_type = self.advance().value

        if imported:
            if not self.match("SEMICOLON"):
                self.add_error("Expected ';' after imported function", current_token.lineno)
            return ImportFunctionDecl(name, params, return_type)
        else:
            body = self.parse_block()
            return FuncDecl(name, params, return_type, body)

    def parse_parameter_list(self):
        """ParamList ::= (ID Type (',' ID Type)*)?"""
        params = []
        current_token = self.peek()
        
        while not self.check("RPAREN") and not self.is_at_end():
            if not self.check("ID"):
                self.add_error("Expected parameter name", current_token.lineno)
                break
                
            param_name = self.advance().value
            
            if not self.check("TYPE"):
                self.add_error("Expected type after parameter name", current_token.lineno)
                break
                
            param_type = self.advance().value
            params.append((param_name, param_type))
            
            if not self.match("COMMA"):
                break

        if not self.match("RPAREN"):
            self.add_error("Expected ')' after parameters", current_token.lineno)
        
        return params

    def parse_var_decl(self):
        """VarDecl ::= 'var' ID Type ('=' Expression)? ';'"""
        current_token = self.peek()
        
        if not self.check("ID"):
            self.add_error("Expected variable name", current_token.lineno)
            return None
            
        name = self.advance().value

        if not self.check("TYPE"):
            self.add_error("Expected type after variable name", current_token.lineno)
            return None
            
        var_type = self.advance().value

        value = None
        if self.match("ASSIGN"):
            value = self.parse_expression()

        if not self.match("SEMICOLON"):
            self.add_error("Expected ';' after variable declaration", current_token.lineno)
            
        return VarDecl(name, var_type, value)

    def parse_const_decl(self):
        """ConstDecl ::= 'const' ID '=' Expression ';'"""
        current_token = self.peek()
        
        if not self.check("ID"):
            self.add_error("Expected constant name", current_token.lineno)
            return None
            
        name = self.advance().value

        if not self.match("ASSIGN"):
            self.add_error("Expected '=' in constant declaration", current_token.lineno)
            return None

        value = self.parse_expression()

        if not self.match("SEMICOLON"):
            self.add_error("Expected ';' after constant declaration", current_token.lineno)
            
        return ConstDecl(name, value)

    def parse_block(self):
        """Block ::= '{' Statement* '}'"""
        lbrace_token = self.peek()
        if not self.match('LBRACE'):
            self.add_error(f"Expected '{{' to start block, got '{lbrace_token.type}'", lbrace_token.lineno)
            return None

        statements = []
        while not self.check('RBRACE') and not self.is_at_end():
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)

        if not self.match('RBRACE'):
            current_token = self.peek()
            self.add_error(f"Expected '}}' to end block, got '{current_token.type}'", current_token.lineno)
            return None

        return Block(statements, lbrace_token.lineno)

    def parse_expression(self):
        """Expression ::= Equality"""
        return self.parse_equality()

    def parse_equality(self):
        """Equality ::= Comparison (('==' | '!=') Comparison)*"""
        expr = self.parse_comparison()
        
        while self.match('EQ', 'NE'):
            operator = self.previous().type
            right = self.parse_comparison()
            expr = BinaryOp(expr, operator, right)
            expr.dtype = 'bool'
            
        return expr

    def parse_comparison(self):
        """Comparison ::= Term (('<' | '>' | '<=' | '>=') Term)*"""
        expr = self.parse_term()
        
        while self.match('LT', 'GT', 'LE', 'GE'):
            operator = self.previous().type
            right = self.parse_term()
            expr = BinaryOp(expr, operator, right)
            expr.dtype = 'bool'
            
        return expr

    def parse_term(self):
        """Term ::= Factor (('+' | '-') Factor)*"""
        expr = self.parse_factor()
        
        while self.match("PLUS", "MINUS"):
            operator = self.previous().type
            right = self.parse_factor()
            expr = BinaryOp(expr, operator, right)
            
        return expr

    def parse_factor(self):
        """Factor ::= Unary (('*' | '/' | '%') Unary)*"""
        expr = self.parse_unary()
        
        while self.match("TIMES", "DIVIDE", "MOD"):
            operator = self.previous().type
            right = self.parse_unary()
            expr = BinaryOp(expr, operator, right)
            
        return expr

    def parse_unary(self):
        """Unary ::= ('-' | '!') Unary | Primary"""
        if self.match("MINUS", "BANG"):
            operator = self.previous().type
            right = self.parse_unary()
            zero = IntLiteral(0) if operator == "MINUS" else BoolLiteral(False)
            return BinaryOp(zero, operator, right)
            
        return self.parse_primary()

    def parse_primary(self):
        """Primary ::= Literal | Identifier | '(' Expression ')' 
                     | TypeCast | MemoryAccess"""
        if self.is_at_end():
            current_token = self.peek()
            self.add_error("Unexpected end of input", current_token.lineno)
            return None

        current_token = self.advance()
        
        if current_token.type == "NUMBER":
            return IntLiteral(int(current_token.value))
        elif current_token.type == "FLOAT":
            return FloatLiteral(float(current_token.value))
        elif current_token.type == "STRING":
            return StringLiteral(current_token.value)
        elif current_token.type == "CHAR":
            return CharLiteral(current_token.value)
        elif current_token.type == "TRUE":
            return BoolLiteral(True)
        elif current_token.type == "FALSE":
            return BoolLiteral(False)
        elif current_token.type == "ID":
            return Identifier(current_token.value)
        elif current_token.type == "LPAREN":
            expr = self.parse_expression()
            if not self.match("RPAREN"):
                self.add_error("Expected ')' after expression", current_token.lineno)
            return expr
            
        self.add_error(f"Unexpected token in expression: {current_token.type}", current_token.lineno)
        return None

    # ===== Métodos de ayuda para el análisis =====
    def match(self, *types):
        """Verifica si el token actual coincide con alguno de los tipos dados"""
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    def check(self, token_type):
        """Verifica el tipo del token actual sin consumirlo"""
        if self.is_at_end():
            return False
        return self.peek().type == token_type

    def advance(self):
        """Consume el token actual y lo devuelve"""
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self):
        """Indica si se llegó al final de los tokens"""
        return self.peek().type == "EOF"

    def peek(self):
        """Devuelve el token actual sin consumirlo"""
        return self.tokens[self.current]

    def previous(self):
        """Devuelve el token anterior"""
        return self.tokens[self.current - 1]