import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os

class GestorContenido:
    """
    Clase para gestionar el archivo JSON de contenido.
    Maneja la carga, guardado, y operaciones CRUD sobre secciones e items.
    """
    def __init__(self, archivo='contenido.json'):
        self.archivo = archivo
        self.datos = self.cargar_datos()

    def cargar_datos(self):
        """
        Carga los datos desde el archivo JSON. Si no existe, crea uno con secciones predeterminadas.
        """
        if os.path.exists(self.archivo):
            try:
                with open(self.archivo, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                messagebox.showerror("Error", "El archivo JSON está corrupto. Se creará uno nuevo.")
        # Crear datos predeterminados
        return {
            "cursos": [],
            "comics": [],
            "libros": [],
            "software": []
        }

    def guardar_datos(self):
        """
        Guarda los datos actuales en el archivo JSON.
        """
        try:
            with open(self.archivo, 'w', encoding='utf-8') as f:
                json.dump(self.datos, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Éxito", "Cambios guardados correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")

    def obtener_secciones(self):
        """
        Devuelve una lista de secciones disponibles.
        """
        return list(self.datos.keys())

    def agregar_seccion(self, nombre):
        """
        Agrega una nueva sección si no existe.
        """
        if nombre not in self.datos:
            self.datos[nombre] = []
            return True
        return False

    def obtener_items(self, seccion):
        """
        Devuelve la lista de items de una sección.
        """
        return self.datos.get(seccion, [])

    def agregar_item(self, seccion, item):
        """
        Agrega un item a una sección.
        """
        if seccion in self.datos:
            self.datos[seccion].append(item)

    def editar_item(self, seccion, indice, item):
        """
        Edita un item en una sección por índice.
        """
        if seccion in self.datos and 0 <= indice < len(self.datos[seccion]):
            self.datos[seccion][indice] = item

    def eliminar_item(self, seccion, indice):
        """
        Elimina un item de una sección por índice.
        """
        if seccion in self.datos and 0 <= indice < len(self.datos[seccion]):
            del self.datos[seccion][indice]

class DialogoItem(tk.Toplevel):
    """
    Diálogo para añadir o editar un item.
    """
    def __init__(self, parent, titulo="Añadir Item", item=None):
        super().__init__(parent)
        self.title(titulo)
        self.geometry("400x300")
        self.resizable(False, False)
        self.item = item or {"titulo": "", "descripcion": "", "enlace": "", "portada": ""}

        # Campos
        ttk.Label(self, text="Título:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.entry_titulo = ttk.Entry(self, width=40)
        self.entry_titulo.grid(row=0, column=1, padx=10, pady=5)
        self.entry_titulo.insert(0, self.item["titulo"])

        ttk.Label(self, text="Descripción:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.entry_descripcion = ttk.Entry(self, width=40)
        self.entry_descripcion.grid(row=1, column=1, padx=10, pady=5)
        self.entry_descripcion.insert(0, self.item["descripcion"])

        ttk.Label(self, text="Enlace:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.entry_enlace = ttk.Entry(self, width=40)
        self.entry_enlace.grid(row=2, column=1, padx=10, pady=5)
        self.entry_enlace.insert(0, self.item["enlace"])

        ttk.Label(self, text="Portada (opcional):").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.entry_portada = ttk.Entry(self, width=40)
        self.entry_portada.grid(row=3, column=1, padx=10, pady=5)
        self.entry_portada.insert(0, self.item["portada"] or "")

        # Botones
        frame_botones = ttk.Frame(self)
        frame_botones.grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(frame_botones, text="Aceptar", command=self.aceptar).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Cancelar", command=self.cancelar).pack(side=tk.LEFT, padx=5)

        self.resultado = None

    def aceptar(self):
        titulo = self.entry_titulo.get().strip()
        descripcion = self.entry_descripcion.get().strip()
        enlace = self.entry_enlace.get().strip()
        portada = self.entry_portada.get().strip() or None

        if not titulo or not descripcion or not enlace:
            messagebox.showerror("Error", "Título, descripción y enlace son obligatorios.")
            return

        self.resultado = {
            "titulo": titulo,
            "descripcion": descripcion,
            "enlace": enlace,
            "portada": portada
        }
        self.destroy()

    def cancelar(self):
        self.resultado = None
        self.destroy()

class EditorGUI:
    """
    Clase principal para la interfaz gráfica del editor.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Biblioteca sin Censura - Editor de Contenido")
        self.root.geometry("900x600")
        self.gestor = GestorContenido()

        # Frame superior: selección de sección
        frame_superior = ttk.Frame(self.root)
        frame_superior.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(frame_superior, text="Sección:").pack(side=tk.LEFT)
        self.combo_seccion = ttk.Combobox(frame_superior, state="readonly")
        self.combo_seccion.pack(side=tk.LEFT, padx=5)
        self.combo_seccion.bind("<<ComboboxSelected>>", self.cargar_items)
        self.actualizar_secciones()

        ttk.Button(frame_superior, text="Nueva Sección", command=self.agregar_seccion).pack(side=tk.LEFT, padx=5)

        # Treeview para items
        frame_central = ttk.Frame(self.root)
        frame_central.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columnas = ("titulo", "descripcion", "enlace", "portada")
        self.tree = ttk.Treeview(frame_central, columns=columnas, show="headings")
        self.tree.heading("titulo", text="Título")
        self.tree.heading("descripcion", text="Descripción")
        self.tree.heading("enlace", text="Enlace")
        self.tree.heading("portada", text="Portada")
        self.tree.column("titulo", width=150)
        self.tree.column("descripcion", width=200)
        self.tree.column("enlace", width=200)
        self.tree.column("portada", width=150)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_central, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame inferior: botones
        frame_inferior = ttk.Frame(self.root)
        frame_inferior.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(frame_inferior, text="Añadir Elemento", command=self.agregar_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_inferior, text="Editar Elemento", command=self.editar_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_inferior, text="Eliminar Elemento", command=self.eliminar_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_inferior, text="Guardar Cambios", command=self.guardar).pack(side=tk.RIGHT, padx=5)

        # Cargar sección inicial
        if self.combo_seccion['values']:
            self.combo_seccion.current(0)
            self.cargar_items()

    def actualizar_secciones(self):
        """
        Actualiza el combobox con las secciones disponibles.
        """
        secciones = sorted(self.gestor.obtener_secciones())
        self.combo_seccion['values'] = secciones

    def agregar_seccion(self):
        """
        Agrega una nueva sección.
        """
        nombre = simpledialog.askstring("Nueva Sección", "Nombre de la sección:")
        if nombre:
            nombre = nombre.strip().lower()
            if self.gestor.agregar_seccion(nombre):
                self.actualizar_secciones()
                self.combo_seccion.set(nombre)
                self.cargar_items()
            else:
                messagebox.showerror("Error", "La sección ya existe.")

    def cargar_items(self, event=None):
        """
        Carga los items de la sección seleccionada en el treeview.
        """
        for i in self.tree.get_children():
            self.tree.delete(i)
        seccion = self.combo_seccion.get()
        items = self.gestor.obtener_items(seccion)
        for idx, item in enumerate(items):
            self.tree.insert("", tk.END, iid=str(idx), values=(item["titulo"], item["descripcion"], item["enlace"], item["portada"] or ""))

    def agregar_item(self):
        """
        Abre el diálogo para añadir un nuevo item.
        """
        dialogo = DialogoItem(self.root)
        self.root.wait_window(dialogo)
        if dialogo.resultado:
            seccion = self.combo_seccion.get()
            self.gestor.agregar_item(seccion, dialogo.resultado)
            self.cargar_items()

    def editar_item(self):
        """
        Abre el diálogo para editar el item seleccionado.
        """
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona un elemento para editar.")
            return
        idx = int(seleccion[0])
        seccion = self.combo_seccion.get()
        items = self.gestor.obtener_items(seccion)
        item = items[idx]
        dialogo = DialogoItem(self.root, titulo="Editar Item", item=item)
        self.root.wait_window(dialogo)
        if dialogo.resultado:
            self.gestor.editar_item(seccion, idx, dialogo.resultado)
            self.cargar_items()

    def eliminar_item(self):
        """
        Elimina el item seleccionado.
        """
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona un elemento para eliminar.")
            return
        if messagebox.askyesno("Confirmar", "¿Eliminar el elemento seleccionado?"):
            idx = int(seleccion[0])
            seccion = self.combo_seccion.get()
            self.gestor.eliminar_item(seccion, idx)
            self.cargar_items()

    def guardar(self):
        """
        Guarda los cambios en el archivo JSON.
        """
        self.gestor.guardar_datos()

if __name__ == "__main__":
    root = tk.Tk()
    app = EditorGUI(root)
    root.mainloop()
