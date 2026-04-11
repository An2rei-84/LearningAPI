"""
API-представления (Views) для моделей Course и Lesson в приложении LMS.
"""
from rest_framework import viewsets, generics

from lms.models import Course, Lesson
from lms.serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Course, предоставляющий полный набор CRUD-операций.
    """

    serializer_class = CourseSerializer
    queryset = Course.objects.all()


class LessonListCreateAPIView(generics.ListCreateAPIView):
    """
    APIView для получения списка всех уроков и создания нового урока.
    """

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    APIView для получения, обновления и удаления отдельного урока.
    """

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
