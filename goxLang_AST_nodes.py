# GoxLang_AST_nodes.py
# AST Node Definitions for GoxLang

class ASTNode:
    """Base class for all AST nodes."""
    def to_dict(self):
        result = {"type": self.__class__.__name__}
        for attr, value in self.__dict__.items():
            if isinstance(value, ASTNode):
                result[attr] = value.to_dict()
            elif isinstance(value, list):
                result[attr] = [v.to_dict() if isinstance(v, ASTNode) else v for v in value]
            else:
                result[attr] = value
        return result

# ---------------------------------------
# Literals and Basic Expressions
# ---------------------------------------

class IntLiteral(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"IntLiteral({self.value})"

class FloatLiteral(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"FloatLiteral({self.value})"

class BoolLiteral(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"BoolLiteral({self.value})"

class StringLiteral(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"StringLiteral('{self.value}')"

# ---------------------------------------
# Operations
# ---------------------------------------

class BinaryOp(ASTNode):
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right

    def __repr__(self):
        return f"BinaryOp('{self.operator}', {self.left}, {self.right})"

class UnaryOp(ASTNode):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

    def __repr__(self):
        return f"UnaryOp('{self.operator}', {self.operand})"

class CompareOp(ASTNode):
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right

    def __repr__(self):
        return f"CompareOp('{self.operator}', {self.left}, {self.right})"

class LogicalOp(ASTNode):
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right

    def __repr__(self):
        return f"LogicalOp('{self.operator}', {self.left}, {self.right})"

# ---------------------------------------
# Variables and Identifiers
# ---------------------------------------

class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Identifier('{self.name}')"

class Assignment(ASTNode):
    def __init__(self, target, expr):
        self.target = target
        self.expr = expr

    def __repr__(self):
        return f"Assignment({self.target}, {self.expr})"

# ---------------------------------------
# Declarations
# ---------------------------------------

class VarDecl(ASTNode):
    def __init__(self, name, var_type, init_expr=None):
        self.name = name
        self.var_type = var_type
        self.init_expr = init_expr

    def __repr__(self):
        return f"VarDecl('{self.name}', '{self.var_type}', {self.init_expr})"

class ConstDecl(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"ConstDecl('{self.name}', {self.value})"

# ---------------------------------------
# Control Structures
# ---------------------------------------

class If(ASTNode):
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def __repr__(self):
        return f"If({self.condition}, {self.then_branch}, {self.else_branch})"

class While(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"While({self.condition}, {self.body})"

class For(ASTNode):
    def __init__(self, init, condition, update, body):
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body

    def __repr__(self):
        return f"For({self.init}, {self.condition}, {self.update}, {self.body})"

class Break(ASTNode):
    def __repr__(self):
        return "Break()"

class Continue(ASTNode):
    def __repr__(self):
        return "Continue()"

# ---------------------------------------
# Functions
# ---------------------------------------

class FunctionDecl(ASTNode):
    def __init__(self, name, parameters, return_type, body):
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.body = body

    def __repr__(self):
        return f"FunctionDecl('{self.name}', {self.parameters}, '{self.return_type}', {self.body})"

class Parameter(ASTNode):
    def __init__(self, name, param_type):
        self.name = name
        self.param_type = param_type

    def __repr__(self):
        return f"Parameter('{self.name}', '{self.param_type}')"

class Return(ASTNode):
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"Return({self.expr})"

class FunctionCall(ASTNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"FunctionCall('{self.name}', {self.args})"

# ---------------------------------------
# Others
# ---------------------------------------

class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Block({self.statements})"

class Print(ASTNode):
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"Print({self.expr})"

class Program(ASTNode):
    def __init__(self, declarations):
        self.declarations = declarations

    def __repr__(self):
        return f"Program({self.declarations})"

