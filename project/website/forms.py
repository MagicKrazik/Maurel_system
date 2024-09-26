# website/forms.py
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from .models import CustomUser
from django.core.validators import RegexValidator
from .models import PaymentReport, ComplaintSuggestion, Document, ExpenseReport

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
        help_text="<ul><li>Su contraseña no puede ser muy similar a su otra información personal.</li><li>Su contraseña debe contener al menos 8 caracteres.</li><li>Su contraseña no puede ser una contraseña comúnmente utilizada.</li><li>Su contraseña no puede ser completamente numérica.</li></ul>",
    )
    new_password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text="Ingrese la misma contraseña que antes, para verificación.",
    )


class PaymentUploadForm(forms.ModelForm):
    class Meta:
        model = PaymentReport
        fields = ['amount_paid', 'payment_date', 'payment_method', 'comments', 'proof_of_payment']
        labels = {
            'amount_paid': 'Monto pagado',
            'payment_date': 'Fecha de pago',
            'payment_method': 'Método de pago',
            'comments': 'Comentarios',
            'proof_of_payment': 'Comprobante de pago',
        }
        help_texts = {
            'amount_paid': 'Ingrese el monto pagado en pesos y centavos.',
            'payment_date': 'Fecha en que realizó el pago.',
            'payment_method': 'Seleccione el método de pago utilizado.',
            'comments': 'Agregue cualquier comentario relevante (opcional).',
            'proof_of_payment': 'Suba una imagen o PDF del comprobante de pago.',
        }
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }


class ComplaintSuggestionForm(forms.ModelForm):
    class Meta:
        model = ComplaintSuggestion
        fields = ['apartment_number', 'type', 'category', 'description', 'attachment']
        labels = {
            'apartment_number': 'Número de Apartamento',
            'type': 'Tipo',
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


class ExpenseUploadForm(forms.ModelForm):
    class Meta:
        model = ExpenseReport
        fields = ['amount', 'expense_date', 'payment_method', 'expense_concept', 'comments', 'proof_of_expense']
        labels = {
            'amount': 'Monto del gasto',
            'expense_date': 'Fecha del gasto',
            'payment_method': 'Método de pago',
            'expense_concept': 'Concepto del gasto',
            'comments': 'Comentarios',
            'proof_of_expense': 'Comprobante del gasto',
        }
        help_texts = {
            'amount': 'Ingrese el monto del gasto en pesos y centavos.',
            'expense_date': 'Fecha en que se realizó el gasto.',
            'payment_method': 'Seleccione el método de pago utilizado.',
            'expense_concept': 'Ingrese un breve concepto o descripción del gasto.',
            'comments': 'Agregue cualquier comentario relevante (opcional).',
            'proof_of_expense': 'Suba una imagen o PDF del comprobante del gasto.',
        }
        widgets = {
            'expense_date': forms.DateInput(attrs={'type': 'date'}),
        }        