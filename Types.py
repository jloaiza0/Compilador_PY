# Types.py
class Types:
    """Manejo de tipos de datos y operaciones para el compilador GoX"""

    # Conjunto de tipos de datos permitidos
    TYPENAMES = {'bool', 'char', 'float', 'int', 'string', 'void'}

    # Jerarquía de tipos para conversiones implícitas
    # Un número mayor implica mayor precedencia para la promoción.
    TYPE_HIERARCHY = {
        'bool': 0,
        'char': 1,
        'int': 2,
        'float': 3
        # 'string' y 'void' no suelen ser parte de la jerarquía de promoción numérica/booleana.
    }

    # Operaciones binarias válidas y su tipo de resultado
    # Tupla: (left_type, operator, right_type) -> result_type
    BIN_OPS = {
        # Operaciones aritméticas para enteros
        ('int', '+', 'int'): 'int',
        ('int', '-', 'int'): 'int',
        ('int', '*', 'int'): 'int',
        ('int', '/', 'int'): 'int',  # División entera
        ('int', '%', 'int'): 'int',  # Módulo

        # Operaciones aritméticas para flotantes
        ('float', '+', 'float'): 'float',
        ('float', '-', 'float'): 'float',
        ('float', '*', 'float'): 'float',
        ('float', '/', 'float'): 'float',  # División de punto flotante
        # Considerar: ('float', '%', 'float'): 'float', # si se desea fmod para flotantes

        # Operaciones aritméticas mixtas (int y float) -> promoción a float
        ('int', '+', 'float'): 'float',
        ('float', '+', 'int'): 'float',
        ('int', '-', 'float'): 'float',
        ('float', '-', 'int'): 'float',
        ('int', '*', 'float'): 'float',
        ('float', '*', 'int'): 'float',
        ('int', '/', 'float'): 'float',
        ('float', '/', 'int'): 'float',

        # Operaciones relacionales (resultan en bool)
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

        # Relacionales mixtas (int y float) -> promoción antes de comparar
        # Aunque la lógica de promoción en check_binop lo cubre, explicitarlos aquí es más claro.
        ('int', '<', 'float'): 'bool',
        ('float', '<', 'int'): 'bool',
        ('int', '<=', 'float'): 'bool',
        ('float', '<=', 'int'): 'bool',
        ('int', '>', 'float'): 'bool',
        ('float', '>', 'int'): 'bool',
        ('int', '>=', 'float'): 'bool',
        ('float', '>=', 'int'): 'bool',
        ('int', '==', 'float'): 'bool',
        ('float', '==', 'int'): 'bool',
        ('int', '!=', 'float'): 'bool',
        ('float', '!=', 'int'): 'bool',

        ('char', '<', 'char'): 'bool',
        ('char', '<=', 'char'): 'bool',
        ('char', '>', 'char'): 'bool',
        ('char', '>=', 'char'): 'bool',
        ('char', '==', 'char'): 'bool',
        ('char', '!=', 'char'): 'bool',

        # Operaciones lógicas para booleanos
        ('bool', '&&', 'bool'): 'bool',  # AND lógico
        ('bool', '||', 'bool'): 'bool',  # OR lógico
        ('bool', '==', 'bool'): 'bool',  # Comparación de igualdad para bool
        ('bool', '!=', 'bool'): 'bool',  # Comparación de desigualdad para bool

        # Operaciones con strings
        ('string', '+', 'string'): 'string',  # Concatenación
        # Considerar para el futuro si se desea:
        # ('string', '==', 'string'): 'bool',
        # ('string', '!=', 'string'): 'bool',
        # ('char', '+', 'string'): 'string',
        # ('string', '+', 'char'): 'string',
    }

    # Operaciones unarias válidas y su tipo de resultado
    # Tupla: (operator, operand_type) -> result_type
    UNARY_OPS = {
        # Para enteros
        ('+', 'int'): 'int',    # Identidad
        ('-', 'int'): 'int',    # Negación aritmética
        ('~', 'int'): 'int',    # Negación de bits (tilde)

        # Para flotantes
        ('+', 'float'): 'float',  # Identidad
        ('-', 'float'): 'float',  # Negación aritmética

        # Para booleanos
        ('!', 'bool'): 'bool',    # Negación lógica (NOT)

        # Operadores de memoria (específicos de GoX según el ejemplo)
        # '^' para `memsize = ^1000;`
        ('^', 'int'): 'int',    # Devuelve un 'int' (tamaño o la propia dirección/referencia)

        # '`' (backtick) es el operador de dereferencia/indirección, ej: `addr
        # El tipo de `addr depende de lo que se almacena o se espera.
        # Para el análisis estático, esto es complejo. Asumimos que puede leerse/escribirse
        # como un 'int' por defecto si no hay otro contexto, pero el análisis semántico
        # debe verificar esto cuidadosamente basándose en el contexto (asignación, cast).
        ('`', 'int'): 'int',  # Dereferencia dirección (tipo base 'int') a 'int'.
                                # El análisis semántico debe gestionar casos como `addr = 1.23` o `char(`addr)`.
    }

    @classmethod
    def is_valid_type(cls, type_name: str) -> bool:
        """Verifica si un nombre de tipo es uno de los tipos base definidos."""
        return type_name in cls.TYPENAMES

    @classmethod
    def check_binop(cls, op: str, left_type: str, right_type: str) -> str | None:
        """
        Verifica si una operación binaria es válida y retorna el tipo de resultado.
        Considera la promoción de tipos según TYPE_HIERARCHY.
        """
        if not (cls.is_valid_type(left_type) and cls.is_valid_type(right_type)):
            return None # Uno o ambos tipos de operando no son válidos

        # 1. Intento de coincidencia directa (ej. 'int' + 'float' -> 'float')
        result_type = cls.BIN_OPS.get((left_type, op, right_type))
        if result_type is not None:
            return result_type

        # 2. Si no hay coincidencia directa, intentar con promoción de tipos.
        #    Esto es para casos donde, por ejemplo, ('int', '+', 'float') no estuviera
        #    explícitamente en BIN_OPS, pero ('float', '+', 'float') sí.
        #    La promoción se aplica a un conjunto específico de operadores.
        promotable_operators = {'+', '-', '*', '/', '<', '<=', '>', '>=', '==', '!='}
        if op in promotable_operators:
            left_rank = cls.TYPE_HIERARCHY.get(left_type, -1)
            right_rank = cls.TYPE_HIERARCHY.get(right_type, -1)

            if left_rank != -1 and right_rank != -1 and left_rank != right_rank:
                # Determinar el tipo promovido (el de mayor rango)
                promoted_type = left_type if left_rank > right_rank else right_type
                
                # Verificar si la operación está definida para el tipo promovido consigo mismo
                # Ejemplo: si op='+', left='int', right='float', promoted_type='float'.
                # Se busca ('float', '+', 'float').
                return cls.BIN_OPS.get((promoted_type, op, promoted_type))
        
        return None # Operación no definida

    @classmethod
    def check_unaryop(cls, op: str, operand_type: str) -> str | None:
        """
        Verifica si una operación unaria es válida y retorna el tipo de resultado.
        """
        if not cls.is_valid_type(operand_type):
            return None
        return cls.UNARY_OPS.get((op, operand_type))

    @classmethod
    def get_wider_type(cls, type1: str, type2: str) -> str | None:
        """
        Compara dos tipos y devuelve el que tiene mayor precedencia en la jerarquía.
        Retorna None si alguno no está en la jerarquía o no son comparables de esta manera.
        """
        if not (cls.is_valid_type(type1) and cls.is_valid_type(type2)):
            return None

        rank1 = cls.TYPE_HIERARCHY.get(type1, -1)
        rank2 = cls.TYPE_HIERARCHY.get(type2, -1)

        if rank1 == -1 or rank2 == -1:
            # Uno o ambos tipos no están en la jerarquía de promoción (ej. 'string', 'void')
            return None

        return type1 if rank1 > rank2 else type2

    @classmethod
    def is_assignable(cls, target_type: str, value_type: str) -> bool:
        """
        Verifica si un valor de tipo 'value_type' puede ser asignado a una variable
        de tipo 'target_type'.
        Permite asignación directa si los tipos son iguales.
        Permite asignación si value_type puede promoverse implícitamente a target_type.
        """
        if not (cls.is_valid_type(target_type) and cls.is_valid_type(value_type)):
            return False

        if target_type == value_type:
            return True

        # No se puede asignar a/desde 'void'
        if target_type == 'void' or value_type == 'void':
            return False
        
        # Casos especiales de asignación para el operador de dereferencia `
        # Si el `target_type` es el resultado de una dereferencia (` `addr), y lo hemos modelado
        # como 'int' en UNARY_OPS, aquí permitimos que se le asignen otros tipos.
        # Esta lógica es una simplificación; el analizador semántico podría necesitar
        # tratar las lvalues de dereferencia de forma más específica.
        # Por ahora, la asignación a un `int` base solo permite `int` o tipos promocionables a `int`.
        # El manejo de ` `addr = valor` requerirá que el semantic checker
        # valide que `valor` puede ser almacenado en memoria y leído coherentemente.

        # Verificar promoción según jerarquía
        target_rank = cls.TYPE_HIERARCHY.get(target_type)
        value_rank = cls.TYPE_HIERARCHY.get(value_type)

        if target_rank is not None and value_rank is not None:
            # Se puede asignar si el tipo de destino es igual o "más ancho" que el tipo de valor
            # Ejemplo: float f; int i = 10; f = i;
            # (target_rank para float es 3, value_rank para int es 2) -> OK (3 >= 2)
            return target_rank >= value_rank
        
        # Por defecto, no es asignable si no hay igualdad o promoción jerárquica.
        return False

    @classmethod
    def is_castable(cls, current_type: str, target_type: str) -> bool:
        """
        Verifica si 'current_type' puede ser explícitamente casteado a 'target_type'.
        Suele ser más permisivo que la asignación implícita.
        Ejemplo: float f = 3.14; int i = (int)f;
        Ejemplo GoX: char c = char(`addr);
        """
        if not (cls.is_valid_type(current_type) and cls.is_valid_type(target_type)):
            return False

        if current_type == target_type:
            return True

        # No tiene sentido castear a/desde 'void' generalmente
        if target_type == 'void' or current_type == 'void':
            return False # O podría permitirse `(void)expresion`

        # Tipos en la jerarquía de promoción son generalmente inter-casteables
        # (int, float, char, bool)
        numeric_promotion_types = set(cls.TYPE_HIERARCHY.keys())
        if current_type in numeric_promotion_types and target_type in numeric_promotion_types:
            return True

        # Casos especiales basados en el ejemplo de GoX `char(addr)`:
        # Si `current_type` es 'int' (resultado de ` `addr ` según UNARY_OPS),
        # y `target_type` es 'char', 'float', o 'int'.
        if current_type == 'int' and target_type in {'char', 'float', 'int'}:
             # Esto refleja que el contenido de una dirección (modelado como 'int')
             # puede ser interpretado/casteado a char, float, o int.
            return True
        
        # Casting a string (ej. str(10)) - si el lenguaje lo soporta y se implementa
        # if target_type == 'string' and current_type in {'int', 'float', 'char', 'bool'}:
        # return True

        # Casting desde string - más complejo, usualmente por funciones dedicadas tipo parseInt()

        return False # Por defecto, no es casteable si no hay regla explícita