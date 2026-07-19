from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField('E-mail', unique=True)
    moeda = models.CharField(
        'Moeda Utilizada',
        max_length=3,
        default='BRL',
        choices=[
            ('BRL', 'Real (R$)'),
            ('USD', 'Dólar ($)'),
            ('EUR', 'Euro (€)'),
        ]
    )
    foto_perfil = models.ImageField(
        'Foto de Perfil',
        upload_to='profiles/',
        null=True,
        blank=True
    )
    is_anonymized = models.BooleanField(
        'Conta Anonimizada',
        default=False
    )
    anonymized_at = models.DateTimeField(
        'Data de Anonimização LGPD',
        null=True,
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.get_full_name() or self.username or self.email

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

