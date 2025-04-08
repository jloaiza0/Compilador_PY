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

    def hay_errores(self):
        """Devuelve True si hay errores almacenados."""
        return len(self._log) > 0

    def mostrar(self):
        """Muestra los errores acumulados en formato legible."""
        for error in self._log:
            ubicacion = f"Línea {error['linea']}"
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
            ubicacion = f"Línea {error['linea']}"
            if error['columna'] is not None:
                ubicacion += f", Columna {error['columna']}"
            mensajes.append(f"[Error] {ubicacion}: {error['descripcion']}")
        return mensajes


# Ejemplo de uso
if __name__ == "__main__":
    errores = ErrorManager()
    errores.registrar("Variable no declarada 'foo'", 4)
    errores.registrar("Tipo incompatible en comparación", 12, 6)

    if errores.hay_errores():
        print("Se detectaron errores durante la compilación:\n")
        errores.mostrar()
