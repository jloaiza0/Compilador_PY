# symtab.py
from rich.table import Table
from rich.console import Console
from rich import print
from goxLang_AST_nodes import (
    Program, Print, If, Block, IntLiteral, FloatLiteral, StringLiteral,
    BoolLiteral, Identifier, ImportFunctionDecl, MemoryAccess, CharLiteral,
    TypeCast, VarDecl, ConstDecl, FuncDecl, Assignment, BinaryOp,
    While, Return, Call, Break, Continue
)
class Symtab:
    '''
    Una tabla de símbolos que mantiene un registro de los nombres de símbolos
    y sus declaraciones correspondientes (variables, funciones, etc.).
    Soporta anidamiento para manejar diferentes ámbitos léxicos.
    '''
    
    class SymbolDefinedError(Exception):
        '''
        Excepción lanzada cuando un símbolo ya está definido en el ámbito actual.
        '''
        def __init__(self, name, lineno=None):
            self.name = name
            self.lineno = lineno
            super().__init__(f"Symbol '{name}' already defined in current scope{'' if lineno is None else f' at line {lineno}'}")

    class SymbolConflictError(Exception):
        '''
        Excepción lanzada cuando un símbolo existe pero con un tipo diferente.
        '''
        def __init__(self, name, existing_type, new_type, lineno=None):
            self.name = name
            self.existing_type = existing_type
            self.new_type = new_type
            self.lineno = lineno
            super().__init__(
                f"Type conflict for symbol '{name}'. "
                f"Existing: {existing_type}, New: {new_type}"
                f"{'' if lineno is None else f' at line {lineno}'}"
            )

    class SymbolNotFoundError(Exception):
        '''
        Excepción lanzada cuando un símbolo no se encuentra en ningún ámbito.
        '''
        def __init__(self, name, lineno=None):
            self.name = name
            self.lineno = lineno
            super().__init__(f"Symbol '{name}' not found{'' if lineno is None else f' at line {lineno}'}")

    def __init__(self, name, parent=None):
        '''
        Crea una nueva tabla de símbolos vacía.
        
        Args:
            name (str): Nombre descriptivo del ámbito
            parent (Symtab, optional): Tabla de símbolos padre. Defaults to None.
        '''
        self.name = name
        self.entries = {}
        self.parent = parent
        if self.parent:
            self.parent.children.append(self)
        self.children = []
        
    def add(self, name, value, lineno=None):
        '''
        Agrega un nuevo símbolo a la tabla.
        
        Args:
            name (str): Nombre del símbolo
            value: Valor asociado (normalmente un nodo AST)
            lineno (int, optional): Número de línea para reporte de errores
            
        Raises:
            SymbolDefinedError: Si el símbolo ya existe en el ámbito actual
            SymbolConflictError: Si el símbolo existe pero con tipo diferente
        '''
        if name in self.entries:
            existing = self.entries[name]
            if hasattr(existing, 'dtype') and hasattr(value, 'dtype'):
                if existing.dtype != value.dtype:
                    raise self.SymbolConflictError(name, existing.dtype, value.dtype, lineno)
            raise self.SymbolDefinedError(name, lineno)
        self.entries[name] = value
        
    def get(self, name, lineno=None):
        '''
        Busca un símbolo en la tabla actual y padres.
        
        Args:
            name (str): Nombre del símbolo a buscar
            lineno (int, optional): Número de línea para reporte de errores
            
        Returns:
            El valor asociado al símbolo o None si no se encuentra
            
        Raises:
            SymbolNotFoundError: Si el símbolo no existe en ningún ámbito
        '''
        if name in self.entries:
            return self.entries[name]
        elif self.parent:
            return self.parent.get(name)
        raise self.SymbolNotFoundError(name, lineno)
        
    def contains_in_current_scope(self, name):
        '''
        Verifica si un símbolo existe solo en el ámbito actual.
        
        Args:
            name (str): Nombre del símbolo
            
        Returns:
            bool: True si el símbolo existe en el ámbito actual
        '''
        return name in self.entries
        
    def print(self, show_all_scopes=False):
        '''
        Imprime la tabla de símbolos usando rich.
        
        Args:
            show_all_scopes (bool): Si True, imprime también los ámbitos hijos
        '''
        table = Table(title=f"Symbol Table: '{self.name}'")
        table.add_column('Name', style='cyan')
        table.add_column('Type', style='magenta')
        table.add_column('Details', style='bright_green')
        
        for name, value in self.entries.items():
            details = f"{value.__class__.__name__}"
            if hasattr(value, 'dtype'):
                details += f" (type: {value.dtype})"
            if isinstance(value, (VarDecl, ConstDecl)):
                details += f" = {value.value.to_dict() if value.value else 'None'}"
            elif isinstance(value, FuncDecl):
                params = ", ".join([f"{p[0]}: {p[1]}" for p in value.params])
                details += f" ({params}) -> {value.return_type}"
                
            table.add_row(name, getattr(value, 'dtype', '?'), details)
        
        print(table)
        
        if show_all_scopes:
            for child in self.children:
                child.print(show_all_scopes)

    def __str__(self):
        return f"Symtab(name='{self.name}', entries={len(self.entries)}, children={len(self.children)})"

    def __repr__(self):
        return self.__str__()