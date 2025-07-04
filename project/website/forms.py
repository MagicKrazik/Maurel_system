# website/forms.py
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from .models import CustomUser
from django.core.validators import RegexValidator
from .models import PaymentReport, ComplaintSuggestion, Document, ExpenseReport, Announcement

class UserProfileForm(forms.ModelForm):
    phone_number = forms.CharField(
        label='Número de teléfono',
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='Ingrese un número de teléfono válido de 10 dígitos.',
                code='invalid_phone_number'
            ),
        ]
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'phone_number']
        labels = {
            'email': 'Correo electrónico',
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and not phone_number.isdigit():
            raise forms.ValidationError("El número de teléfono debe contener solo dígitos.")
        return phone_number

class SpanishPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Contraseña actual",
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'autofocus': True}),
    )
    new_password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text="<ul><li>Su contraseña debe contener al menos 8 caracteres.</li><li>Su contraseña no puede ser completamente numérica.</li></ul>",
    )
    new_password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text="Ingrese la misma contraseña que antes, para verificación.",
    )


class PaymentUploadForm(forms.ModelForm):
    amount_paid = forms.DecimalField(
        label='Monto pagado',
        help_text='Ingrese el monto pagado en pesos',
        max_digits=10,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0.01',
            'placeholder': '0.00',
            'required': True,
            'class': 'form-control'
        })
    )
    
    payment_date = forms.DateField(
        label='Fecha de pago',
        help_text='Fecha de pago',
        required=True,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'required': True,
            'class': 'form-control'
        })
    )
    
    payment_method = forms.ChoiceField(
        label='Método de pago',
        help_text='Método de pago utilizado.',
        required=True,
        choices=[
            ('transfer', 'Transferencia Bancaria'),
            ('deposit', 'Depósito Bancario'),
        ],
        widget=forms.Select(attrs={
            'required': True,
            'class': 'form-control'
        })
    )
    
    comments = forms.CharField(
        label='Comentarios',
        help_text='Comentario (opcional).',
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Ingrese cualquier comentario adicional (opcional)',
            'class': 'form-control'
        })
    )
    
    proof_of_payment = forms.ImageField(
        label='Comprobante de pago',
        help_text='Imagen del comprobante de pago.',
        required=True,
        widget=forms.FileInput(attrs={
            'accept': 'image/*',
            'required': True,
            'class': 'form-control'
        })
    )

    class Meta:
        model = PaymentReport
        fields = ['amount_paid', 'payment_date', 'payment_method', 'comments', 'proof_of_payment']

    def clean_amount_paid(self):
        amount = self.cleaned_data.get('amount_paid')
        if amount is not None and amount <= 0:
            raise forms.ValidationError("El monto debe ser mayor a 0.")
        return amount

    def clean_payment_date(self):
        payment_date = self.cleaned_data.get('payment_date')
        if payment_date:
            from datetime import date
            if payment_date > date.today():
                raise forms.ValidationError("La fecha de pago no puede ser futura.")
        return payment_date

    def clean_proof_of_payment(self):
        file = self.cleaned_data.get('proof_of_payment')
        if file:
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("El archivo es demasiado grande. Máximo permitido: 10MB")
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if file.content_type not in allowed_types:
                raise forms.ValidationError("Solo se permiten archivos de imagen (JPEG, PNG, GIF)")
        
        return file


class ExpenseUploadForm(forms.ModelForm):
    amount = forms.DecimalField(
        label='Monto del gasto',
        help_text='Ingrese el monto del gasto en pesos y centavos.',
        max_digits=10,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0.01',
            'placeholder': '0.00',
            'required': True,
            'class': 'form-control'
        })
    )
    
    expense_date = forms.DateField(
        label='Fecha del gasto',
        help_text='Fecha en que se realizó el gasto.',
        required=True,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'required': True,
            'class': 'form-control'
        })
    )
    
    payment_method = forms.ChoiceField(
        label='Método de pago',
        help_text='Seleccione el método de pago utilizado.',
        required=True,
        choices=[
            ('transfer', 'Transferencia Bancaria'),
            ('cash', 'Efectivo'),
            ('debit_card', 'Tarjeta de Débito'),
            ('credit_card', 'Tarjeta de Crédito'),
        ],
        widget=forms.Select(attrs={
            'required': True,
            'class': 'form-control'
        })
    )
    
    expense_concept = forms.CharField(
        label='Concepto del gasto',
        help_text='Ingrese un breve concepto o descripción del gasto.',
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Descripción del gasto',
            'required': True,
            'class': 'form-control'
        })
    )
    
    comments = forms.CharField(
        label='Comentarios',
        help_text='Agregue cualquier comentario relevante (opcional).',
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Comentarios adicionales (opcional)',
            'class': 'form-control'
        })
    )
    
    proof_of_expense = forms.FileField(
        label='Comprobante del gasto',
        help_text='Suba una imagen o PDF del comprobante del gasto.',
        required=True,
        widget=forms.FileInput(attrs={
            'accept': 'image/*,application/pdf',
            'required': True,
            'class': 'form-control'
        })
    )

    class Meta:
        model = ExpenseReport
        fields = ['amount', 'expense_date', 'payment_method', 'expense_concept', 'comments', 'proof_of_expense']

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError("El monto debe ser mayor a 0.")
        return amount

    def clean_expense_date(self):
        expense_date = self.cleaned_data.get('expense_date')
        if expense_date:
            from datetime import date
            if expense_date > date.today():
                raise forms.ValidationError("La fecha del gasto no puede ser futura.")
        return expense_date

    def clean_proof_of_expense(self):
        file = self.cleaned_data.get('proof_of_expense')
        if file:
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("El archivo es demasiado grande. Máximo permitido: 10MB")
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'application/pdf']
            if file.content_type not in allowed_types:
                raise forms.ValidationError("Solo se permiten archivos de imagen (JPEG, PNG, GIF) o PDF")
        
        return file


class ComplaintSuggestionForm(forms.ModelForm):
    class Meta:
        model = ComplaintSuggestion
        fields = ['apartment_number', 'type', 'category', 'description', 'attachment']
        labels = {
            'apartment_number': 'Número de Departamento',
            'type': 'Tipo de reporte',
            'category': 'Categoría',
            'description': 'Descripción',
            'attachment': 'Adjunto (opcional)',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.apartment_number:
            self.fields['apartment_number'].initial = user.apartment_number
            self.fields['apartment_number'].widget.attrs['readonly'] = True    


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'document_type', 'file', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'title': 'Título',
            'document_type': 'Tipo de Documento',
            'file': 'Archivo',
            'date': 'Fecha del Documento',
        }


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'is_active']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'title': 'Título',
            'content': 'Contenido',
            'is_active': 'Activo',
        }