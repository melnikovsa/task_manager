from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.serializers import UserShortSerializer
from .models import Task, Comment

User = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для комментариев к задачам.
    """
    # Чтение возвращает объект пользователя, а при записи достаточно передать ID
    author = UserShortSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'task', 'author', 'text', 'created_at')
        read_only_fields = ('author', 'created_at')


class TaskSerializer(serializers.ModelSerializer):
    """
    Сериализатор для управления задачами.
    """
    author = UserShortSerializer(read_only=True)
    # Позволяет назначать исполнителя по ID при записи, но возвращает объект при чтении
    assignee_detail = UserShortSerializer(source='assignee', read_only=True)
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    # Вложенные комментарии к задаче (только для чтения)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = (
            'id', 'title', 'description', 'is_completed',
            'author', 'assignee', 'assignee_detail',
            'created_at', 'updated_at', 'comments'
        )
        read_only_fields = ('author', 'created_at', 'updated_at', 'comments')

    def to_representation(self, instance):
        """Добавляет поле assignee в вывод, если оно заполнено"""
        representation = super().to_representation(instance)
        # Если у задачи есть исполнитель, подменяем вывод на детальный объект
        if instance.assignee:
            representation['assignee'] = UserShortSerializer(instance.assignee).data
        else:
            representation['assignee'] = None
        # Убираем временное поле из финального ответа
        representation.pop('assignee_detail', None)
        return representation
