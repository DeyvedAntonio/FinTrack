from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordChangeView
)
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, UpdateView, View

from .forms import RegisterForm, EmailLoginForm, ProfileUpdateForm

User = get_user_model()


class CustomLoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = EmailLoginForm
    success_url = reverse_lazy('dashboard')  # Ajustável conforme rotas do projeto

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        
        user = authenticate(self.request, username=email, password=password)
        if user is None:
            # Tentar autenticar pelo username se email não bateu direto
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(self.request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            if user.is_active:
                login(self.request, user)
                messages.success(self.request, f'Bem-vindo(a) de volta, {user.first_name or user.email}!')
                return redirect(self.get_success_url())
            else:
                messages.error(self.request, 'Sua conta está desativada.')
        else:
            messages.error(self.request, 'E-mail ou senha inválidos.')
            
        return self.form_invalid(form)


class CustomRegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Cadastro realizado com sucesso! Faça login para continuar.')
        return redirect(self.success_url)


class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, 'Você saiu da sua conta.')
        return redirect('accounts:login')

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Perfil atualizado com sucesso!')
        return super().form_valid(form)
