class SymbolTab:
    
    # Excepción para cuando un símbolo ya ha sido definido
    class symbolDefinedError(Exception):
        pass

    # Excepción para cuando hay un conflicto entre símbolos (por ejemplo, tipos distintos)
    class SymbolConflictError(Exception):
        pass

    def __init__(self, name, parent=None):
        # Inicializa la tabla de símbolos
        self.name = name              # Nombre de la tabla (por ejemplo, nombre del bloque o función)
        self.entries = {}             # Diccionario para almacenar los símbolos
        self.parent = parent          # Referencia a la tabla de símbolos padre (si existe)
        if self.parent:
            self.parent.children.append(self)  # Agrega esta tabla como hija de la tabla padre
        self.children = []            # Lista de tablas de símbolos hijas
        
    def add(self, name, value):
        # Agrega un símbolo a la tabla
        if name in self.entries:
            if self.entries[name].dtype != value.dtype:
                raise SymbolTab.SymbolConflictError()  # Error si el tipo de dato es diferente
            else:
                raise SymbolTab.symbolDefinedError()   # Error si el símbolo ya está definido
        self.entries[name] = value

    def get(self, name):
        # Busca un símbolo en la tabla actual y, si no existe, sube recursivamente al padre
        if name in self.entries:
            return self.entries[name]
        elif self.parent:
            return self.parent.get(name)
        return None

    def print(self):
        # Imprime la tabla de símbolos de forma sencilla (sin librerías externas)
        print(f"Tabla de Símbolos: '{self.name}'")
        print(f"{'clave':<20} {'valor':<30}")
        print('-' * 50)
        for k, v in self.entries.items():
            value = f"{v.__class__.__name__}({v.name})"
            print(f"{k:<20} {value:<30}")
        print()
        for child in self.children:
            child.print()
            
    def __contains__(self, key):
        """Permite usar ‘if key in symtab:’ para verificar si un símbolo existe."""
        return self.get(key) is not None