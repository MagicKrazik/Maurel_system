from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, PaymentReport, InitialBalance
from datetime import timezone

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'apartment_number', 'phone_number', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('apartment_number', 'phone_number')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('apartment_number', 'phone_number')}),
    )

@admin.register(InitialBalance)
class InitialBalanceAdmin(admin.ModelAdmin):
    list_display = ['amount', 'effective_date', 'description', 'is_active', 'updated_at', 'created_by']
    list_filter = ['is_active', 'effective_date', 'created_at', 'updated_at']
    search_fields = ['description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'effective_date'
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('amount', 'effective_date', 'description', 'is_active'),
            'description': 'El saldo inicial solo afecta al período especificado en la fecha efectiva. '
                          'Para períodos posteriores, se utilizará el balance acumulado.'
        }),
        ('Información de Auditoría', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete initial balance records
        return request.user.is_superuser
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Show only records from June 2025 onwards
        return qs.filter(effective_date__gte=timezone.datetime(2025, 6, 1).date())

    class Media:
        css = {
            'all': ('admin/css/widgets.css',)
        }

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(PaymentReport)