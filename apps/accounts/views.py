from django.contrib.auth import get_user_model, logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status, permissions, generics
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    PasswordResetRequestSerializer
)

User = get_user_model()


class RegisterAPIView(generics.CreateAPIView):
    """
    Endpoint para cadastro de novo usuário.
    RETORNO: Dados do usuário criado e o Token de autenticação.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        token, _ = Token.objects.get_or_create(user=user)
        user_data = UserSerializer(user, context={'request': request}).data
        
        return Response({
            'message': 'Cadastro realizado com sucesso.',
            'user': user_data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    """
    Endpoint para autenticação/login de usuário.
    RETORNO: Dados do usuário e Token de sessão/API.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        token, _ = Token.objects.get_or_create(user=user)
        user_data = UserSerializer(user, context={'request': request}).data
        
        return Response({
            'message': 'Login realizado com sucesso.',
            'user': user_data,
            'token': token.key
        }, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    """
    Endpoint para desautenticação/logout. Deleta o token atual do usuário.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            request.user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            pass
        logout(request)
        return Response({'message': 'Logout realizado com sucesso.'}, status=status.HTTP_200_OK)


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    """
    Endpoint para consultar e atualizar os dados do perfil do usuário autenticado.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class PasswordResetAPIView(APIView):
    """
    Endpoint para solicitar redefinição de senha via e-mail.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        users = User.objects.filter(email__iexact=email, is_active=True)
        if users.exists():
            for user in users:
                # Gera o token de reset e uids
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                # Aqui o e-mail de recuperação pode ser enviado
                
        return Response({
            'message': 'Se o e-mail estiver cadastrado em nosso sistema, você receberá um link para redefinir sua senha.'
        }, status=status.HTTP_200_OK)
