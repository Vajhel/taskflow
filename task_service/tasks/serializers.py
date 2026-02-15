from rest_framework import serializers
from .models import Project, Task, Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'task', 'author_id', 'text', 'created_at']
        read_only_fields = ['id', 'author_id', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'project', 'title', 'description', 'priority',
            'status', 'assignee_id', 'creator_id', 'created_at',
            'updated_at', 'deadline', 'comments_count',
        ]
        read_only_fields = ['id', 'creator_id', 'created_at', 'updated_at']

    def get_comments_count(self, obj):
        return obj.comments.count()


class TaskDetailSerializer(TaskSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta(TaskSerializer.Meta):
        fields = TaskSerializer.Meta.fields + ['comments']


class ProjectSerializer(serializers.ModelSerializer):
    tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'status', 'owner_id',
            'created_at', 'updated_at', 'deadline', 'tasks_count',
        ]
        read_only_fields = ['id', 'owner_id', 'created_at', 'updated_at']

    def get_tasks_count(self, obj):
        return obj.tasks.count()


class ProjectDetailSerializer(ProjectSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ['tasks']
