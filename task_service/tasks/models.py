from django.db import models


class Project(models.Model):
    """Модель проекта."""

    class Status(models.TextChoices):
        PLANNING = 'planning', 'Планирование'
        ACTIVE = 'active', 'Активный'
        ON_HOLD = 'on_hold', 'Приостановлен'
        COMPLETED = 'completed', 'Завершён'
        CANCELLED = 'cancelled', 'Отменён'

    name = models.CharField('Название', max_length=300)
    description = models.TextField('Описание', blank=True)
    status = models.CharField(
        'Статус', max_length=20,
        choices=Status.choices, default=Status.PLANNING,
    )
    owner_id = models.IntegerField('ID владельца')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    deadline = models.DateTimeField('Крайний срок', null=True, blank=True)

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Task(models.Model):
    """Модель задачи."""

    class Priority(models.TextChoices):
        LOW = 'low', 'Низкий'
        MEDIUM = 'medium', 'Средний'
        HIGH = 'high', 'Высокий'
        CRITICAL = 'critical', 'Критический'

    class Status(models.TextChoices):
        TODO = 'todo', 'К выполнению'
        IN_PROGRESS = 'in_progress', 'В работе'
        REVIEW = 'review', 'На проверке'
        DONE = 'done', 'Выполнена'
        CANCELLED = 'cancelled', 'Отменена'

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE,
        related_name='tasks', verbose_name='Проект',
    )
    title = models.CharField('Заголовок', max_length=300)
    description = models.TextField('Описание', blank=True)
    priority = models.CharField(
        'Приоритет', max_length=20,
        choices=Priority.choices, default=Priority.MEDIUM,
    )
    status = models.CharField(
        'Статус', max_length=20,
        choices=Status.choices, default=Status.TODO,
    )
    assignee_id = models.IntegerField('ID исполнителя', null=True, blank=True)
    creator_id = models.IntegerField('ID автора')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    deadline = models.DateTimeField('Крайний срок', null=True, blank=True)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Модель комментария к задаче."""
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE,
        related_name='comments', verbose_name='Задача',
    )
    author_id = models.IntegerField('ID автора')
    text = models.TextField('Текст комментария')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

    def __str__(self):
        return f"Комментарий к задаче #{self.task_id}"
