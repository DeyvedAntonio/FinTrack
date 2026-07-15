from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

User = get_user_model()


class ProfileAndAuthenticationAPITestCase(APITestCase):

    def setUp(self):
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        self.logout_url = reverse('accounts:logout')
        self.profile_url = reverse('accounts:profile')
        self.change_password_url = reverse('accounts:change_password')

        self.user = User.objects.create_user(
            username='joao@example.com',
            email='joao@example.com',
            password='SenhaSegura123!',
            first_name='João Silva',
            moeda='BRL'
        )
        self.user2 = User.objects.create_user(
            username='maria@example.com',
            email='maria@example.com',
            password='SenhaSegura123!',
            first_name='Maria Souza',
            moeda='USD'
        )
        self.token, _ = Token.objects.get_or_create(user=self.user)

    def test_get_profile_unauthenticated(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'joao@example.com')
        self.assertEqual(response.data['nome'], 'João Silva')
        self.assertEqual(response.data['moeda'], 'BRL')

    def test_update_profile_success(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        update_data = {
            'nome': 'João Silva Sauro',
            'email': 'joaosilva@example.com',
            'moeda': 'EUR'
        }
        response = self.client.patch(self.profile_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Perfil atualizado com sucesso.')
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'João Silva Sauro')
        self.assertEqual(self.user.email, 'joaosilva@example.com')
        self.assertEqual(self.user.moeda, 'EUR')

    def test_update_profile_existing_email(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        update_data = {
            'email': 'maria@example.com'  # E-mail já utilizado pelo user2
        }
        response = self.client.patch(self.profile_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_change_password_success(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        payload = {
            'old_password': 'SenhaSegura123!',
            'new_password': 'NovaSenhaSegura456!',
            'confirm_new_password': 'NovaSenhaSegura456!'
        }
        response = self.client.post(self.change_password_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Senha alterada com sucesso.')
        
        # Limpar cabeçalho com o token antigo antes de autenticar novamente via login endpoint
        self.client.credentials()

        login_response = self.client.post(self.login_url, {
            'email': 'joao@example.com',
            'password': 'NovaSenhaSegura456!'
        })
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('token', login_response.data)

    def test_change_password_wrong_old_password(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        payload = {
            'old_password': 'SenhaErrada123!',
            'new_password': 'NovaSenhaSegura456!',
            'confirm_new_password': 'NovaSenhaSegura456!'
        }
        response = self.client.post(self.change_password_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_mismatch(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        payload = {
            'old_password': 'SenhaSegura123!',
            'new_password': 'NovaSenhaSegura456!',
            'confirm_new_password': 'OutraSenhaDiferente!'
        }
        response = self.client.post(self.change_password_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
