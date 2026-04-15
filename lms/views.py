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


class LessonViewSet(viewsets.ModelViewSet):  # Изменено с Generic API Views
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


class SubscriptionAPIView(APIView):
    """
    API-представление для управления подпиской на курс.
    """

    permission_classes = [IsAuthenticated]

    def post(self, *args, **kwargs):
        """
        Метод для создания/удаления подписки.
        """
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
