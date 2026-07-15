from django.contrib import admin
from .models import Categoria


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'usuario', 'created_at', 'active')
    list_filter = ('tipo', 'active', 'created_at')
    search_fields = ('nome', 'usuario__email', 'usuario__first_name')
    ordering = ('nome',)
