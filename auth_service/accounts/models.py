from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Расширенная модель пользователя."""
    patronymic = models.CharField('Отчество', max_length=150, blank=True)
    position = models.CharField('Должность', max_length=200, blank=True)
    department = models.CharField('Отдел', max_length=200, blank=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.last_name} {self.first_name}" if self.last_name else self.username
