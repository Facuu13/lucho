import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

DB_PATH = "taller.db"

# ------------------ DB ------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS trabajos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        nombre TEXT NOT NULL,
        patente TEXT NOT NULL,
        telefono TEXT,
        descripcion TEXT
    )
    """)
    conn.commit()
    conn.close()

def insertar_trabajo(nombre, patente, telefono, descripcion):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO trabajos (fecha, nombre, patente, telefono, descripcion)
        VALUES (?, ?, ?, ?, ?)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M"), nombre, patente, telefono, descripcion))
    conn.commit()
    conn.close()

def buscar_trabajos(filtro_patente="", filtro_telefono=""):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    query = "SELECT id, fecha, nombre, patente, telefono, descripcion FROM trabajos WHERE 1=1"
    params = []
    if filtro_patente:
        query += " AND patente LIKE ?"
        params.append(f"%{filtro_patente.upper()}%")
    if filtro_telefono:
        query += " AND telefono LIKE ?"
        params.append(f"%{filtro_telefono}%")
    query += " ORDER BY id DESC"
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows

# ------------------ UI ------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Registro de Trabajos - Taller")
        self.geometry("520x420")
        self.resizable(False, False)

        # Campos
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="Nombre y Apellido *").grid(row=0, column=0, sticky="w", pady=4)
        self.e_nombre = ttk.Entry(frm, width=40)
        self.e_nombre.grid(row=0, column=1, sticky="w")

        ttk.Label(frm, text="Patente *").grid(row=1, column=0, sticky="w", pady=4)
        self.e_patente = ttk.Entry(frm, width=20)
        self.e_patente.grid(row=1, column=1, sticky="w")

        ttk.Label(frm, text="Teléfono").grid(row=2, column=0, sticky="w", pady=4)
        self.e_tel = ttk.Entry(frm, width=20)
        self.e_tel.grid(row=2, column=1, sticky="w")

        ttk.Label(frm, text="Descripción del trabajo").grid(row=3, column=0, sticky="nw", pady=4)
        self.t_desc = tk.Text(frm, width=40, height=8)
        self.t_desc.grid(row=3, column=1, sticky="w")

        # Botones
        btns = ttk.Frame(frm)
        btns.grid(row=4, column=1, sticky="e", pady=10)

        ttk.Button(btns, text="Guardar", command=self.on_guardar).grid(row=0, column=0, padx=4)
        ttk.Button(btns, text="Ver registros", command=self.abrir_lista).grid(row=0, column=1, padx=4)
        ttk.Button(btns, text="Limpiar", command=self.limpiar).grid(row=0, column=2, padx=4)

        ttk.Label(frm, text="(*) Obligatorio", foreground="#666").grid(row=5, column=1, sticky="w")

        # Accesibilidad
        self.bind("<Return>", lambda e: self.on_guardar())
        self.e_nombre.focus()

    def on_guardar(self):
        nombre = self.e_nombre.get().strip()
        patente = self.e_patente.get().strip().upper()
        telefono = self.e_tel.get().strip()
        descripcion = self.t_desc.get("1.0", "end").strip()

        # Validaciones mínimas
        if not nombre or not patente:
            messagebox.showwarning("Faltan datos", "Nombre y Patente son obligatorios.")
            return

        # Limpieza básica
        patente = patente.replace(" ", "")
        telefono = telefono.replace(" ", "")

        try:
            insertar_trabajo(nombre, patente, telefono, descripcion)
            messagebox.showinfo("OK", "Trabajo guardado correctamente.")
            self.limpiar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar.\n{e}")

    def limpiar(self):
        self.e_nombre.delete(0, "end")
        self.e_patente.delete(0, "end")
        self.e_tel.delete(0, "end")
        self.t_desc.delete("1.0", "end")
        self.e_nombre.focus()

    def abrir_lista(self):
        ListaVentana(self)

class ListaVentana(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Trabajos guardados")
        self.geometry("860x420")
        self.resizable(True, True)

        frm_filtros = ttk.Frame(self, padding=(10, 8))
        frm_filtros.pack(fill=tk.X)
        ttk.Label(frm_filtros, text="Filtrar por Patente:").grid(row=0, column=0, padx=4)
        self.f_pat = ttk.Entry(frm_filtros, width=18)
        self.f_pat.grid(row=0, column=1)

        ttk.Label(frm_filtros, text="Filtrar por Teléfono:").grid(row=0, column=2, padx=(12, 4))
        self.f_tel = ttk.Entry(frm_filtros, width=18)
        self.f_tel.grid(row=0, column=3)

        ttk.Button(frm_filtros, text="Buscar", command=self.refrescar).grid(row=0, column=4, padx=8)
        ttk.Button(frm_filtros, text="Limpiar", command=self.limpiar_filtros).grid(row=0, column=5)

        columnas = ("id", "fecha", "nombre", "patente", "telefono", "descripcion")
        self.tree = ttk.Treeview(self, columns=columnas, show="headings", height=14)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        headers = {
            "id": "ID",
            "fecha": "Fecha",
            "nombre": "Nombre y Apellido",
            "patente": "Patente",
            "telefono": "Teléfono",
            "descripcion": "Descripción"
        }
        widths = {"id": 50, "fecha": 130, "nombre": 180, "patente": 100, "telefono": 120, "descripcion": 260}
        for col in columnas:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=widths[col], anchor="w")

        self.refrescar()

        # Doble click para ver detalle en popup
        self.tree.bind("<Double-1>", self.on_doble_click)

    def refrescar(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = buscar_trabajos(self.f_pat.get().strip(), self.f_tel.get().strip())
        for r in rows:
            self.tree.insert("", "end", values=r)

    def limpiar_filtros(self):
        self.f_pat.delete(0, "end")
        self.f_tel.delete(0, "end")
        self.refrescar()

    def on_doble_click(self, _event):
        item = self.tree.focus()
        if not item:
            return
        vals = self.tree.item(item, "values")
        _, fecha, nombre, patente, tel, desc = vals
        messagebox.showinfo(
            "Detalle",
            f"Fecha: {fecha}\nNombre: {nombre}\nPatente: {patente}\nTeléfono: {tel}\n\nDescripción:\n{desc}"
        )

# ------------------ Main ------------------
if __name__ == "__main__":
    init_db()
    app = App()
    app.mainloop()
