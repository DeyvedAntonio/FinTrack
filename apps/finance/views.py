import csv
from django.http import HttpResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Movimentacao
from .serializers import MovimentacaoSerializer


class MovimentacaoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Gerenciamento de Movimentações Financeiras (Receitas e Despesas).
    Permite Listar, Criar, Detalhar, Atualizar, Excluir e Exportar para CSV.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MovimentacaoSerializer

    def get_queryset(self):
        queryset = Movimentacao.objects.filter(usuario=self.request.user).select_related('categoria')
        
        # Filtros por parâmetros de URL
        tipo = self.request.query_params.get('tipo')
        if tipo in [Movimentacao.TipoMovimentacao.RECEITA, Movimentacao.TipoMovimentacao.DESPESA]:
            queryset = queryset.filter(tipo=tipo)

        categoria = self.request.query_params.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria_id=categoria)

        mes = self.request.query_params.get('mes')
        if mes and mes.isdigit():
            queryset = queryset.filter(data__month=int(mes))

        ano = self.request.query_params.get('ano')
        if ano and ano.isdigit():
            queryset = queryset.filter(data__year=int(ano))

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
        writer.writerow(['ID', 'Tipo', 'Descrição', 'Valor (R$)', 'Data', 'Categoria', 'Forma de Pagamento', 'Observações'])

        for mov in queryset:
            writer.writerow([
                mov.id,
                mov.get_tipo_display(),
                mov.descricao,
                f"{mov.valor:.2f}".replace('.', ','),
                mov.data.strftime('%d/%m/%Y') if mov.data else '',
                mov.categoria.nome if mov.categoria else '',
                mov.forma_pagamento or '',
                mov.observacoes or ''
            ])

        return response
