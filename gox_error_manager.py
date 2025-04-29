class ErrorManager:
    def __init__(self):
        # Lista de errores registrados
        self._errors = []
        
    def add_error(self, message, lineno=None, columna=None):
        """
        Registra un nuevo error en el sistema.
        
        Args:
            message (str): Mensaje descriptivo del error
            lineno (int, optional): Número de línea donde ocurrió el error
            columna (int, optional): Número de columna donde ocurrió el error
        """
        error_info = {
            'type': 'error',
            'message': message,
            'lineno': lineno,
            'columna': columna
        }
        self._errors.append(error_info)
    
    def add_warning(self, message, lineno=None, columna=None):
        """
        Registra una advertencia en el sistema.
        
        Args:
            message (str): Mensaje descriptivo de la advertencia
            lineno (int, optional): Número de línea
            columna (int, optional): Número de columna
        """
        warning_info = {
            'type': 'warning',
            'message': message,
            'lineno': lineno,
            'columna': columna
        }
        self._errors.append(warning_info)
    
    def has_errors(self):
        """Indica si hay errores registrados"""
        return any(e['type'] == 'error' for e in self._errors)
    
    def has_warnings(self):
        """Indica si hay advertencias registradas"""
        return any(e['type'] == 'warning' for e in self._errors)
    
    def clear(self):
        """Limpia todos los errores y advertencias"""
        self._errors.clear()
    
    def get_errors(self):
        """Devuelve una lista con todos los errores formateados"""
        return self._format_messages('error')
    
    def get_warnings(self):
        """Devuelve una lista con todas las advertencias formateadas"""
        return self._format_messages('warning')
    
    def get_all(self):
        """Devuelve todos los mensajes (errores y advertencias)"""
        return self._format_messages()
    
    def print_errors(self):
        """Imprime todos los errores en la consola"""
        for err in self.get_errors():
            print(err)
    
    def print_warnings(self):
        """Imprime todas las advertencias en la consola"""
        for warn in self.get_warnings():
            print(warn)
    
    def print_all(self):
        """Imprime todos los mensajes en la consola"""
        for msg in self.get_all():
            print(msg)
    
    def _format_messages(self, msg_type=None):
        """
        Formatea los mensajes para su visualización.
        
        Args:
            msg_type (str, optional): 'error', 'warning' o None para todos
        """
        formatted = []
        for msg in self._errors:
            if msg_type and msg['type'] != msg_type:
                continue
                
            location = []
            if msg['lineno'] is not None:
                location.append(f"line {msg['lineno']}")
            if msg['columna'] is not None:
                location.append(f"col {msg['columna']}")
            
            loc_str = f" ({', '.join(location)})" if location else ""
            formatted.append(f"[{msg['type'].upper()}]{loc_str}: {msg['message']}")
        
        return formatted
    
    # Métodos de compatibilidad (pueden eliminarse en versiones futuras)
    def registrar(self, descripcion, linea, columna=None):
        """Alias para add_error (compatibilidad)"""
        self.add_error(descripcion, linea, columna)
    
    def hay_errores(self):
        """Alias para has_errors (compatibilidad)"""
        return self.has_errors()
    
    def mostrar(self):
        """Alias para print_all (compatibilidad)"""
        self.print_all()
    
    def limpiar(self):
        """Alias para clear (compatibilidad)"""
        self.clear()


# Ejemplo de uso
if __name__ == "__main__":
    em = ErrorManager()
    
    # Registrar algunos errores y advertencias
    em.add_error("Variable 'x' no declarada", 10, 5)
    em.add_error("Tipos incompatibles en expresión", 15)
    em.add_warning("Variable 'y' no utilizada", 20, 8)
    em.add_error("Error de sintaxis")
    
    # Mostrar resultados
    print("=== Todos los mensajes ===")
    em.print_all()
    
    print("\n=== Solo errores ===")
    em.print_errors()
    
    print("\n=== Solo advertencias ===")
    em.print_warnings()
    
    print("\n=== Formateados para archivo ===")
    for msg in em.get_all():
        print(msg)