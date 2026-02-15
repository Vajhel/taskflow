import logging
from django.shortcuts import render, redirect
from django.contrib import messages

from .services import auth_client, task_client, notification_client

logger = logging.getLogger(__name__)


def get_token(request):
    """Получение JWT-токена из сессии."""
    return request.session.get('token')


def login_required_custom(view_func):
    """Декоратор для проверки аутентификации."""
    def wrapper(request, *args, **kwargs):
        if not get_token(request):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def index(request):
    """Главная страница."""
    token = get_token(request)
    if token:
        return redirect('dashboard')
    return render(request, 'web/index.html')


def register_view(request):
    """Регистрация пользователя."""
    if request.method == 'POST':
        data = {
            'username': request.POST.get('username'),
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
            'password_confirm': request.POST.get('password_confirm'),
            'first_name': request.POST.get('first_name', ''),
            'last_name': request.POST.get('last_name', ''),
        }
        try:
            result, status_code = auth_client.register(data)
            if status_code == 201:
                request.session['token'] = result['token']
                request.session['user'] = result['user']
                messages.success(request, 'Регистрация успешна!')
                return redirect('dashboard')
            else:
                for field, errors in result.items():
                    if isinstance(errors, list):
                        for error in errors:
                            messages.error(request, f'{field}: {error}')
                    else:
                        messages.error(request, str(errors))
        except Exception as e:
            logger.error('Registration error: %s', e)
            messages.error(request, 'Ошибка соединения с сервисом авторизации.')
    return render(request, 'web/register.html')


def login_view(request):
    """Вход пользователя."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            result, status_code = auth_client.login(username, password)
            if status_code == 200:
                request.session['token'] = result['token']
                request.session['user'] = result['user']
                messages.success(request, 'Вход выполнен успешно!')
                return redirect('dashboard')
            else:
                messages.error(request, result.get('error', 'Ошибка входа.'))
        except Exception as e:
            logger.error('Login error: %s', e)
            messages.error(request, 'Ошибка соединения с сервисом авторизации.')
    return render(request, 'web/login.html')


def logout_view(request):
    """Выход пользователя."""
    request.session.flush()
    messages.info(request, 'Вы вышли из системы.')
    return redirect('login')


@login_required_custom
def dashboard(request):
    """Главная панель управления."""
    token = get_token(request)
    context = {
        'user': request.session.get('user', {}),
        'projects': [],
        'my_tasks': [],
        'unread_count': 0,
    }
    try:
        projects, _ = task_client.get_projects(token)
        context['projects'] = projects if isinstance(projects, list) else projects.get('results', [])
    except Exception as e:
        logger.error('Error fetching projects: %s', e)

    try:
        user_id = request.session.get('user', {}).get('id')
        tasks, _ = task_client.get_tasks(token, assignee=user_id)
        context['my_tasks'] = tasks if isinstance(tasks, list) else tasks.get('results', [])
    except Exception as e:
        logger.error('Error fetching tasks: %s', e)

    try:
        unread, _ = notification_client.get_unread_count(token)
        context['unread_count'] = unread.get('unread_count', 0)
    except Exception as e:
        logger.error('Error fetching notifications: %s', e)

    return render(request, 'web/dashboard.html', context)


@login_required_custom
def project_list(request):
    """Список проектов."""
    token = get_token(request)
    if request.method == 'POST':
        data = {
            'name': request.POST.get('name'),
            'description': request.POST.get('description', ''),
            'deadline': request.POST.get('deadline') or None,
        }
        try:
            result, status_code = task_client.create_project(token, data)
            if status_code == 201:
                messages.success(request, 'Проект создан!')
                return redirect('project-detail', project_id=result['id'])
            else:
                messages.error(request, 'Ошибка создания проекта.')
        except Exception as e:
            logger.error('Error creating project: %s', e)
            messages.error(request, 'Ошибка соединения с сервисом задач.')

    projects = []
    try:
        result, _ = task_client.get_projects(token)
        projects = result if isinstance(result, list) else result.get('results', [])
    except Exception as e:
        logger.error('Error fetching projects: %s', e)
        messages.error(request, 'Ошибка загрузки проектов.')

    return render(request, 'web/projects.html', {'projects': projects})


@login_required_custom
def project_detail(request, project_id):
    """Детали проекта."""
    token = get_token(request)
    try:
        project, status_code = task_client.get_project(token, project_id)
        if status_code != 200:
            messages.error(request, 'Проект не найден.')
            return redirect('projects')
        stats, _ = task_client.get_project_statistics(token, project_id)
    except Exception as e:
        logger.error('Error fetching project: %s', e)
        messages.error(request, 'Ошибка загрузки проекта.')
        return redirect('projects')

    return render(request, 'web/project_detail.html', {
        'project': project,
        'stats': stats,
    })


@login_required_custom
def task_list(request):
    """Список задач."""
    token = get_token(request)
    params = {}
    project_id = request.GET.get('project')
    if project_id:
        params['project'] = project_id
    status_filter = request.GET.get('status')
    if status_filter:
        params['status'] = status_filter

    tasks = []
    projects = []
    try:
        result, _ = task_client.get_tasks(token, **params)
        tasks = result if isinstance(result, list) else result.get('results', [])
        proj_result, _ = task_client.get_projects(token)
        projects = proj_result if isinstance(proj_result, list) else proj_result.get('results', [])
    except Exception as e:
        logger.error('Error fetching tasks: %s', e)
        messages.error(request, 'Ошибка загрузки задач.')

    return render(request, 'web/tasks.html', {
        'tasks': tasks,
        'projects': projects,
        'current_project': project_id,
        'current_status': status_filter,
    })


@login_required_custom
def task_create(request):
    """Создание задачи."""
    token = get_token(request)
    if request.method == 'POST':
        data = {
            'project': request.POST.get('project'),
            'title': request.POST.get('title'),
            'description': request.POST.get('description', ''),
            'priority': request.POST.get('priority', 'medium'),
            'assignee_id': request.POST.get('assignee_id') or None,
            'deadline': request.POST.get('deadline') or None,
        }
        try:
            result, status_code = task_client.create_task(token, data)
            if status_code == 201:
                messages.success(request, 'Задача создана!')
                return redirect('task-detail', task_id=result['id'])
            else:
                messages.error(request, 'Ошибка создания задачи.')
        except Exception as e:
            logger.error('Error creating task: %s', e)
            messages.error(request, 'Ошибка соединения.')

    projects = []
    users = []
    try:
        proj_result, _ = task_client.get_projects(token)
        projects = proj_result if isinstance(proj_result, list) else proj_result.get('results', [])
        users_result, _ = auth_client.get_users(token)
        users = users_result if isinstance(users_result, list) else users_result.get('results', [])
    except Exception as e:
        logger.error('Error fetching data for task creation: %s', e)

    return render(request, 'web/task_create.html', {
        'projects': projects,
        'users': users,
    })


@login_required_custom
def task_detail(request, task_id):
    """Детали задачи."""
    token = get_token(request)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_status':
            new_status = request.POST.get('status')
            try:
                task_client.update_task(token, task_id, {'status': new_status})
                messages.success(request, 'Статус обновлён!')
            except Exception as e:
                logger.error('Error updating task: %s', e)
                messages.error(request, 'Ошибка обновления статуса.')
        elif action == 'add_comment':
            text = request.POST.get('text')
            try:
                task_client.add_comment(token, task_id, text)
                messages.success(request, 'Комментарий добавлен!')
            except Exception as e:
                logger.error('Error adding comment: %s', e)
                messages.error(request, 'Ошибка добавления комментария.')
        return redirect('task-detail', task_id=task_id)

    try:
        task, status_code = task_client.get_task(token, task_id)
        if status_code != 200:
            messages.error(request, 'Задача не найдена.')
            return redirect('tasks')
    except Exception as e:
        logger.error('Error fetching task: %s', e)
        messages.error(request, 'Ошибка загрузки задачи.')
        return redirect('tasks')

    return render(request, 'web/task_detail.html', {'task': task})


@login_required_custom
def notifications_view(request):
    """Уведомления пользователя."""
    token = get_token(request)
    if request.method == 'POST':
        try:
            notification_client.mark_all_read(token)
            messages.success(request, 'Все уведомления отмечены как прочитанные.')
        except Exception as e:
            logger.error('Error marking notifications: %s', e)
        return redirect('notifications')

    notifs = []
    try:
        result, _ = notification_client.get_notifications(token)
        notifs = result if isinstance(result, list) else result.get('results', [])
    except Exception as e:
        logger.error('Error fetching notifications: %s', e)
        messages.error(request, 'Ошибка загрузки уведомлений.')

    return render(request, 'web/notifications.html', {'notifications': notifs})


@login_required_custom
def profile_view(request):
    """Профиль пользователя."""
    token = get_token(request)
    if request.method == 'POST':
        data = {
            'first_name': request.POST.get('first_name', ''),
            'last_name': request.POST.get('last_name', ''),
            'email': request.POST.get('email', ''),
            'phone': request.POST.get('phone', ''),
            'department': request.POST.get('department', ''),
            'position': request.POST.get('position', ''),
        }
        try:
            result, status_code = auth_client.update_profile(token, data)
            if status_code == 200:
                request.session['user'] = result
                messages.success(request, 'Профиль обновлён!')
            else:
                messages.error(request, 'Ошибка обновления профиля.')
        except Exception as e:
            logger.error('Error updating profile: %s', e)
            messages.error(request, 'Ошибка соединения.')
        return redirect('profile')

    try:
        user_data, _ = auth_client.get_profile(token)
    except Exception as e:
        logger.error('Error fetching profile: %s', e)
        user_data = request.session.get('user', {})

    return render(request, 'web/profile.html', {'profile': user_data})
