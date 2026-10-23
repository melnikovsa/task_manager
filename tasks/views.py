from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Task, Comment
from .serializers import TaskSerializer, CommentSerializer


class IsAuthorOrAssigneeOrReadOnly(permissions.BasePermission):
    """
    Кастомное разрешение: редактировать задачу может только автор или исполнитель.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем безопасные методы (GET, HEAD, OPTIONS) для всех
        if request.method in permissions.SAFE_METHODS:
            return True

        # Редактировать/удалять (PUT, PATCH, DELETE) могут только автор или исполнитель
        return obj.author == request.user or obj.assignee == request.user


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrAssigneeOrReadOnly]

    def perform_create(self, serializer):
        # Автоматически назначаем текущего пользователя автором задачи
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def toggle_complete(self, request, pk=None):
        """Быстрое переключение статуса выполнения задачи (Выполнено/Не выполнено)"""
        task = self.get_object()
        task.is_completed = not task.is_completed
        task.save()
        return Response({'status': 'status updated', 'is_completed': task.is_completed}, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Позволяет фильтровать комментарии по id задачи: /api/comments/?task=1
        queryset = Comment.objects.all()
        task_id = self.request.query_params.get('task')
        if task_id is not None:
            queryset = queryset.filter(task_id=task_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
