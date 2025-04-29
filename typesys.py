# typesys.py
'''
Sistema de tipos para goxLang

Implementa las reglas de tipos para el lenguaje, incluyendo:
- Tipos básicos y sus operaciones permitidas
- Verificación de operaciones binarias y unarias
- Conversiones de tipos implícitas
'''

from dataclasses import dataclass
from typing import Dict, Tuple, Optional
from gox_error_manager import ErrorManager

# Tipos básicos del lenguaje
BASIC_TYPES = {
    'int': {'size': 4, 'signed': True},
    'float': {'size': 8, 'signed': True},
    'char': {'size': 1, 'signed': False},
    'bool': {'size': 1, 'signed': False},
    'string': {'size': None, 'signed': None},  # Tipo especial
    'void': {'size': 0, 'signed': None}       # Para funciones sin retorno
}

# Jerarquía de tipos para conversiones implícitas
TYPE_HIERARCHY = ['bool', 'char', 'int', 'float']

# Operadores binarios soportados
BIN_OPS = {
    # Aritméticos
    '+', '-', '*', '/', '%', '^',
    # Comparación
    '==', '!=', '<', '>', '<=', '>=',
    # Lógicos
    '&&', '||'
}

# Operadores unarios soportados
UNARY_OPS = {
    '+', '-', '!'
}

# Tabla de operaciones binarias válidas
BIN_OP_TABLE = {
    # Operaciones con enteros
    ('int', '+', 'int'): 'int',
    ('int', '-', 'int'): 'int',
    ('int', '*', 'int'): 'int',
    ('int', '/', 'int'): 'int',
    ('int', '%', 'int'): 'int',
    ('int', '^', 'int'): 'int',
    
    ('int', '==', 'int'): 'bool',
    ('int', '!=', 'int'): 'bool',
    ('int', '<', 'int'): 'bool',
    ('int', '>', 'int'): 'bool',
    ('int', '<=', 'int'): 'bool',
    ('int', '>=', 'int'): 'bool',

    # Operaciones con floats
    ('float', '+', 'float'): 'float',
    ('float', '-', 'float'): 'float',
    ('float', '*', 'float'): 'float',
    ('float', '/', 'float'): 'float',
    ('float', '^', 'float'): 'float',
    
    ('float', '==', 'float'): 'bool',
    ('float', '!=', 'float'): 'bool',
    ('float', '<', 'float'): 'bool',
    ('float', '>', 'float'): 'bool',
    ('float', '<=', 'float'): 'bool',
    ('float', '>=', 'float'): 'bool',

    # Operaciones mixtas (int y float)
    ('int', '+', 'float'): 'float',
    ('float', '+', 'int'): 'float',
    ('int', '-', 'float'): 'float',
    ('float', '-', 'int'): 'float',
    ('int', '*', 'float'): 'float',
    ('float', '*', 'int'): 'float',
    ('int', '/', 'float'): 'float',
    ('float', '/', 'int'): 'float',

    # Operaciones con booleanos
    ('bool', '&&', 'bool'): 'bool',
    ('bool', '||', 'bool'): 'bool',
    ('bool', '==', 'bool'): 'bool',
    ('bool', '!=', 'bool'): 'bool',

    # Operaciones con chars
    ('char', '==', 'char'): 'bool',
    ('char', '!=', 'char'): 'bool',
    ('char', '<', 'char'): 'bool',
    ('char', '>', 'char'): 'bool',
    ('char', '<=', 'char'): 'bool',
    ('char', '>=', 'char'): 'bool',
}

# Tabla de operaciones unarias válidas
UNARY_OP_TABLE = {
    ('+', 'int'): 'int',
    ('-', 'int'): 'int',
    ('+', 'float'): 'float',
    ('-', 'float'): 'float',
    ('!', 'bool'): 'bool',
}

@dataclass
class TypeInfo:
    name: str
    size: int
    signed: bool = False

def is_valid_type(type_name: str) -> bool:
    """Verifica si un tipo es válido en el lenguaje"""
    return type_name in BASIC_TYPES

def check_binop(op: str, left_type: str, right_type: str, error_manager: ErrorManager = None) -> Optional[str]:
    """
    Verifica si una operación binaria es válida entre dos tipos.
    
    Args:
        op: Operador (+, -, *, etc.)
        left_type: Tipo del operando izquierdo
        right_type: Tipo del operando derecho
        error_manager: Manejador de errores para reportar problemas
        
    Returns:
        El tipo resultante de la operación o None si no es válida
    """
    # Verificar tipos básicos
    if not is_valid_type(left_type) or not is_valid_type(right_type):
        if error_manager:
            error_manager.add_error(f"Invalid type in binary operation: {left_type} {op} {right_type}")
        return None
    
    # Buscar operación exacta
    result_type = BIN_OP_TABLE.get((left_type, op, right_type))
    
    # Si no se encuentra, intentar con conversión implícita
    if result_type is None and left_type != right_type:
        # Encontrar el tipo más alto en la jerarquía
        try:
            left_rank = TYPE_HIERARCHY.index(left_type)
            right_rank = TYPE_HIERARCHY.index(right_type)
            promoted_type = left_type if left_rank > right_rank else right_type
            result_type = BIN_OP_TABLE.get((promoted_type, op, promoted_type))
        except ValueError:
            pass
    
    if result_type is None and error_manager:
        error_manager.add_error(f"Invalid operation: {left_type} {op} {right_type}")
    
    return result_type

def check_unaryop(op: str, operand_type: str, error_manager: ErrorManager = None) -> Optional[str]:
    """
    Verifica si una operación unaria es válida para un tipo.
    
    Args:
        op: Operador (+, -, !)
        operand_type: Tipo del operando
        error_manager: Manejador de errores para reportar problemas
        
    Returns:
        El tipo resultante de la operación o None si no es válida
    """
    if not is_valid_type(operand_type):
        if error_manager:
            error_manager.add_error(f"Invalid type in unary operation: {op}{operand_type}")
        return None
    
    result_type = UNARY_OP_TABLE.get((op, operand_type))
    
    if result_type is None and error_manager:
        error_manager.add_error(f"Invalid unary operation: {op}{operand_type}")
    
    return result_type

def can_assign(target_type: str, source_type: str, error_manager: ErrorManager = None) -> bool:
    """
    Determina si se puede asignar un tipo a otro (conversión implícita).
    
    Args:
        target_type: Tipo de destino
        source_type: Tipo de origen
        error_manager: Manejador de errores para reportar problemas
        
    Returns:
        True si la asignación es válida
    """
    # Tipos iguales siempre son compatibles
    if target_type == source_type:
        return True
    
    # Verificar tipos básicos
    if not is_valid_type(target_type) or not is_valid_type(source_type):
        if error_manager:
            error_manager.add_error(f"Invalid types in assignment: {target_type} = {source_type}")
        return False
    
    # Chequear jerarquía de tipos
    try:
        target_rank = TYPE_HIERARCHY.index(target_type)
        source_rank = TYPE_HIERARCHY.index(source_type)
        return target_rank >= source_rank
    except ValueError:
        # Uno de los tipos no está en la jerarquía (bool, string, etc.)
        return False

def get_type_info(type_name: str) -> Optional[TypeInfo]:
    """
    Obtiene información detallada sobre un tipo.
    
    Args:
        type_name: Nombre del tipo a consultar
        
    Returns:
        TypeInfo con los detalles o None si el tipo no existe
    """
    if type_name in BASIC_TYPES:
        info = BASIC_TYPES[type_name]
        return TypeInfo(name=type_name, size=info['size'], signed=info['signed'])
    return None