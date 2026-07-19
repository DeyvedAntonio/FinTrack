from django.contrib import admin
from .models import Movimentacao, Parcelamento, ConfigCartao


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'valor', 'tipo', 'data', 'mes_referencia', 'categoria', 'cartao', 'confirmado', 'usuario', 'forma_pagamento')
    list_filter = ('tipo', 'data', 'confirmado', 'categoria', 'cartao', 'usuario')
    search_fields = ('descricao', 'observacoes', 'usuario__email')
    ordering = ('-data', '-created_at')


@admin.register(Parcelamento)
class ParcelamentoAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'valor_total', 'num_parcelas', 'valor_parcela', 'data_primeira_parcela', 'categoria', 'cartao', 'usuario')
    list_filter = ('data_primeira_parcela', 'categoria', 'cartao', 'usuario')
    search_fields = ('descricao', 'usuario__email')


@admin.register(ConfigCartao)
class ConfigCartaoAdmin(admin.ModelAdmin):
    list_display = ('apelido', 'ultimos_digitos', 'usuario', 'limite_cartao', 'dia_fechamento', 'dia_vencimento', 'meta_fatura_mensal', 'reducao_mensal_desejada')
    search_fields = ('apelido', 'ultimos_digitos', 'usuario__email')


