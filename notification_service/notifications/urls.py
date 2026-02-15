from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('create/', views.create_notification_view, name='notification-create'),
    path('<int:pk>/read/', views.mark_read_view, name='notification-read'),
    path('read-all/', views.mark_all_read_view, name='notification-read-all'),
    path('unread-count/', views.unread_count_view, name='notification-unread-count'),
]
