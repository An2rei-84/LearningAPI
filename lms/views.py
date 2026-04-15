"""
API-представления (Views) для моделей Course и Lesson в приложении LMS.
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated  # Добавлено
from lms.permissions import IsModerator, IsOwner  # Добавлено

from lms.models import Course, Lesson
from lms.serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Course, предоставляющий полный набор CRUD-операций.
    """

    serializer_class = CourseSerializer
    queryset = Course.objects.all()

    def get_queryset(self):
        # Если пользователь не модератор, показывать только его курсы
        if not self.request.user.groups.filter(name="moderators").exists():
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

    def get_queryset(self):
        # Если пользователь не модератор, показывать только его уроки
        if not self.request.user.groups.filter(name="moderators").exists():
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
