from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from .models import Categoria

User = get_user_model()


class CategoriaAPITestCase(APITestCase):

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

        self.list_url = reverse('categories:categoria-list')

    def test_categorias_padrao_criadas_no_cadastro(self):
        # O signal deve ter criado as 10 categorias padrão para o user1
        categorias_count = Categoria.objects.filter(usuario=self.user1).count()
        self.assertEqual(categorias_count, 10)

    def test_list_categorias_user_isolation(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Deve listar apenas as categorias do user1
        self.assertEqual(len(response.data), 10)
        for cat in response.data:
            cat_obj = Categoria.objects.get(id=cat['id'])
            self.assertEqual(cat_obj.usuario, self.user1)

    def test_filter_categorias_by_tipo(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        response = self.client.get(f"{self.list_url}?tipo=RECEITA")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for cat in response.data:
            self.assertEqual(cat['tipo'], 'RECEITA')

    def test_create_categoria_success(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        payload = {
            'nome': 'Freelance',
            'tipo': Categoria.TipoCategoria.RECEITA
        }
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nome'], 'Freelance')
        self.assertEqual(Categoria.objects.filter(usuario=self.user1, nome='Freelance').count(), 1)

    def test_create_duplicate_categoria(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        payload = {
            'nome': 'Alimentação',
            'tipo': Categoria.TipoCategoria.DESPESA
        }
        # Tenta criar categoria com mesmo nome e tipo já existente
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_categoria(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        categoria = Categoria.objects.filter(usuario=self.user1, nome='Outros', tipo='DESPESA').first()
        detail_url = reverse('categories:categoria-detail', kwargs={'pk': categoria.pk})
        
        payload = {'nome': 'Outras Despesas Variadas', 'tipo': 'DESPESA'}
        response = self.client.put(detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        categoria.refresh_from_db()
        self.assertEqual(categoria.nome, 'Outras Despesas Variadas')

    def test_delete_categoria_sem_movimentacoes(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        categoria = Categoria.objects.filter(usuario=self.user1, nome='Lazer').first()
        detail_url = reverse('categories:categoria-detail', kwargs={'pk': categoria.pk})

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Categoria.objects.filter(pk=categoria.pk).exists())
