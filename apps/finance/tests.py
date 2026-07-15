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
            'forma_pagamento': 'Cartão de Débito'
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
