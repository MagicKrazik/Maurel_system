from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import CustomUser, MonthlyFees, Announcement
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UserProfileForm, SpanishPasswordChangeForm
from django.utils import timezone
from decimal import Decimal
from .forms import PaymentUploadForm
from .models import PaymentReport
from django.conf import settings
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.core.files import File
from django.core.exceptions import ValidationError
from django.db import transaction
from .utils import generate_payment_report, generate_expense_report
from datetime import datetime
from django.db.models import Sum
import json
from dateutil.relativedelta import relativedelta
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .forms import ComplaintSuggestionForm
from .models import ComplaintSuggestion
from .models import Document
from .forms import DocumentUploadForm
from django.db.models import Q
from django.core.files.storage import default_storage
import shutil
from django.core.cache import cache
from django.db import transaction
from .forms import ExpenseUploadForm
from .models import PaymentReport, ExpenseReport
from .forms import AnnouncementForm
import logging
from .utils import send_payment_confirmation_emails
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from .utils import send_qys_notification_emails

## forgot password configuration:
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils.html import strip_tags
from django.urls import reverse

from django.http import HttpResponse

from calendar import month_name
from io import BytesIO
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

logger = logging.getLogger(__name__)

def aviso_priv(request):
    return render(request, 'aviso_priv.html')

def home(request):
    return render(request, 'home.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            
            # Call move_payment_proofs function after successful login
            try:
                move_payment_proofs()
            except Exception as e:
                # Log the error, but don't prevent the user from logging in
                print(f"Error in move_payment_proofs: {e}")
            
            if user.should_change_password():
                return redirect('initial_profile_update')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


@login_required
def initial_profile_update(request):
    if not request.user.should_change_password():
        return redirect('dashboard')

    if request.method == 'POST':
        password_form = SpanishPasswordChangeForm(request.user, request.POST)
        profile_form = UserProfileForm(request.POST, instance=request.user)
        if password_form.is_valid() and profile_form.is_valid():
            user = password_form.save()
            profile_form.save()
            user.is_first_login = False
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, '¡Su perfil ha sido actualizado exitosamente!')
            return redirect('dashboard')
    else:
        password_form = SpanishPasswordChangeForm(request.user)
        profile_form = UserProfileForm(instance=request.user)
    
    return render(request, 'initial_profile_update.html', {
        'password_form': password_form,
        'profile_form': profile_form
    })


@login_required
def profile(request):
    if request.method == 'POST':
        password_form = SpanishPasswordChangeForm(request.user, request.POST)
        profile_form = UserProfileForm(request.POST, instance=request.user)
        if password_form.is_valid() and profile_form.is_valid():
            user = password_form.save()
            profile_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, '¡Su perfil ha sido actualizado exitosamente!')
            return redirect('dashboard')
    else:
        password_form = SpanishPasswordChangeForm(request.user)
        profile_form = UserProfileForm(instance=request.user)
    
    return render(request, 'profile.html', {
        'password_form': password_form,
        'profile_form': profile_form
    })


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente')
    return redirect('home')  # Redirect to the home page after logout




@login_required
def dashboard(request):
    try:
        start_date = timezone.datetime(2025, 1, 1).date()
        end_date = start_date + relativedelta(years=5, months=-1)
        current_date = timezone.now().date()

        selected_date = request.GET.get('date')
        if selected_date:
            selected_year, selected_month = map(int, selected_date.split('-'))
            selected_date = datetime(selected_year, selected_month, 1).date()
        else:
            selected_date = current_date
            selected_year, selected_month = selected_date.year, selected_date.month

        # Get active announcements first to ensure they exist
        active_announcements = Announcement.objects.filter(
            is_active=True
        ).order_by('-created_at').select_related('created_by')

        # Get debtors
        debtors = CustomUser.objects.filter(is_debtor=True)
        
        # Calculate financial data
        income_data = float(MonthlyFees.get_total_paid_amount(selected_year, selected_month))
        expenses_data = float(ExpenseReport.objects.filter(
            expense_date__year=selected_year,
            expense_date__month=selected_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0)

        # Monthly balance
        monthly_balance = income_data - expenses_data

        # Yearly data
        yearly_income_data = []
        yearly_expenses_data = []
        for month in range(1, 13):
            month_income = float(MonthlyFees.get_total_paid_amount(selected_year, month))
            month_expenses = float(ExpenseReport.objects.filter(
                expense_date__year=selected_year,
                expense_date__month=month
            ).aggregate(Sum('amount'))['amount__sum'] or 0)
            yearly_income_data.append(month_income)
            yearly_expenses_data.append(month_expenses)

        yearly_balance = sum(yearly_income_data) - sum(yearly_expenses_data)

        # Generate date range for dropdown
        date_range = []
        current = start_date
        while current <= end_date:
            date_range.append((current.year, current.month))
            current += relativedelta(months=1)

        # Base context depending on user type
        if request.user.is_staff or request.user.is_superuser:
            context = {
                'debtors': debtors,
            }
        else:
            current_fees, created = MonthlyFees.objects.get_or_create(
                user=request.user,
                month=current_date.replace(day=1)
            )
            context = {
                'current_fees': current_fees,
                'current_month': current_date,
            }

        # Update context with all data
        context.update({
            'active_announcements': active_announcements,
            'debtors': debtors,
            'income_data': income_data,
            'expenses_data': expenses_data,
            'monthly_balance': monthly_balance,
            'yearly_balance': yearly_balance,
            'yearly_income_data': json.dumps(yearly_income_data),
            'yearly_expenses_data': json.dumps(yearly_expenses_data),
            'selected_year': selected_year,
            'selected_month': selected_month,
            'selected_date': selected_date,
            'date_range': date_range,
        })

        return render(request, 'dashboard.html', context)

    except Exception as e:
        logger.error(f"Error in dashboard view: {str(e)}")
        messages.error(request, "Error al cargar el dashboard. Por favor, inténtelo de nuevo.")
        return redirect('home')


@login_required
@require_http_methods(["GET", "POST"])
def pagos(request):
    if request.method == 'POST':
        form = PaymentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.user = request.user
            payment.month = payment.payment_date.replace(day=1)
            payment.save()

            # Update MonthlyFees
            monthly_fee, created = MonthlyFees.objects.get_or_create(
                user=request.user, 
                month=payment.month
            )
            monthly_fee.paid_amount += payment.amount_paid
            if monthly_fee.paid_amount >= monthly_fee.total_fee:
                monthly_fee.is_paid = True
            monthly_fee.save()

            # Generate PDF report
            report_filename = f"{request.user.username}.{payment.month.strftime('%m.%Y')}.pdf"
            report_path = generate_payment_report(payment, report_filename)
            
            # Save the report file path to the PaymentReport instance
            payment.report_file.name = report_path
            payment.save()

            # Create a Document object for the payment report
            Document.objects.create(
                title=f"Pago de Mantenimiento - {request.user.username} - {payment.month.strftime('%B %Y')}",
                document_type='pagos_mantenimiento',
                file=payment.report_file,
                date=payment.payment_date,
                uploaded_by=request.user
            )

            # Send confirmation emails
            email_sent = send_payment_confirmation_emails(payment)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                response_data = {
                    'success': True, 
                    'message': 'Comprobante de pago subido exitosamente.'
                }
                if not email_sent:
                    response_data['warning'] = 'El pago se registró correctamente pero hubo un problema al enviar los correos de confirmación.'
                return JsonResponse(response_data)
            else:
                messages.success(request, 'Comprobante de pago subido exitosamente.')
                if not email_sent:
                    messages.warning(request, 'El pago se registró correctamente pero hubo un problema al enviar los correos de confirmación.')
                return redirect('dashboard')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
            else:
                messages.error(request, 'Error en el formulario. Por favor, corrija los errores.')
    else:
        form = PaymentUploadForm()
    
    return render(request, 'pagos.html', {'form': form})

@login_required
def qys(request):
    form = ComplaintSuggestionForm(user=request.user)
    if request.method == 'POST':
        if 'submit_qys' in request.POST:
            form = ComplaintSuggestionForm(request.POST, request.FILES, user=request.user)
            if form.is_valid():
                qys = form.save(commit=False)
                qys.user = request.user
                qys.save()

                # Send notification email
                email_sent = send_qys_notification_emails(qys)
                
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    response_data = {
                        'success': True,
                        'message': 'Su queja o sugerencia ha sido enviada exitosamente.',
                        'new_qys': {
                            'id': qys.id,
                            'type': qys.get_type_display(),
                            'category': qys.get_category_display(),
                            'apartment_number': qys.apartment_number,
                            'description': qys.description,
                            'status': qys.get_status_display(),
                            'created_at': qys.created_at.strftime('%d/%m/%Y %H:%M'),
                            'attended_at': qys.attended_at.strftime('%d/%m/%Y %H:%M') if qys.attended_at else '-',
                            'is_staff': request.user.is_staff,
                            'status_choices': qys.STATUS_CHOICES,
                        }
                    }
                    return JsonResponse(response_data)
                
                messages.success(request, 'Su queja o sugerencia ha sido enviada exitosamente.')
                return redirect('qys')
                
            elif request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
                
        elif 'update_status' in request.POST and request.user.is_staff:
            qys_id = request.POST.get('qys_id')
            new_status = request.POST.get('status')
            qys = ComplaintSuggestion.objects.get(id=qys_id)
            if new_status in dict(ComplaintSuggestion.STATUS_CHOICES):
                qys.status = new_status
                qys.save()
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Estado actualizado exitosamente.',
                    })
                messages.success(request, 'Estado actualizado exitosamente.')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'Estado inválido.',
                    })
                messages.error(request, 'Estado inválido.')
            return redirect('qys')
            
        elif 'delete_qys' in request.POST and request.user.is_staff:
            qys_id = request.POST.get('qys_id')
            return delete_qys(request, qys_id)
    
    all_qys = ComplaintSuggestion.objects.all().order_by('-created_at')
    return render(request, 'qys.html', {'form': form, 'all_qys': all_qys})



@login_required
@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(["POST"])
def delete_qys(request, qys_id):
    qys = get_object_or_404(ComplaintSuggestion, id=qys_id)
    qys.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'La queja o sugerencia ha sido eliminada exitosamente.',
        })
    messages.success(request, 'La queja o sugerencia ha sido eliminada exitosamente.')
    return redirect('qys')


@login_required
@user_passes_test(lambda u: u.is_staff)
def upload_document(request):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.save()
            messages.success(request, 'Documento subido exitosamente.')
            return redirect('documentos')
    else:
        form = DocumentUploadForm()
    
    return render(request, 'upload_document.html', {'form': form})

def move_payment_proofs():
    lock_key = 'move_payment_proofs_lock'
    if cache.add(lock_key, 'true', 300):  # Lock for 5 minutes max
        try:
            source_dir = os.path.join(settings.MEDIA_ROOT, 'proof_of_payments')
            destination_dir = os.path.join(settings.MEDIA_ROOT, 'documents')

            # Ensure the destination directory exists
            os.makedirs(destination_dir, exist_ok=True)

            for root, dirs, files in os.walk(source_dir):
                for filename in files:
                    if filename.endswith('.pdf'):
                        source_path = os.path.join(root, filename)
                        destination_path = os.path.join(destination_dir, filename)
                        
                        # Check if the file already exists in the destination
                        if not os.path.exists(destination_path):
                            # Move the file
                            shutil.move(source_path, destination_path)
                            
                            # Extract date and username from filename (assuming format: username.MM.YYYY.pdf)
                            try:
                                username = filename.split('.')[0]
                                date_str = filename.split('.')[-2] + '.' + filename.split('.')[-3]
                                file_date = datetime.strptime(date_str, '%Y.%m').date()
                            except (ValueError, IndexError):
                                username = 'unknown'
                                file_date = timezone.now().date()

                            # Create a Document object for the moved file
                            with transaction.atomic():
                                Document.objects.get_or_create(
                                    title=filename,
                                    defaults={
                                        'document_type': 'pagos_mantenimiento',
                                        'file': f'documents/{filename}',
                                        'date': file_date,
                                        'uploaded_by': CustomUser.objects.get(username=username)
                                    }
                                )
        finally:
            cache.delete(lock_key)
    else:
        # Function is already running
        pass


@login_required
def documentos(request):
    documents = Document.objects.all()
    
    start_date = timezone.datetime(2025, 1, 1).date()
    end_date = start_date + relativedelta(years=5, months=-1)
    current_date = timezone.now().date()

    selected_date = request.GET.get('date')
    if selected_date:
        selected_year, selected_month = map(int, selected_date.split('-'))
        selected_date = timezone.datetime(selected_year, selected_month, 1).date()
    else:
        selected_date = current_date
        selected_year, selected_month = selected_date.year, selected_date.month

    # Filter documents by selected date
    filtered_documents = documents.filter(
        date__year=selected_year,
        date__month=selected_month
    )

    # Generate month-year pairs for the dropdown
    date_range = []
    current = start_date
    while current <= end_date:
        date_range.append((current.year, current.month))
        current += relativedelta(months=1)

    # Group documents by type
    grouped_documents = {
        'mantenimiento': documents.filter(document_type='mantenimiento'),
        'pagos_mantenimiento': filtered_documents.filter(document_type='pagos_mantenimiento'),
        'gastos_pasivos': filtered_documents.filter(document_type='gastos_pasivos'),
        'minutas': documents.filter(document_type='minutas'),
        'reglamentos': documents.filter(document_type='reglamentos'),
        'reportes': documents.filter(document_type='reportes'),
    }

    # Create a dictionary for document type headers
    document_type_headers = {
        'mantenimiento': 'Mantenimiento y Cotizaciones',
        'pagos_mantenimiento': 'Pagos de Mantenimiento',
        'gastos_pasivos': 'Gastos y Pasivos',
        'minutas': 'Minutas',
        'reglamentos': 'Reglamentos',
        'reportes': 'Reportes',
    }

    context = {
        'grouped_documents': grouped_documents,
        'document_type_headers': document_type_headers,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'selected_date': selected_date,
        'date_range': date_range,
    }
    return render(request, 'documentos.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_document(request, document_id):
    try:
        document = get_object_or_404(Document, id=document_id)
        
        # Delete file from storage
        if document.file:
            if default_storage.exists(document.file.name):
                default_storage.delete(document.file.name)
        
        # Delete database record
        document.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Documento eliminado exitosamente.'
            })
        
        messages.success(request, 'Documento eliminado exitosamente.')
        return redirect('documentos')
        
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Error al eliminar el documento.'
            })
        messages.error(request, 'Error al eliminar el documento.')
        return redirect('documentos')

@login_required
@user_passes_test(lambda u: u.is_staff)
@require_http_methods(["GET", "POST"])
def gastos(request):
    if request.method == 'POST':
        form = ExpenseUploadForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()

            # Generate PDF report
            report_filename = f"{expense.expense_concept.replace(' ', '_')}.{expense.expense_date.strftime('%m.%Y')}.pdf"
            report_path = generate_expense_report(expense, report_filename)
            
            # Save the report file path to the ExpenseReport instance
            expense.report_file.name = report_path
            expense.save()

            # Create a Document object for the expense report
            Document.objects.create(
                title=f"{expense.expense_concept} - {expense.expense_date.strftime('%m/%Y')}",
                document_type='gastos_pasivos',
                file=expense.report_file,
                date=expense.expense_date,
                uploaded_by=request.user
            )

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Comprobante de gasto subido exitosamente.'})
            else:
                messages.success(request, 'Comprobante de gasto subido exitosamente.')
                return redirect('documentos')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
            else:
                messages.error(request, 'Error en el formulario. Por favor, corrija los errores.')
    else:
        form = ExpenseUploadForm()
    
    return render(request, 'gastos.html', {'form': form})



@login_required
@user_passes_test(lambda u: u.is_staff)
def panel(request):
    try:
        # Get initial data
        apartments = CustomUser.objects.filter(apartment_number__isnull=False).order_by('apartment_number')
        current_month = timezone.now().date().replace(day=1)
        announcements = Announcement.objects.all().order_by('-created_at')

        if request.method == 'POST':
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

            # Handle announcements
            if 'create_announcement' in request.POST:
                try:
                    title = request.POST.get('title')
                    content = request.POST.get('content')
                    is_active = request.POST.get('is_active') == 'on'

                    # Create announcement
                    announcement = Announcement.objects.create(
                        title=title,
                        content=content,
                        is_active=is_active,
                        created_by=request.user
                    )

                    if is_ajax:
                        return JsonResponse({'success': True})
                    messages.success(request, 'Anuncio creado exitosamente.')
                    return redirect('panel')
                except Exception as e:
                    if is_ajax:
                        return JsonResponse({'success': False, 'errors': str(e)})
                    messages.error(request, f'Error al crear anuncio: {str(e)}')

            elif 'edit_announcement' in request.POST:
                try:
                    announcement_id = request.POST.get('announcement_id')
                    announcement = Announcement.objects.get(id=announcement_id)
                    
                    # Update announcement fields
                    announcement.title = request.POST.get('title')
                    announcement.content = request.POST.get('content')
                    announcement.is_active = request.POST.get('is_active') == 'on'
                    announcement.save()

                    if is_ajax:
                        return JsonResponse({'success': True})
                    messages.success(request, 'Anuncio actualizado exitosamente.')
                    return redirect('panel')
                except Announcement.DoesNotExist:
                    if is_ajax:
                        return JsonResponse({'success': False, 'errors': 'Anuncio no encontrado'})
                    messages.error(request, 'Anuncio no encontrado.')
                    return redirect('panel')
                except Exception as e:
                    if is_ajax:
                        return JsonResponse({'success': False, 'errors': str(e)})
                    messages.error(request, f'Error al actualizar anuncio: {str(e)}')

            elif 'delete_announcement' in request.POST:
                try:
                    announcement_id = request.POST.get('announcement_id')
                    announcement = Announcement.objects.get(id=announcement_id)
                    announcement.delete()

                    if is_ajax:
                        return JsonResponse({'success': True})
                    messages.success(request, 'Anuncio eliminado exitosamente.')
                    return redirect('panel')
                except Announcement.DoesNotExist:
                    if is_ajax:
                        return JsonResponse({'success': False, 'errors': 'Anuncio no encontrado'})
                    messages.error(request, 'Anuncio no encontrado.')
                    return redirect('panel')

            # Handle apartment fees
            else:
                apartment_id = request.POST.get('apartment_id')
                if apartment_id:
                    try:
                        user = CustomUser.objects.get(id=apartment_id)
                        fees, created = MonthlyFees.objects.get_or_create(
                            user=user, 
                            month=current_month
                        )

                        # Update fees
                        fees.gas_fee = Decimal(request.POST.get('gas_fee', 0))
                        fees.maintenance_fee = Decimal(request.POST.get('maintenance_fee', 1200))
                        fees.parking_fee = Decimal(request.POST.get('parking_fee', 0))
                        fees.extra_fee = Decimal(request.POST.get('extra_fee', 500))
                        fees.past_due = Decimal(request.POST.get('past_due', 0))
                        fees.is_paid = request.POST.get('is_paid') == 'on'
                        fees.paid_amount = Decimal(request.POST.get('paid_amount', 0))
                        fees.save()

                        # Update user debtor status
                        user.is_debtor = request.POST.get('is_debtor') == 'on'
                        user.save()

                        if is_ajax:
                            return JsonResponse({
                                'success': True,
                                'apartment': {
                                    'id': user.id,
                                    'total_fee': str(fees.total_fee),
                                    'remaining_amount': str(fees.remaining_amount),
                                    'is_paid': fees.is_paid,
                                    'is_debtor': user.is_debtor
                                }
                            })
                        messages.success(request, f'Cuotas actualizadas para Departamento {user.apartment_number}')
                    except Exception as e:
                        if is_ajax:
                            return JsonResponse({'success': False, 'errors': str(e)})
                        messages.error(request, f'Error al actualizar cuotas: {str(e)}')

        # Ensure monthly fees exist for all apartments
        for apartment in apartments:
            MonthlyFees.objects.get_or_create(user=apartment, month=current_month)

        # Prepare context
        context = {
            'apartments': apartments,
            'current_month': current_month,
            'announcements': announcements,
        }

        return render(request, 'panel.html', context)

    except Exception as e:
        logger.error(f"Error in panel view: {str(e)}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': 'Error interno del servidor'})
        messages.error(request, 'Error interno del servidor')
        return redirect('panel')


@login_required
@user_passes_test(lambda u: u.is_staff)
def generate_monthly_balance_report(request):
    try:
        if request.method == 'POST':
            year = int(request.POST.get('year'))
            month = int(request.POST.get('month'))
        else:
            year = int(request.GET.get('year'))
            month = int(request.GET.get('month'))

        # Create the PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Title
        title = f"Reporte de Balance Mensual - {month}/{year}"
        elements.append(Paragraph(title, styles['Heading1']))
        elements.append(Spacer(1, 12))

        # Get data
        payments = PaymentReport.objects.filter(
            payment_date__year=year,
            payment_date__month=month
        ).select_related('user')
        
        expenses = ExpenseReport.objects.filter(
            expense_date__year=year,
            expense_date__month=month
        ).select_related('user')

        # Calculate totals
        total_income = sum(payment.amount_paid for payment in payments)
        total_expenses = sum(expense.amount for expense in expenses)
        total_balance = total_income - total_expenses

        # Summary Table
        summary_data = [
            ['Resumen Financiero', 'Monto'],
            ['Total Ingresos', f"${total_income:,.2f}"],
            ['Total Gastos', f"${total_expenses:,.2f}"],
            ['Balance Final', f"${total_balance:,.2f}"]
        ]

        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1896d1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 20))

        # Payments Detail
        elements.append(Paragraph("Detalle de Ingresos", styles['Heading2']))
        elements.append(Spacer(1, 12))

        if payments.exists():
            payment_data = [['Fecha', 'Departamento', 'Método de Pago', 'Monto']]
            for payment in payments:
                payment_data.append([
                    payment.payment_date.strftime('%d/%m/%Y'),
                    payment.user.apartment_number or 'N/A',
                    payment.get_payment_method_display(),
                    f"${payment.amount_paid:,.2f}"
                ])
            payment_data.append(['TOTAL', '', '', f"${total_income:,.2f}"])

            payment_table = Table(payment_data, colWidths=['20%', '25%', '35%', '20%'])
            payment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1896d1')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f5f5f5')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            elements.append(payment_table)
        else:
            elements.append(Paragraph("No hay ingresos registrados para este período", styles['Normal']))

        elements.append(Spacer(1, 20))

        # Expenses Detail
        elements.append(Paragraph("Detalle de Gastos", styles['Heading2']))
        elements.append(Spacer(1, 12))

        if expenses.exists():
            expense_data = [['Fecha', 'Concepto', 'Método de Pago', 'Monto']]
            for expense in expenses:
                expense_data.append([
                    expense.expense_date.strftime('%d/%m/%Y'),
                    expense.expense_concept,
                    expense.get_payment_method_display(),
                    f"${expense.amount:,.2f}"
                ])
            expense_data.append(['TOTAL', '', '', f"${total_expenses:,.2f}"])

            expense_table = Table(expense_data, colWidths=['20%', '25%', '35%', '20%'])
            expense_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1896d1')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f5f5f5')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            elements.append(expense_table)
        else:
            elements.append(Paragraph("No hay gastos registrados para este período", styles['Normal']))

        # Build PDF
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()

        # Create response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="balance_mensual_{month_name[month]}_{year}.pdf"'
        response.write(pdf)

        return response

    except Exception as e:
        logger.error(f"Error generating balance report: {str(e)}")
        messages.error(request, 'Error al generar el reporte. Por favor, inténtelo de nuevo.')
        return redirect('panel')

## forgot password view:

class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        try:
            # The reset URL is already provided in the context
            reset_url = context.get('password_reset_url', '')
            if not reset_url:
                # Fallback to constructing the URL if it's not provided
                protocol = context.get('protocol', 'http')
                domain = context.get('domain', '')
                uid = context.get('uid', '')
                token = context.get('token', '')
                reset_url = f"{protocol}://{domain}/reset/{uid}/{token}/"

            # Update the context with the reset URL
            context.update({'reset_url': reset_url})

            subject = "Restablecer tu contraseña - Torres del Maurel"
            email_message = render_to_string(email_template_name, context)

            send_mail(
                subject,
                email_message,
                from_email,
                [to_email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending password reset email: {str(e)}")
            print(f"Context: {context}")
            raise  # Re-raise the exception after logging

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'password_reset_form.html'
    email_template_name = 'password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')
    
    def get_template_names(self):
        template_names = super().get_template_names()
        logger.debug(f"Template names for password reset: {template_names}")
        return template_names
    
    def form_valid(self, form):
        logger.debug("Password reset form submitted successfully")
        return super().form_valid(form)

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')
    
    def form_valid(self, form):
        messages.success(self.request, 'Tu contraseña ha sido actualizada exitosamente.')
        return super().form_valid(form)

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'


# === CODE END ===     