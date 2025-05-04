# symtab.py
from rich.table import Table
from rich.console import Console
from rich import print
from typing import Any, Optional, Dict, List
from goxLang_AST_nodes import *

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
        def __init__(self, name: str, lineno: Optional[int] = None):
            self.name = name
            self.lineno = lineno
            super().__init__(f"Symbol '{name}' already defined in current scope{'' if lineno is None else f' at line {lineno}'}")

    class SymbolConflictError(Exception):
        '''
        Excepción lanzada cuando un símbolo existe pero con un tipo diferente.
        '''
        def __init__(self, name: str, existing_type: str, new_type: str, lineno: Optional[int] = None):
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
        def __init__(self, name: str, lineno: Optional[int] = None):
            self.name = name
            self.lineno = lineno
            super().__init__(f"Symbol '{name}' not found{'' if lineno is None else f' at line {lineno}'}")

    def __init__(self, name: str, parent: Optional['Symtab'] = None):
        '''
        Crea una nueva tabla de símbolos vacía.
        
        Args:
            name (str): Nombre descriptivo del ámbito
            parent (Symtab, optional): Tabla de símbolos padre. Defaults to None.
        '''
        self.name = name
        self.entries: Dict[str, Any] = {}
        self.parent: Optional['Symtab'] = parent
        self.children: List['Symtab'] = []
        if self.parent:
            self.parent.children.append(self)

    def add(self, name: str, value: Any, lineno: Optional[int] = None) -> None:
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
        
    def get(self, name: str, lineno: Optional[int] = None) -> Any:
        '''
        Busca un símbolo en la tabla actual y padres.
        
        Args:
            name (str): Nombre del símbolo a buscar
            lineno (int, optional): Número de línea para reporte de errores
            
        Returns:
            El valor asociado al símbolo
            
        Raises:
            SymbolNotFoundError: Si el símbolo no existe en ningún ámbito
        '''
        if name in self.entries:
            return self.entries[name]
        if self.parent:
            return self.parent.get(name, lineno)
        raise self.SymbolNotFoundError(name, lineno)
        
    def get_type(self, name: str, lineno: Optional[int] = None) -> Optional[str]:
        '''
        Obtiene específicamente el tipo de un símbolo.
        
        Args:
            name (str): Nombre del símbolo
            lineno (int, optional): Número de línea para reporte de errores
            
        Returns:
            str: Tipo del símbolo o None si no tiene tipo o no existe
        '''
        try:
            symbol = self.get(name, lineno)
            return getattr(symbol, 'dtype', None)
        except self.SymbolNotFoundError:
            return None
        
    def contains_in_current_scope(self, name: str) -> bool:
        '''
        Verifica si un símbolo existe solo en el ámbito actual.
        
        Args:
            name (str): Nombre del símbolo
            
        Returns:
            bool: True si el símbolo existe en el ámbito actual
        '''
        return name in self.entries
        
    def get_symbols(self, scope: str = 'all') -> Dict[str, Any]:
        '''
        Obtiene símbolos del ámbito actual o todos los visibles.
        
        Args:
            scope (str): 'current' para solo ámbito actual, 'all' para todos visibles
            
        Returns:
            Dict[str, Any]: Diccionario de símbolos
        '''
        if scope == 'current':
            return self.entries.copy()
        
        symbols = {}
        if self.parent:
            symbols.update(self.parent.get_symbols())
        symbols.update(self.entries)
        return symbols
        
    def print(self, show_all_scopes: bool = False) -> None:
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
                details += f" = {value.value.to_dict() if hasattr(value, 'value') and value.value else 'None'}"
            elif isinstance(value, (FuncDecl, ImportFunctionDecl)):
                params = ", ".join([f"{p[0]}: {p[1]}" for p in value.params]) if hasattr(value, 'params') else "()"
                return_type = getattr(value, 'return_type', 'void')
                details += f" ({params}) -> {return_type}"
                
            table.add_row(name, getattr(value, 'dtype', '?'), details)
        
        print(table)
        
        if show_all_scopes:
            for child in self.children:
                child.print(show_all_scopes)

    def __str__(self) -> str:
        return f"Symtab(name='{self.name}', entries={len(self.entries)}, children={len(self.children)})"

    def __repr__(self) -> str:
        return self.__str__()