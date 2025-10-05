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

def obtener_trabajo_por_id(reg_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""SELECT id, fecha, nombre, patente, telefono, descripcion
                   FROM trabajos WHERE id = ?""", (reg_id,))
    row = cur.fetchone()
    conn.close()
    return row

def actualizar_trabajo(reg_id: int, nombre: str, patente: str, telefono: str, descripcion: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        UPDATE trabajos
        SET nombre = ?, patente = ?, telefono = ?, descripcion = ?
        WHERE id = ?
    """, (nombre, patente, telefono, descripcion, reg_id))
    conn.commit()
    conn.close()

def borrar_trabajo(reg_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM trabajos WHERE id = ?", (reg_id,))
    conn.commit()
    conn.close()

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
        self.geometry("920x460")
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
        widths = {"id": 50, "fecha": 130, "nombre": 200, "patente": 110, "telefono": 140, "descripcion": 300}
        for col in columnas:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=widths[col], anchor="w")

        # Botonera inferior: Editar / Borrar
        frm_bot = ttk.Frame(self, padding=(10, 6))
        frm_bot.pack(fill=tk.X)
        self.btn_edit = ttk.Button(frm_bot, text="Editar seleccionado", command=self.editar_sel)
        self.btn_del = ttk.Button(frm_bot, text="Borrar seleccionado", command=self.borrar_sel)
        self.btn_edit.pack(side=tk.LEFT, padx=(0, 6))
        self.btn_del.pack(side=tk.LEFT)

        self.refrescar()
        # Doble click abre edición también
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

    def _id_seleccionado(self):
        item = self.tree.focus()
        if not item:
            return None
        vals = self.tree.item(item, "values")
        if not vals:
            return None
        return int(vals[0])

    def on_doble_click(self, _event):
        self.editar_sel()

    def editar_sel(self):
        reg_id = self._id_seleccionado()
        if not reg_id:
            messagebox.showwarning("Seleccioná un registro", "Primero seleccioná una fila.")
            return
        row = obtener_trabajo_por_id(reg_id)
        if not row:
            messagebox.showerror("Error", "No se encontró el registro.")
            return
        EditarVentana(self, reg_id, row, on_saved=self.refrescar)

    def borrar_sel(self):
        reg_id = self._id_seleccionado()
        if not reg_id:
            messagebox.showwarning("Seleccioná un registro", "Primero seleccioná una fila.")
            return
        if messagebox.askyesno("Confirmar borrado", "¿Seguro que querés borrar este registro?"):
            try:
                borrar_trabajo(reg_id)
                self.refrescar()
                messagebox.showinfo("Eliminado", "Registro borrado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo borrar.\n{e}")

class EditarVentana(tk.Toplevel):
    def __init__(self, parent, reg_id: int, row_tuple, on_saved=None):
        super().__init__(parent)
        self.title(f"Editar registro #{reg_id}")
        self.geometry("520x420")
        self.resizable(False, False)
        self.reg_id = reg_id
        self.on_saved = on_saved

        # row_tuple = (id, fecha, nombre, patente, telefono, descripcion)
        _, fecha, nombre, patente, telefono, descripcion = row_tuple

        frm = ttk.Frame(self, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text=f"Fecha (solo lectura): {fecha}", foreground="#555").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,8))

        ttk.Label(frm, text="Nombre y Apellido *").grid(row=1, column=0, sticky="w", pady=4)
        self.e_nombre = ttk.Entry(frm, width=40)
        self.e_nombre.grid(row=1, column=1, sticky="w")
        self.e_nombre.insert(0, nombre)

        ttk.Label(frm, text="Patente *").grid(row=2, column=0, sticky="w", pady=4)
        self.e_patente = ttk.Entry(frm, width=20)
        self.e_patente.grid(row=2, column=1, sticky="w")
        self.e_patente.insert(0, patente)

        ttk.Label(frm, text="Teléfono").grid(row=3, column=0, sticky="w", pady=4)
        self.e_tel = ttk.Entry(frm, width=20)
        self.e_tel.grid(row=3, column=1, sticky="w")
        self.e_tel.insert(0, telefono if telefono else "")

        ttk.Label(frm, text="Descripción del trabajo").grid(row=4, column=0, sticky="nw", pady=4)
        self.t_desc = tk.Text(frm, width=40, height=8)
        self.t_desc.grid(row=4, column=1, sticky="w")
        if descripcion:
            self.t_desc.insert("1.0", descripcion)

        btns = ttk.Frame(frm)
        btns.grid(row=5, column=1, sticky="e", pady=10)
        ttk.Button(btns, text="Guardar cambios", command=self.guardar).grid(row=0, column=0, padx=4)
        ttk.Button(btns, text="Cancelar", command=self.destroy).grid(row=0, column=1, padx=4)

        self.bind("<Return>", lambda e: self.guardar())
        self.e_nombre.focus()

    def guardar(self):
        nombre = self.e_nombre.get().strip()
        patente = self.e_patente.get().strip().upper().replace(" ", "")
        telefono = self.e_tel.get().strip().replace(" ", "")
        descripcion = self.t_desc.get("1.0", "end").strip()

        if not nombre or not patente:
            messagebox.showwarning("Faltan datos", "Nombre y Patente son obligatorios.")
            return

        try:
            actualizar_trabajo(self.reg_id, nombre, patente, telefono, descripcion)
            if self.on_saved:
                self.on_saved()
            messagebox.showinfo("OK", "Cambios guardados correctamente.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar.\n{e}")

# ------------------ Main ------------------
if __name__ == "__main__":
    init_db()
    app = App()
    app.mainloop()
