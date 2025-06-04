try:
    from lexer import *
    from gox_error_manager import *
    from goxLang_AST_nodes import *
    from ASTtoJSON import save_ast_to_json
except ImportError as e:
    print(f"Error de importación: {e}")
    exit(1)

class Parser:
    def __init__(self, tokens, error_handler):
        self.tokens = tokens
        self.error_handler = error_handler
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def peek(self, offset=1):
        peek_pos = self.pos + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None

    def expect(self, token_type, err_msg=None):
        if self.current_token and self.current_token.type == token_type:
            token = self.current_token
            self.advance()
            return token
        else:
            err = err_msg or f"Se esperaba {token_type}"
            if self.current_token:
                self.error_handler.add_error(err, self.current_token.lineno)
            else:
                self.error_handler.add_error(err, "Fin del archivo")
            return None

    def parse(self):
        statements = []
        while self.current_token and self.current_token.type != 'EOF':
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            else:
                self.advance()

        return Program(statements)

    def parse_statement(self):
        if not self.current_token:
            return None

        token_type = self.current_token.type
        
        if token_type == 'VAR':
            decl = self.parse_declaration()
            self.expect('SEMICOLON', "Falta ';' después de la declaración")
            return decl
        elif token_type == 'CONST':
            decl = self.parse_declaration()
            self.expect('SEMICOLON', "Falta ';' después de la constante")
            return decl
        elif token_type == 'FUNC':
            return self.parse_function()
        elif token_type == 'IF':
            return self.parse_if()
        elif token_type == 'WHILE':
            return self.parse_while()
        elif token_type == 'RETURN':
            return self.parse_return()
        elif token_type == 'BREAK':
            self.advance()
            self.expect('SEMICOLON', "Falta ';' después de break")
            return Break()
        elif token_type == 'CONTINUE':
            self.advance()
            self.expect('SEMICOLON', "Falta ';' después de continue")
            return Continue()
        elif token_type == 'PRINT':
            return self.parse_print()
        elif token_type == 'ID':
            if self.peek() and self.peek().type == 'LPAREN':
                return self.parse_function_call()
            else:
                return self.parse_assignment()
        else:
            self.error_handler.add_error(
                f"Declaración inválida: {token_type}", 
                self.current_token.lineno
            )
            self.advance()
            return None

    def parse_expression(self):
        return self.parse_logic_or()

    def parse_logic_or(self):
        node = self.parse_logic_and()
        while self.current_token and self.current_token.type == 'OR':
            op = self.current_token.value
            self.advance()
            right = self.parse_logic_and()
            node = BinOp(op, node, right)
        return node

    def parse_logic_and(self):
        node = self.parse_comparison()
        while self.current_token and self.current_token.type == 'AND':
            op = self.current_token.value
            self.advance()
            right = self.parse_comparison()
            node = BinOp(op, node, right)
        return node

    def parse_comparison(self):
        node = self.parse_term()
        ops = ['LT', 'GT', 'LE', 'GE', 'EQ', 'NE']
        while self.current_token and self.current_token.type in ops:
            op = self.current_token.value
            self.advance()
            right = self.parse_term()
            node = BinOp(op, node, right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.current_token and self.current_token.type in ['PLUS', 'MINUS']:
            op = self.current_token.value
            self.advance()
            right = self.parse_factor()
            node = BinOp(op, node, right)
        return node

    def parse_factor(self):
        node = self.parse_unary()
        while self.current_token and self.current_token.type in ['TIMES', 'DIVIDE', 'MOD']:
            op = self.current_token.value
            self.advance()
            right = self.parse_unary()
            node = BinOp(op, node, right)
        return node

    def parse_unary(self):
        if self.current_token and self.current_token.type in ['PLUS', 'MINUS', 'NOT']:
            op = self.current_token.value
            self.advance()
            return UnaryOp(op, self.parse_primary())
        elif self.current_token and self.current_token.type == 'ADDRESS':
            self.advance()
            return AddressOf(self.parse_primary())
        elif self.current_token and self.current_token.type == 'MEMORY':
            self.advance()
            return MemoryAccess(self.parse_primary())
        return self.parse_primary()

    def parse_primary(self):
        token = self.current_token
        if not token:
            return None

        if token.type == 'INTEGER':
            self.advance()
            return Integer(int(token.value))
        elif token.type == 'FLOAT':
            self.advance()
            return Float(float(token.value))
        elif token.type in ['TRUE', 'FALSE']:
            self.advance()
            return Boolean(token.value == 'true')
        elif token.type == 'STRING':
            self.advance()
            return String(token.value)
        elif token.type == 'CHAR':
            self.advance()
            return Char(token.value[1:-1])
        elif token.type == 'LPAREN':
            self.advance()
            expr = self.parse_expression()
            self.expect('RPAREN', "Falta ')' para cerrar la expresión")
            return expr
        elif token.type == 'ID':
            self.advance()
            if self.current_token and self.current_token.type == 'LPAREN':
                return self.parse_function_call_body(token.value)
            return Variable(token.value)
        else:
            self.error_handler.add_error(
                f"Expresión inválida: {token.type}", 
                token.lineno
            )
            self.advance()
            return None

    def parse_function_call_body(self, name):
        self.expect('LPAREN')
        args = []
        if self.current_token and self.current_token.type != 'RPAREN':
            args.append(self.parse_expression())
            while self.current_token and self.current_token.type == 'COMMA':
                self.advance()
                args.append(self.parse_expression())
        self.expect('RPAREN')
        return FunctionCall(name, args)

    def parse_declaration(self):
        is_const = self.current_token.type == 'CONST'
        self.advance()
        name = self.expect('ID', "Se esperaba nombre de variable").value
        
        var_type = None
        if self.current_token and self.current_token.type == 'TYPE':
            var_type = self.current_token.value
            self.advance()
        
        self.expect('ASSIGN', "Falta '=' en la declaración")
        value = self.parse_expression()
        
        if is_const:
            return ConstDecl(name, var_type, value)
        else:
            return VarDecl(name, var_type, value)

    def parse_function(self):
        self.expect('FUNC')
        name = self.expect('ID', "Se esperaba nombre de función").value
        self.expect('LPAREN')
        
        params = []
        if self.current_token and self.current_token.type != 'RPAREN':
            param_name = self.expect('ID').value
            param_type = None
            if self.current_token and self.current_token.type == 'TYPE':
                param_type = self.current_token.value
                self.advance()
            params.append((param_name, param_type))
            
            while self.current_token and self.current_token.type == 'COMMA':
                self.advance()
                param_name = self.expect('ID').value
                param_type = None
                if self.current_token and self.current_token.type == 'TYPE':
                    param_type = self.current_token.value
                    self.advance()
                params.append((param_name, param_type))
        
        self.expect('RPAREN')
        
        return_type = None
        if self.current_token and self.current_token.type == 'TYPE':
            return_type = self.current_token.value
            self.advance()
        
        self.expect('LBRACE')
        body = []
        while self.current_token and self.current_token.type != 'RBRACE':
            body.append(self.parse_statement())
        self.expect('RBRACE')
        
        return Function(name, params, return_type, body)

    def parse_if(self):
        self.expect('IF')
        condition = self.parse_expression()
        self.expect('LBRACE')
        
        then_block = []
        while self.current_token and self.current_token.type != 'RBRACE':
            then_block.append(self.parse_statement())
        self.expect('RBRACE')
        
        else_block = []
        if self.current_token and self.current_token.type == 'ELSE':
            self.advance()
            self.expect('LBRACE')
            while self.current_token and self.current_token.type != 'RBRACE':
                else_block.append(self.parse_statement())
            self.expect('RBRACE')
        
        return If(condition, then_block, else_block)

    def parse_while(self):
        self.expect('WHILE')
        condition = self.parse_expression()
        self.expect('LBRACE')
        
        body = []
        while self.current_token and self.current_token.type != 'RBRACE':
            body.append(self.parse_statement())
        self.expect('RBRACE')
        
        return While(condition, body)

    def parse_return(self):
        self.expect('RETURN')
        expr = self.parse_expression()
        self.expect('SEMICOLON', "Falta ';' después de return")
        return Return(expr)

    def parse_print(self):
        self.expect('PRINT')
        expr = self.parse_expression()
        self.expect('SEMICOLON', "Falta ';' después de print")
        return Print(expr)

    def parse_assignment(self):
        target = Variable(self.current_token.value)
        self.advance()
        self.expect('ASSIGN', "Falta '=' en la asignación")
        value = self.parse_expression()
        self.expect('SEMICOLON', "Falta ';' después de la asignación")
        return Assign(target, value)