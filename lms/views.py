"""
API-представления (Views) для моделей Course и Lesson в приложении LMS.
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from lms.permissions import IsModerator, IsOwner

from lms.models import Course, Lesson, Subscription
from lms.serializers import CourseSerializer, LessonSerializer
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from lms.paginators import CustomPagination
from drf_spectacular.utils import extend_schema
from django.utils import timezone
from datetime import timedelta


@extend_schema(
    tags=["Курсы"],
    description="Управление курсами. Предоставляет полный набор CRUD-операций.",
    methods={
        "list": extend_schema(
            summary="Получение списка курсов",
            description="Возвращает список всех курсов. Обычные пользователи видят только свои курсы. Модераторы видят все курсы."  # noqa: E501
        ),
        "create": extend_schema(
            summary="Создание нового курса",
            description="Создает новый курс. Модераторы не могут создавать. Владелец устанавливается автоматически."  # noqa: E501
        ),
        "retrieve": extend_schema(
            summary="Получение информации о курсе",
            description="Возвращает детальную информацию об одном курсе. Доступно владельцу и модераторам."
        ),
        "update": extend_schema(
            summary="Полное обновление курса",
            description="Полностью обновляет информацию о курсе. Доступно владельцу и модераторам."
        ),
        "partial_update": extend_schema(
            summary="Частичное обновление курса",
            description="Частично обновляет информацию о курсе. Доступно владельцу и модераторам."
        ),
        "destroy": extend_schema(
            summary="Удаление курса",
            description="Удаляет курс по его ID. Доступно только владельцу."
        ),
    },
)
class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Course, предоставляющий полный набор CRUD-операций.
    """

    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    pagination_class = CustomPagination

    def get_queryset(self):
        if self.action == "list" and not self.request.user.groups.filter(name="moderators").exists():
            return Course.objects.filter(owner=self.request.user)
        return Course.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        """
        Обновляет курс и отправляет уведомление подписчикам.

        Уведомление отправляется только если курс не обновлялся
        более 4 часов назад.
        """
        course = self.get_object()
        old_updated_at = course.updated_at

        response = super().update(request, *args, **kwargs)

        # Проверяем: прошло ли 4 часа с последнего обновления
        should_notify = False
        if old_updated_at is None:
            # Первое обновление (поле только что добавлено)
            should_notify = True
        else:
            time_since_update = timezone.now() - old_updated_at
            if time_since_update >= timedelta(hours=4):
                should_notify = True

        if should_notify:
            from lms.tasks import send_course_update_notification
            # Вызываем Celery задачу асинхронно
            send_course_update_notification.delay(course.id)

        return response

    def partial_update(self, request, *args, **kwargs):
        """
        Частично обновляет курс и отправляет уведомление подписчикам.

        Уведомление отправляется только если курс не обновлялся
        более 4 часов назад.
        """
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [
                IsAuthenticated,
                ~IsModerator,
            ]  # Модераторы не могут создавать
        elif self.action == "list" or self.action == "retrieve":
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action == "update" or self.action == "partial_update":
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action == "destroy":
            self.permission_classes = [
                IsAuthenticated,
                IsOwner,
            ]  # Удалять может только владелец
        else:
            self.permission_classes = [IsAuthenticated]  # Дефолтное разрешение
        return [permission() for permission in self.permission_classes]


@extend_schema(
    tags=["Уроки"],
    description="Управление уроками. Предоставляет полный набор CRUD-операций.",
    methods={
        "list": extend_schema(
            summary="Получение списка уроков",
            description="Возвращает список всех уроков. Обычные пользователи видят только свои уроки. Модераторы видят все уроки."  # noqa: E501
        ),
        "create": extend_schema(
            summary="Создание нового урока",
            description="Создает новый урок. Модераторы не могут создавать. Владелец устанавливается автоматически."  # noqa: E501
        ),
        "retrieve": extend_schema(
            summary="Получение информации об уроке",
            description="Возвращает детальную информацию об одном уроке по ID. Доступно владельцу и модераторам."
        ),
        "update": extend_schema(
            summary="Полное обновление урока",
            description="Полностью обновляет информацию об уроке по ID. Доступно владельцу и модераторам."
        ),
        "partial_update": extend_schema(
            summary="Частичное обновление урока",
            description="Частично обновляет информацию об уроке. Доступно владельцу и модераторам."
        ),
        "destroy": extend_schema(
            summary="Удаление урока",
            description="Удаляет урок по ID. Доступно только владельцу."
        ),
    },
)
class LessonViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Lesson, предоставляющий полный набор CRUD-операций.
    """

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    pagination_class = CustomPagination

    def get_queryset(self):
        if self.action == "list" and not self.request.user.groups.filter(name="moderators").exists():
            return Lesson.objects.filter(owner=self.request.user)
        return Lesson.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        """
        Обновляет урок и отправляет уведомление подписчикам курса.

        Уведомление отправляется только если курс урока не обновлялся
        более 4 часов назад.
        """
        lesson = self.get_object()
        course = lesson.course
        old_course_updated_at = course.updated_at

        response = super().update(request, *args, **kwargs)

        # Проверяем: прошло ли 4 часа с последнего обновления курса
        should_notify = False
        if old_course_updated_at is None:
            should_notify = True
        else:
            time_since_update = timezone.now() - old_course_updated_at
            if time_since_update >= timedelta(hours=4):
                should_notify = True

        if should_notify:
            from lms.tasks import send_course_update_notification
            send_course_update_notification.delay(course.id)

        return response

    def partial_update(self, request, *args, **kwargs):
        """
        Частично обновляет урок и отправляет уведомление подписчикам курса.

        Уведомление отправляется только если курс урока не обновлялся
        более 4 часов назад.
        """
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [
                IsAuthenticated,
                ~IsModerator,
            ]  # Модераторы не могут создавать
        elif self.action == "list" or self.action == "retrieve":
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action == "update" or self.action == "partial_update":
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action == "destroy":
            self.permission_classes = [
                IsAuthenticated,
                IsOwner,
            ]  # Удалять может только владелец
        else:
            self.permission_classes = [IsAuthenticated]  # Дефолтное разрешение
        return [permission() for permission in self.permission_classes]


@extend_schema(tags=["Подписки"])
class SubscriptionAPIView(APIView):
    """
    API-представление для управления подпиской на курс.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Управление подпиской на курс",
        description=(
            "Позволяет подписаться на курс или отписаться от него. "
            "Если пользователь уже подписан на курс, подписка удаляется. "
            "Если подписки нет, она создается."
        ),
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "course_id": {
                        "type": "integer",
                        "description": "ID курса для подписки/отписки.",
                    }
                },
                "required": ["course_id"],
            }
        },
        responses={
            200: {
                "description": "Успешное выполнение",
                "examples": [
                    ("Подписка добавлена", {"value": {"message": "подписка добавлена"}}),  # noqa: E501
                    ("Подписка удалена", {"value": {"message": "подписка удалена"}}),
                ],
            }
        },
    )
    def post(self, *args, **kwargs):
        user = self.request.user
        course_id = self.request.data.get("course_id")
        course_item = get_object_or_404(Course, pk=course_id)

        subs_item = Subscription.objects.filter(user=user, course=course_item)

        # Если подписка у пользователя на этот курс есть - удаляем ее
        if subs_item.exists():
            subs_item.delete()
            message = "подписка удалена"
        # Если подписки у пользователя на этот курс нет - создаем ее
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = "подписка добавлена"
        # Возвращаем ответ в API
        return Response({"message": message})
