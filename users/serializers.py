from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя.
    """
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        # Метод create_user автоматически захэширует пароль в БД
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class UserShortSerializer(serializers.ModelSerializer):
    """
    Упрощенный сериализатор для отображения базовой информации о пользователе
    внутри задач и комментариев.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
