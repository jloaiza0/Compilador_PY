import os
import json
from goxLang_AST_nodes import (
    Program, Print, If, Block, IntLiteral, FloatLiteral, StringLiteral,
    BoolLiteral, Identifier, ImportFunctionDecl, MemoryAccess, CharLiteral,
    TypeCast, VarDecl, ConstDecl, FuncDecl, Assignment, BinaryOp,
    While, Return, Call
)
from lexer import GoxLangLexer, Token
from gox_error_manager import ErrorManager

class GoxLangParser:
    def __init__(self):
        self.lexer = GoxLangLexer()
        self.tokens = []
        self.current = 0
        self.errors = []
        self.error_manager = ErrorManager()

    def tokenize(self, source_code):
        return self.lexer.tokenize(source_code)

    def parse(self, source_code):
        self.tokens, self.errors = self.tokenize(source_code)
        self.tokens.append(Token("EOF", "", self.tokens[-1].lineno if self.tokens else 1))
        self.current = 0

        try:
            program_node = self.parse_program()
        except Exception as e:
            self.error_manager.add_error(str(e))
            return None

        os.makedirs("temp", exist_ok=True)
        with open("temp/ast_output.json", "w") as f:
            json.dump(program_node.to_dict(), f, indent=4)

        with open("temp/error_log.txt", "w") as f:
            for error in self.error_manager.get_errors():
                f.write(error + "\n")

        return program_node

    def parse_program(self):
        statements = []
        while not self.is_at_end():
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return Program(statements)

    def parse_statement(self):
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
        elif self.match("RETURN"):
            return self.parse_return()
        else:
            expr = self.parse_expression()
            if isinstance(expr, Identifier) and self.match("ASSIGN"):
                value = self.parse_expression()
                if not self.match("SEMICOLON"):
                    self.error_manager.add_error("Expected ';' after assignment")
                return Assignment(expr.name, value)
            elif self.match("LPAREN"):
                args = self.parse_argument_list()
                if not self.match("SEMICOLON"):
                    self.error_manager.add_error("Expected ';' after function call")
                return Call(expr.name, args)
            elif self.match("SEMICOLON"):
                return expr  # Expression statement
            else:
                self.error_manager.add_error("Unexpected statement")
                return None

    def parse_argument_list(self):
        args = []
        while not self.check("RPAREN") and not self.is_at_end():
            arg = self.parse_expression()
            args.append(arg)
            if not self.match("COMMA"):
                break
        if not self.match("RPAREN"):
            self.error_manager.add_error("Expected ')' after arguments")
        return args

    def parse_print(self):
        expr = self.parse_expression()
        if not self.match("SEMICOLON"):
            self.error_manager.add_error("Expected ';' after print statement")
        return Print(expr)

    def parse_if(self):
        condition = self.parse_expression()
        then_block = self.parse_block()
        else_block = None
        if self.match("ELSE"):
            else_block = self.parse_block()
        return If(condition, then_block, else_block)

    def parse_while(self):
        condition = self.parse_expression()
        body = self.parse_block()
        return While(condition, body)

    def parse_return(self):
        expr = self.parse_expression()
        if not self.match("SEMICOLON"):
            self.error_manager.add_error("Expected ';' after return statement")
        return Return(expr)

    def parse_import_func(self):
        if not self.match("FUNC"):
            self.error_manager.add_error("Expected 'func' after 'import'")
            return None
        return self._parse_func_signature(imported=True)

    def parse_func_decl(self):
        return self._parse_func_signature(imported=False)

    def _parse_func_signature(self, imported):
        if not self.check("ID"):
            self.error_manager.add_error("Expected function name")
            return None
        name = self.advance().value

        if not self.match("LPAREN"):
            self.error_manager.add_error("Expected '(' after function name")
            return None

        params = []
        while not self.check("RPAREN") and not self.is_at_end():
            if not self.check("ID"):
                self.error_manager.add_error("Expected parameter name")
                break
            param_name = self.advance().value
            if not self.check("TYPE"):
                self.error_manager.add_error("Expected type after parameter name")
                break
            param_type = self.advance().value
            params.append((param_name, param_type))
            if not self.match("COMMA"):
                break

        if not self.match("RPAREN"):
            self.error_manager.add_error("Expected ')' after parameters")

        if not self.check("TYPE"):
            self.error_manager.add_error("Expected return type")
            return None
        return_type = self.advance().value

        if imported:
            if not self.match("SEMICOLON"):
                self.error_manager.add_error("Expected ';' after imported function")
            return ImportFunctionDecl(name, params, return_type)
        else:
            body = self.parse_block()
            return FuncDecl(name, params, return_type, body)

    def parse_var_decl(self):
        if not self.check("ID"):
            self.error_manager.add_error("Expected variable name")
            return None
        name = self.advance().value

        if not self.check("TYPE"):
            self.error_manager.add_error("Expected type after variable name")
            return None
        var_type = self.advance().value

        value = None
        if self.match("ASSIGN"):
            value = self.parse_expression()

        if not self.match("SEMICOLON"):
            self.error_manager.add_error("Expected ';' after variable declaration")
        return VarDecl(name, var_type, value)

    def parse_const_decl(self):
        if not self.check("ID"):
            self.error_manager.add_error("Expected constant name")
            return None
        name = self.advance().value

        if not self.match("ASSIGN"):
            self.error_manager.add_error("Expected '=' in constant declaration")
            return None

        value = self.parse_expression()

        if not self.match("SEMICOLON"):
            self.error_manager.add_error("Expected ';' after constant declaration")
        return ConstDecl(name, value)

    def parse_block(self):
        statements = []
        if not self.match("LBRACE"):
            self.error_manager.add_error("Expected '{' at beginning of block")
            return Block([])

        while not self.check("RBRACE") and not self.is_at_end():
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)

        if not self.match("RBRACE"):
            self.error_manager.add_error("Expected '}' at end of block")
        return Block(statements)

    def parse_expression(self):
        return self.parse_equality()

    def parse_equality(self):
        expr = self.parse_comparison()
        while self.match("EQUAL", "NOTEQUAL"):
            operator = self.previous().type
            right = self.parse_comparison()
            expr = BinaryOp(expr, operator, right)
        return expr

    def parse_comparison(self):
        expr = self.parse_term()
        while self.match("LT", "GT", "LE", "GE"):
            operator = self.previous().type
            right = self.parse_term()
            expr = BinaryOp(expr, operator, right)
        return expr

    def parse_term(self):
        expr = self.parse_factor()
        while self.match("PLUS", "MINUS"):
            operator = self.previous().type
            right = self.parse_factor()
            expr = BinaryOp(expr, operator, right)
        return expr

    def parse_factor(self):
        expr = self.parse_unary()
        while self.match("STAR", "SLASH"):
            operator = self.previous().type
            right = self.parse_unary()
            expr = BinaryOp(expr, operator, right)
        return expr

    def parse_unary(self):
        if self.match("MINUS"):
            operator = self.previous().type
            right = self.parse_unary()
            return BinaryOp(IntLiteral(0), operator, right)
        return self.parse_primary()

    def parse_primary(self):
        tok = self.advance()
        if tok.type == "NUMBER":
            return IntLiteral(int(tok.value))
        elif tok.type == "FLOAT":
            return FloatLiteral(float(tok.value))
        elif tok.type == "STRING":
            return StringLiteral(tok.value)
        elif tok.type == "CHAR":
            return CharLiteral(tok.value)
        elif tok.type == "TRUE":
            return BoolLiteral(True)
        elif tok.type == "FALSE":
            return BoolLiteral(False)
        elif tok.type == "ID":
            return Identifier(tok.value)
        elif tok.type == "TYPECAST":
            type_name = tok.value
            if not self.match("LPAREN"):
                self.error_manager.add_error("Expected '(' after typecast")
                return None
            expr = self.parse_expression()
            if not self.match("RPAREN"):
                self.error_manager.add_error("Expected ')' after typecast")
            return TypeCast(type_name, expr)
        elif tok.type == "BACKTICK":
            if not self.match("LPAREN"):
                self.error_manager.add_error("Expected '(' after '`'")
                return None
            addr_expr = self.parse_expression()
            if not self.match("RPAREN"):
                self.error_manager.add_error("Expected ')' after address expression")
            return MemoryAccess(addr_expr)
        elif tok.type == "LPAREN":
            expr = self.parse_expression()
            if not self.match("RPAREN"):
                self.error_manager.add_error("Expected ')' after expression")
            return expr
        else:
            self.error_manager.add_error(f"Unexpected token in expression: {tok.type}")
            return None

    def match(self, *types):
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    def check(self, token_type):
        if self.is_at_end():
            return False
        return self.peek().type == token_type

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self):
        return self.peek().type == "EOF"

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]


# Ejemplo de uso para verificar funcionamiento básico del parser
if __name__ == "__main__":
    codigo = """
    import func put_image(base int, width int, height int) int;
    
    const xmin = -2.0;
    const xmax = 1.0;
    const ymin = -1.5;
    const ymax = 1.5;
    const threshhold = 1000;

    func in_mandelbrot(x0 float, y0 float, n int) bool {
        var x float = 0.0;
        var y float = 0.0;
        var xtemp float;
        while n > 0 {
            xtemp = x*x - y*y + x0;
            y = 2.0*x*y + y0;
            x = xtemp;
            n = n - 1;
            if x*x + y*y > 4.0 {
                return false;
            }
        }
        return true;
    }

    func mandel(width int, height int) int {
        var dx float = (xmax - xmin)/float(width);
        var dy float = (ymax - ymin)/float(height);
        var ix int = 0;
        var iy int = height-1;
        var addr int = 0;
        var memsize int = ^(width*height*4);

        while iy >= 0 {
            ix = 0;
            while ix < width {
                if in_mandelbrot(float(ix)*dx+xmin, float(iy)*dy+ymin, threshhold) {
            `addr = '\xff';
            `(addr+1) = '\x00';
            `(addr+2) = '\x00';
            `(addr+3) = '\xff';
                } else {
            `addr = '\xff';
            `(addr+1) = '\xff';
            `(addr+2) = '\xff';
            `(addr+3) = '\xff';
                }
                addr = addr + 4;
                ix = ix + 1;
            }
            iy = iy - 1;
        }
        return 0;
    }

    func make_plot(width int, height int) int {
        var result int = mandel(width, height);
        return put_image(0, width, height);
    }

    make_plot(800,800);
    """

    parser = GoxLangParser()
    ast = parser.parse(codigo)

    if ast:
        print("AST generado correctamente:")
        print(json.dumps(ast.to_dict(), indent=4))
    else:
        print("Hubo errores al generar el AST.")
        print("Errores detectados:")
        for err in parser.error_manager.get_errors():
            print(" -", err)


