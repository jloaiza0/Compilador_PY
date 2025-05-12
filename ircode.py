# ircode.py
from goxLang_AST_nodes import *
from gox_error_manager import ErrorManager

class Instruction:
    def __init__(self, op, arg1=None, arg2=None, result=None):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result

    def __str__(self):
        parts = [self.op]
        if self.arg1 is not None:
            parts.append(str(self.arg1))
        if self.arg2 is not None:
            parts.append(str(self.arg2))
        if self.result is not None:
            parts.append(str(self.result))
        return " ".join(parts)

class CodeGenerator:
    def __init__(self):
        self.instructions = []
        self.temp_count = 0
        self.label_count = 0
        self.errors = ErrorManager()

    def new_temp(self):
        temp = f"t{self.temp_count}"
        self.temp_count += 1
        return temp

    def new_label(self):
        label = f"L{self.label_count}"
        self.label_count += 1
        return label

    def emit(self, op, arg1=None, arg2=None, result=None):
        instr = Instruction(op, arg1, arg2, result)
        self.instructions.append(instr)
        return instr

    def generate(self, node):
        method_name = f"gen_{type(node).__name__}"
        method = getattr(self, method_name, self.gen_default)
        return method(node)

    def gen_default(self, node):
        self.errors.add_error(f"No handler for node type {type(node).__name__}")
        return None

    def gen_Program(self, node):
        for stmt in node.statements:
            self.generate(stmt)

    def gen_VarDecl(self, node):
        if node.value:
            temp = self.generate(node.value)
            self.emit("ASSIGN", temp, None, node.name)

    def gen_ConstDecl(self, node):
        temp = self.generate(node.value)
        self.emit("ASSIGN", temp, None, node.name)

    def gen_Assignment(self, node):
        value = self.generate(node.value)
        self.emit("ASSIGN", value, None, node.name)

    def gen_BinaryOp(self, node):
        left = self.generate(node.left)
        right = self.generate(node.right)
        temp = self.new_temp()
        self.emit(node.operator, left, right, temp)
        return temp

    def gen_UnaryOp(self, node):
        operand = self.generate(node.right)
        temp = self.new_temp()
        self.emit(node.operator, operand, None, temp)
        return temp

    def gen_TypeCast(self, node):
        expr = self.generate(node.expression)
        temp = self.new_temp()
        self.emit(f"CAST_{node.cast_type.upper()}", expr, None, temp)
        return temp

    def gen_IntLiteral(self, node):
        temp = self.new_temp()
        self.emit("LOADI", node.value, None, temp)
        return temp

    def gen_FloatLiteral(self, node):
        temp = self.new_temp()
        self.emit("LOADF", node.value, None, temp)
        return temp

    def gen_CharLiteral(self, node):
        temp = self.new_temp()
        self.emit("LOADC", repr(node.value), None, temp)
        return temp

    def gen_BoolLiteral(self, node):
        temp = self.new_temp()
        val = 1 if node.value else 0
        self.emit("LOADI", val, None, temp)
        return temp

    def gen_Identifier(self, node):
        return node.name

    def gen_If(self, node):
        cond = self.generate(node.condition)
        label_else = self.new_label()
        label_end = self.new_label()

        self.emit("IF_FALSE_GOTO", cond, None, label_else)
        for stmt in node.then_block.statements:
            self.generate(stmt)
        self.emit("GOTO", None, None, label_end)

        self.emit("LABEL", None, None, label_else)
        if node.else_block:
            for stmt in node.else_block.statements:
                self.generate(stmt)
        self.emit("LABEL", None, None, label_end)

    def gen_While(self, node):
        label_start = self.new_label()
        label_end = self.new_label()

        self.emit("LABEL", None, None, label_start)
        cond = self.generate(node.condition)
        self.emit("IF_FALSE_GOTO", cond, None, label_end)
        for stmt in node.body.statements:
            self.generate(stmt)
        self.emit("GOTO", None, None, label_start)
        self.emit("LABEL", None, None, label_end)

    def gen_Break(self, node):
        self.emit("BREAK")

    def gen_Continue(self, node):
        self.emit("CONTINUE")

    def gen_Return(self, node):
        value = self.generate(node.value) if node.value else None
        self.emit("RETURN", value)

    def gen_Print(self, node):
        value = self.generate(node.expression)
        self.emit("PRINT", value)

    def gen_FuncCall(self, node):
        args = [self.generate(arg) for arg in node.args]
        for arg in args:
            self.emit("PARAM", arg)
        temp = self.new_temp()
        self.emit("CALL", node.name, len(args), temp)
        return temp

    def get_code(self):
        return "\n".join(str(instr) for instr in self.instructions)

if __name__ == "__main__":
    import sys
    from parser import Parser
    from lexer import Lexer
    from check import TypeChecker

    if len(sys.argv) != 2:
        print("Uso: python ircode.py archivo.gox")
        sys.exit(1)

    filename = sys.argv[1]
    source = open(filename).read()

    lexer = Lexer()
    tokens, lex_errors = lexer.tokenize(source)
    if lex_errors:
        for err in lex_errors:
            print(err)
        sys.exit(1)

    parser = Parser(tokens)
    ast = parser.parse()
    if not ast:
        print("Errores de sintaxis.")
        sys.exit(1)

    checker = TypeChecker()
    if not checker.check(ast):
        print("Errores semánticos.")
        sys.exit(1)

    gen = CodeGenerator()
    gen.generate(ast)
    print(gen.get_code())