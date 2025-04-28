import json
from ASTnodes import *

def ast_to_json(node):
    """
    Convierte un nodo del AST (Abstract Syntax Tree) a un diccionario JSON serializable.
    
    Args:
        node: Nodo del AST a convertir
        
    Returns:
        dict: Diccionario con la representación JSON del nodo, o None si el nodo es None
    """
    # Caso base: nodo nulo
    if node is None:
        return None
    
    # Si es una lista, procesa cada elemento recursivamente
    if isinstance(node, list):
        return [ast_to_json(item) for item in node]

    # Estructura base para todos los nodos
    data = {"type": node.__class__.__name__}
    
    # Procesamiento específico para cada tipo de nodo
    if isinstance(node, Program):
        data["statements"] = ast_to_json(node.statements)
    
    # Literales básicos
    elif isinstance(node, Integer):
        data["value"] = node.value
    elif isinstance(node, Float):
        data["value"] = node.value
    elif isinstance(node, Boolean):
        data["value"] = node.value
    elif isinstance(node, String):
        data["value"] = node.value
    elif isinstance(node, Char):
        data["value"] = node.value
    
    # Operaciones
    elif isinstance(node, BinOp):
        data["operator"] = node.op
        data["left"] = ast_to_json(node.left)
        data["right"] = ast_to_json(node.right)
    elif isinstance(node, UnaryOp):
        data["operator"] = node.op
        data["operand"] = ast_to_json(node.operand)
    
    # Variables y referencias
    elif isinstance(node, Location):
        data["name"] = node.name
    elif isinstance(node, Dereference):
        data["location"] = ast_to_json(node.location)
    
    # Llamadas a función
    elif isinstance(node, FunctionCall):
        data["name"] = node.name
        data["arguments"] = ast_to_json(node.args)
    
    # Instrucciones
    elif isinstance(node, Print):
        data["expression"] = ast_to_json(node.expr)
    elif isinstance(node, Assignment):
        data["target"] = ast_to_json(node.location)
        data["value"] = ast_to_json(node.expr)
    elif isinstance(node, If):
        data["condition"] = ast_to_json(node.test)
        data["consequence"] = ast_to_json(node.consequence)
        data["alternative"] = ast_to_json(node.alternative)
    elif isinstance(node, While):
        data["condition"] = ast_to_json(node.test)
        data["body"] = ast_to_json(node.body)
    elif isinstance(node, Break):
        pass  # No necesita datos adicionales
    elif isinstance(node, Continue):
        pass  # No necesita datos adicionales
    elif isinstance(node, Return):
        data["value"] = ast_to_json(node.expr)
    
    # Declaraciones
    elif isinstance(node, VariableDecl):
        data["name"] = node.name
        data["type"] = node.var_type
        data["initial_value"] = ast_to_json(node.value)
    elif isinstance(node, ConstantDecl):
        data["name"] = node.name
        data["value"] = ast_to_json(node.value)
    elif isinstance(node, FunctionDecl):
        data["name"] = node.name
        data["parameters"] = ast_to_json(node.params)
        data["return_type"] = node.return_type
        data["body"] = ast_to_json(node.body)
    elif isinstance(node, Parameter):
        data["name"] = node.name
        data["type"] = node.param_type
    
    # Importaciones
    elif isinstance(node, ImportDecl):
        data["module_name"] = node.module_name
    elif isinstance(node, FunctionImportDecl):
        data["module_name"] = node.module_name
        data["params"] = ast_to_json(node.params)
        data["return_type"] = node.return_type
    
    return data

def save_ast_to_json(ast, filename="ast_output.json"):
    """
    Guarda la representación JSON del AST en un archivo.
    
    Args:
        ast: Árbol de sintaxis abstracta a serializar
        filename: Nombre del archivo de salida (por defecto "ast_output.json")
        
    Returns:
        dict: La representación JSON del AST
    """
    # Convierte el AST a JSON
    ast_json = ast_to_json(ast)
    
    # Escribe el JSON en el archivo
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(ast_json, f, indent=2, ensure_ascii=False)
    
    return ast_json