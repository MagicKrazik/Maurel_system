from django.db import models
from django.utils import timezone
import os
from django.conf import settings
from django.db.models import Sum
from django.contrib.auth.models import AbstractUser, Group, Permission
import datetime

## New codes
from django.db.models.signals import post_delete
from django.dispatch import receiver
from decimal import Decimal


def payment_report_path(instance, filename):
    # File will be uploaded to STATIC_ROOT/documents/<filename>
    return os.path.join('documents', filename)


class CustomUser(AbstractUser):
    apartment_number = models.CharField(max_length=7, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_first_login = models.BooleanField(default=True)
    is_debtor = models.BooleanField(default=False)

    # Add related_name to avoid clashes
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='customuser_set',
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',
        related_query_name='customuser',
    )

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
    extra_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
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
        ('pagos_mantenimiento', 'Pagos de Mantenimiento'),  # ADD THIS LINE
        ('gastos_pasivos', 'Gastos y Pasivos'),  # ADD THIS LINE IF NOT EXISTS
        ('minutas', 'Minutas'),
        ('reglamentos', 'Reglamentos'),
        ('reportes', 'Reportes'),
    ]

    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='documents/')
    upload_date = models.DateTimeField(auto_now_add=True)
    date = models.DateField()  # The date associated with the document
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

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
    


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
# Signal to handle payment document deletion
@receiver(post_delete, sender=Document)
def handle_payment_document_deletion(sender, instance, **kwargs):
    """
    When a payment document is deleted, also delete the associated PaymentReport
    and update the MonthlyFees accordingly.
    """
    # Only process if this is a payment document
    if instance.document_type == 'pagos_mantenimiento':
        try:
            # Extract information from the document title or filename
            # Expected format: "Pago de Mantenimiento - username - Month Year"
            # Or from filename: "username.MM.YYYY.pdf"
            
            username = None
            payment_month = None
            
            # Try to extract from filename first
            if instance.file and instance.file.name:
                filename = os.path.basename(instance.file.name)
                if '.pdf' in filename:
                    parts = filename.replace('.pdf', '').split('.')
                    if len(parts) >= 3:
                        username = parts[0]
                        try:
                            month = int(parts[1])
                            year = int(parts[2])
                            payment_month = timezone.datetime(year, month, 1).date()
                        except (ValueError, IndexError):
                            pass
            
            # If extraction from filename failed, try from title
            if not username or not payment_month:
                if 'Pago de Mantenimiento' in instance.title:
                    parts = instance.title.split(' - ')
                    if len(parts) >= 2:
                        username = parts[1].strip()
                        # Use the document date as payment month
                        payment_month = instance.date.replace(day=1)
            
            # If we have the necessary information, proceed with deletion
            if username and payment_month:
                try:
                    user = CustomUser.objects.get(username=username)
                    
                    # Find and delete the PaymentReport
                    payment_reports = PaymentReport.objects.filter(
                        user=user,
                        month=payment_month
                    )
                    
                    for payment_report in payment_reports:
                        # Get the amount that was paid
                        amount_paid = payment_report.amount_paid
                        
                        # Update MonthlyFees - subtract the payment amount
                        try:
                            monthly_fee = MonthlyFees.objects.get(
                                user=user,
                                month=payment_month
                            )
                            monthly_fee.paid_amount -= amount_paid
                            if monthly_fee.paid_amount < 0:
                                monthly_fee.paid_amount = 0
                            
                            # Update payment status based on remaining amount
                            monthly_fee.is_paid = monthly_fee.paid_amount >= monthly_fee.total_fee
                            monthly_fee.save()
                            
                            print(f"Updated MonthlyFees for {username}: reduced paid_amount by ${amount_paid}")
                            
                        except MonthlyFees.DoesNotExist:
                            print(f"MonthlyFees not found for {username} in {payment_month}")
                        
                        # Delete the PaymentReport
                        payment_report.delete()
                        print(f"Deleted PaymentReport for {username} - ${amount_paid}")
                
                except CustomUser.DoesNotExist:
                    print(f"User {username} not found")
                except Exception as e:
                    print(f"Error processing payment deletion: {str(e)}")
                    
        except Exception as e:
            print(f"Error in payment document deletion signal: {str(e)}")
            # Don't raise the exception to avoid blocking the document deletion    


class InitialBalance(models.Model):
    amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        verbose_name="Saldo Inicial"
    )
    description = models.CharField(
        max_length=255, 
        default="Saldo inicial del edificio",
        verbose_name="Descripción"
    )
    effective_date = models.DateField(
        default=datetime.date(2025, 6, 1),  # Use datetime.date instead of timezone.datetime().date()
        verbose_name="Fecha Efectiva",
        help_text="Fecha desde la cual aplica este saldo inicial"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Creado por"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )

    class Meta:
        verbose_name = "Saldo Inicial"
        verbose_name_plural = "Saldos Iniciales"
        ordering = ['-effective_date', '-updated_at']

    def __str__(self):
        return f"Saldo Inicial: ${self.amount} - {self.effective_date.strftime('%m/%Y')}"

    @classmethod
    def get_initial_balance_for_period(cls, target_date):
        """Get the initial balance that applies to a specific period"""
        try:
            # Find the most recent initial balance before or equal to target_date
            return cls.objects.filter(
                is_active=True,
                effective_date__lte=target_date
            ).latest('effective_date').amount
        except cls.DoesNotExist:
            return Decimal('0.00')

    @classmethod
    def get_current_balance(cls):
        """Get the current active initial balance"""
        try:
            return cls.objects.filter(is_active=True).latest('effective_date').amount
        except cls.DoesNotExist:
            return Decimal('0.00')

    def save(self, *args, **kwargs):
        # Ensure only one active initial balance exists per effective_date
        if self.is_active:
            cls = self.__class__
            existing = cls.objects.filter(
                is_active=True,
                effective_date=self.effective_date
            ).exclude(pk=self.pk)
            existing.update(is_active=False)
        super().save(*args, **kwargs)