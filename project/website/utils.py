# utils.py

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer, SimpleDocTemplate, PageBreak
from reportlab.lib.units import inch, mm, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
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


### Enhanced Professional PDF Design Functions

# Professional Color Scheme
BRAND_BLUE = colors.HexColor('#4a90e2')
BRAND_BLUE_DARK = colors.HexColor('#357abd')
BRAND_BLUE_LIGHT = colors.HexColor('#e8f4fd')
DARK_GRAY = colors.HexColor('#2a2a2a')
LIGHT_GRAY = colors.HexColor('#f8f9fa')
MEDIUM_GRAY = colors.HexColor('#6c757d')
WHITE = colors.white
BLACK = colors.black

def create_minimalist_table(data, col_widths, header_color=BRAND_BLUE):
    """
    Create a minimalist table with clean styling
    """
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        # Header row styling
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Data rows styling
        ('BACKGROUND', (0, 1), (-1, -1), WHITE),
        ('TEXTCOLOR', (0, 1), (-1, -1), DARK_GRAY),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        
        # Grid and borders
        ('GRID', (0, 0), (-1, -1), 0.5, MEDIUM_GRAY),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, WHITE),
        
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    return table

def calculate_image_dimensions(img, width, height):
    """
    Calculate optimal image dimensions for a fixed area while maintaining aspect ratio.
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

def generate_payment_report(payment, filename):
    """
    Generate enhanced minimalist payment report - COMPLETELY REDESIGNED
    """
    report_path = os.path.join(settings.MEDIA_ROOT, 'documents', filename)
    c = canvas.Canvas(report_path, pagesize=letter)
    width, height = letter

    # Logo path
    logo_path = os.path.join(settings.STATIC_ROOT or settings.BASE_DIR, 'website', 'static', 'images', 'Maurel.png')
    if not os.path.exists(logo_path):
        logo_path = os.path.join(settings.BASE_DIR, 'website', 'static', 'images', 'Maurel.png')

    # Clean blue header like monthly report
    c.setFillColor(BRAND_BLUE)
    c.rect(0, height - 50, width, 80, fill=True, stroke=False)
    
    # Company name in header (centered)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 14)
    company_text = "TORRES DEL MAUREL - 121"
    company_width = c.stringWidth(company_text, "Helvetica-Bold", 14)
    c.drawString((width - company_width) / 2, height - 35, company_text)
    
    # Document title and reference (like monthly report style)
    c.setFillColor(DARK_GRAY)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 85, "COMPROBANTE DE PAGO")
    
    c.setFont("Helvetica", 10)
    c.drawRightString(width - 50, height - 77, f"Referencia: PAG-{payment.id:06d}")
    c.drawRightString(width - 50, height - 91, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    # Format date in Spanish
    months_spanish = {
        'January': 'enero', 'February': 'febrero', 'March': 'marzo', 'April': 'abril',
        'May': 'mayo', 'June': 'junio', 'July': 'julio', 'August': 'agosto',
        'September': 'septiembre', 'October': 'octubre', 'November': 'noviembre', 'December': 'diciembre'
    }
    
    payment_date_spanish = payment.payment_date.strftime('%d de %B de %Y')
    for eng, esp in months_spanish.items():
        payment_date_spanish = payment_date_spanish.replace(eng, esp)
    
    # Main content starts here
    content_start_y = height - 160
    
    # Payment details table - FIXED POSITIONING
    payment_data = [
        ['CAMPO', 'INFORMACIÓN'],
        ['Departamento', str(payment.user.apartment_number)],
        ['Residente', payment.user.get_full_name() or payment.user.username],
        ['Fecha de Pago', payment_date_spanish],
        ['Monto Pagado', f'${payment.amount_paid:,.2f} MXN'],
        ['Método de Pago', payment.get_payment_method_display()],
        ['Estado del Pago', 'PAGADO ✓'],
    ]
    
    table = create_minimalist_table(payment_data, [150, 360])
    table.wrapOn(c, width, height)
    table_y = height - 330
    table.drawOn(c, 50, table_y)
    
    # Comments section
    comments_y = table_y - 30
    if payment.comments:
        c.setFillColor(BRAND_BLUE)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, comments_y, "COMENTARIOS ADICIONALES")
        
        # Comments box
        c.setFillColor(LIGHT_GRAY)
        c.setStrokeColor(MEDIUM_GRAY)
        c.setLineWidth(0.5)
        c.rect(50, comments_y - 50, width - 100, 40, fill=True, stroke=True)
        
        c.setFillColor(DARK_GRAY)
        c.setFont("Helvetica", 10)
        
        # Handle comments text
        lines = payment.comments.split('\n')
        y_offset = comments_y - 25
        for line in lines[:2]:
            if line.strip():
                c.drawString(60, y_offset, line[:70])
                y_offset -= 15
        
        comments_y -= 70
    
    # Image section - COMPLETELY FIXED
    if payment.proof_of_payment:
        image_y = comments_y - 300
        if image_y < 100:  # Ensure it doesn't go too low
            image_y = 100
            
        c.setFillColor(BRAND_BLUE)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 435, "COMPROBANTE DE PAGO ADJUNTO")
        
        # Image container
        image_container_width = width - 100
        image_container_height = 250
        
        try:
            # Ensure file exists and is accessible
            if os.path.exists(payment.proof_of_payment.path):
                img = Image.open(payment.proof_of_payment.path)
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                
                # Calculate dimensions
                padding = 15
                available_width = image_container_width - (2 * padding)
                available_height = image_container_height - (2 * padding)
                
                new_width, new_height, x_offset = calculate_image_dimensions(
                    img, available_width, available_height
                )
                
                # Draw container
                c.setFillColor(WHITE)
                c.setStrokeColor(MEDIUM_GRAY)
                c.setLineWidth(1)
                c.rect(50, image_y, image_container_width, image_container_height, fill=True, stroke=True)
                
                # Process and draw image
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG', quality=95)
                img_buffer.seek(0)
                
                # Center image in container
                center_x = 50 + padding + x_offset
                center_y = image_y + (image_container_height - new_height) / 2
                
                c.drawImage(
                    ImageReader(img_buffer),
                    center_x,
                    center_y,
                    width=new_width,
                    height=new_height
                )
            else:
                # File doesn't exist - show error message
                c.setFillColor(LIGHT_GRAY)
                c.rect(50, image_y, image_container_width, image_container_height, fill=True, stroke=True)
                c.setFillColor(DARK_GRAY)
                c.setFont("Helvetica", 11)
                error_text = "Archivo de imagen no encontrado"
                text_width = c.stringWidth(error_text, "Helvetica", 11)
                c.drawString(50 + (image_container_width - text_width) / 2, 
                           image_y + image_container_height / 2, error_text)
                
        except Exception as e:
            print(f"Error processing payment image: {str(e)}")
            # Show error in PDF
            c.setFillColor(LIGHT_GRAY)
            c.rect(50, image_y, image_container_width, image_container_height, fill=True, stroke=True)
            c.setFillColor(DARK_GRAY)
            c.setFont("Helvetica", 11)
            error_text = f"Error al cargar imagen: {str(e)[:50]}"
            text_width = c.stringWidth(error_text, "Helvetica", 11)
            c.drawString(50 + (image_container_width - text_width) / 2, 
                       image_y + image_container_height / 2, error_text)
    
    # Footer like monthly report
    c.setFillColor(DARK_GRAY)
    c.rect(0, 0, width, 50, fill=True, stroke=False)
    
    c.setFillColor(WHITE)
    c.setFont("Helvetica", 8)
    c.drawString(50, 30, "Torres del Maurel - Administración Residencial")
    c.drawString(50, 15, f"© {datetime.now().year} - Documento Oficial")
    
    c.setFont("Helvetica-Bold", 8)
    c.setFont("Helvetica", 8)
    c.drawRightString(width - 50, 15, f"Página 1 de 1")
    
    # Document verification ID
    c.setFillColor(BRAND_BLUE)
    c.setFont("Helvetica", 8)
    c.drawRightString(width - 50, height - 64, f"Documento verificable con ID: PAG-{payment.id:06d}")
    
    c.save()
    return os.path.join('documents', filename)


def generate_expense_report(expense, filename):
    """
    Generate enhanced minimalist expense report - COMPLETELY REDESIGNED
    """
    report_path = os.path.join(settings.MEDIA_ROOT, 'documents', filename)
    c = canvas.Canvas(report_path, pagesize=letter)
    width, height = letter

    # Logo path
    logo_path = os.path.join(settings.STATIC_ROOT or settings.BASE_DIR, 'website', 'static', 'images', 'Maurel.png')
    if not os.path.exists(logo_path):
        logo_path = os.path.join(settings.BASE_DIR, 'website', 'static', 'images', 'Maurel.png')

    # Clean blue header like monthly report
    c.setFillColor(BRAND_BLUE)
    c.rect(0, height - 50, width, 80, fill=True, stroke=False)
    
    # Company name in header (centered)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 14)
    company_text = "TORRES DEL MAUREL - 121"
    company_width = c.stringWidth(company_text, "Helvetica-Bold", 14)
    c.drawString((width - company_width) / 2, height - 35, company_text)
    
    # Document title and reference (like monthly report style)
    c.setFillColor(DARK_GRAY)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 85, "COMPROBANTE DE GASTO")
    
    c.setFont("Helvetica", 10)
    c.drawRightString(width - 50, height - 77, f"Referencia: GAS-{expense.id:06d}")
    c.drawRightString(width - 50, height - 91, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    # Format date in Spanish
    months_spanish = {
        'January': 'enero', 'February': 'febrero', 'March': 'marzo', 'April': 'abril',
        'May': 'mayo', 'June': 'junio', 'July': 'julio', 'August': 'agosto',
        'September': 'septiembre', 'October': 'octubre', 'November': 'noviembre', 'December': 'diciembre'
    }
    
    expense_date_spanish = expense.expense_date.strftime('%d de %B de %Y')
    for eng, esp in months_spanish.items():
        expense_date_spanish = expense_date_spanish.replace(eng, esp)
    
    # Main content starts here
    content_start_y = height - 160
    
    # Section title
    c.setFillColor(BRAND_BLUE)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, content_start_y, "INFORMACIÓN DEL GASTO")
    
    # Expense details table - FIXED POSITIONING
    expense_data = [
        ['CAMPO', 'INFORMACIÓN'],
        ['Concepto del Gasto', expense.expense_concept],
        ['Registrado por', expense.user.get_full_name() or expense.user.username],
        ['Fecha del Gasto', expense_date_spanish],
        ['Monto del Gasto', f'${expense.amount:,.2f} MXN'],
        ['Método de Pago', expense.get_payment_method_display()],
        ['Estado del Registro', 'REGISTRADO ✓'],
    ]
    
    table = create_minimalist_table(expense_data, [150, 350])
    table.wrapOn(c, width, height)
    table_y = height - 330
    table.drawOn(c, 50, table_y)
    
    # Comments section
    comments_y = table_y - 30
    if expense.comments:
        c.setFillColor(BRAND_BLUE)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, comments_y, "COMENTARIOS ADICIONALES")
        
        # Comments box
        c.setFillColor(LIGHT_GRAY)
        c.setStrokeColor(MEDIUM_GRAY)
        c.setLineWidth(0.5)
        c.rect(50, comments_y - 50, width - 100, 40, fill=True, stroke=True)
        
        c.setFillColor(DARK_GRAY)
        c.setFont("Helvetica", 10)
        
        # Handle comments text
        lines = expense.comments.split('\n')
        y_offset = comments_y - 25
        for line in lines[:2]:
            if line.strip():
                c.drawString(60, y_offset, line[:70])
                y_offset -= 15
        
        comments_y -= 70
    
    # Image section - COMPLETELY FIXED
    if expense.proof_of_expense:
        image_y = comments_y - 300
        if image_y < 100:  # Ensure it doesn't go too low
            image_y = 100
            
        c.setFillColor(BRAND_BLUE)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 435, "COMPROBANTE DE GASTO ADJUNTO")
        
        # Image container
        image_container_width = width - 100
        image_container_height = 250
        
        try:
            # Ensure file exists and is accessible
            if os.path.exists(expense.proof_of_expense.path):
                img = Image.open(expense.proof_of_expense.path)
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                
                # Calculate dimensions
                padding = 15
                available_width = image_container_width - (2 * padding)
                available_height = image_container_height - (2 * padding)
                
                new_width, new_height, x_offset = calculate_image_dimensions(
                    img, available_width, available_height
                )
                
                # Draw container
                c.setFillColor(WHITE)
                c.setStrokeColor(MEDIUM_GRAY)
                c.setLineWidth(1)
                c.rect(50, image_y, image_container_width, image_container_height, fill=True, stroke=True)
                
                # Process and draw image
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG', quality=95)
                img_buffer.seek(0)
                
                # Center image in container
                center_x = 50 + padding + x_offset
                center_y = image_y + (image_container_height - new_height) / 2
                
                c.drawImage(
                    ImageReader(img_buffer),
                    center_x,
                    center_y,
                    width=new_width,
                    height=new_height
                )
            else:
                # File doesn't exist - show error message
                c.setFillColor(LIGHT_GRAY)
                c.rect(50, image_y, image_container_width, image_container_height, fill=True, stroke=True)
                c.setFillColor(DARK_GRAY)
                c.setFont("Helvetica", 11)
                error_text = "Archivo de imagen no encontrado"
                text_width = c.stringWidth(error_text, "Helvetica", 11)
                c.drawString(50 + (image_container_width - text_width) / 2, 
                           image_y + image_container_height / 2, error_text)
                
        except Exception as e:
            print(f"Error processing expense image: {str(e)}")
            # Show error in PDF
            c.setFillColor(LIGHT_GRAY)
            c.rect(50, image_y, image_container_width, image_container_height, fill=True, stroke=True)
            c.setFillColor(DARK_GRAY)
            c.setFont("Helvetica", 11)
            error_text = f"Error al cargar imagen: {str(e)[:50]}"
            text_width = c.stringWidth(error_text, "Helvetica", 11)
            c.drawString(50 + (image_container_width - text_width) / 2, 
                       image_y + image_container_height / 2, error_text)
    
    # Footer like monthly report
    c.setFillColor(DARK_GRAY)
    c.rect(0, 0, width, 50, fill=True, stroke=False)
    
    c.setFillColor(WHITE)
    c.setFont("Helvetica", 8)
    c.drawString(50, 30, "Torres del Maurel - Administración Residencial")
    c.drawString(50, 15, f"© {datetime.now().year} - Documento Oficial")
    
    c.setFont("Helvetica-Bold", 8)
    c.setFont("Helvetica", 8)
    c.drawRightString(width - 50, 15, f"Página 1 de 1")
    
    # Document verification ID - FIXED PARENTHESIS
    c.setFillColor(BRAND_BLUE)
    c.setFont("Helvetica", 8)
    c.drawRightString(width - 50, height - 64, f"Documento verificable con ID: GAS-{expense.id:06d}")
    
    c.save()
    return os.path.join('documents', filename)


### Email confirmation functions (unchanged)
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


# Add this function to your utils.py file, right after the generate_expense_report function

def generate_qys_report(qys, filename):
    """
    Generate enhanced minimalist QYS report - MATCHING PAYMENT/EXPENSE STYLE
    """
    report_path = os.path.join(settings.MEDIA_ROOT, 'documents', filename)
    c = canvas.Canvas(report_path, pagesize=letter)
    width, height = letter

    # Logo path
    logo_path = os.path.join(settings.STATIC_ROOT or settings.BASE_DIR, 'website', 'static', 'images', 'Maurel.png')
    if not os.path.exists(logo_path):
        logo_path = os.path.join(settings.BASE_DIR, 'website', 'static', 'images', 'Maurel.png')

    # Clean blue header like monthly report
    c.setFillColor(BRAND_BLUE)
    c.rect(0, height - 50, width, 80, fill=True, stroke=False)
    
    # Company name in header (centered)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 14)
    company_text = "TORRES DEL MAUREL - 121"
    company_width = c.stringWidth(company_text, "Helvetica-Bold", 14)
    c.drawString((width - company_width) / 2, height - 35, company_text)
    
    # Document title and reference (like monthly report style)
    c.setFillColor(DARK_GRAY)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 85, "REPORTE DE COMUNICACIÓN")
    
    c.setFont("Helvetica", 10)
    c.drawRightString(width - 50, height - 77, f"Referencia: QYS-{qys.id:06d}")
    c.drawRightString(width - 50, height - 91, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    # Format date in Spanish
    months_spanish = {
        'January': 'enero', 'February': 'febrero', 'March': 'marzo', 'April': 'abril',
        'May': 'mayo', 'June': 'junio', 'July': 'julio', 'August': 'agosto',
        'September': 'septiembre', 'October': 'octubre', 'November': 'noviembre', 'December': 'diciembre'
    }
    
    created_date_spanish = qys.created_at.strftime('%d de %B de %Y')
    for eng, esp in months_spanish.items():
        created_date_spanish = created_date_spanish.replace(eng, esp)
    
    # Main content starts here
    content_start_y = height - 160
    
    # QYS details table - MATCHING PAYMENT/EXPENSE STYLE
    qys_data = [
        ['CAMPO', 'INFORMACIÓN'],
        ['Tipo de Reporte', qys.get_type_display()],
        ['Categoría', qys.get_category_display()],
        ['Departamento', str(qys.apartment_number)],
        ['Fecha de Creación', created_date_spanish],
        ['Estado Actual', qys.get_status_display()],
    ]
    
    # Add attended date if available
    if qys.attended_at:
        attended_date_spanish = qys.attended_at.strftime('%d de %B de %Y')
        for eng, esp in months_spanish.items():
            attended_date_spanish = attended_date_spanish.replace(eng, esp)
        qys_data.append(['Fecha de Atención', attended_date_spanish])
    
    table = create_minimalist_table(qys_data, [150, 360])
    table.wrapOn(c, width, height)
    table_y = height - 330
    table.drawOn(c, 50, table_y)
    
    # Description section
    description_y = table_y - 50
    c.setFillColor(BRAND_BLUE)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, description_y + 10, "DESCRIPCIÓN DETALLADA")
    
    # Description box
    c.setFillColor(LIGHT_GRAY)
    c.setStrokeColor(MEDIUM_GRAY)
    c.setLineWidth(0.5)
    description_box_height = 80
    c.rect(50, description_y - description_box_height, width - 100, description_box_height, fill=True, stroke=True)
    
    c.setFillColor(DARK_GRAY)
    c.setFont("Helvetica", 10)
    
    # Handle description text with word wrapping
    description_lines = []
    words = qys.description.split()
    current_line = ""
    max_width = width - 120  # Account for padding
    
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if c.stringWidth(test_line, "Helvetica", 10) <= max_width:
            current_line = test_line
        else:
            if current_line:
                description_lines.append(current_line)
            current_line = word
    
    if current_line:
        description_lines.append(current_line)
    
    # Draw description lines
    y_offset = description_y - 20
    for i, line in enumerate(description_lines[:4]):  # Max 4 lines
        if y_offset > description_y - description_box_height + 10:
            c.drawString(60, y_offset, line)
            y_offset -= 15
        else:
            # Add ellipsis if text is too long
            if i < len(description_lines) - 1:
                c.drawString(60, y_offset, line + "...")
            break
    
    description_y -= description_box_height + 20
    
    # Attachment section - COMPLETELY FIXED
    if qys.attachment:
        attachment_y = description_y - 300
        if attachment_y < 100:  # Ensure it doesn't go too low
            attachment_y = 100
            
        c.setFillColor(BRAND_BLUE)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, description_y - 20, "ARCHIVO ADJUNTO")
        
        # Attachment container
        attachment_container_width = width - 100
        attachment_container_height = 250
        
        try:
            # Check if attachment exists and is accessible
            if os.path.exists(qys.attachment.path):
                # Try to open as image first
                try:
                    img = Image.open(qys.attachment.path)
                    if img.mode not in ('RGB', 'L'):
                        img = img.convert('RGB')
                    
                    # Calculate dimensions
                    padding = 15
                    available_width = attachment_container_width - (2 * padding)
                    available_height = attachment_container_height - (2 * padding)
                    
                    new_width, new_height, x_offset = calculate_image_dimensions(
                        img, available_width, available_height
                    )
                    
                    # Draw container
                    c.setFillColor(WHITE)
                    c.setStrokeColor(MEDIUM_GRAY)
                    c.setLineWidth(1)
                    c.rect(50, attachment_y, attachment_container_width, attachment_container_height, fill=True, stroke=True)
                    
                    # Process and draw image
                    img_buffer = io.BytesIO()
                    img.save(img_buffer, format='PNG', quality=95)
                    img_buffer.seek(0)
                    
                    # Center image in container
                    center_x = 50 + padding + x_offset
                    center_y = attachment_y + (attachment_container_height - new_height) / 2
                    
                    c.drawImage(
                        ImageReader(img_buffer),
                        center_x,
                        center_y,
                        width=new_width,
                        height=new_height
                    )
                    
                except Exception as img_error:
                    # Not an image or can't process as image - show file info
                    c.setFillColor(WHITE)
                    c.setStrokeColor(MEDIUM_GRAY)
                    c.setLineWidth(1)
                    c.rect(50, attachment_y, attachment_container_width, attachment_container_height, fill=True, stroke=True)
                    
                    c.setFillColor(DARK_GRAY)
                    c.setFont("Helvetica-Bold", 12)
                    file_icon_text = "📄"
                    c.drawString(50 + attachment_container_width // 2 - 10, 
                               attachment_y + attachment_container_height // 2 + 20, file_icon_text)
                    
                    c.setFont("Helvetica", 11)
                    filename = os.path.basename(qys.attachment.name)
                    if len(filename) > 40:
                        filename = filename[:37] + "..."
                    
                    filename_width = c.stringWidth(filename, "Helvetica", 11)
                    c.drawString(50 + (attachment_container_width - filename_width) // 2, 
                               attachment_y + attachment_container_height // 2, filename)
                    
                    # File type and size info
                    try:
                        file_size = os.path.getsize(qys.attachment.path)
                        if file_size < 1024:
                            size_text = f"{file_size} bytes"
                        elif file_size < 1024 * 1024:
                            size_text = f"{file_size / 1024:.1f} KB"
                        else:
                            size_text = f"{file_size / (1024 * 1024):.1f} MB"
                        
                        c.setFont("Helvetica", 9)
                        size_width = c.stringWidth(size_text, "Helvetica", 9)
                        c.drawString(50 + (attachment_container_width - size_width) // 2, 
                                   attachment_y + attachment_container_height // 2 - 20, size_text)
                    except:
                        pass
                        
            else:
                # File doesn't exist - show error message
                c.setFillColor(LIGHT_GRAY)
                c.rect(50, attachment_y, attachment_container_width, attachment_container_height, fill=True, stroke=True)
                c.setFillColor(DARK_GRAY)
                c.setFont("Helvetica", 11)
                error_text = "Archivo adjunto no encontrado"
                text_width = c.stringWidth(error_text, "Helvetica", 11)
                c.drawString(50 + (attachment_container_width - text_width) / 2, 
                           attachment_y + attachment_container_height / 2, error_text)
                
        except Exception as e:
            print(f"Error processing QYS attachment: {str(e)}")
            # Show error in PDF
            c.setFillColor(LIGHT_GRAY)
            c.rect(50, attachment_y, attachment_container_width, attachment_container_height, fill=True, stroke=True)
            c.setFillColor(DARK_GRAY)
            c.setFont("Helvetica", 11)
            error_text = f"Error al cargar adjunto: {str(e)[:50]}"
            text_width = c.stringWidth(error_text, "Helvetica", 11)
            c.drawString(50 + (attachment_container_width - text_width) / 2, 
                       attachment_y + attachment_container_height / 2, error_text)
    else:
        # No attachment
        c.setFillColor(BRAND_BLUE)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, description_y - 20, "ARCHIVO ADJUNTO")
        
        c.setFillColor(LIGHT_GRAY)
        c.setStrokeColor(MEDIUM_GRAY)
        c.setLineWidth(0.5)
        c.rect(50, description_y - 70, width - 100, 40, fill=True, stroke=True)
        
        c.setFillColor(DARK_GRAY)
        c.setFont("Helvetica", 10)
        no_attachment_text = "Sin archivo adjunto"
        text_width = c.stringWidth(no_attachment_text, "Helvetica", 10)
        c.drawString(50 + (width - 100 - text_width) / 2, description_y - 45, no_attachment_text)
    
    # Footer like monthly report
    c.setFillColor(DARK_GRAY)
    c.rect(0, 0, width, 50, fill=True, stroke=False)
    
    c.setFillColor(WHITE)
    c.setFont("Helvetica", 8)
    c.drawString(50, 30, "Torres del Maurel - Administración Residencial")
    c.drawString(50, 15, f"© {datetime.now().year} - Documento Oficial")
    
    c.setFont("Helvetica-Bold", 8)
    c.setFont("Helvetica", 8)
    c.drawRightString(width - 50, 15, f"Página 1 de 1")
    
    # Document verification ID
    c.setFillColor(BRAND_BLUE)
    c.setFont("Helvetica", 8)
    c.drawRightString(width - 50, height - 64, f"Documento verificable con ID: QYS-{qys.id:06d}")
    
    c.save()
    return os.path.join('documents', filename)


def send_qys_notification_emails(qys):
    """
    Send QyS notification emails to admin users with PDF report attached - PYTHONANYWHERE COMPATIBLE VERSION
    Following the same pattern as payment and expense reports with enhanced error handling
    """
    try:
        print(f"DEBUG: Starting QYS email notification for ID: {qys.id}")
        
        # Check if email is properly configured
        if not hasattr(settings, 'EMAIL_HOST') or not settings.EMAIL_HOST:
            print("WARNING: Email not configured - EMAIL_HOST missing")
            return False
        
        if not hasattr(settings, 'DEFAULT_FROM_EMAIL') or not settings.DEFAULT_FROM_EMAIL:
            print("WARNING: Email not configured - DEFAULT_FROM_EMAIL missing")
            return False
        
        context = {
            'qys': qys,
        }

        # Generate the PDF report if it doesn't exist yet
        if not hasattr(qys, 'report_file_path') or not qys.report_file_path:
            try:
                qys_type = qys.get_type_display().replace(' ', '_')
                qys_category = qys.get_category_display().replace(' ', '_')
                created_date = qys.created_at.strftime('%d-%m-%Y')
                report_filename = f"QYS_{qys_type}_{qys_category}_Apto{qys.apartment_number}_{created_date}_{qys.id}.pdf"
                
                print(f"DEBUG: Generating QYS PDF for email: {report_filename}")
                report_path = generate_qys_report(qys, report_filename)
                qys.report_file_path = report_path
                print(f"DEBUG: QYS PDF generated: {report_path}")
            except Exception as e:
                print(f"ERROR: Failed to generate PDF report: {str(e)}")
                # Continue without PDF attachment
                qys.report_file_path = None

        # Get admin users
        admin_users = get_user_model().objects.filter(is_superuser=True)
        print(f"DEBUG: Found {admin_users.count()} admin users")
        
        if not admin_users.exists():
            print("WARNING: No admin users found to send notification")
            return True  # Not really an error if no admins exist
        
        admin_subject = f"Nueva {qys.get_type_display()} - Departamento {qys.apartment_number}"
        print(f"DEBUG: Email subject: {admin_subject}")
        
        # Render email content with error handling
        try:
            admin_message_html = render_to_string('qys_admin_notification_email.html', context)
            print("DEBUG: Email template rendered successfully")
        except Exception as e:
            print(f"ERROR: Failed to render email template: {str(e)}")
            # Fallback to simple HTML message
            admin_message_html = f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #4a90e2;">Nueva {qys.get_type_display()} Registrada</h2>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #4a90e2; margin: 20px 0;">
                        <strong>Se ha registrado una nueva {qys.get_type_display().lower()} en el sistema que requiere su atención.</strong>
                    </div>
                    
                    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                        <tr style="border-bottom: 1px solid #dee2e6;">
                            <td style="padding: 10px; font-weight: bold; color: #495057;">Usuario:</td>
                            <td style="padding: 10px; color: #6c757d;">{qys.user.get_full_name() or qys.user.username}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #dee2e6;">
                            <td style="padding: 10px; font-weight: bold; color: #495057;">Departamento:</td>
                            <td style="padding: 10px; color: #6c757d;">{qys.apartment_number}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #dee2e6;">
                            <td style="padding: 10px; font-weight: bold; color: #495057;">Tipo:</td>
                            <td style="padding: 10px; color: #6c757d;">{qys.get_type_display()}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #dee2e6;">
                            <td style="padding: 10px; font-weight: bold; color: #495057;">Categoría:</td>
                            <td style="padding: 10px; color: #6c757d;">{qys.get_category_display()}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #dee2e6;">
                            <td style="padding: 10px; font-weight: bold; color: #495057;">Fecha:</td>
                            <td style="padding: 10px; color: #6c757d;">{qys.created_at.strftime('%d/%m/%Y %H:%M')} hrs</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #dee2e6;">
                            <td style="padding: 10px; font-weight: bold; color: #495057;">Estado:</td>
                            <td style="padding: 10px; color: #6c757d;">{qys.get_status_display()}</td>
                        </tr>
                    </table>
                    
                    <div style="background-color: #f7fafc; padding: 15px; border: 1px solid #e2e8f0; margin: 20px 0;">
                        <strong>Descripción:</strong>
                        <p style="margin: 10px 0 0 0; line-height: 1.6;">{qys.description}</p>
                    </div>
                    
                    {f'<div style="background-color: #e8f4fd; padding: 15px; border: 1px solid #4a90e2; margin: 20px 0;"><strong>Archivo Adjunto:</strong> Se ha incluido un archivo con esta {qys.get_type_display().lower()}.</div>' if qys.attachment else ''}
                    
                    <div style="background-color: #e8f4fd; padding: 15px; border: 1px solid #4a90e2; margin: 20px 0;">
                        <strong>Reporte PDF:</strong> Se ha adjuntado el reporte completo en formato PDF.
                    </div>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; text-align: center; color: #6c757d; font-size: 12px;">
                        <p><strong>TORRES DEL MAUREL</strong><br>
                        Sistema de Gestión de Comunicaciones<br>
                        Este es un correo automático generado por el sistema</p>
                    </div>
                </div>
            </body>
            </html>
            """
        
        admin_emails = list(admin_users.values_list('email', flat=True))
        print(f"DEBUG: Admin emails: {admin_emails}")
        
        # Filter out empty emails
        admin_emails = [email for email in admin_emails if email and email.strip()]
        if not admin_emails:
            print("WARNING: No valid admin email addresses found")
            return False
        
        # Create plain text version as fallback
        plain_text_message = f"""
Nueva {qys.get_type_display()} Registrada - Torres del Maurel

DETALLES:
- Usuario: {qys.user.get_full_name() or qys.user.username}
- Departamento: {qys.apartment_number}
- Tipo: {qys.get_type_display()}
- Categoría: {qys.get_category_display()}
- Fecha: {qys.created_at.strftime('%d/%m/%Y %H:%M')} hrs
- Estado: {qys.get_status_display()}

DESCRIPCIÓN:
{qys.description}

{f'ARCHIVO ADJUNTO: {qys.attachment.name}' if qys.attachment else 'Sin archivos adjuntos.'}

Se ha adjuntado el reporte PDF completo.

---
Este es un correo automático de Torres del Maurel.
No responda directamente a esta dirección de correo.
        """
        
        # Try to send email with enhanced error handling
        try:
            # Import here to avoid circular imports
            from django.core.mail import EmailMultiAlternatives
            
            # Create email message with both text and HTML versions
            admin_email = EmailMultiAlternatives(
                subject=admin_subject,
                body=plain_text_message,  # Plain text version
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=admin_emails
            )
            
            # Attach HTML version
            admin_email.attach_alternative(admin_message_html, "text/html")
            
            # Add QYS attachment if exists (original user attachment)
            attachment_added = False
            if qys.attachment:
                try:
                    if hasattr(qys.attachment, 'path') and os.path.exists(qys.attachment.path):
                        admin_email.attach_file(qys.attachment.path)
                        attachment_added = True
                        print(f"DEBUG: Original attachment added: {qys.attachment.name}")
                    else:
                        print(f"WARNING: Original attachment file does not exist or path not available")
                except Exception as e:
                    print(f"ERROR: Failed to attach original file: {str(e)}")
            
            # Add PDF report attachment (MAIN FEATURE - following payment/expense pattern)
            pdf_attached = False
            if hasattr(qys, 'report_file_path') and qys.report_file_path:
                try:
                    pdf_path = os.path.join(settings.MEDIA_ROOT, qys.report_file_path)
                    if os.path.exists(pdf_path):
                        with open(pdf_path, 'rb') as pdf_file:
                            admin_email.attach(
                                f"Reporte_QYS_{qys.id}.pdf", 
                                pdf_file.read(), 
                                'application/pdf'
                            )
                        pdf_attached = True
                        print(f"DEBUG: PDF report attached: {qys.report_file_path}")
                    else:
                        print(f"WARNING: PDF report file does not exist: {pdf_path}")
                except Exception as e:
                    print(f"ERROR: Failed to attach PDF report: {str(e)}")
            
            # Send email with connection error handling
            try:
                result = admin_email.send(fail_silently=False)
                print(f"DEBUG: Email send result: {result}")
                
                if result == 1:
                    print("SUCCESS: QYS notification email sent successfully")
                    print(f"DEBUG: Attachments included - Original: {attachment_added}, PDF: {pdf_attached}")
                    return True
                else:
                    print("ERROR: Email send returned 0 (failed)")
                    return False
                    
            except Exception as e:
                print(f"ERROR: Failed to send email: {str(e)}")
                error_msg = str(e).lower()
                
                # Provide specific error guidance for common PythonAnywhere issues
                if "authentication" in error_msg or "login" in error_msg:
                    print("ERROR: Email authentication failed")
                    print("SOLUTION: Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in settings")
                elif "connection" in error_msg or "refused" in error_msg:
                    print("ERROR: Email connection failed")
                    print("SOLUTION: Check EMAIL_HOST and EMAIL_PORT settings")
                    print("NOTE: PythonAnywhere free accounts have email restrictions")
                elif "timeout" in error_msg:
                    print("ERROR: Email timeout")
                    print("SOLUTION: Check EMAIL_TIMEOUT setting or try a different SMTP server")
                elif "ssl" in error_msg or "tls" in error_msg:
                    print("ERROR: SSL/TLS configuration issue")
                    print("SOLUTION: Check EMAIL_USE_TLS and EMAIL_USE_SSL settings")
                elif "quota" in error_msg or "limit" in error_msg:
                    print("ERROR: Email quota or rate limit exceeded")
                    print("SOLUTION: Wait before sending more emails or upgrade PythonAnywhere account")
                else:
                    print(f"ERROR: Unexpected email error: {str(e)}")
                
                return False
                
        except ImportError as e:
            print(f"ERROR: Failed to import email modules: {str(e)}")
            return False
        except Exception as e:
            print(f"ERROR: Unexpected error in email preparation: {str(e)}")
            return False
            
    except Exception as e:
        print(f"CRITICAL ERROR in QYS email notification: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False