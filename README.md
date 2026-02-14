# TaskFlow — Система управления проектами и задачами

Микросервисное веб-приложение на Django для управления проектами, задачами и уведомлениями. Все сервисы упакованы в Docker-контейнеры и оркестрируются через Docker Compose.

## Архитектура

```
┌──────────┐     ┌─────────────────────────────────────────────────┐
│  Браузер │────>│                   Nginx :80                     │
└──────────┘     │  reverse proxy / маршрутизация запросов          │
                 └──┬──────────┬───────────┬───────────┬───────────┘
                    │          │           │           │
              /api/auth/*  /api/tasks/*  /api/notif/*    /*
                    │          │           │           │
                    v          v           v           v
              ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
              │  auth    │ │  task    │ │ notific. │ │ frontend │
              │ service  │ │ service  │ │ service  │ │ (Django  │
              │ :8000    │ │ :8000    │ │ :8000    │ │ templates│
              └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────────┘
                   │            │            │
                   v            v            v
              ┌─────────────────────────────────────┐
              │          PostgreSQL :5432           │
              │ auth_db │ tasks_db │notifications_db│
              └─────────────────────────────────────┘
```

| Сервис | Описание | Технологии |
|--------|----------|------------|
| **auth_service** | Регистрация, JWT-аутентификация, профили пользователей | Django + DRF |
| **task_service** | CRUD проектов, задач, комментариев, статистика | Django + DRF |
| **notification_service** | Уведомления о событиях (создание задач, смена статусов) | Django + DRF |
| **frontend** | Веб-интерфейс с боковой навигацией и дашбордом | Django Templates + Bootstrap 5 |
| **nginx** | Обратный прокси, маршрутизация API и фронтенда | Nginx 1.25 |
| **postgres** | Три отдельные БД для каждого микросервиса | PostgreSQL 15 |

## Быстрый старт

### Требования

- Docker 20+
- Docker Compose v2+

### Запуск

```bash
git clone https://github.com/Vajhel/taskflow.git
cd newtest
docker-compose up --build
```

После запуска приложение доступно по адресу: **http://localhost:8080/**

### Остановка

```bash
docker-compose down
```

Остановка с удалением данных (БД, тома):

```bash
docker-compose down -v
```

## API-эндпоинты

### auth_service — `/api/auth/`

| Метод | URL | Описание | Авторизация |
|-------|-----|----------|-------------|
| POST | `/api/auth/register/` | Регистрация | Нет |
| POST | `/api/auth/login/` | Вход (получение JWT) | Нет |
| GET | `/api/auth/profile/` | Профиль текущего пользователя | JWT |
| PATCH | `/api/auth/profile/update/` | Обновление профиля | JWT |
| POST | `/api/auth/validate/` | Валидация токена | JWT |
| GET | `/api/auth/users/` | Список пользователей | JWT |

### task_service — `/api/tasks/`

| Метод | URL | Описание |
|-------|-----|----------|
| GET, POST | `/api/tasks/projects/` | Список / создание проектов |
| GET, PATCH, DELETE | `/api/tasks/projects/{id}/` | Операции с проектом |
| GET | `/api/tasks/projects/{id}/statistics/` | Статистика задач проекта |
| GET, POST | `/api/tasks/tasks/` | Список / создание задач |
| GET, PATCH, DELETE | `/api/tasks/tasks/{id}/` | Операции с задачей |
| GET, POST | `/api/tasks/tasks/{id}/comments/` | Комментарии к задаче |

Фильтрация задач: `?project=1`, `?status=in_progress`, `?assignee=2`

### notification_service — `/api/notifications/`

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/notifications/` | Уведомления текущего пользователя |
| POST | `/api/notifications/create/` | Создание уведомления (межсервисный) |
| POST | `/api/notifications/{id}/read/` | Отметить как прочитанное |
| POST | `/api/notifications/read-all/` | Отметить все как прочитанные |
| GET | `/api/notifications/unread-count/` | Количество непрочитанных |

## Структура проекта

```
.
├── docker-compose.yml
├── .env.example
├── .gitignore
├── auth_service/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── requirements.txt
│   ├── manage.py
│   ├── auth_service/          # settings, urls, wsgi
│   └── accounts/              # models, views, serializers, tests
├── task_service/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── requirements.txt
│   ├── manage.py
│   ├── task_service/          # settings, urls, wsgi
│   └── tasks/                 # models, views, serializers, tests
├── notification_service/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── requirements.txt
│   ├── manage.py
│   ├── notification_service/  # settings, urls, wsgi
│   └── notifications/         # models, views, serializers, tests
├── frontend/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── requirements.txt
│   ├── manage.py
│   ├── frontend/              # settings, urls, wsgi
│   └── web/
│       ├── views.py           # представления
│       ├── services.py        # HTTP-клиенты к микросервисам
│       ├── tests.py
│       └── templates/web/     # HTML-шаблоны (11 страниц)
├── nginx/
│   ├── Dockerfile
│   └── nginx.conf
└── postgres/
    └── init-databases.sh
```

## Тестирование

Запуск тестов внутри контейнеров:

```bash
docker-compose exec auth_service python manage.py test
docker-compose exec task_service python manage.py test
docker-compose exec notification_service python manage.py test
docker-compose exec frontend python manage.py test
```

Всего 42 unit-теста: модели, API, аутентификация, веб-интерфейс.

## Переменные окружения

Все сервисы конфигурируются через переменные окружения (см. `.env.example`):

| Переменная | Описание | Значение по умолчанию |
|------------|----------|-----------------------|
| `JWT_SECRET` | Общий секрет для JWT-токенов | `taskflow-jwt-shared-secret-2024` |
| `DB_HOST` | Хост PostgreSQL | `postgres` |
| `DB_USER` | Пользователь БД | `postgres` |
| `DB_PASSWORD` | Пароль БД | `postgres` |
| `DEBUG` | Режим отладки | `True` |

## Логирование

Каждый микросервис записывает HTTP-запросы (время, IP, метод, путь, статус, длительность):

```
2026-11-25 14:30:12 INFO http HTTP GET /api/tasks/projects/ | IP: 172.18.0.7 | Status: 200 | Duration: 0.045s
```

Просмотр логов:

```bash
docker logs taskflow_auth
docker logs taskflow_tasks
docker logs taskflow_notifications
docker logs taskflow_frontend
```

## Технологический стек

- **Backend:** Python 3.11, Django 4.2, Django REST Framework 3.15
- **Frontend:** Django Templates, Bootstrap 5, Bootstrap Icons
- **БД:** PostgreSQL 15
- **Сервер:** Gunicorn, Nginx
- **Контейнеризация:** Docker, Docker Compose
- **Аутентификация:** JWT (PyJWT)
- **VCS:** Git
