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

---

## CI/CD и Деплой на сервер

### GitHub Actions Workflow

Проект использует GitHub Actions для автоматического тестирования и деплоя.

**Workflow запускается:**
- При каждом `push` в ветки `main` и `feature`
- При создании Pull Request в `main`

**Этапы workflow:**
1. **Test** — запуск тестов проекта
2. **Lint** — проверка кода (Black, Flake8)
3. **Build** — сборка Docker образа
4. **Deploy** — деплой на сервер (только при push в `main`)

### GitHub Secrets

Для работы деплоя необходимо создать Secrets в репозитории:

**Settings → Secrets and variables → Actions → New repository secret**

| Secret name | Описание | Пример значения |
|-------------|----------|------------------|
| `SSH_PRIVATE_KEY` | Приватный SSH ключ для подключения к серверу | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `SERVER_HOST` | IP адрес сервера | `144.124.249.130` |
| `SERVER_USER` | Пользователь SSH | `root` |
| `SECRET_KEY` | Django секретный ключ | `django-insecure-...` |
| `ALLOWED_HOSTS` | Разрешённые хосты | `example.com,www.example.com` |
| `DB_NAME` | Имя базы данных | `lms_db` |
| `DB_USER` | Пользователь БД | `postgres` |
| `DB_PASSWORD` | Пароль БД | `secure_password` |
| `STRIPE_SECRET_KEY` | Stripe секретный ключ | `sk_test_...` |
| `STRIPE_PUBLIC_KEY` | Stripe публичный ключ | `pk_test_...` |

### Настройка сервера

**Требования:**
- Ubuntu 20.04+ / Debian 11+
- Docker и Docker Compose
- SSH доступ

**Установка Docker на Ubuntu:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**SSH ключи для GitHub Actions:**
```bash
# На сервере
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
cat ~/.ssh/github_actions  # Скопировать и добавить в GitHub Secrets
```

**Развертывание на сервере:**
```bash
# Клонирование репозитория
git clone -b feature <your-repo-url> ~/app
cd ~/app

# Создание .env файла
cp .env.template .env
nano .env  # Заполнить реальными значениями

# Запуск
docker compose build
docker compose up -d
```

### Создание Pull Request

1. Создай ветку для изменений:
   ```bash
   git checkout -b feature/my-changes
   ```

2. Внеси изменения и закоммить:
   ```bash
   git add .
   git commit -m "Описание изменений"
   git push origin feature/my-changes
   ```

3. Создай Pull Request в GitHub:
   - Base: `main`
   - Compare: `feature/my-changes`

4. После прохождения тестов — смёрджи в `main` для автоматического деплоя.

---

## Структура проекта:

```
LearningAPI/
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions workflow
├── config/                     # Django конфигурация
│   ├── settings.py            # Основные настройки
│   ├── celery.py              # Celery конфигурация
│   └── urls.py                # Root URL конфиг
├── lms/                       # Приложение курсов
│   ├── models.py              # Модели Course, Lesson, Subscription
│   ├── serializers.py         # DRF сериализаторы
│   ├── views.py               # API ViewSets
│   └── permissions.py         # Кастомные разрешения
├── users/                     # Приложение пользователей
│   ├── models.py              # Модель User, Payment
│   ├── serializers.py         # DRF сериализаторы
│   ├── views.py               # API ViewSets
│   └── tasks.py               # Celery задачи
├── Dockerfile                  # Docker образ для приложения
├── docker-compose.yml          # Docker Compose конфигурация
├── nginx.conf                 # Nginx reverse proxy конфигурация
├── requirements.txt           # Python зависимости
├── .env.template             # Шаблон переменных окружения
└── README.md                 # Этот файл
```
