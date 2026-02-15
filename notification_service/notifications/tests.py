from django.test import TestCase, override_settings
from rest_framework.test import APIClient
import jwt
from datetime import datetime, timedelta
from django.conf import settings

from .models import Notification


TEST_DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}


def make_token(user_id=1, username='testuser'):
    """Создание тестового JWT-токена."""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')


@override_settings(DATABASES=TEST_DATABASES)
class NotificationModelTest(TestCase):
    """Тесты модели Notification."""

    def test_create_notification(self):
        """Тест создания уведомления."""
        notif = Notification.objects.create(
            event_type=Notification.EventType.TASK_CREATED,
            recipient_id=1,
            sender_id=2,
            title='Новая задача',
            message='Создана задача: Тестовая задача',
        )
        self.assertEqual(notif.event_type, 'task_created')
        self.assertFalse(notif.is_read)
        self.assertIn('task_created', str(notif))

    def test_notification_default_read_status(self):
        """Тест статуса прочтения по умолчанию."""
        notif = Notification.objects.create(
            event_type='task_created',
            recipient_id=1,
            title='Test',
            message='Test message',
        )
        self.assertFalse(notif.is_read)


@override_settings(DATABASES=TEST_DATABASES)
class NotificationAPITest(TestCase):
    """Тесты API уведомлений."""

    def setUp(self):
        self.client = APIClient()
        self.token = make_token(user_id=1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_list_notifications(self):
        """Тест получения списка уведомлений."""
        Notification.objects.create(
            event_type='task_created',
            recipient_id=1,
            title='Уведомление 1',
            message='Сообщение 1',
        )
        Notification.objects.create(
            event_type='task_created',
            recipient_id=2,
            title='Уведомление 2',
            message='Сообщение 2',
        )
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, 200)
        # Должно показать только уведомления для user_id=1
        results = response.data if isinstance(response.data, list) else response.data.get('results', [])
        self.assertEqual(len(results), 1)

    def test_create_notification(self):
        """Тест создания уведомления через API."""
        data = {
            'event_type': 'task_created',
            'task_id': 1,
            'title': 'Тестовая задача',
            'project_id': 1,
            'creator_id': 1,
        }
        response = self.client.post('/api/notifications/create/', data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_unread_count(self):
        """Тест подсчёта непрочитанных уведомлений."""
        Notification.objects.create(
            event_type='task_created', recipient_id=1,
            title='N1', message='M1', is_read=False,
        )
        Notification.objects.create(
            event_type='task_created', recipient_id=1,
            title='N2', message='M2', is_read=True,
        )
        response = self.client.get('/api/notifications/unread-count/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 1)

    def test_mark_all_read(self):
        """Тест отметки всех уведомлений как прочитанных."""
        Notification.objects.create(
            event_type='task_created', recipient_id=1,
            title='N1', message='M1', is_read=False,
        )
        Notification.objects.create(
            event_type='task_created', recipient_id=1,
            title='N2', message='M2', is_read=False,
        )
        response = self.client.post('/api/notifications/read-all/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['marked_read'], 2)

    def test_mark_single_read(self):
        """Тест отметки одного уведомления как прочитанного."""
        notif = Notification.objects.create(
            event_type='task_created', recipient_id=1,
            title='N1', message='M1', is_read=False,
        )
        response = self.client.post(f'/api/notifications/{notif.id}/read/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['is_read'])

    def test_unauthenticated_access(self):
        """Тест доступа без авторизации."""
        client = APIClient()
        response = client.get('/api/notifications/')
        self.assertEqual(response.status_code, 403)
