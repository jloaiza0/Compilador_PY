import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
import os
import sys
import io
from contextlib import redirect_stdout
from lexer import tokenize, Token  # Importar las funciones/clases que sí existen
from Error import ErrorHandler  # Importar el manejador de errores

# Importaciones del compilador
from parser import Parser
from SemanticVisitor import SemanticVisitor
from IntermediateCode import IntermediateCodeGenerator
from StackMachine import StackMachine

# Importaciones de los nodos AST
from ASTnodes import (
    ASTNode, Integer, Float, Boolean, String, Char, 
    Location, BinOp, CompareOp, LogicalOp
)

class CompilerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Compilador GoX")
        self.root.geometry("800x600")
        
        # Configuración de la interfaz
        self.create_widgets()
        self.current_file = None
        self.quadruples = []
        self.function_directory = {}
        
    def create_widgets(self):
        # Frame superior para botones
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Botones
        self.open_button = tk.Button(button_frame, text="Abrir Archivo", command=self.open_file)
        self.open_button.pack(side=tk.LEFT, padx=5)
        
        self.compile_button = tk.Button(button_frame, text="Compilar", command=self.compile, state=tk.DISABLED)
        self.compile_button.pack(side=tk.LEFT, padx=5)
        
        self.run_button = tk.Button(button_frame, text="Ejecutar", command=self.run, state=tk.DISABLED)
        self.run_button.pack(side=tk.LEFT, padx=5)
        
        # Pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de código fuente
        self.source_tab = tk.Frame(self.notebook)
        self.source_text = scrolledtext.ScrolledText(self.source_tab, wrap=tk.WORD)
        self.source_text.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(self.source_tab, text="Código Fuente")
        
        # Pestaña de tokens
        self.tokens_tab = tk.Frame(self.notebook)
        self.tokens_text = scrolledtext.ScrolledText(self.tokens_tab, wrap=tk.WORD)
        self.tokens_text.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(self.tokens_tab, text="Tokens")
        
        # Pestaña de AST
        self.ast_tab = tk.Frame(self.notebook)
        self.ast_text = scrolledtext.ScrolledText(self.ast_tab, wrap=tk.WORD)
        self.ast_text.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(self.ast_tab, text="AST")
        
        # Pestaña de código intermedio
        self.quad_tab = tk.Frame(self.notebook)
        self.quad_text = scrolledtext.ScrolledText(self.quad_tab, wrap=tk.WORD)
        self.quad_text.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(self.quad_tab, text="Cuádruplos")
        
        # Pestaña de salida
        self.output_tab = tk.Frame(self.notebook)
        self.output_text = scrolledtext.ScrolledText(self.output_tab, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(self.output_tab, text="Salida")
        
        # Configurar colores
        self.configure_colors()
    
    def configure_colors(self):
        self.source_text.config(bg='#282c34', fg='#abb2bf', insertbackground='white')
        self.tokens_text.config(bg='#f5f5f5')
        self.ast_text.config(bg='#f5f5f5')
        self.quad_text.config(bg='#f5f5f5')
        self.output_text.config(bg='#282c34', fg='#abb2bf')
    
    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Archivos GoX", "*.gox"), ("Todos los archivos", "*.*")],
            initialdir=os.path.expanduser("~")
        )
        
        if file_path:
            self.current_file = file_path
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.source_text.delete(1.0, tk.END)
                    self.source_text.insert(tk.END, content)
                    self.compile_button.config(state=tk.NORMAL)
                    self.clear_all_tabs()
            except Exception as e:
                messagebox.showerror("Error", f"Error al abrir el archivo:\n{str(e)}")
    
    def clear_all_tabs(self):
        for text_widget in [self.tokens_text, self.ast_text, self.quad_text, self.output_text]:
            text_widget.delete(1.0, tk.END)
    
    def compile(self):
        if not self.current_file:
            messagebox.showwarning("Advertencia", "No hay archivo seleccionado")
            return
            
        try:
            # Limpiar pestañas
            self.clear_all_tabs()
            
            # 1. Análisis léxico
            with open(self.current_file, 'r', encoding='utf-8') as file:
                source_code = file.read()
            
            # Crear manejador de errores y tokenizar
            error_handler = ErrorHandler()
            tokens = tokenize(source_code, error_handler)
            
            # Verificar si hay errores léxicos
            if error_handler.has_errors():
                self.show_lexical_errors(error_handler.errors)
                return
            
            # Mostrar tokens
            self.tokens_text.insert(tk.END, "TOKENS:\n" + "="*50 + "\n")
            for token in tokens:
                self.tokens_text.insert(tk.END, f"{token}\n")
            
            # 2. Análisis sintáctico - LÍNEA CORREGIDA
            # Crear un nuevo error_handler para el parser o reutilizar el existente
            parser_error_handler = ErrorHandler()  # Nuevo manejador para el parser
            parser = Parser(tokens, parser_error_handler)
            ast = parser.parse()
            
            # Verificar si hay errores sintácticos
            if parser_error_handler.has_errors():
                self.show_parsing_errors(parser_error_handler.errors)
                return
            
            self.ast_text.insert(tk.END, "ÁRBOL DE SINTAXIS ABSTRACTA (AST):\n" + "="*50 + "\n")
            self.ast_text.insert(tk.END, self.ast_to_string(ast))
            
            # 3. Análisis semántico
            semantic_visitor = SemanticVisitor()
            if not semantic_visitor.visit(ast):
                self.show_errors(semantic_visitor.errors)
                return
                
            # 4. Generación de código intermedio
            code_generator = IntermediateCodeGenerator()
            ast.accept(code_generator)
            self.quadruples = code_generator.quadruples
            self.function_directory = code_generator.function_directory
            
            self.quad_text.insert(tk.END, "CÓDIGO INTERMEDIO (CUÁDRUPLOS):\n" + "="*50 + "\n")
            for i, quad in enumerate(self.quadruples):
                self.quad_text.insert(tk.END, f"{i:4d} | {quad}\n")
            
            self.run_button.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, "Compilación exitosa!\n")
            
        except ImportError as e:
            error_msg = f"Error de importación: {str(e)}\nVerifica que todos los módulos existan y estén correctamente nombrados."
            self.output_text.insert(tk.END, error_msg + "\n")
            messagebox.showerror("Error de importación", error_msg)
        except AttributeError as e:
            error_msg = f"Error de atributo: {str(e)}\nVerifica que las clases tengan los métodos esperados."
            self.output_text.insert(tk.END, error_msg + "\n")
            messagebox.showerror("Error de atributo", error_msg)
        except Exception as e:
            error_msg = f"Error durante la compilación:\n{str(e)}"
            self.output_text.insert(tk.END, error_msg + "\n")
            messagebox.showerror("Error de compilación", error_msg)
    
    def run(self):
        if not self.quadruples:
            messagebox.showwarning("Advertencia", "No hay código compilado para ejecutar")
            return
            
        try:
            self.output_text.insert(tk.END, "\nEJECUCIÓN:\n" + "="*50 + "\n")
            
            # Redirigir stdout a nuestro widget de salida
            output = io.StringIO()
            with redirect_stdout(output):
                machine = StackMachine(self.quadruples, self.function_directory)
                machine.execute()
            
            self.output_text.insert(tk.END, output.getvalue())
            self.output_text.insert(tk.END, "\nEjecución completada exitosamente!\n")
            
        except Exception as e:
            error_msg = f"Error durante la ejecución:\n{str(e)}"
            self.output_text.insert(tk.END, error_msg + "\n")
            messagebox.showerror("Error de ejecución", error_msg)
    
    def ast_to_string(self, node, indent=0):
        """Convierte el AST a una representación de cadena legible"""
        if node is None:
            return "  " * indent + "None\n"
        
        result = "  " * indent + f"{node.__class__.__name__}"
        
        # Mostrar atributos relevantes
        if isinstance(node, (Integer, Float, Boolean, String, Char)):
            result += f"(value={getattr(node, 'value', 'N/A')})"
        elif isinstance(node, Location):
            result += f"(name={getattr(node, 'name', 'N/A')})"
        elif isinstance(node, (BinOp, CompareOp, LogicalOp)):
            result += f"(op={getattr(node, 'op', 'N/A')})"
        elif hasattr(node, 'name'):
            result += f"(name={getattr(node, 'name', 'N/A')})"
        
        result += "\n"
        
        # Recorrer hijos
        for child_name, child in vars(node).items():
            if child_name.startswith('_') or child_name in ['symbol', 'type', 'temp_var', 'quad']:
                continue
                
            if isinstance(child, ASTNode):
                result += self.ast_to_string(child, indent + 1)
            elif isinstance(child, list):
                for i, item in enumerate(child):
                    if isinstance(item, ASTNode):
                        result += "  " * (indent + 1) + f"[{i}]:\n"
                        result += self.ast_to_string(item, indent + 2)
        
        return result
    
    def show_errors(self, errors):
        """Muestra errores en el output"""
        self.output_text.insert(tk.END, "ERRORES DE COMPILACIÓN:\n" + "="*50 + "\n")
        for error in errors:
            self.output_text.insert(tk.END, f"- {error}\n")
        messagebox.showerror("Errores de compilación", "Se encontraron errores durante la compilación")
    
    def show_lexical_errors(self, errors):
        """Muestra errores léxicos en el output"""
        self.output_text.insert(tk.END, "ERRORES LÉXICOS:\n" + "="*50 + "\n")
        for error in errors:
            self.output_text.insert(tk.END, f"- {error}\n")
        messagebox.showerror("Errores léxicos", "Se encontraron errores durante el análisis léxico")
    
    def show_parsing_errors(self, errors):
        """Muestra errores sintácticos en el output"""
        self.output_text.insert(tk.END, "ERRORES SINTÁCTICOS:\n" + "="*50 + "\n")
        for error in errors:
            self.output_text.insert(tk.END, f"- {error}\n")
        messagebox.showerror("Errores sintácticos", "Se encontraron errores durante el análisis sintáctico")

def main():
    try:
        root = tk.Tk()
        app = CompilerGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        input("Presiona Enter para continuar...")

if __name__ == "__main__":
    main()