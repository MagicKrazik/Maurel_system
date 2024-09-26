# utils.py

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from django.conf import settings
import os
from PIL import Image
import io

def generate_payment_report(payment, filename):
    report_path = os.path.join(settings.MEDIA_ROOT, 'documents', filename)
    
    c = canvas.Canvas(report_path, pagesize=letter)
    width, height = letter

    # Add content to the PDF
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Comprobante de Pago")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Usuario: {payment.user.username}")
    c.drawString(50, height - 100, f"Apartamento: {payment.user.apartment_number}")
    c.drawString(50, height - 120, f"Fecha de pago: {payment.payment_date}")
    c.drawString(50, height - 140, f"Monto pagado: ${payment.amount_paid}")
    c.drawString(50, height - 160, f"Método de pago: {payment.get_payment_method_display()}")
    
    if payment.comments:
        c.drawString(50, height - 180, "Comentarios:")
        c.drawString(70, height - 200, payment.comments[:50])  # Limit to first 50 characters

    # Add the proof of payment image
    if payment.proof_of_payment:
        img_path = payment.proof_of_payment.path
        img = Image.open(img_path)
        
        # Resize image to fit within the PDF
        max_width = 400
        max_height = 300
        img.thumbnail((max_width, max_height))
        
        # Convert image for ReportLab
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Calculate position to center the image
        img_width, img_height = img.size
        x = (width - img_width) / 2
        y = height - 250 - img_height  # Position below the text content
        
        c.drawImage(ImageReader(img_buffer), x, y, width=img_width, height=img_height)
        c.drawString(50, y - 20, "Comprobante de pago adjunto")

    c.save()
    
    return os.path.join('documents', filename)


def generate_expense_report(expense, filename):
    report_path = os.path.join(settings.MEDIA_ROOT, 'documents', filename)
    c = canvas.Canvas(report_path, pagesize=letter)
    width, height = letter

    # Add content to the PDF
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Reporte de Gasto")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Concepto: {expense.expense_concept}")
    c.drawString(50, height - 100, f"Monto: ${expense.amount}")
    c.drawString(50, height - 120, f"Fecha: {expense.expense_date.strftime('%d/%m/%Y')}")
    c.drawString(50, height - 140, f"Método de pago: {expense.get_payment_method_display()}")
    c.drawString(50, height - 160, f"Comentarios: {expense.comments}")

    # Add the proof of expense image
    if expense.proof_of_expense:
        img_path = expense.proof_of_expense.path
        img = Image.open(img_path)
        
        # Resize image to fit within the PDF
        max_width = 400
        max_height = 300
        img.thumbnail((max_width, max_height))
        
        # Convert image for ReportLab
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Calculate position to center the image
        img_width, img_height = img.size
        x = (width - img_width) / 2
        y = height - 250 - img_height  # Position below the text content
        
        c.drawImage(ImageReader(img_buffer), x, y, width=img_width, height=img_height)
        c.drawString(50, y - 20, "Comprobante de gasto adjunto")

    c.save()
    return os.path.join('documents', filename)