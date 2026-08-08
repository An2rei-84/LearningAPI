"""
Конфигурация пакета config.

Этот модуль гарантирует, что приложение Celery будет загружено
при запуске Django.
"""

# Это гарантирует, что приложение Celery всегда будет импортировано
# когда Django запускается, чтобы shared_task мог использовать @shared_task
from .celery import app as celery_app

__all__ = ("celery_app",)
