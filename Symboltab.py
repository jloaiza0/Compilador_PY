class SymbolTab:
    """Tabla de símbolos jerárquica para el compilador"""
    
    class SymbolDefinedError(Exception):
        """Excepción para cuando un símbolo ya ha sido definido"""
        def __init__(self, symbol_name, scope_name):
            super().__init__(f"Symbol '{symbol_name}' already defined in scope '{scope_name}'")
            self.symbol_name = symbol_name
            self.scope_name = scope_name

    class SymbolConflictError(Exception):
        """Excepción para conflictos de tipos entre símbolos"""
        def __init__(self, symbol_name, existing_type, new_type):
            super().__init__(f"Type conflict for '{symbol_name}': existing={existing_type}, new={new_type}")
            self.symbol_name = symbol_name
            self.existing_type = existing_type
            self.new_type = new_type

    class SymbolNotFoundError(Exception):
        """Excepción para símbolos no encontrados"""
        def __init__(self, symbol_name):
            super().__init__(f"Symbol '{symbol_name}' not found in current or parent scopes")
            self.symbol_name = symbol_name

    def __init__(self, name, parent=None, scope_type="block"):
        """
        Inicializa la tabla de símbolos
        
        Args:
            name: Nombre identificador del ámbito (e.g. nombre de función)
            parent: Tabla de símbolos padre (None para ámbito global)
            scope_type: Tipo de ámbito ('global', 'function', 'block', 'class')
        """
        self.name = name
        self.scope_type = scope_type
        self.entries = {}          # {symbol_name: symbol_info}
        self.parent = parent
        self.children = []
        if self.parent:
            self.parent.children.append(self)
            
        # Para funciones: parámetros, tipo de retorno, etc.
        self.function_attributes = None if scope_type != "function" else {
            'return_type': None,
            'params': [],
            'has_return': False
        }

    def add(self, name, symbol_info, overwrite=False):
        """
        Agrega un símbolo a la tabla
        
        Args:
            name: Nombre del símbolo
            symbol_info: Información del símbolo (debe tener atributo 'dtype')
            overwrite: Si es True, permite sobreescribir símbolos existentes
        
        Raises:
            SymbolDefinedError: Si el símbolo ya existe y overwrite=False
            SymbolConflictError: Si hay conflicto de tipos
        """
        if name in self.entries:
            if not overwrite:
                if self.entries[name].dtype != symbol_info.dtype:
                    raise self.SymbolConflictError(
                        name, self.entries[name].dtype, symbol_info.dtype)
                raise self.SymbolDefinedError(name, self.name)
            # Si overwrite=True, actualizamos el símbolo
        self.entries[name] = symbol_info

    def get(self, name, current_scope_only=False):
        """
        Busca un símbolo en la tabla
        
        Args:
            name: Nombre del símbolo a buscar
            current_scope_only: Si True, no busca en ámbitos padres
        
        Returns:
            La información del símbolo o None si no se encuentra
        """
        if name in self.entries:
            return self.entries[name]
        if not current_scope_only and self.parent:
            return self.parent.get(name)
        return None

    def get_scope_level(self, name):
        """
        Determina en qué nivel de ámbito se encuentra un símbolo
        
        Returns:
            int: 0 para ámbito actual, 1 para padre, etc. o -1 si no existe
        """
        if name in self.entries:
            return 0
        if self.parent:
            parent_level = self.parent.get_scope_level(name)
            return parent_level + 1 if parent_level != -1 else -1
        return -1

    def print(self, indent=0, show_children=True):
        """Imprime la tabla de símbolos de forma jerárquica"""
        indent_str = '  ' * indent
        print(f"{indent_str}Scope: {self.name} ({self.scope_type})")
        
        if not self.entries:
            print(f"{indent_str}  (empty)")
        else:
            max_name_len = max(len(k) for k in self.entries.keys()) if self.entries else 0
            for name, info in self.entries.items():
                details = f"type={info.dtype}"
                if hasattr(info, 'value'):
                    details += f", value={info.value}"
                print(f"{indent_str}  {name.ljust(max_name_len)} : {details}")
        
        if show_children and self.children:
            print(f"{indent_str}  Sub-scopes:")
            for child in self.children:
                child.print(indent + 2)

    def __contains__(self, key):
        """Permite usar 'if key in symtab' para verificar existencia"""
        return self.get(key) is not None

    def __str__(self):
        """Representación compacta para debugging"""
        return f"SymbolTable(name={self.name}, entries={len(self.entries)}, children={len(self.children)})"