from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Task, Comment

User = get_user_model()


class TaskManagerAPITests(APITestCase):

    def setUp(self):
        """
        Предварительное создание данных для тестов.
        Выполняется перед каждым тестовым методом.
        """
        # Создаем двух пользователей
        self.user1 = User.objects.create_user(
            username="ivan_author",
            email="ivan@example.com",
            password="securepassword123"
        )
        self.user2 = User.objects.create_user(
            username="petr_assignee",
            email="petr@example.com",
            password="securepassword123"
        )

        # Создаем тестовую задачу, где автор — user1, исполнитель — user2
        self.task = Task.objects.create(
            title="Тестовая задача",
            description="Описание тестовой задачи",
            author=self.user1,
            assignee=self.user2
        )

        # URLs для эндпоинтов задач
        self.task_list_url = reverse('task-list')
        self.task_detail_url = reverse('task-detail', kwargs={'pk': self.task.pk})
        self.task_toggle_url = reverse('task-toggle-complete', kwargs={'pk': self.task.pk})

        # URL для эндпоинта комментариев
        self.comment_list_url = reverse('comment-list')

    def authenticate_user(self, user):
        """Вспомогательный метод для JWT-авторизации пользователя в тестах"""
        token_url = reverse('token_obtain_pair')
        response = self.client.post(token_url, {
            'username': user.username,
            'password': 'securepassword123'
        }, format='json')
        access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # --- ТЕСТЫ ДОСТУПА И АВТОРnetworkИЗАЦИИ ---

    def test_anonymous_user_cannot_create_task(self):
        """Проверка: анонимный пользователь получает 401 Unauthorized при создании задачи"""
        data = {'title': 'Анонимная задача'}
        response = self.client.post(self.task_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- ТЕСТЫ ОПЕРАЦИЙ С ЗАДАЧАМИ (CRUD) ---

    def test_authenticated_user_can_create_task(self):
        """Проверка: авторизованный пользователь может успешно создать задачу"""
        self.authenticate_user(self.user1)
        data = {
            'title': 'Новая важная задача',
            'description': 'Сделать до пятницы',
            'assignee': self.user2.id
        }
        response = self.client.post(self.task_list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)
        # Проверяем, что автором автоматически проставился авторизованный юзер
        self.assertEqual(Task.objects.latest('id').author, self.user1)

    def test_author_can_update_task(self):
        """Проверка: автор задачи имеет право изменять её содержимое"""
        self.authenticate_user(self.user1)
        data = {'title': 'Измененное название'}
        response = self.client.patch(self.task_detail_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Измененное название')

    def test_non_related_user_cannot_update_task(self):
        """Проверка: посторонний пользователь (не автор и не исполнитель) получает 403 Forbidden"""
        # Создаем третьего юзера с таким же паролем, как у остальных (securepassword123)
        stranger_user = User.objects.create_user(
            username="stranger",
            email="stranger@example.com",
            password="securepassword123"  # <-- Исправлено здесь!
        )
        self.authenticate_user(stranger_user)

        data = {'title': 'Попытка взлома'}
        response = self.client.patch(self.task_detail_url, data, format='json')
        # Так как кастомный пермишен возвращает False, ожидаем 403 ошибку
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_toggle_task_complete_status(self):
        """Проверка: кастомный метод изменения статуса выполнения (выполнено / не выполнено) работает корректно"""
        self.authenticate_user(self.user1)

        # Изначально задача не выполнена (is_completed=False)
        self.assertFalse(self.task.is_completed)

        # Отправляем запрос на переключение статуса
        response = self.client.post(self.task_toggle_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.task.refresh_from_db()
        self.assertTrue(self.task.is_completed)

    # --- ТЕСТЫ КОММЕНТАРИЕВ ---

    def test_authenticated_user_can_comment_task(self):
        """Проверка: авторизованный пользователь может оставить комментарий к задаче"""
        self.authenticate_user(self.user2)

        data = {
            'task': self.task.id,
            'text': 'Это отличная задача, я приступаю к выполнению!'
        }
        response = self.client.post(self.comment_list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)

        comment = Comment.objects.first()
        self.assertEqual(comment.author, self.user2)
        self.assertEqual(comment.task, self.task)
