from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'username', 'first_name', 'last_name', 'moeda', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('moeda', 'foto_perfil')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {'fields': ('email', 'moeda', 'foto_perfil')}),
    )
