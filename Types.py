#types.py
class Types:
    """Manejo de tipos de datos y operaciones para el compilador"""
    
    # Conjunto de tipos de datos permitidos
    TYPENAMES = {'bool', 'char', 'float', 'int', 'string', 'void'}
    
    # Jerarquía de tipos para conversiones implícitas
    TYPE_HIERARCHY = {
        'bool': 0,
        'char': 1,
        'int': 2,
        'float': 3
    }
    
    # Operaciones binarias válidas
    BIN_OPS = {
        # Operaciones aritméticas
        ('int', '+', 'int'): 'int',
        ('int', '-', 'int'): 'int',
        ('int', '*', 'int'): 'int', 
        ('int', '/', 'int'): 'int',
        ('int', '%', 'int'): 'int',
        
        ('float', '+', 'float'): 'float',
        ('float', '-', 'float'): 'float',
        ('float', '*', 'float'): 'float',
        ('float', '/', 'float'): 'float',
        
        # Operaciones mixtas (int + float -> float)
        ('int', '+', 'float'): 'float',
        ('float', '+', 'int'): 'float',
        ('int', '-', 'float'): 'float',
        ('float', '-', 'int'): 'float',
        ('int', '*', 'float'): 'float',
        ('float', '*', 'int'): 'float',
        ('int', '/', 'float'): 'float',
        ('float', '/', 'int'): 'float',
        
        # Operaciones relacionales
        ('int', '<', 'int'): 'bool',
        ('int', '<=', 'int'): 'bool',
        ('int', '>', 'int'): 'bool',
        ('int', '>=', 'int'): 'bool',
        ('int', '==', 'int'): 'bool',
        ('int', '!=', 'int'): 'bool',
        
        ('float', '<', 'float'): 'bool',
        ('float', '<=', 'float'): 'bool',
        ('float', '>', 'float'): 'bool',
        ('float', '>=', 'float'): 'bool',
        ('float', '==', 'float'): 'bool',
        ('float', '!=', 'float'): 'bool',
        
        ('float', '<', 'int'): 'bool',
        ('float', '<=', 'int'): 'bool',
        ('int', '<', 'float'): 'bool',
        ('int', '<=', 'float'): 'bool',
        
        # Operaciones booleanas
        ('bool', '&&', 'bool'): 'bool',
        ('bool', '||', 'bool'): 'bool',
        ('bool', '==', 'bool'): 'bool',
        ('bool', '!=', 'bool'): 'bool',
        
        # Operaciones con caracteres
        ('char', '<', 'char'): 'bool',
        ('char', '<=', 'char'): 'bool',
        ('char', '>', 'char'): 'bool',
        ('char', '>=', 'char'): 'bool',
        ('char', '==', 'char'): 'bool',
        ('char', '!=', 'char'): 'bool',
        
        # Operaciones con strings (concatenación)
        ('string', '+', 'string'): 'string',
    }
    
    # Operaciones unarias válidas
    UNARY_OPS = {
        # Enteros
        ('+', 'int'): 'int',
        ('-', 'int'): 'int',
        ('~', 'int'): 'int',  # Negación de bits
        
        # Flotantes
        ('+', 'float'): 'float',
        ('-', 'float'): 'float',
        
        # Booleanos
        ('!', 'bool'): 'bool',
        
        # Memoria
        ('^', 'int'): 'int',  # Operador de puntero
    }
    
    @classmethod
    def is_valid_type(cls, type_name):
        """Verifica si un tipo es válido"""
        return type_name in cls.TYPENAMES
    
    @classmethod
    def check_binop(cls, op, left_type, right_type):
        """
        Verifica si una operación binaria es válida.
        Retorna el tipo de resultado si es válida, o None si no es válida.
        """
        # Primero verifica la operación exacta
        result_type = cls.BIN_OPS.get((left_type, op, right_type))
        if result_type is not None:
            return result_type
        
        # Si no encuentra, verifica si hay conversión implícita posible
        if op in {'+', '-', '*', '/', '<', '<=', '>', '>=', '==', '!='}:
            # Para operaciones aritméticas y comparativas
            left_rank = cls.TYPE_HIERARCHY.get(left_type, -1)
            right_rank = cls.TYPE_HIERARCHY.get(right_type, -1)
            
            if left_rank != -1 and right_rank != -1:
                promoted_type = left_type if left_rank > right_rank else right_type
                return cls.BIN_OPS.get((promoted_type, op, promoted_type))
        
        return None
    
    @classmethod
    def check_unaryop(cls, op, operand_type):
        """
        Verifica si una operación unaria es válida.
        Retorna el tipo de resultado si es válida, o None si no es válida.
        """
        return cls.UNARY_OPS.get((op, operand_type))
    
    @classmethod
    def get_wider_type(cls, type1, type2):
        """
        Obtiene el tipo más amplio entre dos tipos para conversiones implícitas.
        """
        rank1 = cls.TYPE_HIERARCHY.get(type1, -1)
        rank2 = cls.TYPE_HIERARCHY.get(type2, -1)
        
        if rank1 == -1 or rank2 == -1:
            return None
        
        return type1 if rank1 > rank2 else type2