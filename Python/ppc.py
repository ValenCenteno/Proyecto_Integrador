import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error


# ----- MENÚ PRINCIPAL -----
class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Menú Principal")
        self.root.geometry("500x250")
        self.root.configure(bg="#2c3e50")

        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(
            self.root,
            text="🌱 Bienvenido al CRUD del inventario de plantas 🌱",
            font=("Arial", 14, "bold"),
            bg="#2c3e50",
            fg="white",  # Cambié el color del texto a negro
            wraplength=450,
            justify="center"
        )
        title_label.pack(pady=30)

        enter_button = ttk.Button(self.root, text="Entrar", command=self.open_crud)
        enter_button.pack(pady=15)

    def open_crud(self):
        self.root.destroy()
        crud_root = tk.Tk()
        CRUDApp(crud_root)
        crud_root.mainloop()


# ----- APLICACIÓN CRUD -----
class CRUDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplicación CRUD - Plantas")
        self.root.geometry("700x500")

        # ---- Estilos ----
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 10), foreground="black")  # Cambié a negro
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), foreground="black")  # Cambié a negro
        style.configure("TButton", font=("Arial", 10, "bold"), padding=6, foreground="black")  # Cambié a negro

        # Conectar a la base de datos
        try:
            self.conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='root',  # Ajustá según tu configuración
                database='proyecto_planta'
            )
            self.c = self.conn.cursor()
        except Error as e:
            messagebox.showerror("Error", f"No se pudo conectar a MySQL: {e}")
            self.root.destroy()
            return

        self.create_tab_plantas()

    def create_tab_plantas(self):
        tab_control = ttk.Notebook(self.root)
        self.plantas_tab = ttk.Frame(tab_control)
        tab_control.add(self.plantas_tab, text="Plantas")
        tab_control.pack(expand=1, fill="both")

        self.create_plantas_grilla()

    def create_plantas_grilla(self):
        self.tree = ttk.Treeview(
            self.plantas_tab,
            columns=("id", "nombre", "humedad", "porcentaje"),
            show="headings",
            height=15
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("humedad", text="Humedad")
        self.tree.heading("porcentaje", text="Porcentaje")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nombre", width=200)
        self.tree.column("humedad", width=150, anchor="center")
        self.tree.column("porcentaje", width=100, anchor="center")

        self.tree.pack(fill="both", expand=True, pady=10, padx=10)

        # Botones
        btn_frame = ttk.Frame(self.plantas_tab)
        btn_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(btn_frame, text="➕ Nuevo", command=self.open_nuevo).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="✏️ Modificar", command=self.open_modificar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑️ Eliminar", command=self.eliminar_elemento).pack(side="left", padx=5)

        # Búsqueda
        search_frame = ttk.Frame(self.plantas_tab)
        search_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(search_frame, text="🔍 Buscar:", font=("Arial", 12), fg="black").pack(side="left", padx=5)  # Cambié a negro
        self.search_entry = ttk.Entry(search_frame, font=("Arial", 12))
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.update_table())
        ttk.Button(search_frame, text="Buscar", command=self.update_table).pack(side="left", padx=5)

        self.update_table()

    # ----- CRUD -----
    def open_nuevo(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Nuevo registro")
        ventana.geometry("300x250")

        tk.Label(ventana, text="Nombre:", font=("Arial", 12), fg="black").grid(row=0, column=0, padx=10, pady=10)  # Cambié a negro
        nombre_entry = tk.Entry(ventana, font=("Arial", 12))
        nombre_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(ventana, text="Humedad:", font=("Arial", 12), fg="black").grid(row=1, column=0, padx=10, pady=10)  # Cambié a negro
        humedad_entry = tk.Entry(ventana, font=("Arial", 12))
        humedad_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(ventana, text="Porcentaje:", font=("Arial", 12), fg="black").grid(row=2, column=0, padx=10, pady=10)  # Cambié a negro
        porcentaje_entry = tk.Entry(ventana, font=("Arial", 12))
        porcentaje_entry.grid(row=2, column=1, padx=10, pady=10)

        ttk.Button(
            ventana, text="💾 Guardar",
            command=lambda: self.guardar_elemento(nombre_entry.get(), humedad_entry.get(), porcentaje_entry.get(), ventana),
            style="TButton"
        ).grid(row=3, column=0, columnspan=2, pady=20)

    def guardar_elemento(self, nombre, humedad, porcentaje, ventana):
        if not nombre or not humedad or not porcentaje:
            messagebox.showwarning("Campos vacíos", "Completa todos los campos")
            return

        try:
            # Intentamos convertir el porcentaje a float
            try:
                # Reemplazamos comas por puntos en caso de que el porcentaje use coma decimal
                porcentaje = porcentaje.replace(",", ".")
                porcentaje = float(porcentaje)  # Intentamos convertirlo a float
            except ValueError:
                messagebox.showwarning("Porcentaje inválido", "El porcentaje debe ser un número válido.")
                return  # Salimos de la función si el porcentaje no es válido

            # Obtener siguiente ID manualmente (MAX + 1)
            self.c.execute("SELECT IFNULL(MAX(id), 0) + 1 FROM plantas")
            next_id = self.c.fetchone()[0]

            # Insertamos el nuevo registro en la base de datos
            self.c.execute("INSERT INTO plantas (id, nombre, humedad, porcentaje) VALUES (%s, %s, %s, %s)",
                           (next_id, nombre, humedad, porcentaje))
            self.conn.commit()  # Confirmamos la transacción
            messagebox.showinfo("Éxito", f"Registro guardado con ID {next_id}")
            ventana.destroy()  # Cerramos la ventana de nuevo registro
            self.update_table()  # Actualizamos la tabla

        except Error as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")  # En caso de error en la base de datos

    def open_modificar(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Modificar", "Selecciona un registro")
            return
        item = self.tree.item(selected)
        item_id, item_nombre, item_humedad, item_porcentaje = item['values']

        ventana = tk.Toplevel(self.root)
        ventana.title("Modificar registro")
        ventana.geometry("300x250")

        tk.Label(ventana, text="Nombre:", font=("Arial", 12), fg="black").grid(row=0, column=0, padx=10, pady=10)  # Cambié a negro
        nombre_entry = tk.Entry(ventana, font=("Arial", 12))
        nombre_entry.grid(row=0, column=1, padx=10, pady=10)
        nombre_entry.insert(0, item_nombre)

        tk.Label(ventana, text="Humedad:", font=("Arial", 12), fg="black").grid(row=1, column=0, padx=10, pady=10)  # Cambié a negro
        humedad_entry = tk.Entry(ventana, font=("Arial", 12))
        humedad_entry.grid(row=1, column=1, padx=10, pady=10)
        humedad_entry.insert(0, item_humedad)

        tk.Label(ventana, text="Porcentaje:", font=("Arial", 12), fg="black").grid(row=2, column=0, padx=10, pady=10)  # Cambié a negro
        porcentaje_entry = tk.Entry(ventana, font=("Arial", 12))
        porcentaje_entry.grid(row=2, column=1, padx=10, pady=10)
        porcentaje_entry.insert(0, item_porcentaje)

        ttk.Button(
            ventana, text="💾 Guardar",
            command=lambda: self.guardar_modificacion(item_id, nombre_entry.get(), humedad_entry.get(), porcentaje_entry.get(), ventana),
            style="TButton"
        ).grid(row=3, column=0, columnspan=2, pady=20)

    def guardar_modificacion(self, item_id, nombre, humedad, porcentaje, ventana):
        try:
            # Validar porcentaje
            try:
                porcentaje = porcentaje.replace(",", ".")
                porcentaje = float(porcentaje)
            except ValueError:
                messagebox.showwarning("Porcentaje inválido", "El porcentaje debe ser un número válido.")
                return  # No se guarda si el porcentaje es inválido

            self.c.execute("UPDATE plantas SET nombre=%s, humedad=%s, porcentaje=%s WHERE id=%s",
                           (nombre, humedad, porcentaje, item_id))
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

    def update_table(self):
        search_text = self.search_entry.get()
        for row in self.tree.get_children():
            self.tree.delete(row)
        if search_text:
            self.c.execute("SELECT id, nombre, humedad, porcentaje FROM plantas WHERE nombre LIKE %s", (f"%{search_text}%",))
        else:
            self.c.execute("SELECT id, nombre, humedad, porcentaje FROM plantas")
        for row in self.c.fetchall():
            self.tree.insert("", "end", values=row)


# ----- EJECUCIÓN -----
if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
