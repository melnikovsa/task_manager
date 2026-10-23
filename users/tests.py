from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UsersAPITests(APITestCase):

    def setUp(self):
        """
        Предварительное создание данных для тестов авторизации.
        """
        self.register_url = reverse('auth_register')
        self.token_url = reverse('token_obtain_pair')

        # Создаем тестового пользователя для проверки авторизации
        self.existing_user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="securepassword123"
        )

    # --- ТЕСТЫ РЕГИСТРАЦИИ ---

    def test_user_can_register_successfully(self):
        """Проверка: новый пользователь может успешно зарегистрироваться"""
        data = {
            "username": "new_user",
            "email": "new_user@example.com",
            "password": "mysecretpassword"
        }
        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)  # existing_user + new_user

        # Проверяем, что пароль не отдается в ответе в открытом виде
        self.assertNotIn('password', response.data)
        self.assertEqual(response.data['username'], "new_user")

    def test_registration_fails_with_existing_username(self):
        """Проверка: нельзя зарегистрироваться с уже занятым username"""
        data = {
            "username": "testuser",  # Уже существует в системе (создан в setUp)
            "email": "another_email@example.com",
            "password": "password123"
        }
        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_registration_fails_with_short_password(self):
        """Проверка: валидатор сериализатора отклоняет слишком короткий пароль"""
        data = {
            "username": "valid_username",
            "email": "valid_email@example.com",
            "password": "123"  # Меньше 6 символов, настроенных в сериализаторе
        }
        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    # --- ТЕСТЫ JWT-АВТОРИЗАЦИИ ---

    def test_user_can_obtain_jwt_tokens(self):
        """Проверка: пользователь получает access и refresh токены при верных учетных данных"""
        data = {
            "username": "testuser",
            "password": "securepassword123"
        }
        response = self.client.post(self.token_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Убеждаемся, что SimpleJWT вернул оба токена
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_fails_with_wrong_password(self):
        """Проверка: система возвращает 401 Unauthorized при неверном пароле"""
        data = {
            "username": "testuser",
            "password": "wrong_password_here"
        }
        response = self.client.post(self.token_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.data)
