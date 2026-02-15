from django.test import TestCase, RequestFactory
from unittest.mock import patch, MagicMock
from django.test import Client


class FrontendViewsTest(TestCase):
    """Тесты представлений фронтенда."""

    def setUp(self):
        self.client = Client()

    def test_index_page(self):
        """Тест главной страницы."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TaskFlow')

    def test_login_page(self):
        """Тест страницы входа."""
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Войдите в систему')

    def test_register_page(self):
        """Тест страницы регистрации."""
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Создайте аккаунт')

    def test_dashboard_redirect_unauthenticated(self):
        """Тест редиректа неавторизованного пользователя с дашборда."""
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/')

    def test_projects_redirect_unauthenticated(self):
        """Тест редиректа неавторизованного пользователя со страницы проектов."""
        response = self.client.get('/projects/')
        self.assertEqual(response.status_code, 302)

    def test_tasks_redirect_unauthenticated(self):
        """Тест редиректа неавторизованного пользователя со страницы задач."""
        response = self.client.get('/tasks/')
        self.assertEqual(response.status_code, 302)

    def test_logout(self):
        """Тест выхода из системы."""
        session = self.client.session
        session['token'] = 'test-token'
        session.save()
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 302)

    @patch('web.views.auth_client')
    def test_login_success(self, mock_auth):
        """Тест успешного входа."""
        mock_auth.login.return_value = (
            {
                'token': 'test-token-123',
                'user': {'id': 1, 'username': 'testuser', 'first_name': 'Иван'},
            },
            200,
        )
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)

    @patch('web.views.auth_client')
    def test_login_failure(self, mock_auth):
        """Тест неудачного входа."""
        mock_auth.login.return_value = (
            {'error': 'Неверные учётные данные.'},
            401,
        )
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)

    @patch('web.views.auth_client')
    def test_register_success(self, mock_auth):
        """Тест успешной регистрации."""
        mock_auth.register.return_value = (
            {
                'token': 'new-token-123',
                'user': {'id': 2, 'username': 'newuser'},
            },
            201,
        )
        response = self.client.post('/register/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
        })
        self.assertEqual(response.status_code, 302)
