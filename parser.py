try:
    from Lexer import *
    from ASTnodes import *
    from Error import ErrorHandler
    from ASTtoJSON import save_ast_to_json  # Importa la función para serializar el AST a JSON
except ImportError as e:
    print(f"Error de importación: {e}")
    exit(1)

class Parser:
    def __init__(self, tokens, error_handler):
        self.tokens = tokens  # Lista de tokens generados por el Lexer
        self.error_handler = error_handler  # Manejador de errores
        self.pos = 0  # Posición actual en la lista de tokens
        self.current_token = self.tokens[0] if tokens else None  # Token actual

    def advance(self):
        """Avanza al siguiente token en la lista"""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None  # Fin de los tokens

    def peek(self, offset=1):
        """Mira el token futuro sin consumirlo (lookahead)"""
        peek_pos = self.pos + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None

    def expect(self, token_type, err_msg=None):
        """Verifica si el token actual coincide con el tipo esperado"""
        if self.current_token and self.current_token.type == token_type:
            token = self.current_token
            self.advance()
            return token
        else:
            # Manejo de error si el token no coincide
            err = err_msg or f"Se esperaba {token_type}"
            if self.current_token:
                self.error_handler.add_error(err, self.current_token.lineno)
            else:
                self.error_handler.add_error(err, "Fin del archivo")
            return False

    def parse(self):
        """Punto de entrada para analizar el programa completo"""
        statements = []
        while self.current_token:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            else:
                # Omite tokens inválidos para evitar bucles infinitos
                self.advance()

        # Envuelve los statements en un nodo Program para representar el AST completo
        if self.current_token is None:
            return Program(statements)
        else:
            self.error_handler.add_error("Fin de archivo inesperado", self.current_token.lineno)
            return None

    def parse_statement(self):
        """Analiza un solo statement (declaración, expresión, control, etc.)"""
        if not self.current_token:
            return None

        # Casos para diferentes tipos de statements
        if self.current_token.type == 'IMPORT':
            return self.parse_import()
        elif self.current_token.type in ['VAR', 'CONST']:
            stmt = self.parse_declaration()
            self.expect('SEMI', "Falta ';' después de la declaración")
            return stmt
        elif self.current_token.type == 'PRINT':
            return self.parse_print()
        elif self.current_token.type == 'IF':
            return self.parse_if()
        elif self.current_token.type == 'WHILE':
            return self.parse_while()
        elif self.current_token.type == 'FUNC':
            return self.parse_function()
        elif self.current_token.type == 'RETURN':
            return self.parse_return()
        elif self.current_token.type == 'BREAK':
            self.advance()
            self.expect('SEMI', "Falta ';' después de break")
            return Break()
        elif self.current_token.type == 'CONTINUE':
            self.advance()
            self.expect('SEMI', "Falta ';' después de continue")
            return Continue()
        elif self.current_token.type == 'ID':
            # Verifica si es una llamada a función o una asignación
            if self.peek() and self.peek().type == 'LPAREN':
                return self.parse_function_call()
            else:
                return self.parse_assignment()
        else:
            self.error_handler.add_error(
                f"Token inesperado: {self.current_token.type}", 
                self.current_token.lineno
            )
            self.advance()
            return None
        
    def parse_expression(self):
        """Inicia el análisis de una expresión (jerarquía de operadores)"""
        return self.parse_logic_and()

    def parse_logic_and(self):
        """Analiza operadores lógicos AND (&&)"""
        node = self.parse_comparison()
        while self.current_token and self.current_token.type == 'LAND':
            op = self.current_token.value
            self.advance()
            right = self.parse_comparison()
            node = BinOp(op, node, right)
        return node

    def parse_comparison(self):
        """Analiza operadores de comparación (<, >, <=, >=, ==, !=)"""
        node = self.parse_term()
        while self.current_token and self.current_token.type in ['LT', 'GT', 'LE', 'GE', 'EQ', 'NE']:
            op = self.current_token.value
            self.advance()
            right = self.parse_term()
            node = BinOp(op, node, right)
        return node

    def parse_term(self):
        """Analiza operadores de suma y resta (+, -)"""
        node = self.parse_factor()
        while self.current_token and self.current_token.type in ['PLUS', 'MINUS']:
            op = self.current_token.value
            self.advance()
            right = self.parse_factor()
            node = BinOp(op, node, right)
        return node

    def parse_factor(self):
        """Analiza operadores de multiplicación, división y módulo (*, /, %, //)"""
        node = self.parse_unary()
        while self.current_token and self.current_token.type in ['TIMES', 'DIVIDE', 'MOD', 'INT_DIV']:
            op = self.current_token.value
            self.advance()
            right = self.parse_unary()
            node = BinOp(op, node, right)
        return node

    def parse_unary(self):
        """Analiza operadores unarios (+, -, !, *)"""
        if self.current_token and self.current_token.type in ['PLUS', 'MINUS', 'NOT', 'DEREF']:
            op = self.current_token.value
            self.advance()
            if self.current_token.type == 'DEREF':
                return Dereference(self.parse_primary())
            return UnaryOp(op, self.parse_primary())
        return self.parse_primary()

    def parse_primary(self):
        """Analiza elementos primarios (literales, identificadores, paréntesis)"""
        token = self.current_token
        if token.type == 'INTEGER':
            self.advance()
            return Integer(int(token.value))
        elif token.type == 'FLOAT':
            self.advance()
            return Float(float(token.value))
        elif token.type == 'LPAREN':
            self.advance()
            expr = self.parse_expression()
            self.expect('RPAREN', "Falta ')' para cerrar la expresión")
            return expr
        elif token.type == 'ID':
            self.advance()
            node = Location(token.value)
            if self.current_token and self.current_token.type == 'LPAREN':
                # Llamada a función
                self.advance()  # Consume '('
                args = []
                if self.current_token.type != 'RPAREN':
                    args.append(self.parse_expression())
                    while self.current_token and self.current_token.type == 'COMMA':
                        self.advance()
                        args.append(self.parse_expression())
                self.expect('RPAREN', "Se esperaba ')' después de los argumentos")
                node = FunctionCall(token.value, args)
            return node
        elif token.type in ['TRUE', 'FALSE']:
            self.advance()
            return Boolean(token.value.lower() == 'true')
        elif token.type == 'STRING':
            self.advance()
            return String(token.value)
        elif token.type == 'CHAR':
            self.advance()
            return Char(token.value)
        else:
            self.error_handler.add_error("Expresión inválida", token.lineno)
            self.advance()
            return None

    def parse_location(self):
        """Analiza una ubicación (identificador)"""
        ident = self.current_token.value
        self.expect('ID')
        return Location(ident)

    def parse_print(self):
        """Analiza una sentencia print"""
        self.expect('PRINT')
        expr = self.parse_expression()
        self.expect('SEMI', "Falta ';' después de print")
        return Print(expr)

    def parse_assignment(self):
        """Analiza una asignación (=)"""
        location = self.parse_location()
        self.expect('ASSIGN', "Falta '=' en la asignación")
        expr = self.parse_expression()
        self.expect('SEMI', "Falta ';' después de la asignación")
        return Assignment(location, expr)

    def parse_if(self):
        """Analiza una sentencia if-else"""
        self.expect('IF')
        test = self.parse_expression()
        self.expect('LBRACE', "Falta '{' después de la condición if")
        consequence = []
        while self.current_token and self.current_token.type != 'RBRACE':
            consequence.append(self.parse_statement())
        self.expect('RBRACE', "Falta '}' al final del bloque if")
        
        alternative = []
        if self.current_token and self.current_token.type == 'ELSE':
            self.advance()
            self.expect('LBRACE', "Falta '{' después de else")
            while self.current_token and self.current_token.type != 'RBRACE':
                alternative.append(self.parse_statement())
            self.expect('RBRACE', "Falta '}' al final del bloque else")
        return If(test, consequence, alternative)

    def parse_while(self):
        """Analiza una sentencia while"""
        self.expect('WHILE')
        test = self.parse_expression()
        self.expect('LBRACE', "Falta '{' después de la condición while")
        body = []
        while self.current_token and self.current_token.type != 'RBRACE':
            body.append(self.parse_statement())
        self.expect('RBRACE', "Falta '}' al final del bloque while")
        return While(test, body)
    
    def parse_declaration(self):
        """Analiza declaraciones (var/const)"""
        is_const = self.current_token.type == 'CONST'
        self.advance()
        ident = self.expect('ID', "Se esperaba un identificador en la declaración").value
        
        # Manejo de tipos (opcional)
        var_type = None
        if self.current_token and self.current_token.type in ['INT', 'FLOAT_TYPE', 'BOOL', 'STRING_TYPE', 'CHAR_TYPE', 'ID']:
            var_type = self.current_token.value
            self.advance()
        
        self.expect('ASSIGN', "Se esperaba '=' en la declaración")
        value = self.parse_expression()
        
        self.expect('SEMI', "Falta ';' después de la declaración")
        
        if is_const:
            return ConstantDecl(ident, value)
        else:
            return VariableDecl(ident, var_type, value)

    def parse_function_call(self):
        """Analiza una llamada a función"""
        name = self.current_token.value
        self.expect('ID', "Se esperaba un nombre de función")
        self.expect('LPAREN', "Se esperaba '(' después del nombre de la función")
        args = []
        if self.current_token.type != 'RPAREN':
            args.append(self.parse_expression())
            while self.current_token and self.current_token.type == 'COMMA':
                self.advance()
                args.append(self.parse_expression())
        self.expect('RPAREN', "Se esperaba ')' después de los argumentos")
        self.expect('SEMI', "Falta ';' después de la llamada a función")
        return FunctionCall(name, args)

    def parse_function(self):
        """Analiza una declaración de función"""
        self.expect('FUNC')
        name = self.expect('ID', "Se esperaba un nombre de función después de FUNC").value
        self.expect('LPAREN', "Se esperaba '(' después del nombre de la función")
        params = []
        if self.current_token.type != 'RPAREN':
            param_name = self.expect('ID', "Se esperaba un nombre de parámetro").value
            
            # Manejo de tipo de parámetro (opcional)
            param_type = None
            if self.current_token and self.current_token.type in ['INT', 'FLOAT_TYPE', 'BOOL', 'STRING_TYPE', 'CHAR_TYPE', 'ID']:
                param_type = self.current_token.value
                self.advance()
            
            params.append(Parameter(param_name, param_type))
            while self.current_token and self.current_token.type == 'COMMA':
                self.advance()
                param_name = self.expect('ID', "Se esperaba un nombre de parámetro").value
                
                param_type = None
                if self.current_token and self.current_token.type in ['INT', 'FLOAT_TYPE', 'BOOL', 'STRING_TYPE', 'CHAR_TYPE', 'ID']:
                    param_type = self.current_token.value
                    self.advance()
                
                params.append(Parameter(param_name, param_type))
        self.expect('RPAREN', "Se esperaba ')' después de los parámetros")
        
        # Manejo de tipo de retorno (opcional)
        return_type = None
        if self.current_token and self.current_token.type in ['INT', 'FLOAT_TYPE', 'BOOL', 'STRING_TYPE', 'CHAR_TYPE', 'ID']:
            return_type = self.current_token.value
            self.advance()
        
        self.expect('LBRACE', "Se esperaba '{' para iniciar el cuerpo de la función")
        body = []
        while self.current_token and self.current_token.type != 'RBRACE':
            body.append(self.parse_statement())
        self.expect('RBRACE', "Se esperaba '}' para cerrar el cuerpo de la función")
        return FunctionDecl(name, params, return_type, body)

    def parse_return(self):
        """Analiza una sentencia return"""
        self.expect('RETURN')
        expr = self.parse_expression()
        self.expect('SEMI', "Falta ';' después de return")
        return Return(expr)

    def parse_import(self):
        """Analiza una declaración import"""
        self.expect('IMPORT')
        
        # Verifica si es una importación de función
        is_func_import = False
        if self.current_token and self.current_token.type == 'FUNC':
            is_func_import = True
            self.advance()
        
        module_name = self.expect('ID', "Se esperaba un nombre de módulo después de IMPORT").value
        
        # Si es una importación de función, analiza la firma
        if is_func_import:
            self.expect('LPAREN', "Se esperaba '(' después del nombre de la función")
            params = []
            
            # Analiza parámetros
            while self.current_token and self.current_token.type != 'RPAREN':
                param_name = self.expect('ID', "Se esperaba un nombre de parámetro").value
                
                # Manejo de tipo de parámetro
                param_type = None
                if self.current_token and self.current_token.type in ['INT', 'FLOAT_TYPE', 'BOOL', 'STRING_TYPE', 'CHAR_TYPE', 'ID']:
                    param_type = self.current_token.value
                    self.advance()
                
                params.append(Parameter(param_name, param_type))
                
                if self.current_token.type == 'COMMA':
                    self.advance()
            
            self.expect('RPAREN', "Se esperaba ')' después de los parámetros")
            
            # Manejo de tipo de retorno
            return_type = None
            if self.current_token and self.current_token.type in ['INT', 'FLOAT_TYPE', 'BOOL', 'STRING_TYPE', 'CHAR_TYPE', 'ID']:
                return_type = self.current_token.value
                self.advance()
            
            self.expect('SEMI', "Falta ';' después de la declaración import")
            return FunctionImportDecl(module_name, params, return_type)
        else:
            self.expect('SEMI', "Falta ';' después de la declaración import")
            return ImportDecl(module_name)