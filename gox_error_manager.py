# gox_error_manager.py
# Manejador personalizado de errores para el compilador de GoxLang

class ErrorManager:
    def __init__(self):
        # Lista de mensajes de error registrados
        self._log = []

    def registrar(self, descripcion, linea, columna=None):
        """
        Guarda un error en el registro.
        - descripcion: mensaje de lo ocurrido
        - linea: número de línea
        - columna: número de columna (opcional)
        """
        entrada = {
            'descripcion': descripcion,
            'linea': linea,
            'columna': columna
        }
        self._log.append(entrada)

    def add_error(self, mensaje):
        """
        Versión simplificada para registrar errores sin info detallada.
        Se puede usar para excepciones generales.
        """
        self._log.append({
            'descripcion': mensaje,
            'linea': -1,
            'columna': None
        })

    def hay_errores(self):
        """Devuelve True si hay errores almacenados."""
        return len(self._log) > 0

    def mostrar(self):
        """Muestra los errores acumulados en formato legible."""
        for error in self._log:
            ubicacion = f"Línea {error['linea']}" if error['linea'] != -1 else "Ubicación desconocida"
            if error['columna'] is not None:
                ubicacion += f", Columna {error['columna']}"
            print(f"[Error] {ubicacion}: {error['descripcion']}")

    def limpiar(self):
        """Limpia la lista de errores."""
        self._log.clear()

    def get_errors(self):
        """Devuelve los errores como lista de strings para guardar en archivo."""
        mensajes = []
        for error in self._log:
            ubicacion = f"Línea {error['linea']}" if error['linea'] != -1 else "Ubicación desconocida"
            if error['columna'] is not None:
                ubicacion += f", Columna {error['columna']}"
            mensajes.append(f"[Error] {ubicacion}: {error['descripcion']}")
        return mensajes
# Ejemplo de uso
if __name__ == "__main__":
    errores = ErrorManager()
    
    # Error con línea y columna conocida
    errores.registrar("Variable no declarada 'x'", 10, 5)
    
    # Error con solo línea
    errores.registrar("Falta ';' al final de la instrucción", 12)
    
    # Error general sin ubicación (por ejemplo, una excepción)
    errores.add_error("Error inesperado durante el análisis del programa")
    
    # Mostrar errores en consola
    print("Errores detectados:")
    errores.mostrar()