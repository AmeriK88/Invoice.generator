import tkinter as tk
from tkinter import ttk, messagebox
from fpdf import FPDF
from datetime import datetime
import os
import sys

# Route for invoice Logo
def get_resource_path(relative_path):
    """ Obtiene la ruta del archivo, compatible con PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Obtaining invoice Nº
def obtener_numero_factura():
    archivo = "ultimo_numero_factura.txt"
    if os.path.exists(archivo):
        with open(archivo, "r") as f:
            ultimo_numero = int(f.read())
    else:
        ultimo_numero = 0

    nuevo_numero = ultimo_numero + 1

    with open(archivo, "w") as f:
        f.write(str(nuevo_numero))

    return f"2025-{nuevo_numero:03d}"

# Class for generating PDF
class FacturaPDF(FPDF):
    def header(self):
        image_path = get_resource_path("amgd.jpg")  
        try:
            self.image(image_path, 10, 8, 33)  
        except:
            print(f"⚠️ Advertencia: No se encontró la imagen en {image_path}. Verifica la ruta.")

        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'FACTURA', ln=True, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-35)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 5, "COMPANY NAME", ln=True, align='C')
        self.cell(0, 5, "LOCAL ADDRESS", ln=True, align='C')
        self.cell(0, 5, "NIF: YOUR ID NUMBER", ln=True, align='C')
        self.ln(5)
        self.set_font('Arial', 'B', 8)
        self.cell(0, 5, "Forma de Pago: Transferencia Bancaria", ln=True, align='C')
        self.set_font('Arial', '', 8)
        self.cell(0, 5, "IBAN: ESXX XXXX XXXX XXXX XXXX XXXX", ln=True, align='C')
        self.ln(5)
        self.cell(0, 5, f'Página {self.page_no()}', 0, 0, 'C')

    def datos_factura(self, numero_factura, fecha):
        self.set_font('Arial', 'B', 10)
        self.cell(0, 8, 'Datos de la Factura', ln=True)
        self.cell(95, 8, f'Factura Nº: {numero_factura}', 1)
        self.cell(95, 8, f'Fecha: {fecha}', 1, ln=True)
        self.ln(5)

    def datos_contacto(self, titulo, nombre, nif, direccion, negocio=None):
        self.set_font('Arial', 'B', 10)
        self.cell(0, 8, titulo, ln=True)
        self.set_font('Arial', '', 9)
        self.cell(95, 8, f'Nombre: {nombre}', 1, 0, 'L')
        if negocio:
            self.cell(95, 8, f'Negocio: {negocio}', 1, 1, 'L')
        else:
            self.cell(95, 8, '', 1, 1, 'L')
        self.cell(95, 8, f'NIF: {nif}', 1, 0, 'L')
        self.multi_cell(95, 8, f'Dirección: {direccion}', 1, 'L')
        self.ln(5)

    # Méthod`deatil service()`
    def detalle_servicios(self, servicios):
        self.set_font('Arial', 'B', 10)
        self.cell(150, 8, 'Descripción', 1, 0, 'C')
        self.cell(40, 8, 'Precio (EUR)', 1, 1, 'C')

        self.set_font('Arial', '', 9)
        for descripcion, precio in servicios:
            self.cell(150, 8, descripcion, 1, 0, 'L')
            self.cell(40, 8, f"{precio:.2f}", 1, 1, 'R')

        self.ln(5)

    # Méthod total
    def total(self, total, aplicar_igic):
        self.set_font('Arial', 'B', 12)
        self.cell(150, 10, 'Subtotal:', 1, 0, 'R')
        self.cell(40, 10, f'{total:.2f} EUR', 1, 1, 'R')

        if aplicar_igic:
            igic = total * 0.07
            total_con_igic = total + igic
            self.cell(150, 10, 'IGIC (7%):', 1, 0, 'R')
            self.cell(40, 10, f'{igic:.2f} EUR', 1, 1, 'R')
            self.cell(150, 10, 'Total con IGIC:', 1, 0, 'R')
            self.cell(40, 10, f'{total_con_igic:.2f} EUR', 1, 1, 'R')



# Function to update pdf
def actualizar_total():
    global tree, total_label  
    total = sum(float(tree.item(item, 'values')[1]) for item in tree.get_children())
    total_label.config(text=f"Total: {total:.2f} EUR")

# Funtion to add services 
def agregar_servicio():
    global tree  
    descripcion = entry_servicio.get()
    try:
        precio = float(entry_precio.get())
    except ValueError:
        messagebox.showerror("Error", "El precio debe ser un número válido.")
        return

    if not descripcion or precio <= 0:
        messagebox.showerror("Error", "Debe ingresar una descripción y un precio válido.")
        return

    tree.insert("", "end", values=(descripcion, f"{precio:.2f}"))
    entry_servicio.delete(0, tk.END)
    entry_precio.delete(0, tk.END)
    actualizar_total()

# Generate invoice
def generar_factura():
    global tree  
    nombre = entry_nombre.get()
    nif = entry_nif.get()
    direccion = entry_direccion.get()
    negocio = entry_negocio.get()
    aplicar_igic = igic_var.get()

    if not nombre or not nif or not direccion:
        messagebox.showerror("Error", "Todos los campos deben estar llenos.")
        return

    servicios = [(tree.item(item, 'values')[0], float(tree.item(item, 'values')[1])) for item in tree.get_children()]

    if not servicios:
        messagebox.showerror("Error", "Debe añadir al menos un servicio.")
        return

    numero_factura = obtener_numero_factura()
    fecha_factura = datetime.now().strftime("%d/%m/%Y")
    total_factura = sum(precio for _, precio in servicios)

    pdf = FacturaPDF()
    pdf.add_page()
    pdf.datos_factura(numero_factura, fecha_factura)
    pdf.datos_contacto("Cliente", nombre, nif, direccion, negocio)
    pdf.detalle_servicios(servicios)
    pdf.total(total_factura, aplicar_igic)

    pdf.output(f"Factura_{numero_factura}.pdf")
    messagebox.showinfo("Éxito", f"Factura {numero_factura} generada correctamente.")

# UI 
root = tk.Tk()
root.title("Generador de Facturas")
root.geometry("600x600")

frame = ttk.LabelFrame(root, text="Datos del Cliente")
frame.pack(fill="x", padx=10, pady=5)

entry_nombre = ttk.Entry(frame, width=30)
entry_nombre.grid(row=0, column=1)

entry_nif = ttk.Entry(frame, width=30)
entry_nif.grid(row=1, column=1)

entry_direccion = ttk.Entry(frame, width=30)
entry_direccion.grid(row=2, column=1)

entry_negocio = ttk.Entry(frame, width=30)
entry_negocio.grid(row=3, column=1)

# Section to add services
frame_servicios = ttk.LabelFrame(root, text="Añadir Servicio")
frame_servicios.pack(fill="x", padx=10, pady=5)

entry_servicio = ttk.Entry(frame_servicios, width=40)
entry_servicio.grid(row=0, column=0, padx=5, pady=5)

entry_precio = ttk.Entry(frame_servicios, width=10)
entry_precio.grid(row=0, column=1, padx=5, pady=5)

ttk.Button(frame_servicios, text="Añadir", command=agregar_servicio).grid(row=0, column=2, padx=5, pady=5)

# Service table
tree = ttk.Treeview(root, columns=("Servicio", "Precio"), show="headings", height=5)
tree.heading("Servicio", text="Servicio")
tree.heading("Precio", text="Precio (EUR)")
tree.pack(pady=5)

# IGIC Checkbox
igic_var = tk.BooleanVar()
ttk.Checkbutton(root, text="Aplicar IGIC (7%)", variable=igic_var).pack()

# Label for total
total_label = ttk.Label(root, text="Total: 0.00 EUR", font=("Arial", 10, "bold"))
total_label.pack(pady=5)

# Button to generate invoice
ttk.Button(root, text="Generar Factura", command=generar_factura).pack(pady=10)

root.mainloop()
