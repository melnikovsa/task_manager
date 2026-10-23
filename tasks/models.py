from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Task(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_completed = models.BooleanField(default=False, verbose_name="Статус выполнения")

    # Автором задачи становится тот, кто её создал
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='created_tasks', verbose_name="Автор"
    )
    # Исполнитель, которому назначена задача
    assignee = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_tasks', verbose_name="Исполнитель"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

    def __str__(self):
        return self.title


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments', verbose_name="Задача")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор комментария")
    text = models.TextField(verbose_name="Текст комментария")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        ordering = ['created_at']
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return f"Комментарий от {self.author.username} к задаче {self.task.id}"
