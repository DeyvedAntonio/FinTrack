from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from apps.core.models import BaseModel
from apps.categories.models import Categoria


class Movimentacao(BaseModel):
    class TipoMovimentacao(models.TextChoices):
        RECEITA = 'RECEITA', 'Receita'
        DESPESA = 'DESPESA', 'Despesa'

    descricao = models.CharField('Descrição', max_length=255)
    valor = models.DecimalField('Valor', max_digits=12, decimal_places=2)
    tipo = models.CharField('Tipo', max_length=10, choices=TipoMovimentacao.choices)
    data = models.DateField('Data da Movimentação')
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='movimentacoes',
        verbose_name='Categoria'
    )
    forma_pagamento = models.CharField('Forma de Pagamento', max_length=50, blank=True, null=True)
    observacoes = models.TextField('Observações', blank=True, null=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='movimentacoes',
        verbose_name='Usuário'
    )

    class Meta:
        verbose_name = 'Movimentação'
        verbose_name_plural = 'Movimentações'
        ordering = ['-data', '-created_at']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.descricao} (R$ {self.valor})"

    def clean(self):
        super().clean()
        if self.valor is not None and self.valor <= 0:
            raise ValidationError({'valor': 'O valor da movimentação deve ser estritamente maior que zero.'})
        
        if hasattr(self, 'categoria') and self.categoria and hasattr(self, 'usuario') and self.usuario:
            if self.categoria.usuario != self.usuario:
                raise ValidationError({'categoria': 'A categoria selecionada não pertence ao seu usuário.'})
            if self.categoria.tipo != self.tipo:
                raise ValidationError({'categoria': f'A categoria selecionada é do tipo {self.categoria.get_tipo_display()}, mas a movimentação é {self.get_tipo_display()}.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
