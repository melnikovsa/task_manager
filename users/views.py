from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .serializers import UserRegisterSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    Эндпоинт для регистрации нового пользователя в системе.
    """
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]  # Доступно без авторизации
