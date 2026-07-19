import csv
from django.http import HttpResponse
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Movimentacao, Parcelamento, ConfigCartao
from .serializers import MovimentacaoSerializer, ParcelamentoSerializer, ConfigCartaoSerializer



class MovimentacaoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Gerenciamento de Movimentações Financeiras (Receitas e Despesas).
    Permite Listar, Criar, Detalhar, Atualizar, Excluir e Exportar para CSV.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MovimentacaoSerializer

    def get_queryset(self):
        queryset = Movimentacao.objects.filter(usuario=self.request.user).select_related('categoria', 'cartao')
        
        # Filtros por parâmetros de URL
        tipo = self.request.query_params.get('tipo')
        if tipo in [Movimentacao.TipoMovimentacao.RECEITA, Movimentacao.TipoMovimentacao.DESPESA]:
            queryset = queryset.filter(tipo=tipo)

        categoria = self.request.query_params.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria_id=categoria)

        cartao = self.request.query_params.get('cartao')
        if cartao:
            queryset = queryset.filter(cartao_id=cartao)

        mes = self.request.query_params.get('mes')
        if mes and mes.isdigit():
            queryset = queryset.filter(data__month=int(mes))

        ano = self.request.query_params.get('ano')
        if ano and ano.isdigit():
            queryset = queryset.filter(data__year=int(ano))

        confirmado = self.request.query_params.get('confirmado')
        if confirmado is not None:
            queryset = queryset.filter(confirmado=(confirmado.lower() in ['true', '1']))

        descricao = self.request.query_params.get('descricao') or self.request.query_params.get('search')
        if descricao:
            queryset = queryset.filter(descricao__icontains=descricao)

        return queryset

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @action(detail=False, methods=['get'], url_path='export-csv')
    def export_csv(self, request, *args, **kwargs):
        """
        Endpoint que gera e exporta os lançamentos de movimentações em formato CSV com base nos filtros ativos.
        """
        queryset = self.get_queryset()

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="movimentacoes_fintrack.csv"'
        response.write('\ufeff')  # BOM (Byte Order Mark) para compatibilidade com Excel em UTF-8

        writer = csv.writer(response, delimiter=';')
        writer.writerow(['ID', 'Tipo', 'Descrição', 'Valor (R$)', 'Data', 'Mês Referência', 'Categoria', 'Cartão', 'Forma de Pagamento', 'Confirmado', 'Observações'])

        for mov in queryset:
            writer.writerow([
                mov.id,
                mov.get_tipo_display(),
                mov.descricao,
                f"{mov.valor:.2f}".replace('.', ','),
                mov.data.strftime('%d/%m/%Y') if mov.data else '',
                mov.mes_referencia.strftime('%m/%Y') if mov.mes_referencia else '',
                mov.categoria.nome if mov.categoria else '',
                mov.cartao.nome_exibicao if mov.cartao else '',
                mov.get_forma_pagamento_display() if mov.forma_pagamento else '',
                'Sim' if mov.confirmado else 'Não',
                mov.observacoes or ''
            ])

        return response


class ParcelamentoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Gerenciamento de Compras Parceladas Recorrentes.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ParcelamentoSerializer

    def get_queryset(self):
        return Parcelamento.objects.filter(usuario=self.request.user).select_related('categoria', 'cartao')

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class ConfigCartaoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Gerenciamento Multiusuário de Cartões de Crédito.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConfigCartaoSerializer

    def get_queryset(self):
        return ConfigCartao.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


