"""
Celery задачи для приложения users.

Здесь определены асинхронные задачи для управления пользователями
и периодического обслуживания.
"""

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


@shared_task
def block_inactive_users():
    """
    Блокирует пользователей, которые не заходили более месяца.

    Эта периодическая задача проверяет поле last_login у всех пользователей.
    Если пользователь не входил в систему более 30 дней,
    его аккаунт блокируется (is_active=False).

    Returns:
        str: Количество заблокированных пользователей
    """
    # Вычисляем дату месяц назад от текущего момента
    month_ago = timezone.now() - timedelta(days=30)

    # Выбираем пользователей, которые не входили более месяца
    # и ещё активны (чтобы не блокировать повторно)
    inactive_users = User.objects.filter(
        last_login__lt=month_ago,
        is_active=True
    )

    # Батчевое обновление - блокируем всех выбранных пользователей
    count = inactive_users.update(is_active=False)

    if count > 0:
        print(f"Заблокировано пользователей: {count}")

    return f"Заблокировано пользователей: {count}"
