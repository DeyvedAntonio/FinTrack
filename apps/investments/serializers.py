from rest_framework import serializers
from .models import Ativo, OperacaoInvestimento


class AtivoSerializer(serializers.ModelSerializer):
    tipo_ativo_display = serializers.CharField(source='get_tipo_ativo_display', read_only=True)

    class Meta:
        model = Ativo
        fields = (
            'id',
            'uuid',
            'codigo',
            'nome',
            'tipo_ativo',
            'tipo_ativo_display',
            'setor',
            'created_at',
            'modified_at'
        )
        read_only_fields = ('id', 'uuid', 'created_at', 'modified_at')

    def validate_codigo(self, value):
        return value.strip().upper()


class OperacaoInvestimentoSerializer(serializers.ModelSerializer):
    ativo_codigo = serializers.CharField(source='ativo.codigo', read_only=True)
    ativo_nome = serializers.CharField(source='ativo.nome', read_only=True)
    tipo_ativo = serializers.CharField(source='ativo.tipo_ativo', read_only=True)
    tipo_ativo_display = serializers.CharField(source='ativo.get_tipo_ativo_display', read_only=True)
    tipo_operacao_display = serializers.CharField(source='get_tipo_operacao_display', read_only=True)
    valor_total_operacao = serializers.SerializerMethodField()

    class Meta:
        model = OperacaoInvestimento
        fields = (
            'id',
            'uuid',
            'ativo',
            'ativo_codigo',
            'ativo_nome',
            'tipo_ativo',
            'tipo_ativo_display',
            'tipo_operacao',
            'tipo_operacao_display',
            'quantidade',
            'preco_unitario',
            'taxas',
            'valor_total_operacao',
            'data_operacao',
            'observacoes',
            'created_at',
            'modified_at'
        )
        read_only_fields = ('id', 'uuid', 'created_at', 'modified_at')

    def get_valor_total_operacao(self, obj):
        val = (obj.quantidade * obj.preco_unitario) + obj.taxas
        return round(val, 2)

    def validate_quantidade(self, value):
        if value <= 0:
            raise serializers.ValidationError("A quantidade deve ser maior que zero.")
        return value

    def validate_preco_unitario(self, value):
        if value <= 0:
            raise serializers.ValidationError("O preço unitário deve ser maior que zero.")
        return value

    def validate(self, attrs):
        request = self.context.get('request')
        usuario = request.user if request else None
        ativo = attrs.get('ativo', self.instance.ativo if self.instance else None)

        if usuario and ativo and ativo.usuario != usuario:
            raise serializers.ValidationError({"ativo": "O ativo selecionado não pertence ao seu usuário."})

        return attrs
