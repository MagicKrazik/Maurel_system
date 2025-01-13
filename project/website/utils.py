# utils.py

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.units import inch
from django.conf import settings
import os
from PIL import Image
import io
from datetime import datetime
from io import BytesIO
from calendar import month_name
from django.utils import timezone
from django.utils import formats
from django.utils.translation import gettext as _
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model



### Functions for proper reports creation and layout handling

def calculate_image_dimensions(img, width, height):
    """
    Calculate optimal image dimensions for a fixed area while maintaining aspect ratio.
    
    Args:
        img: PIL Image object
        width: Fixed width of the container area
        height: Fixed height of the container area
    
    Returns:
        tuple: (new_width, new_height, x_offset)
    """
    img_width, img_height = img.size
    aspect_ratio = img_width / img_height

    # First try to fit by width
    new_width = width
    new_height = width / aspect_ratio

    # If too tall, fit by height instead
    if new_height > height:
        new_height = height
        new_width = height * aspect_ratio

    # Center the image horizontally
    x_offset = (width - new_width) / 2 if new_width < width else 0

    return new_width, new_height, x_offset

def add_image_to_report(c, img_path, x, y, container_width, container_height):
    """
    Add an image to the report within a fixed container area.
    
    Args:
        c: Canvas object
        img_path: Path to the image file
        x: Left position of container
        y: Bottom position of container
        container_width: Width of the container area
        container_height: Height of the container area
    """
    try:
        img = Image.open(img_path)
        
        # Convert image if necessary
        if img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')
        
        # Calculate dimensions
        new_width, new_height, x_offset = calculate_image_dimensions(
            img, container_width, container_height
        )
        
        # Create buffer for ReportLab
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Draw image
        c.drawImage(
            ImageReader(img_buffer),
            x + x_offset,
            y,
            width=new_width,
            height=new_height
        )
        
        return True
    except Exception as e:
        print(f"Error adding image to report: {str(e)}")
        return False
    

def add_footer(c, width, height, y_position):
    """
    Add footer to the PDF at the specified position.
    
    Args:
        c: Canvas object
        width: Page width
        height: Page height
        y_position: Y position for the footer
    """
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor('#1e1e1e'))
    current_year = datetime.now().year
    c.drawString(50, 30, f"© {current_year} Torres del Maurel - Documento oficial")
    c.drawString(width - 150, 30, "Página 1 de 1")


def generate_payment_report(payment, filename):
    report_path = os.path.join(settings.MEDIA_ROOT, 'documents', filename)
    c = canvas.Canvas(report_path, pagesize=letter)
    width, height = letter

    # Define fixed dimensions
    margin = 50
    image_container_width = width - (2 * margin)  # 512 points
    image_container_height = 300  # Fixed height for image section

    # Colors
    primary_color = colors.HexColor('#1896d1')
    secondary_color = colors.HexColor('#1e1e1e')
    text_color = colors.HexColor('#333333')


    # Title and decorative elements
    c.setFillColor(primary_color)
    c.rect(0, height - 120, width, 2, fill=True)
    c.rect(0, 50, width, 2, fill=True)
    
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(primary_color)
    c.drawString(170, height - 60, "Comprobante de Pago")
    
    # Reference info
    c.setFillColor(secondary_color)
    c.setFont("Helvetica", 10)
    c.drawString(width - 200, height - 90, f"Referencia: {payment.id:06d}")
    c.drawString(width - 200, height - 105, f"Fecha de emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    # Payment details
    y_position = height - 150
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y_position, "Detalles del Pago")
    
    # Payment details table
    payment_data = [
        ['Información', 'Detalle'],
        ['Departamento', payment.user.apartment_number],
        ['Usuario', payment.user.get_full_name() or payment.user.username],
        ['Fecha de pago', payment.payment_date.strftime('%d/%m/%Y')],
        ['Monto pagado', f'${payment.amount_paid:,.2f}'],
        ['Método de pago', payment.get_payment_method_display()],
    ]
    
    table = Table(payment_data, colWidths=[200, 250])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.Color(0.95, 0.95, 0.95)),
        ('TEXTCOLOR', (0, 1), (-1, -1), text_color),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('CELLPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    table.wrapOn(c, width, height)
    y_position = height - 280
    table.drawOn(c, margin, y_position)

    # Comments section
    y_position -= 40
    if payment.comments:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y_position, "Comentarios:")
        c.setFont("Helvetica", 10)
        y_position -= 20
        
        # Handle multiline comments
        for line in payment.comments.split('\n'):
            c.drawString(margin + 20, y_position, line)
            y_position -= 20

    # Image section
    if payment.proof_of_payment:
        y_position -= 30
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y_position, "Comprobante Adjunto:")
        
        # Define image container position
        image_y = y_position - image_container_height - 10
        
        # Add frame for image container
        c.setStrokeColor(colors.lightgrey)
        c.rect(margin, image_y, image_container_width, image_container_height)
        
        # Add image
        add_image_to_report(
            c, 
            payment.proof_of_payment.path,
            margin,
            image_y,
            image_container_width,
            image_container_height
        )

    # Footer
    c.setFont("Helvetica", 8)
    c.setFillColor(secondary_color)
    footer_text = f"© {datetime.now().year} Torres del Maurel - Documento oficial"
    c.drawString(margin, 30, footer_text)
    c.drawString(width - 150, 30, "Página 1 de 1")

    c.save()
    return os.path.join('documents', filename)


def generate_expense_report(expense, filename):
    report_path = os.path.join(settings.MEDIA_ROOT, 'documents', filename)
    c = canvas.Canvas(report_path, pagesize=letter)
    width, height = letter

    # Define fixed dimensions
    margin = 50
    image_container_width = width - (2 * margin)  # 512 points
    image_container_height = 300  # Fixed height for image section

    # Colors
    primary_color = colors.HexColor('#1896d1')
    secondary_color = colors.HexColor('#1e1e1e')
    text_color = colors.HexColor('#333333')


    # Title and decorative elements
    c.setFillColor(primary_color)
    c.rect(0, height - 120, width, 2, fill=True)
    c.rect(0, 50, width, 2, fill=True)
    
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(primary_color)
    c.drawString(170, height - 60, "Comprobante de Gasto")
    
    # Reference info
    c.setFillColor(secondary_color)
    c.setFont("Helvetica", 10)
    c.drawString(width - 200, height - 90, f"Referencia: E{expense.id:06d}")
    c.drawString(width - 200, height - 105, f"Fecha de emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    # Expense details
    y_position = height - 150
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y_position, "Detalles del Gasto")
    
    # Expense details table
    expense_data = [
        ['Información', 'Detalle'],
        ['Concepto', expense.expense_concept],
        ['Registrado por', expense.user.get_full_name() or expense.user.username],
        ['Fecha del gasto', expense.expense_date.strftime('%d/%m/%Y')],
        ['Monto', f'${expense.amount:,.2f}'],
        ['Método de pago', expense.get_payment_method_display()],
    ]
    
    table = Table(expense_data, colWidths=[200, 250])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.Color(0.95, 0.95, 0.95)),
        ('TEXTCOLOR', (0, 1), (-1, -1), text_color),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('CELLPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    table.wrapOn(c, width, height)
    y_position = height - 280
    table.drawOn(c, margin, y_position)

    # Comments section
    y_position -= 40
    if expense.comments:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y_position, "Comentarios:")
        c.setFont("Helvetica", 10)
        y_position -= 20
        
        # Handle multiline comments
        for line in expense.comments.split('\n'):
            c.drawString(margin + 20, y_position, line)
            y_position -= 20

    # Image section
    if expense.proof_of_expense:
        y_position -= 30
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y_position, "Comprobante Adjunto:")
        
        # Define image container position
        image_y = y_position - image_container_height - 10
        
        # Add frame for image container
        c.setStrokeColor(colors.lightgrey)
        c.rect(margin, image_y, image_container_width, image_container_height)
        
        # Add image
        add_image_to_report(
            c, 
            expense.proof_of_expense.path,
            margin,
            image_y,
            image_container_width,
            image_container_height
        )

    # Footer
    c.setFont("Helvetica", 8)
    c.setFillColor(secondary_color)
    footer_text = f"© {datetime.now().year} Torres del Maurel - Este documento es un comprobante oficial de gasto"
    c.drawString(margin, 30, footer_text)
    c.drawString(width - 150, 30, "Página 1 de 1")

    c.save()
    return os.path.join('documents', filename)


### Email confimation for both users and admin when payment is received
def send_payment_confirmation_emails(payment):
    """
    Send payment confirmation emails to both the user and admin with the proof of payment attached.
    """
    try:
        context = {
            'user': payment.user,
            'payment': payment,
        }

        # Prepare the attachment
        if payment.report_file:
            file_path = payment.report_file.path
            file_name = os.path.basename(payment.report_file.name)
        
        # Send confirmation to user
        user_subject = "Confirmación de Pago - Torres del Maurel"
        user_message = render_to_string('payment_confirmation_email.html', context)
        
        user_email = EmailMessage(
            subject=user_subject,
            body=user_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[payment.user.email]
        )
        
        if payment.report_file:
            user_email.attach_file(file_path, mimetype='application/pdf')
        
        user_email.send(fail_silently=False)

        # Send notification to admin users
        admin_users = get_user_model().objects.filter(is_superuser=True)
        if admin_users.exists():
            admin_subject = f"Nuevo Pago Registrado - Departamento {payment.user.apartment_number}"
            admin_message = render_to_string('payment_admin_notification_email.html', context)
            
            admin_emails = list(admin_users.values_list('email', flat=True))
            
            admin_email = EmailMessage(
                subject=admin_subject,
                body=admin_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=admin_emails
            )
            
            if payment.report_file:
                admin_email.attach_file(file_path, mimetype='application/pdf')
            
            admin_email.send(fail_silently=False)
            
        return True
    except Exception as e:
        # Log the error but don't prevent the payment from being processed
        print(f"Error sending payment confirmation emails: {str(e)}")
        return False