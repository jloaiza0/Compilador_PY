import sys
from Error import ErrorHandler
from Lexer import tokenize
from Parser import Parser

def main():
    # Verifica que se haya proporcionado un argumento (el nombre del archivo)
    if len(sys.argv) < 2:
        print("Uso: python Reader_script.py [archivo].gox")
        sys.exit(1)

    filename = sys.argv[1]
    
    # Verifica que el archivo tenga extensión .gox
    if not filename.endswith('.gox'):
        print("Error: El archivo debe tener extensión .gox")
        sys.exit(1)

    try:
        # Intenta abrir y leer el archivo
        with open(filename, 'r') as file:
            code = file.read()

        error_handler = ErrorHandler()
        
        # Tokeniza el código fuente
        tokens = tokenize(code, error_handler)
        
        # Analiza sintácticamente los tokens
        parser = Parser(tokens, error_handler)
        ast = parser.parse()

        # Define el nombre del archivo de salida (.json)
        output_filename = filename.rsplit('.', 1)[0] + '.json'

        # Verifica si hubo errores durante la tokenización o el análisis
        if error_handler.has_errors():
            print(f"Error de análisis en {filename}:")
            error_handler.report_errors()
            sys.exit(1)
        else:
            # Si no hay errores, guarda el AST en un archivo JSON
            print(f"Análisis exitoso de {filename}")
            parser.save_ast_to_json(output_filename)
            print(f"AST guardado en {output_filename}")

    except FileNotFoundError:
        # Error si no se encuentra el archivo
        print(f"Error: Archivo '{filename}' no encontrado")
        sys.exit(1)
    except Exception as e:
        # Captura cualquier otro error inesperado
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()