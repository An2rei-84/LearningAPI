# LMS API - Бэкенд для Системы Управления Обучением

Это бэкенд для платформы онлайн-обучения (LMS), разработанный на Django и Django REST Framework.
API позволяет управлять курсами, уроками, пользователями и платежами, используя JWT-аутентификацию и
ролевую модель (модераторы и обычные пользователи).

## Технологический стек

*   **Python 3.11+**
*   **Django 5.0+**
*   **Django REST Framework**
*   **djangorestframework-simplejwt** для JWT-аутентификации
*   **drf-spectacular** для документации API
*   **Celery + Redis** для асинхронных задач
*   **django-celery-beat** для периодических задач
*   **Stripe** для обработки платежей
*   **PostgreSQL**
*   **Docker & Docker Compose** для контейнеризации
*   **Poetry** для управления зависимостями
*   **django-filter** для фильтрации

## Документация API

Проект использует `drf-spectacular` для автоматической генерации документации OpenAPI.

*   **Swagger UI:** `http://127.0.0.1:8000/api/docs/`
*   **Schema JSON:** `http://127.0.0.1:8000/api/schema/`

## Установка и запуск проекта

1.  **Клонируйте репозиторий:**
    ```bash
    git clone <your-repository-url>
    cd <project-folder>
    ```

2.  **Создайте и настройте `.env` файл:**
    *   Создайте файл `.env` в корне проекта.
    *   Заполните его необходимыми данными для базы данных и Stripe:
        ```ini
        # Django
        SECRET_KEY=<your-django-secret-key>
        
        # PostgreSQL
        DB_NAME=your_db_name
        DB_USER=postgres
        DB_PASSWORD=<your-db-password>
        DB_HOST=localhost
        DB_PORT=5432

        # Stripe
        STRIPE_SECRET_KEY=sk_test_...
        STRIPE_API_KEY=pk_test_...
        ```

3.  **Установите зависимости:**
    *   Убедитесь, что у вас установлен [Poetry](https://python-poetry.org/).
    *   Выполните команду:
        ```bash
        poetry install
        ```

4.  **Настройте базу данных PostgreSQL:**
    *   Убедитесь, что у вас запущен сервер PostgreSQL.
    *   Создайте базу данных `your_db_name` и предоставьте права доступа пользователю, указанному в `.env`.

5.  **Примените миграции Django:**
    ```bash
    poetry run python manage.py migrate
    ```

6.  **Создайте необходимые группы и суперпользователя:**
    *   Создайте группу "moderators":
        ```bash
        poetry run python manage.py create_groups
        ```
    *   Создайте суперпользователя для доступа к админ-панели:
        ```bash
        poetry run python manage.py createsuperuser
        ```

7.  **Запустите сервер для разработки:**
    ```bash
    poetry run python manage.py runserver
    ```
    Сервер будет доступен по адресу `http://127.0.0.1:8000/`.

## Запуск через Docker

Рекомендуемый способ запуска проекта в production и для разработки.

### Требования
- Установленный [Docker](https://docs.docker.com/get-docker/)
- Установленный [Docker Compose](https://docs.docker.com/compose/install/)

### Быстрый старт

1.  **Клонируйте репозиторий и перейдите в папку проекта:**
    ```bash
    git clone <your-repository-url>
    cd <project-folder>
    ```

2.  **Создайте и настройте `.env` файл:**
    ```bash
    cp .env.example .env
    ```
    Отредактируйте `.env` при необходимости:
    - Измените `SECRET_KEY` на случайное значение (можно сгенерировать через `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
    - Установите `DB_PASSWORD` для PostgreSQL
    - Добавьте ключи Stripe (если используете платежи)

3.  **Запустите все сервисы одной командой:**
    ```bash
    docker-compose up --build
    ```
    Первая сборка может занять несколько минут.

    Проект запустит следующие сервисы:
    - **web** — Django приложение (порт 8000)
    - **db** — PostgreSQL база данных (внутренний порт)
    - **redis** — Redis для Celery (внутренний порт)
    - **celery_worker** — обработчик фоновых задач
    - **celery_beat** — планировщик периодических задач

4.  **Создайте суперпользователя** (в новом терминале):
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```

5.  **Приложение доступно по адресу:**
    - API: `http://127.0.0.1:8000/`
    - Swagger UI: `http://127.0.0.1:8000/api/docs/`
    - Admin панель: `http://127.0.0.1:8000/admin/`

### Полезные команды Docker

| Команда | Описание |
|---------|----------|
| `docker-compose up -d` | Запуск в фоновом режиме |
| `docker-compose down` | Остановка и удаление контейнеров |
| `docker-compose logs -f web` | Логи Django приложения |
| `docker-compose logs -f celery_worker` | Логи Celery worker |
| `docker-compose exec web python manage.py migrate` | Применить миграции |
| `docker-compose exec web python manage.py createsuperuser` | Создать суперюзера |
| `docker-compose exec web python manage.py create_groups` | Создать группы модераторов |
| `docker-compose exec web shell` | Django shell |
| `docker-compose volume rm` | Удалить все volumes (данные БД!) |

### Остановка проекта

```bash
docker-compose down
```

Для удаления всех данных (включая базу данных):

```bash
docker-compose down -v
```

### Структура volumes

Данные сохраняются в Docker volumes даже после остановки контейнеров:
- `postgres_data` — данные PostgreSQL
- `redis_data` — данные Redis
- `static_files` — статические файлы
- `media_files` — медиа файлы

## API-аутентификация (JWT)

API использует JWT для аутентификации.

1.  **Регистрация:** Отправьте `POST` запрос на `/api/users/` с вашими данными (email, password и др.).
2.  **Получение токена:** Отправьте `POST` запрос на `/api/token/` с вашими `email` и `password`. В ответе вы получите `access` и `refresh` токены.
3.  **Аутентификация запросов:** Для доступа к защищенным эндпоинтам включайте `access` токен в заголовок `Authorization`:
    ```
    Authorization: Bearer <your_access_token>
    ```

## Основные API-эндпоинты

### Аутентификация
*   `POST /api/users/` - Регистрация нового пользователя.
*   `POST /api/token/` - Получение JWT токена.
*   `POST /api/token/refresh/` - Обновление JWT токена.

### Пользователи
*   `GET /api/users/` - Список всех пользователей (только для авторизованных).
*   `GET /api/users/{id}/` - Просмотр профиля пользователя. Ограниченная информация для чужих профилей.
*   `PUT/PATCH /api/users/{id}/` - Редактирование своего профиля.
*   `DELETE /api/users/{id}/` - Удаление своего профиля.

### Курсы и Уроки
*   `/api/courses/` - CRUD для курсов.
*   `/api/lessons/` - CRUD для уроков.
*   `POST /api/subscriptions/` - Подписка/отписка от курса.

### Платежи
*   `GET /api/payments/` - Список платежей с возможностью фильтрации.
*   `POST /api/payments/create/` - Создание платежа для курса и получение ссылки на оплату в Stripe.
*   `GET /api/payments/{id}/` - Получение информации о конкретном платеже, включая статус оплаты из Stripe.

## Ролевая модель

*   **Обычные пользователи:** Могут создавать, просматривать, редактировать и удалять только *свои* курсы и уроки.
*   **Модераторы:** Могут просматривать и редактировать *любые* курсы и уроки, но не могут их создавать или удалять. Назначение в группу "moderators" производится через админ-панель.
*   **Суперпользователи:** Имеют полный доступ через админ-панель.
