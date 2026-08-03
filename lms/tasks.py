"""
Celery задачи для приложения LMS.

Здесь определены асинхронные задачи для отправки уведомлений
и других фоновых операций.
"""

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_course_update_notification(course_id):
    """
    Отправляет уведомление по email всем подписчикам курса об обновлении.

    Args:
        course_id: ID обновлённого курса

    Эта задача асинхронно отправляет email всем пользователям,
    которые подписаны на указанный курс. Каждый подписчик получает
    индивидуальное письмо с информацией об обновлении.
    """
    from lms.models import Course, Subscription

    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return f"Курс с id={course_id} не найден"

    # Получаем всех подписчиков курса
    subscriptions = Subscription.objects.filter(course=course).select_related("user")

    if not subscriptions.exists():
        return f"Нет подписчиков для курса '{course.title}'"

    subject = f"Обновление курса: {course.title}"
    message = (
        f"Здравствуйте!\n\n"
        f"Курс '{course.title}' был обновлён.\n"
        f"Зайдите на платформу, чтобы увидеть изменения.\n\n"
        f"С уважением,\nКоманда LMS"
    )

    success_count = 0
    failed_count = 0

    for subscription in subscriptions:
        user_email = subscription.user.email
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user_email],
                fail_silently=False,
            )
            success_count += 1
        except Exception as e:
            failed_count += 1
            print(f"Ошибка отправки email на {user_email}: {e}")

    return f"Отправлено: {success_count}, не удалось: {failed_count}"
