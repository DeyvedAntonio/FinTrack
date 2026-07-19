from decimal import Decimal
from datetime import date
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from .models import Ativo, OperacaoInvestimento

User = get_user_model()


class InvestmentAPITestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='inv_user1@exemplo.com', email='inv_user1@exemplo.com', password='password123', first_name='User One')
        self.token1 = Token.objects.create(user=self.user1)

        self.user2 = User.objects.create_user(username='inv_user2@exemplo.com', email='inv_user2@exemplo.com', password='password123', first_name='User Two')
        self.token2 = Token.objects.create(user=self.user2)

        self.ativo_petr = Ativo.objects.create(
            codigo='PETR4',
            nome='Petrobras PN',
            tipo_ativo=Ativo.TipoAtivo.ACOES,
            setor='Energia',
            usuario=self.user1
        )

        self.list_ativos_url = reverse('investments:ativo-list')
        self.list_operacoes_url = reverse('investments:operacao-list')
        self.carteira_url = reverse('investments:carteira')

    def test_create_ativo_success(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        payload = {
            'codigo': 'hglg11',
            'nome': 'CSHG Logística',
            'tipo_ativo': Ativo.TipoAtivo.FII,
            'setor': 'Imobiliário'
        }
        res = self.client.post(self.list_ativos_url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['codigo'], 'HGLG11')

    def test_multi_tenant_isolation(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)
        res = self.client.get(self.list_ativos_url)
        self.assertEqual(len(res.data), 0)

    def test_preco_medio_and_carteira_calculation(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # 1ª Compra: 100 cotas a R$ 30.00 (taxa R$ 5.00) => Custo R$ 3005.00 => Preço Médio R$ 30.05
        OperacaoInvestimento.objects.create(
            ativo=self.ativo_petr,
            tipo_operacao=OperacaoInvestimento.TipoOperacao.COMPRA,
            quantidade=Decimal('100.000000'),
            preco_unitario=Decimal('30.00'),
            taxas=Decimal('5.00'),
            data_operacao=date(2026, 1, 10),
            usuario=self.user1
        )

        # 2ª Compra: 100 cotas a R$ 40.00 (taxa R$ 5.00) => Custo R$ 4005.00 => Total Custo 7010 / 200 => PM R$ 35.05
        OperacaoInvestimento.objects.create(
            ativo=self.ativo_petr,
            tipo_operacao=OperacaoInvestimento.TipoOperacao.COMPRA,
            quantidade=Decimal('100.000000'),
            preco_unitario=Decimal('40.00'),
            taxas=Decimal('5.00'),
            data_operacao=date(2026, 2, 10),
            usuario=self.user1
        )

        res = self.client.get(self.carteira_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['posicao_ativos']), 1)
        
        pos = res.data['posicao_ativos'][0]
        self.assertEqual(pos['codigo'], 'PETR4')
        self.assertEqual(pos['quantidade'], 200.0)
        self.assertEqual(pos['preco_medio'], 35.05)
        self.assertEqual(pos['total_investido'], 7010.0)
