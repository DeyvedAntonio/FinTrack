from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from apps.core.models import BaseModel
from apps.categories.models import Categoria


class Movimentacao(BaseModel):
    class TipoMovimentacao(models.TextChoices):
        RECEITA = 'RECEITA', 'Receita'
        DESPESA = 'DESPESA', 'Despesa'

    class MeioPagamento(models.TextChoices):
        CREDITO_1X = 'CREDITO_1X', 'Crédito À Vista'
        DEBITO = 'DEBITO', 'Débito'
        PIX_TRANSFERENCIA = 'PIX_TRANSFERENCIA', 'PIX / Transferência'
        DINHEIRO = 'DINHEIRO', 'Dinheiro'
        BOLETO = 'BOLETO', 'Boleto'

    descricao = models.CharField('Descrição', max_length=255)
    valor = models.DecimalField('Valor', max_digits=12, decimal_places=2)
    tipo = models.CharField('Tipo', max_length=10, choices=TipoMovimentacao.choices)
    data = models.DateField('Data da Transação')
    mes_referencia = models.DateField('Mês de Referência (Competência)', null=True, blank=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes',
        verbose_name='Categoria'
    )
    forma_pagamento = models.CharField('Forma de Pagamento', max_length=50, choices=MeioPagamento.choices, blank=True, null=True)
    cartao = models.ForeignKey(
        'ConfigCartao',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes',
        verbose_name='Cartão de Crédito'
    )
    observacoes = models.TextField('Observações', blank=True, null=True)
    confirmado = models.BooleanField('Confirmado / Pago', default=False)
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
        
        if self.categoria and hasattr(self, 'usuario') and self.usuario:
            if self.categoria.usuario != self.usuario:
                raise ValidationError({'categoria': 'A categoria selecionada não pertence ao seu usuário.'})
            if self.categoria.tipo != self.tipo:
                raise ValidationError({'categoria': f'A categoria selecionada é do tipo {self.categoria.get_tipo_display()}, mas a movimentação é {self.get_tipo_display()}.'})

        if self.cartao and hasattr(self, 'usuario') and self.usuario:
            if self.cartao.usuario != self.usuario:
                raise ValidationError({'cartao': 'O cartão selecionado não pertence ao seu usuário.'})

    def save(self, *args, **kwargs):
        if self.data and not self.mes_referencia:
            # Preenche o mês de referência padrão como 1º dia do mês da transação
            self.mes_referencia = self.data.replace(day=1)
        self.full_clean()
        super().save(*args, **kwargs)


class Parcelamento(BaseModel):
    descricao = models.CharField('Descrição do Parcelamento', max_length=255)
    valor_total = models.DecimalField('Valor Total Global', max_digits=12, decimal_places=2)
    num_parcelas = models.PositiveIntegerField('Número Total de Parcelas')
    data_primeira_parcela = models.DateField('Data da 1ª Parcela')
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='parcelamentos',
        verbose_name='Categoria'
    )
    cartao = models.ForeignKey(
        'ConfigCartao',
        on_delete=models.CASCADE,
        default=1,
        related_name='parcelamentos',
        verbose_name='Cartão de Crédito'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='parcelamentos',
        verbose_name='Usuário'
    )

    class Meta:
        verbose_name = 'Parcelamento'
        verbose_name_plural = 'Parcelamentos'
        ordering = ['-data_primeira_parcela', '-created_at']

    def __str__(self):
        return f"{self.descricao} ({self.num_parcelas}x de R$ {self.valor_parcela:.2f})"

    @property
    def valor_parcela(self):
        if self.num_parcelas and self.num_parcelas > 0:
            return round(self.valor_total / self.num_parcelas, 2)
        return self.valor_total

    def clean(self):
        super().clean()
        if self.valor_total is not None and self.valor_total <= 0:
            raise ValidationError({'valor_total': 'O valor total do parcelamento deve ser maior que zero.'})
        if self.num_parcelas is not None and self.num_parcelas <= 0:
            raise ValidationError({'num_parcelas': 'O número de parcelas deve ser maior que zero.'})
        if self.categoria and hasattr(self, 'usuario') and self.usuario:
            if self.categoria.usuario != self.usuario:
                raise ValidationError({'categoria': 'A categoria selecionada não pertence ao seu usuário.'})
        if not self.cartao_id:
            raise ValidationError({'cartao': 'O cartão de crédito é obrigatório para compras parceladas.'})
        if self.cartao and hasattr(self, 'usuario') and self.usuario:
            if self.cartao.usuario != self.usuario:
                raise ValidationError({'cartao': 'O cartão selecionado não pertence ao seu usuário.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ConfigCartao(BaseModel):
    apelido = models.CharField('Apelido do Cartão', max_length=50, default='Cartão Principal')
    ultimos_digitos = models.CharField('Últimos 4 Dígitos', max_length=4, blank=True, default='')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cartoes',
        verbose_name='Usuário'
    )
    limite_cartao = models.DecimalField('Limite Disponível do Cartão', max_digits=12, decimal_places=2, default=0.00)
    dia_fechamento = models.PositiveSmallIntegerField('Dia do Fechamento da Fatura', default=5)
    dia_vencimento = models.PositiveSmallIntegerField('Dia do Vencimento da Fatura', default=12)
    meta_fatura_mensal = models.DecimalField('Meta Mensal de Fatura', max_digits=12, decimal_places=2, default=0.00)
    reducao_mensal_desejada = models.DecimalField('Redução Mensal Desejada', max_digits=12, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = 'Configuração do Cartão'
        verbose_name_plural = 'Configurações dos Cartões'
        ordering = ['apelido', '-created_at']

    @property
    def nome_exibicao(self):
        if self.ultimos_digitos:
            return f"{self.apelido} (**** {self.ultimos_digitos})"
        return self.apelido

    def __str__(self):
        return self.nome_exibicao

    def clean(self):
        super().clean()
        if self.dia_fechamento and not (1 <= self.dia_fechamento <= 31):
            raise ValidationError({'dia_fechamento': 'O dia de fechamento deve estar entre 1 e 31.'})
        if self.dia_vencimento and not (1 <= self.dia_vencimento <= 31):
            raise ValidationError({'dia_vencimento': 'O dia de vencimento deve estar entre 1 e 31.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class PlanejamentoMensal(BaseModel):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='planejamentos',
        verbose_name='Usuário'
    )
    mes_referencia = models.DateField('Mês de Referência (1º dia do mês)')
    receita_esperada = models.DecimalField('Receita Mensal Esperada', max_digits=12, decimal_places=2, default=0.00)
    meta_investimento_mensal = models.DecimalField('Meta de Investimento Mensal', max_digits=12, decimal_places=2, default=0.00)
    alocacao_essenciais_pct = models.PositiveIntegerField('Percentual Essenciais (%)', default=50)
    alocacao_estilo_vida_pct = models.PositiveIntegerField('Percentual Estilo de Vida (%)', default=30)
    alocacao_investimentos_pct = models.PositiveIntegerField('Percentual Investimentos (%)', default=20)

    class Meta:
        verbose_name = 'Planejamento Mensal'
        verbose_name_plural = 'Planejamentos Mensais'
        unique_together = ('usuario', 'mes_referencia')
        ordering = ['-mes_referencia']

    def __str__(self):
        return f"Planejamento {self.mes_referencia.strftime('%m/%Y')} - R$ {self.receita_esperada:.2f}"

    def clean(self):
        super().clean()
        if self.mes_referencia and self.mes_referencia.day != 1:
            self.mes_referencia = self.mes_referencia.replace(day=1)

    def save(self, *args, **kwargs):
        if self.mes_referencia and self.mes_referencia.day != 1:
            self.mes_referencia = self.mes_referencia.replace(day=1)
        self.full_clean()
        super().save(*args, **kwargs)
