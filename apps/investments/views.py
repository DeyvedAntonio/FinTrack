from decimal import Decimal
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Ativo, OperacaoInvestimento
from .serializers import AtivoSerializer, OperacaoInvestimentoSerializer


class AtivoViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AtivoSerializer

    def get_queryset(self):
        return Ativo.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class OperacaoInvestimentoViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OperacaoInvestimentoSerializer

    def get_queryset(self):
        return OperacaoInvestimento.objects.filter(usuario=self.request.user).select_related('ativo')

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class CarteiraAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        ativos = Ativo.objects.filter(usuario=request.user)
        posicao_carteira = []
        total_investido_carteira = Decimal('0.00')

        for ativo in ativos:
            operacoes = ativo.operacoes.filter(usuario=request.user).order_by('data_operacao', 'created_at')
            
            qtd_acumulada = Decimal('0.000000')
            custo_acumulado = Decimal('0.000000')
            preco_medio = Decimal('0.000000')

            for op in operacoes:
                if op.tipo_operacao == OperacaoInvestimento.TipoOperacao.COMPRA:
                    custo_compra = (op.quantidade * op.preco_unitario) + op.taxas
                    qtd_acumulada += op.quantidade
                    custo_acumulado += custo_compra
                    if qtd_acumulada > 0:
                        preco_medio = custo_acumulado / qtd_acumulada
                elif op.tipo_operacao == OperacaoInvestimento.TipoOperacao.VENDA:
                    qtd_acumulada -= op.quantidade
                    if qtd_acumulada < 0:
                        qtd_acumulada = Decimal('0.000000')
                    custo_acumulado = qtd_acumulada * preco_medio

            if qtd_acumulada > 0:
                total_ativo = round(qtd_acumulada * preco_medio, 2)
                total_investido_carteira += total_ativo
                posicao_carteira.append({
                    'ativo_id': ativo.id,
                    'codigo': ativo.codigo,
                    'nome': ativo.nome,
                    'tipo_ativo': ativo.tipo_ativo,
                    'tipo_ativo_display': ativo.get_tipo_ativo_display(),
                    'quantidade': float(qtd_acumulada),
                    'preco_medio': float(round(preco_medio, 2)),
                    'total_investido': float(total_ativo)
                })

        # Adicionar percentual de alocação
        alocacao_por_tipo = {}
        for pos in posicao_carteira:
            pct = round((Decimal(str(pos['total_investido'])) / total_investido_carteira * 100), 2) if total_investido_carteira > 0 else 0.0
            pos['percentual_carteira'] = float(pct)

            tipo = pos['tipo_ativo_display']
            alocacao_por_tipo[tipo] = float(round(Decimal(str(alocacao_por_tipo.get(tipo, 0.0))) + Decimal(str(pos['total_investido'])), 2))

        return Response({
            'total_investido': float(total_investido_carteira),
            'posicao_ativos': posicao_carteira,
            'alocacao_por_tipo': alocacao_por_tipo
        }, status=status.HTTP_200_OK)
