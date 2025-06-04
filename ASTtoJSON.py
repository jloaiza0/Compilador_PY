import json
from ASTnodes import *
from typing import Any, Dict, List, Optional, Union

def ast_to_json(node: Any) -> Optional[Union[Dict, List]]:
    """
    Convierte un nodo del AST a una estructura JSON serializable.
    
    Args:
        node: Nodo del AST o lista de nodos
        
    Returns:
        Diccionario o lista con la representación JSON, o None si el nodo es None
    """
    if node is None:
        return None
        
    if isinstance(node, list):
        return [ast_to_json(item) for item in node if item is not None]

    data = {"type": node.__class__.__name__}

    # Nodos base
    if isinstance(node, Program):
        data["statements"] = ast_to_json(node.statements)
    
    # Literales
    elif isinstance(node, (Integer, Float, Boolean, String, Char)):
        data["value"] = node.value
        if hasattr(node, 'type'):
            data["value_type"] = node.type
    
    # Operaciones
    elif isinstance(node, BinOp):
        data["op"] = node.op
        data["left"] = ast_to_json(node.left)
        data["right"] = ast_to_json(node.right)
    elif isinstance(node, UnaryOp):
        data["op"] = node.op
        data["operand"] = ast_to_json(node.operand)
    
    # Variables y memoria
    elif isinstance(node, Location):
        data["name"] = node.name
        if hasattr(node, 'symbol'):
            data["symbol"] = node.symbol.name if node.symbol else None
    
    # Estructuras de control
    elif isinstance(node, If):
        data["test"] = ast_to_json(node.test)
        data["consequence"] = ast_to_json(node.consequence)
        data["alternative"] = ast_to_json(node.alternative if node.alternative else None)
    elif isinstance(node, While):
        data["test"] = ast_to_json(node.test)
        data["body"] = ast_to_json(node.body)
    elif isinstance(node, For):
        data["init"] = ast_to_json(node.init)
        data["test"] = ast_to_json(node.test)
        data["update"] = ast_to_json(node.update)
        data["body"] = ast_to_json(node.body)
    
    # Funciones
    elif isinstance(node, FunctionCall):
        data["name"] = node.name
        data["args"] = ast_to_json(node.args)
    elif isinstance(node, FunctionDecl):
        data["name"] = node.name
        data["params"] = ast_to_json(node.params)
        data["return_type"] = node.return_type
        data["body"] = ast_to_json(node.body)
    
    # Declaraciones
    elif isinstance(node, VariableDecl):
        data["name"] = node.name
        data["var_type"] = node.var_type
        data["value"] = ast_to_json(node.value)
    elif isinstance(node, ConstantDecl):
        data["name"] = node.name
        data["value"] = ast_to_json(node.value)
    
    # Sentencias
    elif isinstance(node, Assignment):
        data["location"] = ast_to_json(node.location)
        data["expr"] = ast_to_json(node.expr)
    elif isinstance(node, Print):
        data["expr"] = ast_to_json(node.expr)
    elif isinstance(node, Return):
        data["expr"] = ast_to_json(node.expr)
    
    # Otros
    elif isinstance(node, (Break, Continue)):
        pass  # No necesitan datos adicionales
    elif isinstance(node, Parameter):
        data["name"] = node.name
        data["param_type"] = node.param_type
    elif isinstance(node, ImportDecl):
        data["module_name"] = node.module_name
    elif isinstance(node, FunctionImportDecl):
        data["module_name"] = node.module_name
        data["params"] = ast_to_json(node.params)
        data["return_type"] = node.return_type
    elif isinstance(node, Block):
        data["statements"] = ast_to_json(node.statements)
    else:
        raise ValueError(f"Tipo de nodo no soportado: {type(node).__name__}")

    # Campos comunes a todos los nodos
    if hasattr(node, 'lineno'):
        data["lineno"] = node.lineno
    if hasattr(node, 'type'):
        data["type_annotation"] = node.type
    if hasattr(node, 'symbol'):
        data["symbol"] = node.symbol.name if node.symbol else None
    if hasattr(node, 'temp_var'):
        data["temp_var"] = str(node.temp_var) if node.temp_var else None

    return data

def save_ast_to_json(ast: ASTNode, filename: str = "ast_output.json") -> Dict:
    """
    Guarda el AST como JSON en un archivo.
    
    Args:
        ast: Nodo raíz del AST
        filename: Ruta del archivo de salida
        
    Returns:
        Diccionario con la representación JSON
    """
    ast_json = ast_to_json(ast)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(ast_json, f, indent=2, ensure_ascii=False)
    
    return ast_json