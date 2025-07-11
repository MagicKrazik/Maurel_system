from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import (CustomPasswordResetView, CustomPasswordResetConfirmView, CustomPasswordResetDoneView, CustomPasswordResetCompleteView)


urlpatterns = [
    path('', views.home, name='home'),
    path('aviso_priv/', views.aviso_priv, name='aviso_priv'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('pagos/', views.pagos, name='pagos'),
    path('qys/', views.qys, name='qys'),
    path('qys/report/<int:qys_id>/', views.generate_qys_report_view, name='generate_qys_report'),
    path('panel/', views.panel, name='panel'),
    path('initial-profile-update/', views.initial_profile_update, name='initial_profile_update'),
    path('profile/', views.profile, name='profile'),
    path('documentos/', views.documentos, name='documentos'),
    path('delete_document/<int:document_id>/', views.delete_document, name='delete_document'),
    path('documentos/upload/', views.upload_document, name='upload_document'),
    path('gastos/', views.gastos, name='gastos'),
    path('password_reset/', CustomPasswordResetView.as_view(template_name='password_reset_form.html',email_template_name='password_reset_email.html',success_url='/password_reset/done/'), name='password_reset'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(template_name='password_reset_confirm.html',success_url='/reset/done/'), name='password_reset_confirm'),
    path('reset/done/', CustomPasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('generate_monthly_balance_report/', views.generate_monthly_balance_report, name='generate_monthly_balance_report'),

]