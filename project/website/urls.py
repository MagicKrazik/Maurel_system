from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetView, password_reset_done, password_reset_confirm, password_reset_complete


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('pagos/', views.pagos, name='pagos'),
    path('qys/', views.qys, name='qys'),
    path('panel/', views.panel, name='panel'),
    path('initial-profile-update/', views.initial_profile_update, name='initial_profile_update'),
    path('profile/', views.profile, name='profile'),
    path('documentos/', views.documentos, name='documentos'),
    path('documentos/upload/', views.upload_document, name='upload_document'),
    path('gastos/', views.gastos, name='gastos'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]