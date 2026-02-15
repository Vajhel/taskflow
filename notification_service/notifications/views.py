from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer, CreateNotificationSerializer


class NotificationListView(generics.ListAPIView):
    """Список уведомлений текущего пользователя."""
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(recipient_id=self.request.user.id)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_notification_view(request):
    """Создание уведомления (вызывается другими микросервисами)."""
    serializer = CreateNotificationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    event_type = data['event_type']
    task_title = data.get('title', '')

    if event_type == 'task_created':
        notification = Notification.objects.create(
            event_type=event_type,
            recipient_id=data.get('creator_id', request.user.id),
            sender_id=request.user.id,
            title='Новая задача создана',
            message=f'Создана задача: {task_title}',
            metadata={'task_id': data.get('task_id'), 'project_id': data.get('project_id')},
        )
    elif event_type == 'task_status_changed':
        notification = Notification.objects.create(
            event_type=event_type,
            recipient_id=request.user.id,
            sender_id=request.user.id,
            title='Статус задачи изменён',
            message=f'Задача "{task_title}": {data.get("old_status")} → {data.get("new_status")}',
            metadata={'task_id': data.get('task_id')},
        )
    else:
        notification = Notification.objects.create(
            event_type=event_type,
            recipient_id=request.user.id,
            sender_id=request.user.id,
            title='Уведомление',
            message=str(data),
            metadata=data,
        )

    return Response(
        NotificationSerializer(notification).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_read_view(request, pk):
    """Отметить уведомление как прочитанное."""
    try:
        notification = Notification.objects.get(pk=pk, recipient_id=request.user.id)
    except Notification.DoesNotExist:
        return Response({'error': 'Уведомление не найдено.'}, status=status.HTTP_404_NOT_FOUND)

    notification.is_read = True
    notification.save()
    return Response(NotificationSerializer(notification).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read_view(request):
    """Отметить все уведомления как прочитанные."""
    count = Notification.objects.filter(
        recipient_id=request.user.id, is_read=False
    ).update(is_read=True)
    return Response({'marked_read': count})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_count_view(request):
    """Количество непрочитанных уведомлений."""
    count = Notification.objects.filter(
        recipient_id=request.user.id, is_read=False
    ).count()
    return Response({'unread_count': count})
