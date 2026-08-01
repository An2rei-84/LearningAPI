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
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes


@extend_schema(tags=["Курсы"],
               description="Управление курсами. Предоставляет полный набор CRUD-операций для курсов.",
               methods={
                   'list': extend_schema(
                       summary="Получение списка курсов",
                       description="Возвращает список всех курсов. Обычные пользователи видят только свои собственные курсы. Модераторы видят все курсы."
                   ),
                   'create': extend_schema(
                       summary="Создание нового курса",
                       description="Создает новый курс. Модераторы не могут создавать курсы. Владелец курса устанавливается автоматически на текущего пользователя."
                   ),
                   'retrieve': extend_schema(
                       summary="Получение информации о курсе",
                       description="Возвращает детальную информацию об одном курсе по его ID. Доступно владельцу курса и модераторам."
                   ),
                   'update': extend_schema(
                       summary="Полное обновление курса",
                       description="Полностью обновляет информацию о курсе по его ID. Доступно владельцу курса и модераторам."
                   ),
                   'partial_update': extend_schema(
                       summary="Частичное обновление курса",
                       description="Частично обновляет информацию о курсе по его ID. Доступно владельцу курса и модераторам."
                   ),
                   'destroy': extend_schema(
                       summary="Удаление курса",
                       description="Удаляет курс по его ID. Доступно только владельцу курса."
                   )
               })
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


@extend_schema(tags=["Уроки"],
               description="Управление уроками. Предоставляет полный набор CRUD-операций для уроков.",
               methods={
                   'list': extend_schema(
                       summary="Получение списка уроков",
                       description="Возвращает список всех уроков. Обычные пользователи видят только свои собственные уроки. Модераторы видят все уроки."
                   ),
                   'create': extend_schema(
                       summary="Создание нового урока",
                       description="Создает новый урок. Модераторы не могут создавать уроки. Владелец урока устанавливается автоматически на текущего пользователя."
                   ),
                   'retrieve': extend_schema(
                       summary="Получение информации об уроке",
                       description="Возвращает детальную информацию об одном уроке по его ID. Доступно владельцу урока и модераторам."
                   ),
                   'update': extend_schema(
                       summary="Полное обновление урока",
                       description="Полностью обновляет информацию об уроке по его ID. Доступно владельцу урока и модераторам."
                   ),
                   'partial_update': extend_schema(
                       summary="Частичное обновление урока",
                       description="Частично обновляет информацию об уроке по его ID. Доступно владельцу урока и модераторам."
                   ),
                   'destroy': extend_schema(
                       summary="Удаление урока",
                       description="Удаляет урок по его ID. Доступно только владельцу урока."
                   )
               })
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
        description="Позволяет подписаться на курс или отписаться от него. Если пользователь уже подписан на указанный курс, подписка удаляется. Если подписки нет, она создается.",
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
                    ("Подписка добавлена", {"value": {"message": "подписка добавлена"}}),
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
