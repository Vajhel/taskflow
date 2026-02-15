from django.test import TestCase, override_settings
from rest_framework.test import APIClient
import jwt
from datetime import datetime, timedelta
from django.conf import settings

from .models import Project, Task, Comment


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
class ProjectModelTest(TestCase):
    """Тесты модели Project."""

    def test_create_project(self):
        """Тест создания проекта."""
        project = Project.objects.create(
            name='Тестовый проект',
            description='Описание тестового проекта',
            owner_id=1,
        )
        self.assertEqual(project.name, 'Тестовый проект')
        self.assertEqual(project.status, Project.Status.PLANNING)
        self.assertEqual(str(project), 'Тестовый проект')

    def test_project_statuses(self):
        """Тест статусов проекта."""
        project = Project.objects.create(name='Проект', owner_id=1)
        project.status = Project.Status.ACTIVE
        project.save()
        project.refresh_from_db()
        self.assertEqual(project.status, 'active')


@override_settings(DATABASES=TEST_DATABASES)
class TaskModelTest(TestCase):
    """Тесты модели Task."""

    def setUp(self):
        self.project = Project.objects.create(
            name='Тестовый проект', owner_id=1,
        )

    def test_create_task(self):
        """Тест создания задачи."""
        task = Task.objects.create(
            project=self.project,
            title='Тестовая задача',
            description='Описание задачи',
            creator_id=1,
        )
        self.assertEqual(task.title, 'Тестовая задача')
        self.assertEqual(task.status, Task.Status.TODO)
        self.assertEqual(task.priority, Task.Priority.MEDIUM)
        self.assertEqual(str(task), 'Тестовая задача')

    def test_task_with_comments(self):
        """Тест задачи с комментариями."""
        task = Task.objects.create(
            project=self.project,
            title='Задача',
            creator_id=1,
        )
        Comment.objects.create(task=task, author_id=1, text='Комментарий 1')
        Comment.objects.create(task=task, author_id=2, text='Комментарий 2')
        self.assertEqual(task.comments.count(), 2)


@override_settings(
    DATABASES=TEST_DATABASES,
    NOTIFICATION_SERVICE_URL='http://localhost:9999',
)
class ProjectAPITest(TestCase):
    """Тесты API проектов."""

    def setUp(self):
        self.client = APIClient()
        self.token = make_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_create_project(self):
        """Тест создания проекта через API."""
        data = {
            'name': 'Новый проект',
            'description': 'Описание проекта',
        }
        response = self.client.post('/api/tasks/projects/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], 'Новый проект')
        self.assertEqual(response.data['owner_id'], 1)

    def test_list_projects(self):
        """Тест получения списка проектов."""
        Project.objects.create(name='Проект 1', owner_id=1)
        Project.objects.create(name='Проект 2', owner_id=2)
        response = self.client.get('/api/tasks/projects/')
        self.assertEqual(response.status_code, 200)

    def test_project_detail(self):
        """Тест получения деталей проекта."""
        project = Project.objects.create(name='Проект', owner_id=1)
        response = self.client.get(f'/api/tasks/projects/{project.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Проект')

    def test_project_statistics(self):
        """Тест статистики проекта."""
        project = Project.objects.create(name='Проект', owner_id=1)
        Task.objects.create(project=project, title='Task 1', creator_id=1, status='todo')
        Task.objects.create(project=project, title='Task 2', creator_id=1, status='done')
        response = self.client.get(f'/api/tasks/projects/{project.id}/statistics/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total'], 2)
        self.assertEqual(response.data['todo'], 1)
        self.assertEqual(response.data['done'], 1)

    def test_unauthenticated_access(self):
        """Тест доступа без авторизации."""
        client = APIClient()
        response = client.get('/api/tasks/projects/')
        self.assertEqual(response.status_code, 403)


@override_settings(
    DATABASES=TEST_DATABASES,
    NOTIFICATION_SERVICE_URL='http://localhost:9999',
)
class TaskAPITest(TestCase):
    """Тесты API задач."""

    def setUp(self):
        self.client = APIClient()
        self.token = make_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.project = Project.objects.create(name='Проект', owner_id=1)

    def test_create_task(self):
        """Тест создания задачи через API."""
        data = {
            'project': self.project.id,
            'title': 'Новая задача',
            'description': 'Описание',
            'priority': 'high',
        }
        response = self.client.post('/api/tasks/tasks/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['title'], 'Новая задача')
        self.assertEqual(response.data['creator_id'], 1)

    def test_list_tasks(self):
        """Тест получения списка задач."""
        Task.objects.create(project=self.project, title='Task 1', creator_id=1)
        Task.objects.create(project=self.project, title='Task 2', creator_id=1)
        response = self.client.get('/api/tasks/tasks/')
        self.assertEqual(response.status_code, 200)

    def test_filter_tasks_by_project(self):
        """Тест фильтрации задач по проекту."""
        project2 = Project.objects.create(name='Проект 2', owner_id=1)
        Task.objects.create(project=self.project, title='Task 1', creator_id=1)
        Task.objects.create(project=project2, title='Task 2', creator_id=1)
        response = self.client.get(f'/api/tasks/tasks/?project={self.project.id}')
        self.assertEqual(response.status_code, 200)

    def test_update_task_status(self):
        """Тест обновления статуса задачи."""
        task = Task.objects.create(
            project=self.project, title='Task', creator_id=1,
        )
        response = self.client.patch(
            f'/api/tasks/tasks/{task.id}/',
            {'status': 'in_progress'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'in_progress')

    def test_delete_task(self):
        """Тест удаления задачи."""
        task = Task.objects.create(
            project=self.project, title='Task', creator_id=1,
        )
        response = self.client.delete(f'/api/tasks/tasks/{task.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Task.objects.filter(id=task.id).exists())
