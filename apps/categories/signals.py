from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from .services import criar_categorias_padrao_para_usuario

User = get_user_model()


@receiver(post_save, sender=User)
def ao_criar_usuario_criar_categorias_padrao(sender, instance, created, **kwargs):
    if created:
        criar_categorias_padrao_para_usuario(instance)
