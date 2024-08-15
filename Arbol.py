import tkinter as tk
from tkinter import simpledialog, messagebox

class Nodo:
    def __init__(self, valor):
        self.valor = valor
        self.hijos = []

    def agregar_hijo(self, nodo_hijo):
        self.hijos.append(nodo_hijo)

class Arbol:
    def __init__(self, raiz):
        self.raiz = Nodo(raiz)

    def agregar_nodo(self, valor_padre, valor_hijo):
        nodo_padre = self.buscar_nodo(self.raiz, valor_padre)
        if nodo_padre:
            nodo_hijo = Nodo(valor_hijo)
            nodo_padre.agregar_hijo(nodo_hijo)

    def buscar_nodo(self, nodo, valor):
        if nodo.valor == valor:
            return nodo
        for hijo in nodo.hijos:
            resultado = self.buscar_nodo(hijo, valor)
            if resultado:
                return resultado
        return None

    def calcular_altura(self, nodo=None):
        if nodo is None:
            nodo = self.raiz
        if not nodo.hijos:
            return 1
        return 1 + max(self.calcular_altura(hijo) for hijo in nodo.hijos)

    def calcular_grado(self):
        if self.raiz:
            return len(self.raiz.hijos)
        return 0

    def calcular_ancho(self, nodo):
        if not nodo.hijos:
            return 1
        return sum(self.calcular_ancho(hijo) for hijo in nodo.hijos)

    def mostrar_arbol(self, canvas, nodo, x, y, dx, dy):
        ancho_subarbol = self.calcular_ancho(nodo) * dx
        x_inicial = x - ancho_subarbol // 2

        texto = canvas.create_text(x, y, text=nodo.valor, font=("Arial", 12, "bold"))
        bbox = canvas.bbox(texto)
        ancho_texto = bbox[2] - bbox[0]
        altura_texto = bbox[3] - bbox[1]

        if nodo.hijos:
            total_hijos = len(nodo.hijos)
            x_hijo = x_inicial + dx // 2

            for i, hijo in enumerate(nodo.hijos):
                ancho_hijo = self.calcular_ancho(hijo) * dx
                x_hijo_centro = x_inicial + ancho_hijo // 2
                y_hijo = y + dy + altura_texto
                canvas.create_line(x, y + altura_texto // 2, x_hijo_centro, y_hijo - altura_texto // 2, arrow=tk.LAST)
                self.mostrar_arbol(canvas, hijo, x_hijo_centro, y_hijo, dx, dy)
                x_inicial += ancho_hijo

class Aplicacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Árbol")
        self.root.geometry("1000x700")
        
        self.canvas = tk.Canvas(self.root, width=1000, height=600)
        self.canvas.pack()

        self.arbol = None

        # Botones para agregar nodos
        btn_raiz = tk.Button(root, text="Agregar Raíz", command=self.agregar_raiz)
        btn_raiz.pack(side=tk.LEFT, padx=10, pady=10)
        
        btn_nodo = tk.Button(root, text="Agregar Nodo", command=self.agregar_nodo)
        btn_nodo.pack(side=tk.LEFT, padx=10, pady=10)

        btn_mostrar = tk.Button(root, text="Mostrar Árbol", command=self.mostrar_arbol)
        btn_mostrar.pack(side=tk.LEFT, padx=10, pady=10)

        btn_altura = tk.Button(root, text="Mostrar Altura", command=self.mostrar_altura)
        btn_altura.pack(side=tk.LEFT, padx=10, pady=10)

        btn_grado = tk.Button(root, text="Mostrar Grado", command=self.mostrar_grado)
        btn_grado.pack(side=tk.LEFT, padx=10, pady=10)

    def agregar_raiz(self):
        valor_raiz = simpledialog.askstring("Input", "Ingrese el valor de la raíz:", parent=self.root)
        if valor_raiz:
            self.arbol = Arbol(valor_raiz)
            self.canvas.delete("all")
            self.mostrar_arbol()

    def agregar_nodo(self):
        if not self.arbol:
            messagebox.showerror("Error", "Primero debe agregar la raíz del árbol.")
            return
        valor_padre = simpledialog.askstring("Input", "Ingrese el valor del nodo padre:", parent=self.root)
        if valor_padre:
            valor_hijo = simpledialog.askstring("Input", "Ingrese el valor del nodo hijo:", parent=self.root)
            if valor_hijo:
                nodo_padre = self.arbol.buscar_nodo(self.arbol.raiz, valor_padre)
                if nodo_padre:
                    self.arbol.agregar_nodo(valor_padre, valor_hijo)
                    self.canvas.delete("all")
                    self.mostrar_arbol()
                else:
                    messagebox.showerror("Error", f"El nodo padre '{valor_padre}' no existe en el árbol.")

    def mostrar_arbol(self):
        if not self.arbol:
            messagebox.showerror("Error", "Primero debe agregar la raíz del árbol.")
            return
        self.canvas.delete("all")
        self.arbol.mostrar_arbol(self.canvas, self.arbol.raiz, 500, 50, 100, 100)

    def mostrar_altura(self):
        if not self.arbol:
            messagebox.showerror("Error", "Primero debe agregar la raíz del árbol.")
            return
        altura = self.arbol.calcular_altura()
        messagebox.showinfo("Altura del Árbol", f"La altura del árbol es: {altura}")

    def mostrar_grado(self):
        if not self.arbol:
            messagebox.showerror("Error", "Primero debe agregar la raíz del árbol.")
            return
        grado = self.arbol.calcular_grado()
        messagebox.showinfo("Grado del Árbol", f"El grado del árbol es: {grado}")

# Inicializar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacion(root)
    root.mainloop()
