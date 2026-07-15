from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('cadastro/', views.CustomRegisterView.as_view(), name='register'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('perfil/', views.ProfileView.as_view(), name='profile'),
    
    # Recuperação de Senha
    path('recuperar-senha/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='accounts/password_reset_email.html',
        success_url='/auth/recuperar-senha/enviado/'
    ), name='password_reset'),
    
    path('recuperar-senha/enviado/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('recuperar-senha/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url='/auth/recuperar-senha/concluido/'
    ), name='password_reset_confirm'),
    
    path('recuperar-senha/concluido/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
]
