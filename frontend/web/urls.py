from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('projects/', views.project_list, name='projects'),
    path('projects/<int:project_id>/', views.project_detail, name='project-detail'),
    path('tasks/', views.task_list, name='tasks'),
    path('tasks/create/', views.task_create, name='task-create'),
    path('tasks/<int:task_id>/', views.task_detail, name='task-detail'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('profile/', views.profile_view, name='profile'),
]
