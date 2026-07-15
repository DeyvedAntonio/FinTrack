from django.contrib import admin
from .models import Movimentacao


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'valor', 'tipo', 'data', 'categoria', 'usuario', 'forma_pagamento')
    list_filter = ('tipo', 'data', 'categoria', 'usuario')
    search_fields = ('descricao', 'observacoes', 'usuario__email')
    ordering = ('-data', '-created_at')
