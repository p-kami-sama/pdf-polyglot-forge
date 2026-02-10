# This script creates a simple PDF document using ReportLab without null bytes, a requirement to create a valid PDF/Python hybrid file.

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_pdf(filename):
    # Configurar la página
    width, height = letter
    c = canvas.Canvas(filename, pagesize=letter)

    # Texto a mostrar
    text = "This is a sample PDF document"
    font_name = "Helvetica"
    font_size = 12

    # Configurar fuente
    c.setFont(font_name, font_size)

    # Calcular posición centrada
    text_width = c.stringWidth(text, font_name, font_size)
    x = (width - text_width) / 2
    y = height / 2

    # Dibujar texto
    c.drawString(x, y, text)

    # Guardar el PDF
    c.save()

# Crear el PDF

create_pdf("sample.pdf")

with open("sample.pdf", "rb") as f:
    content = f.read()
    assert b"\x00" not in content, "El archivo contiene bytes nulos"
