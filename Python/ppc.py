import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error

# ----- MENÚ PRINCIPAL -----
class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Menú Principal")
        self.root.geometry("450x200")
        self.create_widgets()

    def create_widgets(self):
        title_label = ttk.Label(
            self.root,
            text="Bienvenido al CRUD del inventario del laboratorio",
            font=("Arial", 12, "bold"),
            anchor="center",
            justify="center",
            wraplength=400
        )
        title_label.pack(pady=20)

        enter_button = ttk.Button(self.root, text="Entrar", command=self.open_crud)
        enter_button.pack(pady=10)

    def open_crud(self):
        # Cerrar menú principal
        self.root.destroy()
        # Abrir CRUD en una nueva ventana principal
        crud_root = tk.Tk()
        CRUDApp(crud_root)
        crud_root.mainloop()
# ----- APLICACIÓN CRUD -----
class CRUDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplicación CRUD")
        self.root.geometry("600x400")

        # Conectar a la base de datos
        try:
            self.conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='root',  # Cambiar según tu configuración
                database='proyecto_planta'
            )
            self.c = self.conn.cursor()
        except Error as e:
            messagebox.showerror("Error", f"No se pudo conectar a MySQL: {e}")
            self.root.destroy()
            return

        self.create_tab_plantas()

    # ----- TAB PLANTAS -----
    def create_tab_plantas(self):
        tab_control = ttk.Notebook(self.root)
        self.plantas_tab = ttk.Frame(tab_control)
        tab_control.add(self.plantas_tab, text="Plantas")
        tab_control.pack(expand=1, fill="both")
        self.create_plantas_grilla()

    # ----- TREEVIEW -----
    def create_plantas_grilla(self):
        self.tree = ttk.Treeview(self.plantas_tab, columns=("id", "nombre", "humedad"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("humedad", text="Humedad")
        self.tree.pack(fill="both", expand=True)

        # Botones
        btn_frame = ttk.Frame(self.plantas_tab)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(btn_frame, text="Nuevo", command=self.open_nuevo).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Modificar", command=self.open_modificar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.eliminar_elemento).pack(side="left", padx=5)

        # Búsqueda
        search_frame = ttk.Frame(self.plantas_tab)
        search_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(search_frame, text="Buscar:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.update_table())
        ttk.Button(search_frame, text="Buscar", command=self.update_table).pack(side="left", padx=5)

        self.update_table()

    # ----- FUNCIONES CRUD -----
    def open_nuevo(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Nuevo registro")

        tk.Label(ventana, text="ID:").grid(row=0, column=0, padx=10, pady=5)
        id_entry = tk.Entry(ventana)
        id_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(ventana, text="Nombre:").grid(row=1, column=0, padx=10, pady=5)
        nombre_entry = tk.Entry(ventana)
        nombre_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(ventana, text="Humedad:").grid(row=2, column=0, padx=10, pady=5)
        humedad_entry = tk.Entry(ventana)
        humedad_entry.grid(row=2, column=1, padx=10, pady=5)

        ttk.Button(ventana, text="💾 Guardar",
                   command=lambda: self.guardar_elemento(id_entry.get(), nombre_entry.get(), humedad_entry.get(), ventana)
                   ).grid(row=3, column=0, columnspan=2, pady=10)

    def guardar_elemento(self, id, nombre, humedad, ventana):
        if not id or not nombre or not humedad:
            messagebox.showwarning("Campos vacíos", "Completa todos los campos")
            return
        try:
            self.c.execute("INSERT INTO plantas (nombre, humedad) VALUES (%s, %s)", (nombre, humedad))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Registro guardado")
            ventana.destroy()
            self.update_table()
        except Error as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")

    def open_modificar(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Modificar", "Selecciona un registro")
            return
        item = self.tree.item(selected)
        item_id, item_nombre, item_humedad = item['values']

        ventana = tk.Toplevel(self.root)
        ventana.title("Modificar registro")

        tk.Label(ventana, text="Nombre:").grid(row=0, column=0, padx=10, pady=5)
        nombre_entry = tk.Entry(ventana)
        nombre_entry.grid(row=0, column=1, padx=10, pady=5)
        nombre_entry.insert(0, item_nombre)

        tk.Label(ventana, text="Humedad:").grid(row=1, column=0, padx=10, pady=5)
        humedad_entry = tk.Entry(ventana)
        humedad_entry.grid(row=1, column=1, padx=10, pady=5)
        humedad_entry.insert(0, item_humedad)

        ttk.Button(ventana, text="💾 Guardar",
                   command=lambda: self.guardar_modificacion(item_id, nombre_entry.get(), humedad_entry.get(), ventana)
                   ).grid(row=2, column=0, columnspan=2, pady=10)

    def guardar_modificacion(self, item_id, nombre, humedad, ventana):
        try:
            self.c.execute("UPDATE plantas SET nombre=%s, humedad=%s WHERE id=%s", (nombre, humedad, item_id))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Registro modificado")
            ventana.destroy()
            self.update_table()
        except Error as e:
            messagebox.showerror("Error", f"No se pudo modificar: {e}")

    def eliminar_elemento(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Eliminar", "Selecciona un registro")
            return
        item = self.tree.item(selected)
        item_id = item['values'][0]
        try:
            self.c.execute("DELETE FROM plantas WHERE id=%s", (item_id,))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Registro eliminado")
            self.update_table()
        except Error as e:
            messagebox.showerror("Error", f"No se pudo eliminar: {e}")

    # ----- ACTUALIZAR TREEVIEW -----
    def update_table(self):
        search_text = self.search_entry.get()
        for row in self.tree.get_children():
            self.tree.delete(row)
        if search_text:
            self.c.execute("SELECT id, nombre, humedad FROM plantas WHERE nombre LIKE %s", (f"%{search_text}%",))
        else:
            self.c.execute("SELECT id, nombre, humedad FROM plantas")
        for row in self.c.fetchall():
            self.tree.insert("", "end", values=row)


# ----- EJECUCIÓN -----
if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()