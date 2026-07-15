from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError

User = get_user_model()


class RegisterForm(UserCreationForm):
    nome = forms.CharField(
        label='Nome Completo',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Seu nome completo'})
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'placeholder': 'seuemail@exemplo.com'})
    )

    class Meta:
        model = User
        fields = ('nome', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este e-mail já está cadastrado.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']
        
        # Atribui o nome informado ao first_name
        nome = self.cleaned_data.get('nome', '')
        user.first_name = nome
        
        if commit:
            user.save()
        return user


class EmailLoginForm(forms.Form):
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'placeholder': 'seuemail@exemplo.com'})
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'placeholder': 'Sua senha'})
    )


class ProfileUpdateForm(forms.ModelForm):
    nome = forms.CharField(
        label='Nome',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Seu nome completo'})
    )

    class Meta:
        model = User
        fields = ('nome', 'email', 'moeda', 'foto_perfil')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['nome'].initial = self.instance.first_name or self.instance.get_full_name()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['nome']
        if commit:
            user.save()
        return user
