from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='first_name', required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('id', 'nome', 'email', 'moeda', 'foto_perfil', 'date_joined')
        read_only_fields = ('id', 'date_joined')

    def validate_email(self, value):
        user = self.instance
        if user and User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("Este e-mail já está sendo utilizado por outro usuário.")
        return value

    def update(self, instance, validated_data):
        email = validated_data.get('email', instance.email)
        if email != instance.email:
            instance.username = email
        return super().update(instance, validated_data)


class RegisterSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('nome', 'email', 'password', 'confirm_password')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("E-mail já cadastrado.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "As senhas não conferem."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        nome = validated_data.pop('nome')
        email = validated_data['email']
        
        user = User.objects.create_user(
            username=email,
            email=email,
            password=validated_data['password'],
            first_name=nome
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), username=email, password=password)
            if not user:
                try:
                    user_obj = User.objects.get(email=email)
                    user = authenticate(request=self.context.get('request'), username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None

            if not user:
                raise serializers.ValidationError("E-mail ou senha inválidos.", code='authorization')
            if not user.is_active:
                raise serializers.ValidationError("Conta de usuário desativada.", code='authorization')
        else:
            raise serializers.ValidationError("É necessário informar e-mail e senha.", code='authorization')

        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_new_password = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("A senha atual informada está incorreta.")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({"new_password": "A nova senha e a confirmação não conferem."})
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError({"new_password": "A nova senha deve ser diferente da senha atual."})
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, write_only=True)

    def validate_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("A senha informada está incorreta.")
        return value

