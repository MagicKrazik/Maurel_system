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
from .models import ExpenseReport
from .forms import AnnouncementForm




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
    start_date = timezone.datetime(2024, 9, 1).date()
    end_date = start_date + relativedelta(years=5, months=-1)
    current_date = timezone.now().date()

    selected_date = request.GET.get('date')
    if selected_date:
        selected_year, selected_month = map(int, selected_date.split('-'))
        selected_date = datetime(selected_year, selected_month, 1).date()
    else:
        selected_date = current_date
        selected_year, selected_month = selected_date.year, selected_date.month

    debtors = CustomUser.objects.filter(is_debtor=True)
    
    # Get income data for the selected month
    income_data = float(MonthlyFees.get_total_paid_amount(selected_year, selected_month))

    # Get expenses data for the selected month
    expenses_data = float(ExpenseReport.objects.filter(
        expense_date__year=selected_year,
        expense_date__month=selected_month
    ).aggregate(Sum('amount'))['amount__sum'] or 0)

    # Generate month-year pairs for the dropdown
    date_range = []
    current = start_date
    while current <= end_date:
        date_range.append((current.year, current.month))
        current += relativedelta(months=1)

    # Get income data for all months in the selected year
    yearly_income_data = [float(MonthlyFees.get_total_paid_amount(selected_year, month)) for month in range(1, 13)]

    # Get expenses data for all months in the selected year
    yearly_expenses_data = [
        float(ExpenseReport.objects.filter(
            expense_date__year=selected_year,
            expense_date__month=month
        ).aggregate(Sum('amount'))['amount__sum'] or 0)
        for month in range(1, 13)
    ]

    if request.user.is_staff or request.user.is_superuser:
        context = {
            'debtors': debtors,
        }
    else:
        current_fees, created = MonthlyFees.objects.get_or_create(user=request.user, month=current_date.replace(day=1))
        context = {
            'current_fees': current_fees,
            'current_month': current_date,
        }
    
    active_announcements = Announcement.objects.filter(is_active=True).order_by('-created_at')

    context.update({
        'debtors': debtors,
        'income_data': income_data,
        'expenses_data': expenses_data,
        'yearly_income_data': json.dumps(yearly_income_data),
        'yearly_expenses_data': json.dumps(yearly_expenses_data),
        'selected_year': selected_year,
        'selected_month': selected_month,
        'selected_date': selected_date,
        'date_range': date_range,
        'active_announcements': active_announcements,
    })

    return render(request, 'dashboard.html', context)


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

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Comprobante de pago subido exitosamente.'})
            else:
                messages.success(request, 'Comprobante de pago subido exitosamente.')
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
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
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
                    })
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
    
    start_date = timezone.datetime(2024, 9, 1).date()
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
        'otros': documents.filter(document_type='otros'),
    }

    # Create a dictionary for document type headers
    document_type_headers = {
        'mantenimiento': 'Mantenimiento y Cotizaciones',
        'pagos_mantenimiento': 'Pagos de Mantenimiento',
        'gastos_pasivos': 'Gastos y Pasivos',
        'minutas': 'Minutas',
        'reglamentos': 'Reglamentos',
        'otros': 'Otros Documentos',
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
    apartments = CustomUser.objects.filter(apartment_number__isnull=False).order_by('apartment_number')
    current_month = timezone.now().date().replace(day=1)
    announcements = Announcement.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        if 'create_announcement' in request.POST:
            form = AnnouncementForm(request.POST)
            if form.is_valid():
                announcement = form.save(commit=False)
                announcement.created_by = request.user
                announcement.save()
                messages.success(request, 'Anuncio creado exitosamente.')
                return redirect('panel')
        elif 'edit_announcement' in request.POST:
            announcement_id = request.POST.get('announcement_id')
            announcement = get_object_or_404(Announcement, id=announcement_id)
            form = AnnouncementForm(request.POST, instance=announcement)
            if form.is_valid():
                form.save()
                messages.success(request, 'Anuncio actualizado exitosamente.')
                return redirect('panel')
        elif 'delete_announcement' in request.POST:
            announcement_id = request.POST.get('announcement_id')
            announcement = get_object_or_404(Announcement, id=announcement_id)
            announcement.delete()
            messages.success(request, 'Anuncio eliminado exitosamente.')
            return redirect('panel')
        else:
            # Existing code for handling apartment fees...
            apartment_id = request.POST.get('apartment_id')
            user = CustomUser.objects.get(id=apartment_id)
            
            fees, created = MonthlyFees.objects.get_or_create(user=user, month=current_month)
            
            fees.gas_fee = Decimal(request.POST.get('gas_fee', 0))
            fees.maintenance_fee = Decimal(request.POST.get('maintenance_fee', 1200))
            fees.parking_fee = Decimal(request.POST.get('parking_fee', 0))
            fees.extra_fee = Decimal(request.POST.get('extra_fee', 500))
            fees.past_due = Decimal(request.POST.get('past_due', 0))
            fees.is_paid = request.POST.get('is_paid') == 'on'
            fees.paid_amount = Decimal(request.POST.get('paid_amount', 0))
            fees.save()
            
            user.is_debtor = request.POST.get('is_debtor') == 'on'
            user.save()
            
            messages.success(request, f'Fees updated for Apartment {user.apartment_number}')
    
    for apartment in apartments:
        MonthlyFees.objects.get_or_create(user=apartment, month=current_month)
    
    context = {
        'apartments': apartments,
        'current_month': current_month,
        'announcements': announcements,
        'announcement_form': AnnouncementForm(),
    }
    return render(request, 'panel.html', context)