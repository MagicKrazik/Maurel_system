from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

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

]