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


def send_qys_notification_emails(qys):
    """
    Send QyS notification emails to admin users.
    """
    try:
        context = {
            'qys': qys,
        }

        # Send notification to admin users
        admin_users = get_user_model().objects.filter(is_superuser=True)
        if admin_users.exists():
            admin_subject = f"Nueva {qys.get_type_display()} - Departamento {qys.apartment_number}"
            admin_message = render_to_string('qys_admin_notification_email.html', context)
            
            admin_emails = list(admin_users.values_list('email', flat=True))
            
            admin_email = EmailMessage(
                subject=admin_subject,
                body=admin_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=admin_emails
            )
            
            if qys.attachment:
                admin_email.attach_file(qys.attachment.path)
            
            admin_email.send(fail_silently=False)
            
        return True
    except Exception as e:
        print(f"Error sending QyS notification emails: {str(e)}")
        return False