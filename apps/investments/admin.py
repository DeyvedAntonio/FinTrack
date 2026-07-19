from django.contrib import admin
from .models import Ativo, OperacaoInvestimento


@admin.register(Ativo)
class AtivoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'tipo_ativo', 'setor', 'usuario')
    list_filter = ('tipo_ativo', 'usuario')
    search_fields = ('codigo', 'nome', 'usuario__email')


@admin.register(OperacaoInvestimento)
class OperacaoInvestimentoAdmin(admin.ModelAdmin):
    list_display = ('ativo', 'tipo_operacao', 'quantidade', 'preco_unitario', 'taxas', 'data_operacao', 'usuario')
    list_filter = ('tipo_operacao', 'data_operacao', 'usuario')
    search_fields = ('ativo__codigo', 'ativo__nome', 'usuario__email')
