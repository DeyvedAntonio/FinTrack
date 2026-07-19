from django.conf import settings
from django.db import models
from apps.core.models import BaseModel


class Categoria(BaseModel):
    class TipoCategoria(models.TextChoices):
        RECEITA = 'RECEITA', 'Receita'
        DESPESA = 'DESPESA', 'Despesa'

    nome = models.CharField('Nome da Categoria', max_length=100)
    tipo = models.CharField('Tipo', max_length=10, choices=TipoCategoria.choices)
    limite_mensal = models.DecimalField(
        'Limite Mensal (Orçamento)',
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categorias',
        verbose_name='Usuário'
    )

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'nome', 'tipo'],
                name='unique_categoria_por_usuario'
            )
        ]

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"
