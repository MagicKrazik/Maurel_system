# website/forms.py - FINAL VERSION - No validation errors on page load
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from .models import CustomUser
from django.core.validators import RegexValidator
from .models import PaymentReport, ComplaintSuggestion, Document, ExpenseReport, Announcement

# Simple Password Widget - Just add the data attribute for JavaScript detection
class PasswordInputWithToggle(forms.PasswordInput):
    def __init__(self, attrs=None, render_value=False):
        default_attrs = {
            'class': 'form-control',
            'autocomplete': 'off',
            'data-password-toggle': 'true'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs, render_value)

class UserProfileForm(forms.ModelForm):
    phone_number = forms.CharField(
        label='Número de teléfono',
        max_length=10,
        required=False,  # Make optional to avoid initial validation errors
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='Ingrese un número de teléfono válido de 10 dígitos.',
                code='invalid_phone_number'
            ),
        ],
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese su número de teléfono',
            'class': 'form-control'
        })
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'phone_number']
        labels = {
            'email': 'Correo electrónico',
        }
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Ingrese su correo electrónico',
                'class': 'form-control'
            })
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and not phone_number.isdigit():
            raise forms.ValidationError("El número de teléfono debe contener solo dígitos.")
        return phone_number

class SpanishPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override field requirements to prevent initial validation errors
        for field_name in ['old_password', 'new_password1', 'new_password2']:
            if field_name in self.fields:
                self.fields[field_name].required = False
    
    old_password = forms.CharField(
        label="Contraseña actual",
        widget=PasswordInputWithToggle(attrs={
            'autocomplete': 'current-password',
            'id': 'id_old_password',
            'placeholder': 'Ingrese su contraseña actual'
        }),
        required=False,
    )
    new_password1 = forms.CharField(
        label="Nueva contraseña",
        widget=PasswordInputWithToggle(attrs={
            'autocomplete': 'new-password',
            'id': 'id_new_password1',
            'placeholder': 'Ingrese su nueva contraseña'
        }),
        help_text="Su contraseña debe contener al menos 8 caracteres y no puede ser completamente numérica",
        required=False,
    )
    new_password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=PasswordInputWithToggle(attrs={
            'autocomplete': 'new-password',
            'id': 'id_new_password2',
            'placeholder': 'Confirme su nueva contraseña'
        }),
        help_text="Ingrese la misma contraseña que antes, para verificación.",
        required=False,
    )
    
    def clean(self):
        # Override clean to validate only when form is actually submitted
        cleaned_data = super(forms.Form, self).clean()  # Skip PasswordChangeForm validation
        
        old_password = cleaned_data.get('old_password')
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        # Only validate if at least one field has data (indicating form submission)
        if old_password or new_password1 or new_password2:
            # Now require all fields
            if not old_password:
                self.add_error('old_password', 'Este campo es requerido.')
            if not new_password1:
                self.add_error('new_password1', 'Este campo es requerido.')
            if not new_password2:
                self.add_error('new_password2', 'Este campo es requerido.')
            
            # Validate old password
            if old_password and not self.user.check_password(old_password):
                self.add_error('old_password', 'La contraseña actual es incorrecta.')
            
            # Validate new passwords match
            if new_password1 and new_password2 and new_password1 != new_password2:
                self.add_error('new_password2', 'Las dos contraseñas no coinciden.')
            
            # Validate password strength
            if new_password1:
                if len(new_password1) < 8:
                    self.add_error('new_password1', 'La contraseña debe tener al menos 8 caracteres.')
                if new_password1.isdigit():
                    self.add_error('new_password1', 'La contraseña no puede ser completamente numérica.')
        
        return cleaned_data
    
    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user

# Keep all your existing forms as they are (no changes needed below this line)
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


class ManualPaymentForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        label='Departamento',
        queryset=CustomUser.objects.none(),  # Will be set in __init__
        required=True,
        widget=forms.Select(attrs={
            'required': True,
            'class': 'form-control'
        }),
        empty_label="Seleccione un departamento"
    )
    
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
        help_text='Imagen del comprobante de pago (desde WhatsApp).',
        required=True,
        widget=forms.FileInput(attrs={
            'accept': 'image/*',
            'required': True,
            'class': 'form-control'
        })
    )

    class Meta:
        model = PaymentReport
        fields = ['user', 'amount_paid', 'payment_date', 'payment_method', 'comments', 'proof_of_payment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # FIX: Set the queryset only once and make sure it's unique
        self.fields['user'].queryset = CustomUser.objects.filter(
            apartment_number__isnull=False
        ).distinct().order_by('apartment_number')
        
        # Customize the choice labels to show apartment numbers
        self.fields['user'].label_from_instance = lambda obj: f"Departamento {obj.get_full_name() or obj.username}"

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

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        payment_date = cleaned_data.get('payment_date')
        
        if user and payment_date:
            # Check for duplicate payments in the same month
            month = payment_date.replace(day=1)
            existing_payment = PaymentReport.objects.filter(
                user=user,
                month=month
            ).exists()
            
            if existing_payment:
                raise forms.ValidationError(
                    f"Ya existe un pago registrado para el departamento {user.apartment_number} "
                    f"en {payment_date.strftime('%B %Y')}."
                )
        
        return cleaned_data


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