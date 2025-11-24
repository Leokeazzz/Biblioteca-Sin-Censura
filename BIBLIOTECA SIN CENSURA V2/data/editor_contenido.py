import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os

class GestorContenido:
    """
    Ahora cada sección usa su propio archivo JSON:
    cursos.json, comics.json, libros.json, software.json, etc.
    """
    def __init__(self, carpeta="data"):
        self.carpeta = carpeta
        os.makedirs(self.carpeta, exist_ok=True)

        # Secciones iniciales
        self.secciones = ["cursos", "comics", "libros", "software"]

        # Asegurar archivos
        for s in self.secciones:
            self._asegurar_archivo(s)

    def _ruta(self, seccion):
        return os.path.join(self.carpeta, f"{seccion}.json")

    def _asegurar_archivo(self, seccion):
        ruta = self._ruta(seccion)
        if not os.path.exists(ruta):
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4, ensure_ascii=False)

    def obtener_secciones(self):
        return self.secciones

    def agregar_seccion(self, nombre):
        nombre = nombre.lower()
        if nombre in self.secciones:
            return False

        self.secciones.append(nombre)
        self._asegurar_archivo(nombre)
        return True

    def cargar_items(self, seccion):
        ruta = self._ruta(seccion)
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("Error", f"El archivo {ruta} está corrupto.")
            return []

    def guardar_items(self, seccion, items):
        ruta = self._ruta(seccion)
        try:
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(items, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar {ruta}: {str(e)}")

    def obtener_items(self, seccion):
        return self.cargar_items(seccion)

    def agregar_item(self, seccion, item):
        items = self.cargar_items(seccion)
        items.append(item)
        self.guardar_items(seccion, items)

    def editar_item(self, seccion, indice, item):
        items = self.cargar_items(seccion)
        if 0 <= indice < len(items):
            items[indice] = item
            self.guardar_items(seccion, items)

    def eliminar_item(self, seccion, indice):
        items = self.cargar_items(seccion)
        if 0 <= indice < len(items):
            del items[indice]
            self.guardar_items(seccion, items)


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
        self.entry_portada.insert(0, self.item.get("portada", ""))

        frame_botones = ttk.Frame(self)
        frame_botones.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(frame_botones, text="Aceptar", command=self.aceptar).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Cancelar", command=self.cancelar).pack(side=tk.LEFT, padx=5)

        self.resultado = None

    def aceptar(self):
        t = self.entry_titulo.get().strip()
        d = self.entry_descripcion.get().strip()
        e = self.entry_enlace.get().strip()
        p = self.entry_portada.get().strip() or None

        if not t or not d or not e:
            messagebox.showerror("Error", "Título, descripción y enlace son obligatorios.")
            return

        self.resultado = {
            "titulo": t,
            "descripcion": d,
            "enlace": e,
            "imagen": p
        }

        self.destroy()

    def cancelar(self):
        self.resultado = None
        self.destroy()


class EditorGUI:
    """
    Interfaz gráfica actualizada para trabajar con múltiples archivos JSON.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Contenido – Biblioteca sin Censura")
        self.root.geometry("900x600")

        self.gestor = GestorContenido()

        frame_superior = ttk.Frame(root)
        frame_superior.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(frame_superior, text="Sección:").pack(side=tk.LEFT)
        self.combo_seccion = ttk.Combobox(frame_superior, state="readonly")
        self.combo_seccion.pack(side=tk.LEFT, padx=5)
        self.combo_seccion.bind("<<ComboboxSelected>>", self.cargar_items)

        self.combo_seccion["values"] = self.gestor.obtener_secciones()
        if self.combo_seccion["values"]:
            self.combo_seccion.current(0)

        #ttk.Button(frame_superior, text="Nueva Sección", command=self.agregar_seccion).pack(side=tk.LEFT, padx=5)

        frame_central = ttk.Frame(root)
        frame_central.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columnas = ("titulo", "descripcion", "enlace", "portada")
        self.tree = ttk.Treeview(frame_central, columns=columnas, show="headings")
        for col in columnas:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=160)

        self.tree.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame_central, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        frame_inferior = ttk.Frame(root)
        frame_inferior.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(frame_inferior, text="Añadir Elemento", command=self.agregar_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_inferior, text="Editar Elemento", command=self.editar_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_inferior, text="Eliminar Elemento", command=self.eliminar_item).pack(side=tk.LEFT, padx=5)

        self.cargar_items()

    def cargar_items(self, event=None):
        for i in self.tree.get_children():
            self.tree.delete(i)

        seccion = self.combo_seccion.get()
        items = self.gestor.obtener_items(seccion)

        for idx, item in enumerate(items):
            self.tree.insert("", tk.END, iid=str(idx),
                             values=(item["titulo"], item["descripcion"], item["enlace"], item.get("portada", "")))

    def agregar_item(self):
        dialogo = DialogoItem(self.root)
        self.root.wait_window(dialogo)

        if dialogo.resultado:
            sec = self.combo_seccion.get()
            self.gestor.agregar_item(sec, dialogo.resultado)
            self.cargar_items()

    def editar_item(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Advertencia", "Seleccione un item.")
            return

        idx = int(sel[0])
        sec = self.combo_seccion.get()

        items = self.gestor.obtener_items(sec)
        item = items[idx]

        dialogo = DialogoItem(self.root, "Editar Item", item)
        self.root.wait_window(dialogo)

        if dialogo.resultado:
            self.gestor.editar_item(sec, idx, dialogo.resultado)
            self.cargar_items()

    def eliminar_item(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Advertencia", "Seleccione un item.")
            return

        if not messagebox.askyesno("Confirmar", "¿Eliminar item?"):
            return

        idx = int(sel[0])
        sec = self.combo_seccion.get()

        self.gestor.eliminar_item(sec, idx)
        self.cargar_items()


if __name__ == "__main__":
    root = tk.Tk()
    EditorGUI(root)
    root.mainloop()
