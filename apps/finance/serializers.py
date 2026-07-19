from rest_framework import serializers
from apps.categories.models import Categoria
from .models import Movimentacao, Parcelamento, ConfigCartao


class MovimentacaoSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    forma_pagamento_display = serializers.CharField(source='get_forma_pagamento_display', read_only=True)
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True, default='')
    cartao_nome = serializers.CharField(source='cartao.nome_exibicao', read_only=True, default='')

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
            'mes_referencia',
            'categoria',
            'categoria_nome',
            'forma_pagamento',
            'forma_pagamento_display',
            'cartao',
            'cartao_nome',
            'observacoes',
            'confirmado',
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
        cartao = attrs.get('cartao', self.instance.cartao if self.instance else None)
        tipo = attrs.get('tipo', self.instance.tipo if self.instance else None)

        if usuario and categoria:
            if categoria.usuario != usuario:
                raise serializers.ValidationError({"categoria": "A categoria selecionada não pertence ao seu usuário."})
            if tipo and categoria.tipo != tipo:
                raise serializers.ValidationError({
                    "categoria": f"A categoria selecionada ({categoria.get_tipo_display()}) não é compatível com o tipo de movimentação ({dict(Movimentacao.TipoMovimentacao.choices).get(tipo)})."
                })

        if usuario and cartao and cartao.usuario != usuario:
            raise serializers.ValidationError({"cartao": "O cartão selecionado não pertence ao seu usuário."})

        return attrs


class ParcelamentoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True, default='')
    cartao_nome = serializers.CharField(source='cartao.nome_exibicao', read_only=True, default='')
    valor_parcela = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Parcelamento
        fields = (
            'id',
            'uuid',
            'descricao',
            'valor_total',
            'num_parcelas',
            'valor_parcela',
            'data_primeira_parcela',
            'categoria',
            'categoria_nome',
            'cartao',
            'cartao_nome',
            'created_at',
            'modified_at'
        )
        read_only_fields = ('id', 'uuid', 'valor_parcela', 'created_at', 'modified_at')

    def validate_valor_total(self, value):
        if value <= 0:
            raise serializers.ValidationError("O valor total deve ser maior que zero.")
        return value

    def validate_num_parcelas(self, value):
        if value <= 0:
            raise serializers.ValidationError("O número de parcelas deve ser maior que zero.")
        return value

    def validate(self, attrs):
        request = self.context.get('request')
        usuario = request.user if request else None
        categoria = attrs.get('categoria', self.instance.categoria if self.instance else None)
        cartao = attrs.get('cartao', self.instance.cartao if self.instance else None)

        if usuario and categoria and categoria.usuario != usuario:
            raise serializers.ValidationError({"categoria": "A categoria selecionada não pertence ao seu usuário."})

        if usuario and cartao and cartao.usuario != usuario:
            raise serializers.ValidationError({"cartao": "O cartão selecionado não pertence ao seu usuário."})

        return attrs


class ConfigCartaoSerializer(serializers.ModelSerializer):
    nome_exibicao = serializers.CharField(read_only=True)

    class Meta:
        model = ConfigCartao
        fields = (
            'id',
            'apelido',
            'ultimos_digitos',
            'nome_exibicao',
            'limite_cartao',
            'dia_fechamento',
            'dia_vencimento',
            'meta_fatura_mensal',
            'reducao_mensal_desejada',
            'modified_at'
        )
        read_only_fields = ('id', 'nome_exibicao', 'modified_at')

    def validate_dia_fechamento(self, value):
        if not (1 <= value <= 31):
            raise serializers.ValidationError("O dia de fechamento deve estar entre 1 e 31.")
        return value

    def validate_dia_vencimento(self, value):
        if not (1 <= value <= 31):
            raise serializers.ValidationError("O dia de vencimento deve estar entre 1 e 31.")
        return value


