import logging
import requests
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Project, Task, Comment
from .serializers import (
    ProjectSerializer, ProjectDetailSerializer,
    TaskSerializer, TaskDetailSerializer,
    CommentSerializer,
)

logger = logging.getLogger(__name__)


def notify_service(event_type, data, token):
    """Отправка уведомления через notification_service."""
    try:
        requests.post(
            f"{settings.NOTIFICATION_SERVICE_URL}/api/notifications/create/",
            json={'event_type': event_type, **data},
            headers={'Authorization': f'Bearer {token}'},
            timeout=5,
        )
    except requests.RequestException as e:
        logger.warning('Не удалось отправить уведомление: %s', e)


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet для управления проектами."""
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        return ProjectSerializer

    def perform_create(self, serializer):
        serializer.save(owner_id=self.request.user.id)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Статистика проекта по задачам."""
        project = self.get_object()
        tasks = project.tasks.all()
        stats = {
            'total': tasks.count(),
            'todo': tasks.filter(status=Task.Status.TODO).count(),
            'in_progress': tasks.filter(status=Task.Status.IN_PROGRESS).count(),
            'review': tasks.filter(status=Task.Status.REVIEW).count(),
            'done': tasks.filter(status=Task.Status.DONE).count(),
            'cancelled': tasks.filter(status=Task.Status.CANCELLED).count(),
        }
        return Response(stats)


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet для управления задачами."""
    serializer_class = TaskSerializer

    def get_queryset(self):
        queryset = Task.objects.select_related('project').all()
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        assignee_id = self.request.query_params.get('assignee')
        if assignee_id:
            queryset = queryset.filter(assignee_id=assignee_id)
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TaskDetailSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        task = serializer.save(creator_id=self.request.user.id)
        token = self.request.auth
        notify_service('task_created', {
            'task_id': task.id,
            'title': task.title,
            'project_id': task.project_id,
            'creator_id': task.creator_id,
        }, token)

    def perform_update(self, serializer):
        old_status = self.get_object().status
        task = serializer.save()
        if task.status != old_status:
            token = self.request.auth
            notify_service('task_status_changed', {
                'task_id': task.id,
                'title': task.title,
                'old_status': old_status,
                'new_status': task.status,
            }, token)

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        """Комментарии к задаче."""
        task = self.get_object()
        if request.method == 'GET':
            comments = task.comments.all()
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        else:
            serializer = CommentSerializer(data={**request.data, 'task': task.id})
            serializer.is_valid(raise_exception=True)
            serializer.save(author_id=request.user.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для комментариев."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        serializer.save(author_id=self.request.user.id)
