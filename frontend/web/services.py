"""Сервисный слой для взаимодействия с микросервисами через REST API."""
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class AuthServiceClient:
    """Клиент для взаимодействия с auth_service."""

    def __init__(self):
        self.base_url = settings.AUTH_SERVICE_URL

    def register(self, data):
        resp = requests.post(f'{self.base_url}/api/auth/register/', json=data, timeout=10)
        return resp.json(), resp.status_code

    def login(self, username, password):
        resp = requests.post(
            f'{self.base_url}/api/auth/login/',
            json={'username': username, 'password': password},
            timeout=10,
        )
        return resp.json(), resp.status_code

    def get_profile(self, token):
        resp = requests.get(
            f'{self.base_url}/api/auth/profile/',
            headers={'Authorization': f'Bearer {token}'},
            timeout=10,
        )
        return resp.json(), resp.status_code

    def update_profile(self, token, data):
        resp = requests.patch(
            f'{self.base_url}/api/auth/profile/update/',
            json=data,
            headers={'Authorization': f'Bearer {token}'},
            timeout=10,
        )
        return resp.json(), resp.status_code

    def get_users(self, token):
        resp = requests.get(
            f'{self.base_url}/api/auth/users/',
            headers={'Authorization': f'Bearer {token}'},
            timeout=10,
        )
        return resp.json(), resp.status_code


class TaskServiceClient:
    """Клиент для взаимодействия с task_service."""

    def __init__(self):
        self.base_url = settings.TASK_SERVICE_URL

    def _headers(self, token):
        return {'Authorization': f'Bearer {token}'}

    # --- Проекты ---
    def get_projects(self, token):
        resp = requests.get(
            f'{self.base_url}/api/tasks/projects/',
            headers=self._headers(token), timeout=10,
        )
        return resp.json(), resp.status_code

    def get_project(self, token, project_id):
        resp = requests.get(
            f'{self.base_url}/api/tasks/projects/{project_id}/',
            headers=self._headers(token), timeout=10,
        )
        return resp.json(), resp.status_code

    def create_project(self, token, data):
        resp = requests.post(
            f'{self.base_url}/api/tasks/projects/',
            json=data, headers=self._headers(token), timeout=10,
        )
        return resp.json(), resp.status_code

    def update_project(self, token, project_id, data):
        resp = requests.patch(
            f'{self.base_url}/api/tasks/projects/{project_id}/',
            json=data, headers=self._headers(token), timeout=10,
        )
        return resp.json(), resp.status_code

    def delete_project(self, token, project_id):
        resp = requests.delete(
            f'{self.base_url}/api/tasks/projects/{project_id}/',
            headers=self._headers(token), timeout=10,
        )
        return resp.status_code

    def get_project_statistics(self, token, project_id):
        resp = requests.get(
            f'{self.base_url}/api/tasks/projects/{project_id}/statistics/',
            headers=self._headers(token), timeout=10,
        )
        return resp.json(), resp.status_code

    # --- Задачи ---
    def get_tasks(self, token, **params):
        resp = requests.get(
            f'{self.base_url}/api/tasks/tasks/',
            params=params, headers=self._headers(token), timeout=10,
        )
        return resp.json(), resp.status_code

    def get_task(self, token, task_id):
        resp = requests.get(
            f'{self.base_url}/api/tasks/tasks/{task_id}/',
            headers=self._headers(token), timeout=10,
        )
        return resp.json(), resp.status_code

    def create_task(self, token, data):
        resp = requests.post(
            f'{self.base_url}/api/tasks/tasks/',
            json=data, headers=self._headers(token), timeout=10,
        )
        return resp.json(), resp.status_code

    def update_task(self, token, task_id, data):
        resp = requests.patch(
            f'{self.base_url}/api/tasks/tasks/{task_id}/',
            json=data, headers=self._headers(token), timeout=10,
        )
        return resp.json(), resp.status_code

    def delete_task(self, token, task_id):
        resp = requests.delete(
            f'{self.base_url}/api/tasks/tasks/{task_id}/',
            headers=self._headers(token), timeout=10,
        )
        return resp.status_code

    # --- Комментарии ---
    def add_comment(self, token, task_id, text):
        resp = requests.post(
            f'{self.base_url}/api/tasks/tasks/{task_id}/comments/',
            json={'text': text},
            headers=self._headers(token), timeout=10,
        )
        return resp.json(), resp.status_code


class NotificationServiceClient:
    """Клиент для взаимодействия с notification_service."""

    def __init__(self):
        self.base_url = settings.NOTIFICATION_SERVICE_URL

    def _headers(self, token):
        return {'Authorization': f'Bearer {token}'}

    def get_notifications(self, token):
        resp = requests.get(
            f'{self.base_url}/api/notifications/',
            headers=self._headers(token), timeout=10,
        )
        return resp.json(), resp.status_code

    def get_unread_count(self, token):
        resp = requests.get(
            f'{self.base_url}/api/notifications/unread-count/',
            headers=self._headers(token), timeout=10,
        )
        return resp.json(), resp.status_code

    def mark_all_read(self, token):
        resp = requests.post(
            f'{self.base_url}/api/notifications/read-all/',
            headers=self._headers(token), timeout=10,
        )
        return resp.json(), resp.status_code


auth_client = AuthServiceClient()
task_client = TaskServiceClient()
notification_client = NotificationServiceClient()
