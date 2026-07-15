from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

User = get_user_model()


class AuthenticationAPITestCase(APITestCase):

    def setUp(self):
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        self.logout_url = reverse('accounts:logout')
        self.profile_url = reverse('accounts:profile')

        self.user_data = {
            'nome': 'João Silva',
            'email': 'joao@example.com',
            'password': 'SenhaSegura123!',
            'confirm_password': 'SenhaSegura123!'
        }
        self.user = User.objects.create_user(
            username='joao@example.com',
            email='joao@example.com',
            password='SenhaSegura123!',
            first_name='João Silva',
            moeda='BRL'
        )

    def test_user_registration_success(self):
        data = {
            'nome': 'Maria Oliveira',
            'email': 'maria@example.com',
            'password': 'SenhaForte456!',
            'confirm_password': 'SenhaForte456!'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(User.objects.filter(email='maria@example.com').count(), 1)

    def test_user_registration_duplicate_email(self):
        data = {
            'nome': 'Outro João',
            'email': 'joao@example.com',
            'password': 'OutraSenha123!',
            'confirm_password': 'OutraSenha123!'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_success(self):
        data = {
            'email': 'joao@example.com',
            'password': 'SenhaSegura123!'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_user_login_invalid_credentials(self):
        data = {
            'email': 'joao@example.com',
            'password': 'SenhaIncorreta!'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_profile_authenticated(self):
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'joao@example.com')

    def test_update_profile(self):
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        update_data = {
            'nome': 'João Silva Atualizado',
            'email': 'joao@example.com',
            'moeda': 'USD'
        }
        response = self.client.patch(self.profile_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'João Silva Atualizado')
        self.assertEqual(self.user.moeda, 'USD')

    def test_logout(self):
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Token.objects.filter(user=self.user).exists())
