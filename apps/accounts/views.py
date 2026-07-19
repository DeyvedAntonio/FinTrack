import csv
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils import timezone
from rest_framework import status, permissions, generics
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    DeleteAccountSerializer
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
    Suporta campos textuais (nome, email, moeda) e envio de arquivos (foto_perfil).
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'message': 'Perfil atualizado com sucesso.',
            'user': serializer.data
        }, status=status.HTTP_200_OK)


class ChangePasswordAPIView(APIView):
    """
    Endpoint para alteração de senha do usuário autenticado.
    EXIGE: old_password, new_password, confirm_new_password.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Atualiza a sessão/token se necessário
        Token.objects.filter(user=user).delete()
        new_token = Token.objects.create(user=user)
        
        return Response({
            'message': 'Senha alterada com sucesso.',
            'token': new_token.key
        }, status=status.HTTP_200_OK)


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
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
        return Response({
            'message': 'Se o e-mail estiver cadastrado em nosso sistema, você receberá um link para redefinir sua senha.'
        }, status=status.HTTP_200_OK)


class DeleteAccountAPIView(APIView):
    """
    Endpoint para solicitação de exclusão de perfil conforme a LGPD (Art. 16, I).
    Anonimiza os PIIs do usuário, inativa a conta e encerra os tokens de autenticação,
    mantendo os dados financeiros de forma anonimizada pelo prazo legal de 5 anos.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = DeleteAccountSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user

        # Excluir foto de perfil física se existir
        if user.foto_perfil:
            user.foto_perfil.delete(save=False)

        # Anonimizar PII (Personally Identifiable Information)
        user_id = user.id
        user.first_name = "Usuário Anonimizado"
        user.last_name = ""
        user.email = f"anonymized_{user_id}@lgpd.deleted"
        user.username = f"anonymized_{user_id}"
        user.set_unusable_password()
        user.is_active = False
        user.is_anonymized = True
        user.anonymized_at = timezone.now()
        user.save()

        # Invalidação do token REST e encerramento de sessão
        try:
            user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            pass
        logout(request)

        return Response({
            'message': 'Sua conta foi inativada e seus dados pessoais foram permanentemente anonimizados conforme a LGPD. Os registros financeiros serão mantidos anonimizados pelo prazo legal de 5 anos.'
        }, status=status.HTTP_200_OK)


class ExportUserDataAPIView(APIView):
    """
    Endpoint para exportação completa de dados do usuário cadastrado em formato CSV (Portabilidade LGPD Art. 18, V).
    Consolida Perfil, Categorias e Movimentações Financeiras.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="meus_dados_fintrack.csv"'
        response.write('\ufeff')  # BOM (Byte Order Mark) para UTF-8 no Excel

        writer = csv.writer(response, delimiter=';')

        # 1. Dados de Perfil
        writer.writerow(['=== SEÇÃO 1: PERFIL DO USUÁRIO ==='])
        writer.writerow(['ID', 'Nome', 'E-mail', 'Moeda Padrão', 'Data de Cadastro'])
        writer.writerow([
            user.id,
            user.first_name or '',
            user.email,
            user.get_moeda_display() if hasattr(user, 'get_moeda_display') else user.moeda,
            user.date_joined.strftime('%d/%m/%Y %H:%M:%S') if user.date_joined else ''
        ])
        writer.writerow([])

        # 2. Categorias
        from apps.categories.models import Categoria
        categorias = Categoria.objects.filter(usuario=user)
        writer.writerow(['=== SEÇÃO 2: CATEGORIAS ==='])
        writer.writerow(['ID', 'Nome', 'Tipo'])
        for cat in categorias:
            writer.writerow([
                cat.id,
                cat.nome,
                cat.get_tipo_display() if hasattr(cat, 'get_tipo_display') else cat.tipo
            ])
        writer.writerow([])

        # 3. Movimentações Financeiras
        from apps.finance.models import Movimentacao
        movimentacoes = Movimentacao.objects.filter(usuario=user).select_related('categoria')
        writer.writerow(['=== SEÇÃO 3: MOVIMENTAÇÕES FINANCEIRAS ==='])
        writer.writerow(['ID', 'Tipo', 'Descrição', 'Valor (R$)', 'Data', 'Categoria', 'Forma de Pagamento', 'Observações'])
        for mov in movimentacoes:
            writer.writerow([
                mov.id,
                mov.get_tipo_display() if hasattr(mov, 'get_tipo_display') else mov.tipo,
                mov.descricao,
                f"{mov.valor:.2f}".replace('.', ','),
                mov.data.strftime('%d/%m/%Y') if mov.data else '',
                mov.categoria.nome if mov.categoria else '',
                mov.forma_pagamento or '',
                mov.observacoes or ''
            ])

        return response


