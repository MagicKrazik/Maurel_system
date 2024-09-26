from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import os
from django.conf import settings
from django.db.models import Sum


def payment_report_path(instance, filename):
    # File will be uploaded to STATIC_ROOT/documents/<filename>
    return os.path.join('documents', filename)

class CustomUser(AbstractUser):
    apartment_number = models.CharField(max_length=7, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_first_login = models.BooleanField(default=True)
    is_debtor = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} - {self.apartment_number}"

    def should_change_password(self):
        return self.is_first_login and not self.is_superuser

    
class MonthlyFees(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='monthly_fees')
    month = models.DateField()
    gas_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    maintenance_fee = models.DecimalField(max_digits=10, decimal_places=2, default=1200)
    parking_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    extra_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    past_due = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ('user', 'month')

    @classmethod
    def get_total_paid_amount(cls, year, month):
        return cls.objects.filter(month__year=year, month__month=month).aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0    

    @property
    def total_fee(self):
        return self.gas_fee + self.maintenance_fee + self.parking_fee + self.extra_fee + self.past_due

    @property
    def remaining_amount(self):
        return self.total_fee - self.paid_amount

    def __str__(self):
        return f"{self.user.apartment_number} - {self.month.strftime('%B %Y')}"    
    


def proof_of_payment_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/proof_of_payments/<username>/<filename>
    return os.path.join('proof_of_payments', instance.user.username, filename)

class PaymentReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_reports')
    month = models.DateField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=50, choices=[
        ('transfer', 'Transferencia Bancaria'),
        ('deposit', 'Depósito Bancario'),
    ])
    comments = models.TextField(blank=True, null=True)
    proof_of_payment = models.ImageField(upload_to=proof_of_payment_path)
    report_file = models.FileField(upload_to='documents/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.month.strftime('%B %Y')}"

    class Meta:
        ordering = ['-payment_date']
        verbose_name = 'Payment Report'
        verbose_name_plural = 'Payment Reports'


class ComplaintSuggestion(models.Model):
    TYPE_CHOICES = [
        ('queja', 'Queja'),
        ('sugerencia', 'Sugerencia'),
    ]
    CATEGORY_CHOICES = [
        ('mantenimiento', 'Mantenimiento'),
        ('seguridad', 'Seguridad'),
        ('ruido', 'Ruido'),
        ('limpieza', 'Limpieza'),
        ('estacionamiento', 'Estacionamiento'),
        ('otro', 'Otro'),
    ]
    STATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('atendido', 'Atendido'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    apartment_number = models.CharField(max_length=10)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    attachment = models.FileField(upload_to='qys_attachments/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendiente')
    created_at = models.DateTimeField(auto_now_add=True)
    attended_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_type_display()} - {self.get_category_display()} - Apto {self.apartment_number}"  
    
    def save(self, *args, **kwargs):
        if self.status == 'atendido' and not self.attended_at:
            self.attended_at = timezone.now()
        elif self.status != 'atendido':
            self.attended_at = None
        super().save(*args, **kwargs)      


class Document(models.Model):
    DOCUMENT_TYPES = [
        ('mantenimiento', 'Mantenimiento y Cotizaciones'),
        ('pagos_mantenimiento', 'Pagos de Mantenimiento'),
        ('gastos_pasivos', 'Gastos y Pasivos'),
        ('minutas', 'Minutas'),
        ('reglamentos', 'Reglamentos'),
        ('otros', 'Otros'),
    ]

    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='documents/')
    upload_date = models.DateTimeField(auto_now_add=True)
    date = models.DateField()  # The date associated with the document
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    related_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='related_documents')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date', '-upload_date']


class ExpenseReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expense_reports')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateField()
    payment_method = models.CharField(max_length=50, choices=[
        ('transfer', 'Transferencia Bancaria'),
        ('cash', 'Efectivo'),
        ('debit_card', 'Tarjeta de Débito'),
        ('credit_card', 'Tarjeta de Crédito'),
    ])
    expense_concept = models.CharField(max_length=255)
    comments = models.TextField(blank=True, null=True)
    proof_of_expense = models.FileField(upload_to='expense_reports/')
    report_file = models.FileField(upload_to='documents/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-expense_date']
        verbose_name = 'Expense Report'
        verbose_name_plural = 'Expense Reports'

    def __str__(self):
        return f"{self.expense_concept} - {self.expense_date.strftime('%B %Y')}"        