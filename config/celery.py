"""
Конфигурация Celery для асинхронных задач.

Этот файл создаёт и конфигурирует экземпляр Celery, который используется
для выполнения асинхронных и периодических задач в проекте.
"""

import os

from celery import Celery

# Устанавливаем стандартную настройку Django для модуля 'celery'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Загружаем настройки из Django settings
# Celery будет искать настройки, начинающиеся с 'CELERY_'
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автообнаружение задач в зарегистрированных приложениях
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """
    Отладочная задача для проверки работы Celery.

    Args:
        self: Экземпляр задачи

    Returns:
        str: Информация о запросе
    """
    print(f"Request: {self.request!r}")
