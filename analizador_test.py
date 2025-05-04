from goxLang_AST_nodes import *
from check import TypeChecker

# Programa CORRECTO usando nodos AST apropiados
valid_program = Program([
    
])

checker = TypeChecker()
if checker.check(valid_program):
    print("✅ Programa válido - Todo funciona correctamente")
    print("\nTabla de símbolos:")
    checker.current_symtab.print()
else:
    print("❌ Errores encontrados:")
    for error in checker.error_manager.errors:
        print(f"- {error}")