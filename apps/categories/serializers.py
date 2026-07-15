from rest_framework import serializers
from .models import Categoria


class CategoriaSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = Categoria
        fields = ('id', 'uuid', 'nome', 'tipo', 'tipo_display', 'created_at')
        read_only_fields = ('id', 'uuid', 'created_at')

    def validate(self, attrs):
        request = self.context.get('request')
        usuario = request.user if request else None
        nome = attrs.get('nome', self.instance.nome if self.instance else None)
        tipo = attrs.get('tipo', self.instance.tipo if self.instance else None)

        if usuario and nome and tipo:
            query = Categoria.objects.filter(usuario=usuario, nome__iexact=nome, tipo=tipo)
            if self.instance:
                query = query.exclude(pk=self.instance.pk)
            if query.exists():
                raise serializers.ValidationError({"nome": "Você já possui uma categoria cadastrada com este nome e tipo."})

        return attrs
