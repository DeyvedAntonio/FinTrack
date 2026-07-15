import uuid

from django.conf import settings
from django.db import models


class UUIDModel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        abstract = True


class TimestampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, )
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CreatedBy(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Criado por'
    )

    class Meta:
        abstract = True


class ModifiedBy(models.Model):
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Modificado por'
    )

    class Meta:
        abstract = True


class Active(models.Model):
    active = models.BooleanField(default=True, verbose_name='Ativo')

    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimestampModel, CreatedBy, ModifiedBy, Active):
    class Meta:
        abstract = True
