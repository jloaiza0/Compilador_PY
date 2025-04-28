import tkinter as tk
from tkinter import filedialog
import subprocess
import os
import sys
from Readerscript import read_script
from Parser import Parser
from Semanticcheker import SemanticChecker
from Interpreter import Interpreter

def runReaderScript(filename):
    try:
        # Obtiene la ruta del directorio donde se encuentra este archivo
        script_dir = os.path.dirname(os.path.abspath(__file__))
        reader_path = os.path.join(script_dir, 'Reader_script.py')
        # Usa el mismo intérprete de Python que está ejecutando la GUI
        result = subprocess.run(
            [sys.executable, reader_path, filename],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        # Muestra el error en caso de fallo al ejecutar el script
        print(e.stderr)

def openFileDialog():
    # Abre un cuadro de diálogo para seleccionar un archivo
    filename = filedialog.askopenfilename(
        initialdir=".",
        title="Seleccionar un archivo",
        filetypes=(("Archivos Gox", "*.gox"), ("Todos los archivos", "*.*"))
    )
    if filename:
        runReaderScript(filename)

def main():
    # Función principal que ejecuta las fases: lectura, análisis sintáctico, semántico e interpretación
    script = read_script(sys.argv[1])
    ast = Parser(script).parse()
    SemanticChecker().visit(ast)
    result = Interpreter().visit_Program(ast)
    return 0

if __name__ == "__main__":
    # Configura la ventana principal de la interfaz gráfica
    root = tk.Tk()
    root.title("Compiler GUI")

    # Crea un botón para seleccionar archivos .gox
    button = tk.Button(root, text="Seleccionar archivo Gox", command=openFileDialog)
    button.pack(pady=20)

    root.mainloop()
    sys.exit(main())