import csv
from datetime import datetime, date, timedelta
from decimal import Decimal
from django.db.models import Sum, Q
from django.http import HttpResponse
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Movimentacao, Parcelamento, ConfigCartao, PlanejamentoMensal
from .serializers import MovimentacaoSerializer, ParcelamentoSerializer, ConfigCartaoSerializer, PlanejamentoMensalSerializer


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
        ano = self.request.query_params.get('ano')
        if mes and mes.isdigit() and ano and ano.isdigit():
            m_int, a_int = int(mes), int(ano)
            first_day = date(a_int, m_int, 1)
            next_m = m_int % 12 + 1
            next_y = a_int + (1 if m_int == 12 else 0)
            last_day = date(next_y, next_m, 1) - timedelta(days=1)
            
            queryset = queryset.filter(
                Q(data__year=a_int, data__month=m_int, is_recorrente=False) |
                Q(is_recorrente=True, data__lte=last_day, data_fim_recorrencia__gte=first_day) |
                Q(is_recorrente=True, data__lte=last_day, data_fim_recorrencia__isnull=True)
            )
        elif mes and mes.isdigit():
            queryset = queryset.filter(Q(data__month=int(mes)) | Q(is_recorrente=True))
        elif ano and ano.isdigit():
            queryset = queryset.filter(Q(data__year=int(ano)) | Q(is_recorrente=True))

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


class PlanejamentoMensalViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Planejamento Financeiro Mensal do Usuário.
    Suporta criação e atualização transparente (upsert) por usuário e mês.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PlanejamentoMensalSerializer

    def get_queryset(self):
        return PlanejamentoMensal.objects.filter(usuario=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mes_ref = serializer.validated_data['mes_referencia'].replace(day=1)
        defaults = {
            'receita_esperada': serializer.validated_data.get('receita_esperada', Decimal('0.00')),
            'meta_investimento_mensal': serializer.validated_data.get('meta_investimento_mensal', Decimal('0.00')),
            'alocacao_essenciais_pct': serializer.validated_data.get('alocacao_essenciais_pct', 50),
            'alocacao_estilo_vida_pct': serializer.validated_data.get('alocacao_estilo_vida_pct', 30),
            'alocacao_investimentos_pct': serializer.validated_data.get('alocacao_investimentos_pct', 20),
        }
        # Aplica a metodologia configurada como base padrão para todos os registros do usuário
        PlanejamentoMensal.objects.filter(usuario=request.user).update(**defaults)

        plan, created = PlanejamentoMensal.objects.update_or_create(
            usuario=request.user,
            mes_referencia=mes_ref,
            defaults=defaults
        )
        res_serializer = self.get_serializer(plan)
        return Response(res_serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class ResumoPlanejamentoAPIView(APIView):
    """
    APIView que consolida o resumo do Planejamento Consciente vs Realizado do mês.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        mes_str = request.query_params.get('mes')
        hoje = date.today()
        if mes_str:
            try:
                dt_ref = datetime.strptime(mes_str, "%Y-%m").date().replace(day=1)
            except ValueError:
                dt_ref = hoje.replace(day=1)
        else:
            dt_ref = hoje.replace(day=1)

        usuario = request.user
        plan = PlanejamentoMensal.objects.filter(usuario=usuario, mes_referencia=dt_ref).first()
        if not plan:
            plan = PlanejamentoMensal.objects.filter(usuario=usuario).order_by('-mes_referencia').first()

        receita_esperada = plan.receita_esperada if plan else Decimal('0.00')
        meta_investimento = plan.meta_investimento_mensal if plan else Decimal('0.00')
        pct_essencial = plan.alocacao_essenciais_pct if plan else 50
        pct_estilo = plan.alocacao_estilo_vida_pct if plan else 30
        pct_invest = plan.alocacao_investimentos_pct if plan else 20

        # Lançamentos do mês (diretos + recorrentes ativos no período)
        next_m = dt_ref.month % 12 + 1
        next_y = dt_ref.year + (1 if dt_ref.month == 12 else 0)
        last_day = date(next_y, next_m, 1) - timedelta(days=1)

        movs_mes = Movimentacao.objects.filter(usuario=usuario).filter(
            Q(data__year=dt_ref.year, data__month=dt_ref.month, is_recorrente=False) |
            Q(is_recorrente=True, data__lte=last_day, data_fim_recorrencia__gte=dt_ref) |
            Q(is_recorrente=True, data__lte=last_day, data_fim_recorrencia__isnull=True)
        )

        receita_realizada = movs_mes.filter(tipo='RECEITA').aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        movs_despesas = movs_mes.filter(tipo='DESPESA')
        despesa_realizada = movs_despesas.aggregate(total=Sum('valor'))['total'] or Decimal('0.00')

        # Agregação precisa por pilar orçamentário
        gastos_essenciais_realizados = movs_despesas.filter(
            Q(categoria__pilar='ESSENCIAL') | Q(categoria__isnull=True)
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')

        gastos_estilo_vida_realizados = movs_despesas.filter(
            categoria__pilar='ESTILO_DE_VIDA'
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')

        investimento_movs = movs_despesas.filter(
            categoria__pilar='INVESTIMENTO'
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')

        from apps.investments.models import OperacaoInvestimento
        ops = OperacaoInvestimento.objects.filter(
            usuario=usuario,
            tipo_operacao='COMPRA',
            data_operacao__year=dt_ref.year,
            data_operacao__month=dt_ref.month
        )
        investimento_ops = Decimal(str(sum((op.quantidade * op.preco_unitario + op.taxas) for op in ops)))

        investimento_realizado = investimento_movs + investimento_ops

        # Soma das parcelas ativas + despesas diretas no cartão de crédito que cobrem o mês de referência
        fatura_cartao_direta = movs_despesas.filter(
            Q(forma_pagamento='CREDITO_1X') | Q(cartao__isnull=False)
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')

        parcelamentos = Parcelamento.objects.filter(usuario=usuario)
        soma_parcelamentos_mes = Decimal('0.00')
        for p in parcelamentos:
            d_inicio = p.data_primeira_parcela.replace(day=1)
            # adiciona p.num_parcelas meses
            m_end = (d_inicio.month - 1 + p.num_parcelas)
            y_end = d_inicio.year + (m_end // 12)
            m_end = (m_end % 12) + 1
            d_fim = date(y_end, m_end, 1)

            if d_inicio <= dt_ref < d_fim:
                soma_parcelamentos_mes += p.valor_parcela

        # Total de Faturas + Parcelas no mês (usado nos indicadores de exposição a crédito)
        total_parcelas_mes = fatura_cartao_direta + soma_parcelamentos_mes

        # Base de cálculo para o orçamento consciente (Renda Esperada cadastrada ou Renda Realizada se nula)
        base_receita = receita_esperada if receita_esperada > 0 else receita_realizada
        teto_essenciais = base_receita * Decimal(str(pct_essencial / 100))
        teto_estilo_vida = base_receita * Decimal(str(pct_estilo / 100))
        teto_investimentos = base_receita * Decimal(str(pct_invest / 100))

        # Disponível Livre: Renda - Despesas Diretas - Compras Parceladas - Meta de Investimento
        disponivel_livre = base_receita - despesa_realizada - soma_parcelamentos_mes - meta_investimento

        # Cálculo do Score de Saúde (0 - 100)
        score = 100
        if base_receita > 0:
            taxa_comprometimento_parcelas = (total_parcelas_mes / base_receita) * 100
            if taxa_comprometimento_parcelas > 30:
                score -= 30
            elif taxa_comprometimento_parcelas > 15:
                score -= 15

            total_saida_caixa = despesa_realizada + soma_parcelamentos_mes
            if total_saida_caixa > base_receita:
                score -= 40
            elif (total_saida_caixa + meta_investimento) > base_receita:
                score -= 25

            if disponivel_livre < 0 and (total_saida_caixa + meta_investimento) <= base_receita:
                score -= 20

            if meta_investimento > 0 and (receita_realizada < meta_investimento):
                score -= 10

        score = max(0, min(100, score))

        return Response({
            'mes_referencia': dt_ref.strftime("%Y-%m"),
            'receita_esperada': float(receita_esperada),
            'receita_realizada': float(receita_realizada),
            'despesa_realizada': float(despesa_realizada),
            'gastos_essenciais_realizados': float(gastos_essenciais_realizados),
            'gastos_estilo_vida_realizados': float(gastos_estilo_vida_realizados),
            'investimento_realizado': float(investimento_realizado),
            'compromissos_parcelas': float(total_parcelas_mes),
            'meta_investimento': float(meta_investimento),
            'disponivel_livre': float(disponivel_livre),
            'teto_essenciais': float(teto_essenciais),
            'teto_estilo_vida': float(teto_estilo_vida),
            'teto_investimentos': float(teto_investimentos),
            'score_saude': score,
            'pct_essenciais': pct_essencial,
            'pct_estilo_vida': pct_estilo,
            'pct_investimentos': pct_invest,
            'has_planejamento': plan is not None,
            'planejamento_id': plan.id if plan else None
        })


