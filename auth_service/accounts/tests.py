from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from .models import User
from .authentication import generate_token, decode_token


TEST_DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}


@override_settings(DATABASES=TEST_DATABASES)
class UserModelTest(TestCase):
    """Тесты модели User."""

    def test_create_user(self):
        """Тест создания пользователя."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Иван',
            last_name='Петров',
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)

    def test_user_str(self):
        """Тест строкового представления пользователя."""
        user = User.objects.create_user(
            username='testuser',
            first_name='Иван',
            last_name='Петров',
            password='testpass123',
        )
        self.assertEqual(str(user), 'Петров Иван')

    def test_user_str_no_name(self):
        """Тест строкового представления без фамилии."""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
        )
        self.assertEqual(str(user), 'testuser')


@override_settings(DATABASES=TEST_DATABASES)
class JWTTokenTest(TestCase):
    """Тесты JWT-токенов."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
        )

    def test_generate_token(self):
        """Тест генерации токена."""
        token = generate_token(self.user)
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)

    def test_decode_token(self):
        """Тест декодирования токена."""
        token = generate_token(self.user)
        payload = decode_token(token)
        self.assertEqual(payload['user_id'], self.user.id)
        self.assertEqual(payload['username'], self.user.username)


@override_settings(DATABASES=TEST_DATABASES)
class AuthAPITest(TestCase):
    """Тесты API аутентификации."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.token = generate_token(self.user)

    def test_register(self):
        """Тест регистрации нового пользователя."""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
        }
        response = self.client.post(reverse('register'), data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)

    def test_register_password_mismatch(self):
        """Тест регистрации с несовпадающими паролями."""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password_confirm': 'different',
        }
        response = self.client.post(reverse('register'), data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_login_success(self):
        """Тест успешного входа."""
        data = {
            'username': 'testuser',
            'password': 'testpass123',
        }
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_login_wrong_password(self):
        """Тест входа с неверным паролем."""
        data = {
            'username': 'testuser',
            'password': 'wrongpass',
        }
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_profile_authenticated(self):
        """Тест получения профиля авторизованным пользователем."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'testuser')

    def test_profile_unauthenticated(self):
        """Тест получения профиля без авторизации."""
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 403)

    def test_validate_token(self):
        """Тест валидации токена."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.post(reverse('validate-token'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['valid'])

    def test_user_list(self):
        """Тест получения списка пользователей."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, 200)
