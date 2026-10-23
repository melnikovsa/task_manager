from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, CommentViewSet

# Инициализируем роутер DRF
router = DefaultRouter()

# Регистрируем эндпоинты для задач (/api/tasks/) и комментариев (/api/comments/)
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    # Подключаем автоматически сгенерированные маршруты роутера
    path('', include(router.urls)),
]
