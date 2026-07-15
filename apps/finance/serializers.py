from rest_framework import serializers
from apps.categories.models import Categoria
from .models import Movimentacao


class MovimentacaoSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)

    class Meta:
        model = Movimentacao
        fields = (
            'id',
            'uuid',
            'descricao',
            'valor',
            'tipo',
            'tipo_display',
            'data',
            'categoria',
            'categoria_nome',
            'forma_pagamento',
            'observacoes',
            'created_at',
            'modified_at'
        )
        read_only_fields = ('id', 'uuid', 'created_at', 'modified_at')

    def validate_valor(self, value):
        if value <= 0:
            raise serializers.ValidationError("O valor da movimentação deve ser maior que zero.")
        return value

    def validate(self, attrs):
        request = self.context.get('request')
        usuario = request.user if request else None
        
        categoria = attrs.get('categoria', self.instance.categoria if self.instance else None)
        tipo = attrs.get('tipo', self.instance.tipo if self.instance else None)

        if usuario and categoria:
            if categoria.usuario != usuario:
                raise serializers.ValidationError({"categoria": "A categoria selecionada não pertence ao seu usuário."})
            if tipo and categoria.tipo != tipo:
                raise serializers.ValidationError({
                    "categoria": f"A categoria selecionada ({categoria.get_tipo_display()}) não é compatível com o tipo de movimentação ({dict(Movimentacao.TipoMovimentacao.choices).get(tipo)})."
                })

        return attrs
