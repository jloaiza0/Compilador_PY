class Program:
    def __init__(self, statements):
        self.statements = statements

    def to_dict(self):
        return {
            "type": "Program",
            "statements": [stmt.to_dict() for stmt in self.statements]
        }

class Print:
    def __init__(self, expression):
        self.expression = expression

    def to_dict(self):
        return {
            "type": "Print",
            "expression": self.expression.to_dict()
        }

class If:
    def __init__(self, condition, then_block, else_block=None):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

    def to_dict(self):
        return {
            "type": "If",
            "condition": self.condition.to_dict(),
            "then": self.then_block.to_dict(),
            "else": self.else_block.to_dict() if self.else_block else None
        }

class Block:
    def __init__(self, statements):
        self.statements = statements

    def to_dict(self):
        return {
            "type": "Block",
            "statements": [stmt.to_dict() for stmt in self.statements]
        }

class IntLiteral:
    def __init__(self, value):
        self.value = value

    def to_dict(self):
        return {"type": "IntLiteral", "value": self.value}

class FloatLiteral:
    def __init__(self, value):
        self.value = value

    def to_dict(self):
        return {"type": "FloatLiteral", "value": self.value}

class StringLiteral:
    def __init__(self, value):
        self.value = value

    def to_dict(self):
        return {"type": "StringLiteral", "value": self.value}

class BoolLiteral:
    def __init__(self, value):
        self.value = value

    def to_dict(self):
        return {"type": "BoolLiteral", "value": self.value}

class CharLiteral:
    def __init__(self, value):
        self.value = value

    def to_dict(self):
        return {"type": "CharLiteral", "value": self.value}

class Identifier:
    def __init__(self, name):
        self.name = name

    def to_dict(self):
        return {"type": "Identifier", "name": self.name}

class TypeCast:
    def __init__(self, cast_type, expression):
        self.cast_type = cast_type
        self.expression = expression

    def to_dict(self):
        return {
            "type": "TypeCast",
            "cast_type": self.cast_type,
            "expression": self.expression.to_dict()
        }

class MemoryAccess:
    def __init__(self, expression):
        self.expression = expression

    def to_dict(self):
        return {
            "type": "MemoryAccess",
            "expression": self.expression.to_dict()
        }

class ImportFunctionDecl:
    def __init__(self, name, params, return_type):
        self.name = name
        self.params = params  # list of (param_name, param_type)
        self.return_type = return_type

    def to_dict(self):
        return {
            "type": "ImportFunctionDecl",
            "name": self.name,
            "params": [{"name": name, "type": type_} for name, type_ in self.params],
            "return_type": self.return_type
        }

class ConstDecl:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def to_dict(self):
        return {
            "type": "ConstDecl",
            "name": self.name,
            "value": self.value.to_dict()
        }

class VarDecl:
    def __init__(self, name, var_type, value=None):
        self.name = name
        self.var_type = var_type
        self.value = value

    def to_dict(self):
        return {
            "type": "VarDecl",
            "name": self.name,
            "var_type": self.var_type,
            "value": self.value.to_dict() if self.value else None
        }

class Assignment:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def to_dict(self):
        return {
            "type": "Assignment",
            "name": self.name,
            "value": self.value.to_dict()
        }

class FuncDecl:
    def __init__(self, name, params, return_type, body):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body

    def to_dict(self):
        return {
            "type": "FuncDecl",
            "name": self.name,
            "params": [{"name": p[0], "type": p[1]} for p in self.params],
            "return_type": self.return_type,
            "body": self.body.to_dict()
        }

class Return:
    def __init__(self, value):
        self.value = value

    def to_dict(self):
        return {
            "type": "Return",
            "value": self.value.to_dict() if self.value else None
        }

class While:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def to_dict(self):
        return {
            "type": "While",
            "condition": self.condition.to_dict(),
            "body": self.body.to_dict()
        }

class BinaryOp:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def to_dict(self):
        return {
            "type": "BinaryOp",
            "operator": self.operator,
            "left": self.left.to_dict(),
            "right": self.right.to_dict()
        }

class FuncCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def to_dict(self):
        return {
            "type": "FuncCall",
            "name": self.name,
            "args": [arg.to_dict() for arg in self.args]
        }

# Alias for compatibility with parser import
Call = FuncCall

class Break:
    def to_dict(self):
        return {"type": "Break"}

class Continue:
    def to_dict(self):
        return {"type": "Continue"}


