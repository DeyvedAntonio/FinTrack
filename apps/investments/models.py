from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from apps.core.models import BaseModel


class Ativo(BaseModel):
    class TipoAtivo(models.TextChoices):
        ACOES = 'ACOES', 'Ações (B3)'
        FII = 'FII', 'Fundos Imobiliários (FIIs)'
        RENDA_FIXA = 'RENDA_FIXA', 'Renda Fixa (CDB, LCI, Tesouro)'
        ETFS = 'ETFS', 'ETFs'
        CRIPTO = 'CRIPTO', 'Criptomoedas'
        INTERNACIONAL = 'INTERNACIONAL', 'Investimentos no Exterior (Stocks/REITs)'

    codigo = models.CharField('Código / Ticker', max_length=20)
    nome = models.CharField('Nome do Ativo', max_length=150)
    tipo_ativo = models.CharField('Tipo de Ativo', max_length=20, choices=TipoAtivo.choices)
    setor = models.CharField('Setor / Segmento', max_length=100, blank=True, null=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ativos',
        verbose_name='Usuário'
    )

    class Meta:
        verbose_name = 'Ativo'
        verbose_name_plural = 'Ativos'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

    def clean(self):
        super().clean()
        if self.codigo:
            self.codigo = self.codigo.strip().upper()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class OperacaoInvestimento(BaseModel):
    class TipoOperacao(models.TextChoices):
        COMPRA = 'COMPRA', 'Compra / Aporte'
        VENDA = 'VENDA', 'Venda / Resgate'

    ativo = models.ForeignKey(
        Ativo,
        on_delete=models.CASCADE,
        related_name='operacoes',
        verbose_name='Ativo'
    )
    tipo_operacao = models.CharField('Tipo de Operação', max_length=10, choices=TipoOperacao.choices)
    quantidade = models.DecimalField('Quantidade', max_digits=14, decimal_places=6)
    preco_unitario = models.DecimalField('Preço Unitário (R$)', max_digits=12, decimal_places=2)
    taxas = models.DecimalField('Taxas e Corretagem (R$)', max_digits=12, decimal_places=2, default=0.00)
    data_operacao = models.DateField('Data da Operação')
    observacoes = models.TextField('Observações', blank=True, null=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='operacoes_investimento',
        verbose_name='Usuário'
    )

    class Meta:
        verbose_name = 'Operação de Investimento'
        verbose_name_plural = 'Operações de Investimentos'
        ordering = ['-data_operacao', '-created_at']

    def __str__(self):
        return f"{self.get_tipo_operacao_display()} - {self.quantidade}x {self.ativo.codigo} @ R$ {self.preco_unitario}"

    def clean(self):
        super().clean()
        if self.quantidade is not None and self.quantidade <= 0:
            raise ValidationError({'quantidade': 'A quantidade deve ser maior que zero.'})
        if self.preco_unitario is not None and self.preco_unitario <= 0:
            raise ValidationError({'preco_unitario': 'O preço unitário deve ser maior que zero.'})
        if self.taxas is not None and self.taxas < 0:
            raise ValidationError({'taxas': 'As taxas não podem ser negativas.'})
        if self.ativo and hasattr(self, 'usuario') and self.usuario:
            if self.ativo.usuario != self.usuario:
                raise ValidationError({'ativo': 'O ativo selecionado não pertence ao seu usuário.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
