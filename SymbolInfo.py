from Types import Types

class SymbolInfo:
    """Clase base para información de símbolos con capacidades extendidas"""
    def __init__(self, name, dtype, scope_level=0):
        self.name = name
        self.dtype = self._validate_type(dtype)
        self.scope_level = scope_level
        self.is_constant = False
        self.is_initialized = False
        self.memory_address = None
        self.size = self._calculate_size()
        self.scope_name = ""  # Se establecerá al insertar en SymbolTab

    def _validate_type(self, dtype):
        """Valida el tipo y maneja tipos complejos"""
        if dtype in Types.TYPENAMES:
            return dtype
        
        # Manejo de tipos complejos (arrays, punteros)
        if dtype.startswith(('array[', 'pointer[')):
            base_type = dtype.split('[')[1][:-1]
            if base_type in Types.TYPENAMES:
                return dtype
            
        raise ValueError(f"Tipo inválido '{dtype}' para símbolo")

    def _calculate_size(self):
        """Calcula tamaño en bytes para asignación de memoria"""
        simple_types = {
            'int': 4,
            'float': 8,
            'char': 1,
            'bool': 1,
            'void': 0
        }
        if self.dtype in simple_types:
            return simple_types[self.dtype]
        return 0  # Se calculará dinámicamente para tipos complejos

    def get_base_type(self):
        """Obtiene el tipo base para tipos complejos"""
        if '[' in self.dtype:
            return self.dtype.split('[')[1][:-1]
        return self.dtype

class VariableSymbol(SymbolInfo):
    def __init__(self, name, dtype, value=None, is_param=False):
        super().__init__(name, dtype)
        self.value = value
        self.is_param = is_param
        self.is_reference = is_param  # Parámetros se pasan por referencia
        if value is not None:
            self.is_initialized = True

class FunctionSymbol(SymbolInfo):
    def __init__(self, name, return_type, params=None):
        super().__init__(name, return_type)
        self.params = params or []  # Lista de tuplas (name, dtype, is_reference)
        self.return_type = return_type
        self.defined = False
        self.local_symbols = None
        self.quad_start = -1  # Para generación de código

    def add_param(self, name, dtype, is_reference=False):
        self.params.append((name, dtype, is_reference))

class ConstantSymbol(SymbolInfo):
    def __init__(self, name, dtype, value):
        super().__init__(name, dtype)
        self.value = value
        self.is_constant = True
        self.is_initialized = True

class ArraySymbol(SymbolInfo):
    def __init__(self, name, dtype, dimensions):
        super().__init__(name, f"array[{dtype}]")
        self.dimensions = dimensions
        self.base_type = dtype
        self.size = self._calculate_array_size()

    def _calculate_array_size(self):
        base_size = super()._calculate_size()
        total = 1
        for dim in self.dimensions:
            if isinstance(dim, int):
                total *= dim
        return total * base_size

class PointerSymbol(SymbolInfo):
    def __init__(self, name, base_type):
        super().__init__(name, f"pointer[{base_type}]")
        self.base_type = base_type
        self.size = 8  # Tamaño estándar para punteros (64 bits)
        self.points_to = None

class TemporarySymbol(SymbolInfo):
    _counter = 0
    
    def __init__(self, dtype):
        TemporarySymbol._counter += 1
        super().__init__(f"$t{TemporarySymbol._counter}", dtype)
        self.is_temp = True

class SymbolFactory:
    @staticmethod
    def create(symbol_type, **kwargs):
        symbol_map = {
            'var': VariableSymbol,
            'func': FunctionSymbol,
            'const': ConstantSymbol,
            'array': ArraySymbol,
            'ptr': PointerSymbol,
            'temp': TemporarySymbol
        }
        if symbol_type not in symbol_map:
            raise ValueError(f"Tipo de símbolo inválido: {symbol_type}")
        return symbol_map[symbol_type](**kwargs)

    @staticmethod
    def create_temp(dtype):
        return TemporarySymbol(dtype)