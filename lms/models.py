"""
Модели для приложения LMS (Learning Management System).
"""

from django.db import models
from django.conf import settings  # Import settings


class Course(models.Model):
    """
    Модель, представляющая обучающий курс.
    """

    title = models.CharField(max_length=255, verbose_name="название", unique=True)
    preview = models.ImageField(
        upload_to="lms/previews/",
        verbose_name="превью (картинка)",
        blank=True,
        null=True,
    )
    description = models.TextField(verbose_name="описание", blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses",
        verbose_name="владелец",
    )

    class Meta:
        verbose_name = "курс"
        verbose_name_plural = "курсы"

    def __str__(self):
        """
        Возвращает строковое представление курса.
        """
        return self.title


class Lesson(models.Model):
    """
    Модель, представляющая урок, входящий в курс.
    """

    title = models.CharField(max_length=255, verbose_name="название")
    description = models.TextField(verbose_name="описание", blank=True, null=True)
    preview = models.ImageField(
        upload_to="lms/previews/",
        verbose_name="превью (картинка)",
        blank=True,
        null=True,
    )
    video_link = models.URLField(verbose_name="ссылка на видео", blank=True, null=True)

    # Связь с моделью Course (один ко многим)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="курс",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lessons_owned",  # Changed related_name to avoid clash with courses
        verbose_name="владелец",
    )

    class Meta:
        verbose_name = "урок"
        verbose_name_plural = "уроки"
        # Уникальность названия урока в рамках одного курса
        unique_together = ("title", "course")

    def __str__(self):
        """
        Возвращает строковое представление урока.
        """
        return f"{self.title} ({self.course.title})"


class Subscription(models.Model):
    """
    Модель подписки пользователя на курс.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="пользователь",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="курс",
    )

    class Meta:
        verbose_name = "подписка"
        verbose_name_plural = "подписки"
        # Пользователь может подписаться на курс только один раз
        unique_together = ("user", "course")

    def __str__(self):
        return f"{self.user} подписан на {self.course}"
