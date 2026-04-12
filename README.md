# LMS API - Бэкенд для Системы Управления Обучением

Это бэкенд для платформы онлайн-обучения (LMS), разработанный на Django и Django REST Framework. API позволяет управлять курсами, уроками, пользователями и платежами.

## Технологический стек

*   **Python 3.11+**
*   **Django 5.0+**
*   **Django REST Framework**
*   **PostgreSQL**
*   **Poetry** для управления зависимостями
*   **django-filter** для фильтрации

## Установка и запуск проекта

1.  **Клонируйте репозиторий:**
    ```bash
    git clone <your-repository-url>
    cd <project-folder>
    ```

2.  **Создайте и настройте `.env` файл:**
    *   Создайте файл `.env` в корне проекта, скопировав `.env.example` (если он есть) или создав новый.
    *   Заполните его необходимыми данными:
        ```ini
        SECRET_KEY=<your-django-secret-key>
        DB_NAME=your_db_name
        DB_USER=postgres
        DB_PASSWORD=<your-db-password>
        DB_HOST=localhost
        DB_PORT=5432
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

6.  **(Опционально) Создайте суперпользователя:**
    ```bash
    poetry run python manage.py createsuperuser
    ```

7.  **Запустите сервер для разработки:**
    ```bash
    poetry run python manage.py runserver
    ```
    Сервер будет доступен по адресу `http://127.0.0.1:8000/`.

## Основные API-эндпоинты

*   `/api/users/` - CRUD для пользователей
*   `/api/courses/` - CRUD для курсов
*   `/api/lessons/` - CRUD для уроков
*   `/api/payments/` - Список платежей с возможностью фильтрации
