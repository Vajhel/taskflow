from django.db import models


class Notification(models.Model):
    """Модель уведомления."""

    class EventType(models.TextChoices):
        TASK_CREATED = 'task_created', 'Задача создана'
        TASK_STATUS_CHANGED = 'task_status_changed', 'Статус задачи изменён'
        TASK_ASSIGNED = 'task_assigned', 'Задача назначена'
        COMMENT_ADDED = 'comment_added', 'Добавлен комментарий'
        PROJECT_CREATED = 'project_created', 'Проект создан'

    event_type = models.CharField(
        'Тип события', max_length=50,
        choices=EventType.choices,
    )
    recipient_id = models.IntegerField('ID получателя')
    sender_id = models.IntegerField('ID отправителя', null=True, blank=True)
    title = models.CharField('Заголовок', max_length=300)
    message = models.TextField('Сообщение')
    is_read = models.BooleanField('Прочитано', default=False)
    metadata = models.JSONField('Метаданные', default=dict, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.event_type}] {self.title}"
