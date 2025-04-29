class Program:
    def __init__(self, statements):
        self.statements = statements

    def to_dict(self):
        return {
            "type": "Program",
            "statements": [stmt.to_dict() for stmt in self.statements]
        }

    def accept(self, visitor, env):
        return visitor.visit_Program(self, env)

class Print:
    def __init__(self, expression):
        self.expression = expression
        self.dtype = None

    def to_dict(self):
        return {
            "type": "Print",
            "expression": self.expression.to_dict()
        }

    def accept(self, visitor, env):
        return visitor.visit_Print(self, env)

class If:
    def __init__(self, condition, then_block, else_block=None):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block
        self.dtype = None

    def to_dict(self):
        return {
            "type": "If",
            "condition": self.condition.to_dict(),
            "then": self.then_block.to_dict(),
            "else": self.else_block.to_dict() if self.else_block else None
        }

    def accept(self, visitor, env):
        return visitor.visit_If(self, env)

class Block:
    def __init__(self, statements):
        self.statements = statements
        self.dtype = None

    def to_dict(self):
        return {
            "type": "Block",
            "statements": [stmt.to_dict() for stmt in self.statements]
        }

    def accept(self, visitor, env):
        return visitor.visit_Block(self, env)

class IntLiteral:
    def __init__(self, value):
        self.value = value
        self.dtype = 'int'

    def to_dict(self):
        return {"type": "IntLiteral", "value": self.value}

    def accept(self, visitor, env):
        return visitor.visit_IntLiteral(self, env)

class FloatLiteral:
    def __init__(self, value):
        self.value = value
        self.dtype = 'float'

    def to_dict(self):
        return {"type": "FloatLiteral", "value": self.value}

    def accept(self, visitor, env):
        return visitor.visit_FloatLiteral(self, env)

class StringLiteral:
    def __init__(self, value):
        self.value = value
        self.dtype = 'string'

    def to_dict(self):
        return {"type": "StringLiteral", "value": self.value}

    def accept(self, visitor, env):
        return visitor.visit_StringLiteral(self, env)

class BoolLiteral:
    def __init__(self, value):
        self.value = value
        self.dtype = 'bool'

    def to_dict(self):
        return {"type": "BoolLiteral", "value": self.value}

    def accept(self, visitor, env):
        return visitor.visit_BoolLiteral(self, env)

class CharLiteral:
    def __init__(self, value):
        self.value = value
        self.dtype = 'char'

    def to_dict(self):
        return {"type": "CharLiteral", "value": self.value}

    def accept(self, visitor, env):
        return visitor.visit_CharLiteral(self, env)

class Identifier:
    def __init__(self, name):
        self.name = name
        self.dtype = None

    def to_dict(self):
        return {"type": "Identifier", "name": self.name}

    def accept(self, visitor, env):
        return visitor.visit_Identifier(self, env)

class TypeCast:
    def __init__(self, cast_type, expression):
        self.cast_type = cast_type
        self.expression = expression
        self.dtype = cast_type

    def to_dict(self):
        return {
            "type": "TypeCast",
            "cast_type": self.cast_type,
            "expression": self.expression.to_dict()
        }

    def accept(self, visitor, env):
        return visitor.visit_TypeCast(self, env)

class MemoryAccess:
    def __init__(self, expression):
        self.expression = expression
        self.dtype = None

    def to_dict(self):
        return {
            "type": "MemoryAccess",
            "expression": self.expression.to_dict()
        }

    def accept(self, visitor, env):
        return visitor.visit_MemoryAccess(self, env)

class ImportFunctionDecl:
    def __init__(self, name, params, return_type):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.dtype = return_type

    def to_dict(self):
        return {
            "type": "ImportFunctionDecl",
            "name": self.name,
            "params": [{"name": name, "type": type_} for name, type_ in self.params],
            "return_type": self.return_type
        }

    def accept(self, visitor, env):
        return visitor.visit_ImportFunctionDecl(self, env)

class ConstDecl:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.dtype = None

    def to_dict(self):
        return {
            "type": "ConstDecl",
            "name": self.name,
            "value": self.value.to_dict()
        }

    def accept(self, visitor, env):
        return visitor.visit_ConstDecl(self, env)

class VarDecl:
    def __init__(self, name, var_type, value=None):
        self.name = name
        self.var_type = var_type
        self.value = value
        self.dtype = var_type

    def to_dict(self):
        return {
            "type": "VarDecl",
            "name": self.name,
            "var_type": self.var_type,
            "value": self.value.to_dict() if self.value else None
        }

    def accept(self, visitor, env):
        return visitor.visit_VarDecl(self, env)

class Assignment:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.dtype = None

    def to_dict(self):
        return {
            "type": "Assignment",
            "name": self.name,
            "value": self.value.to_dict()
        }

    def accept(self, visitor, env):
        return visitor.visit_Assignment(self, env)

class FuncDecl:
    def __init__(self, name, params, return_type, body):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body
        self.dtype = return_type

    def to_dict(self):
        return {
            "type": "FuncDecl",
            "name": self.name,
            "params": [{"name": p[0], "type": p[1]} for p in self.params],
            "return_type": self.return_type,
            "body": self.body.to_dict()
        }

    def accept(self, visitor, env):
        return visitor.visit_FuncDecl(self, env)

class Return:
    def __init__(self, value):
        self.value = value
        self.dtype = None

    def to_dict(self):
        return {
            "type": "Return",
            "value": self.value.to_dict() if self.value else None
        }

    def accept(self, visitor, env):
        return visitor.visit_Return(self, env)

class While:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
        self.dtype = None

    def to_dict(self):
        return {
            "type": "While",
            "condition": self.condition.to_dict(),
            "body": self.body.to_dict()
        }

    def accept(self, visitor, env):
        return visitor.visit_While(self, env)

class BinaryOp:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
        self.dtype = None

    def to_dict(self):
        return {
            "type": "BinaryOp",
            "operator": self.operator,
            "left": self.left.to_dict(),
            "right": self.right.to_dict()
        }

    def accept(self, visitor, env):
        return visitor.visit_BinaryOp(self, env)

class FuncCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args
        self.dtype = None

    def to_dict(self):
        return {
            "type": "FuncCall",
            "name": self.name,
            "args": [arg.to_dict() for arg in self.args]
        }

    def accept(self, visitor, env):
        return visitor.visit_FuncCall(self, env)

Call = FuncCall  # Alias

class Break:
    def __init__(self):
        self.dtype = None
        
    def to_dict(self):
        return {"type": "Break"}

    def accept(self, visitor, env):
        return visitor.visit_Break(self, env)

class Continue:
    def __init__(self):
        self.dtype = None
        
    def to_dict(self):
        return {"type": "Continue"}

    def accept(self, visitor, env):
        return visitor.visit_Continue(self, env)