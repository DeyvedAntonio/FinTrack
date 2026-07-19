from datetime import date
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from apps.categories.models import Categoria
from .models import Movimentacao

User = get_user_model()


class MovimentacaoAPITestCase(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1@example.com',
            email='user1@example.com',
            password='Password123!',
            first_name='Usuário Um'
        )
        self.token1, _ = Token.objects.get_or_create(user=self.user1)

        self.user2 = User.objects.create_user(
            username='user2@example.com',
            email='user2@example.com',
            password='Password123!',
            first_name='Usuário Dois'
        )
        self.token2, _ = Token.objects.get_or_create(user=self.user2)

        # Categorias do User 1 (criadas automaticamente pelo signal)
        self.cat_salario = Categoria.objects.get(usuario=self.user1, nome='Salário', tipo='RECEITA')
        self.cat_alimentacao = Categoria.objects.get(usuario=self.user1, nome='Alimentação', tipo='DESPESA')

        # Categoria do User 2
        self.cat_user2 = Categoria.objects.get(usuario=self.user2, nome='Salário', tipo='RECEITA')

        self.list_url = reverse('finance:movimentacao-list')
        self.export_csv_url = reverse('finance:movimentacao-export-csv')

    def test_create_receita_success(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        payload = {
            'descricao': 'Salário Mensal',
            'valor': '5000.00',
            'tipo': Movimentacao.TipoMovimentacao.RECEITA,
            'data': '2026-07-01',
            'categoria': self.cat_salario.id,
            'observacoes': 'Pagamento referente a Julho'
        }
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['descricao'], 'Salário Mensal')
        self.assertEqual(Decimal(response.data['valor']), Decimal('5000.00'))

    def test_create_despesa_success(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        payload = {
            'descricao': 'Supermercado',
            'valor': '450.50',
            'tipo': Movimentacao.TipoMovimentacao.DESPESA,
            'data': '2026-07-05',
            'categoria': self.cat_alimentacao.id,
            'forma_pagamento': 'DEBITO'
        }
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['descricao'], 'Supermercado')

    def test_reject_zero_or_negative_valor(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        payload = {
            'descricao': 'Inválida',
            'valor': '0.00',
            'tipo': Movimentacao.TipoMovimentacao.RECEITA,
            'data': '2026-07-01',
            'categoria': self.cat_salario.id
        }
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('valor', response.data)

    def test_reject_categoria_de_outro_usuario(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        payload = {
            'descricao': 'Tentativa Inválida',
            'valor': '100.00',
            'tipo': Movimentacao.TipoMovimentacao.RECEITA,
            'data': '2026-07-01',
            'categoria': self.cat_user2.id  # Pertence ao user2
        }
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_categoria_tipo_incompativel(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        payload = {
            'descricao': 'Incompatível',
            'valor': '100.00',
            'tipo': Movimentacao.TipoMovimentacao.RECEITA,
            'data': '2026-07-01',
            'categoria': self.cat_alimentacao.id  # É do tipo DESPESA
        }
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_movimentacoes_isolation_and_filters(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        # Cria 2 movimentações para o user1
        Movimentacao.objects.create(
            usuario=self.user1,
            descricao='Freela Web',
            valor=Decimal('1200.00'),
            tipo=Movimentacao.TipoMovimentacao.RECEITA,
            data=date(2026, 7, 10),
            categoria=self.cat_salario
        )
        Movimentacao.objects.create(
            usuario=self.user1,
            descricao='Almoço Restaurante',
            valor=Decimal('60.00'),
            tipo=Movimentacao.TipoMovimentacao.DESPESA,
            data=date(2026, 7, 12),
            categoria=self.cat_alimentacao
        )

        # Listar todas (deve retornar 2)
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

        # Filtrar por tipo DESPESA
        res_despesa = self.client.get(f"{self.list_url}?tipo=DESPESA")
        self.assertEqual(len(res_despesa.data), 1)
        self.assertEqual(res_despesa.data[0]['descricao'], 'Almoço Restaurante')

        # Busca por palavra-chave 'Freela'
        res_search = self.client.get(f"{self.list_url}?search=Freela")
        self.assertEqual(len(res_search.data), 1)

    def test_export_csv(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        Movimentacao.objects.create(
            usuario=self.user1,
            descricao='Venda de Item',
            valor=Decimal('150.00'),
            tipo=Movimentacao.TipoMovimentacao.RECEITA,
            data=date(2026, 7, 14),
            categoria=self.cat_salario
        )
        response = self.client.get(self.export_csv_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('Venda de Item', response.content.decode('utf-8'))

    def test_parcelamento_and_config_cartao_endpoints(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Test Cartão POST & GET (Multi-tenant)
        cartao_url = reverse('finance:cartao-list')
        cartao_payload = {
            'apelido': 'Nubank Black',
            'ultimos_digitos': '1234',
            'limite_cartao': '8000.00',
            'dia_fechamento': 5,
            'dia_vencimento': 12,
            'meta_fatura_mensal': '2500.00',
            'reducao_mensal_desejada': '300.00'
        }
        res_c = self.client.post(cartao_url, cartao_payload)
        self.assertEqual(res_c.status_code, status.HTTP_201_CREATED)
        cartao_id = res_c.data['id']
        self.assertEqual(res_c.data['nome_exibicao'], 'Nubank Black (**** 1234)')

        # User2 isolation test
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)
        res_user2 = self.client.get(cartao_url)
        self.assertEqual(len(res_user2.data), 0)

        # Voltar credenciais para User1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)

        # Test Parcelamento Create com vinculo de Cartão
        parc_url = reverse('finance:parcelamento-list')
        parc_payload = {
            'descricao': 'Notebook Novo',
            'valor_total': '3600.00',
            'num_parcelas': 12,
            'data_primeira_parcela': '2026-08-10',
            'categoria': self.cat_alimentacao.id,
            'cartao': cartao_id
        }
        res_parc = self.client.post(parc_url, parc_payload)
        self.assertEqual(res_parc.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(res_parc.data['valor_parcela']), Decimal('300.00'))
        self.assertEqual(res_parc.data['cartao_nome'], 'Nubank Black (**** 1234)')


