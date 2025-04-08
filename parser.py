import os
import json
from goxLang_AST_nodes import Program, Print, If, Block, IntLiteral, FloatLiteral, StringLiteral, BoolLiteral, Identifier
from lexer import GoxLangLexer, Token
from gox_error_manager import ErrorManager

class GoxLangParser:
    def __init__(self):
        self.lexer = GoxLangLexer()
        self.tokens = []
        self.current = 0
        self.errors = []
        self.error_manager = ErrorManager()

    def parse(self, source_code):
        self.tokens = self.lexer.tokenize(source_code)
        self.tokens.append(Token("EOF", "", self.tokens[-1].lineno if self.tokens else 1))
        self.current = 0

        try:
            program_node = self.parse_program()
        except Exception as e:
            self.error_manager.log_error(str(e))
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
        else:
            self.error_manager.log_error(f"Unexpected token: {self.peek().type}")
            self.advance()
            return None

    def parse_print(self):
        expression = self.parse_expression()
        if not self.match("SEMICOLON"):
            self.error_manager.log_error("Expected ';' after print statement")
        return Print(expression)

    def parse_if(self):
        condition = self.parse_expression()
        then_block = self.parse_block()
        else_block = None
        if self.match("ELSE"):
            else_block = self.parse_block()
        return If(condition, then_block, else_block)

    def parse_block(self):
        statements = []
        if not self.match("LBRACE"):
            self.error_manager.log_error("Expected '{' at beginning of block")
            return Block([])

        while not self.check("RBRACE") and not self.is_at_end():
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)

        if not self.match("RBRACE"):
            self.error_manager.log_error("Expected '}' at end of block")

        return Block(statements)

    def parse_expression(self):
        tok = self.advance()
        if tok.type == "NUMBER" or tok.type == "FLOAT":
            if "." in tok.value:
                return FloatLiteral(float(tok.value))
            else:
                return IntLiteral(int(tok.value))
        elif tok.type == "STRING":
            return StringLiteral(tok.value)
        elif tok.type == "TRUE" or tok.type == "FALSE":
            return BoolLiteral(tok.value == "true")
        elif tok.type == "ID":
            return Identifier(tok.value)
        else:
            self.error_manager.log_error(f"Unexpected token in expression: {tok.type}")
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
    print 42;
    if true {
        print 100;
    } else {
        print 0;
    }
    """

    parser = GoxLangParser()
    ast = parser.parse(codigo)

    if ast:
        print("AST generado correctamente:")
        print(json.dumps(ast.to_dict(), indent=4))
    else:
        print("Hubo errores al generar el AST.")


