from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'event_type', 'recipient_id', 'sender_id',
            'title', 'message', 'is_read', 'metadata', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class CreateNotificationSerializer(serializers.Serializer):
    """Сериализатор для создания уведомлений от других микросервисов."""
    event_type = serializers.CharField()
    task_id = serializers.IntegerField(required=False)
    title = serializers.CharField(required=False, default='')
    project_id = serializers.IntegerField(required=False)
    creator_id = serializers.IntegerField(required=False)
    old_status = serializers.CharField(required=False)
    new_status = serializers.CharField(required=False)
