"""
Сериализаторы для моделей Course и Lesson в приложении LMS.
"""
from rest_framework import serializers

from lms.models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Lesson.
    """

    class Meta:
        model = Lesson
        fields = "__all__"


class LessonInCourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Lesson, используемый внутри CourseSerializer.
    Исключает поле course для избежания циклических ссылок.
    """

    class Meta:
        model = Lesson
        exclude = ("course",)


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Course.
    """

    # Добавляем поле для отображения количества уроков в курсе
    lesson_count = serializers.SerializerMethodField()
    # Добавляем поле для вывода списка уроков, связанных с курсом
    lessons = LessonInCourseSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "preview",
            "description",
            "lesson_count",
            "lessons",
        )

    def get_lesson_count(self, obj):
        """
        Возвращает количество уроков, связанных с данным курсом.
        """
        return obj.lessons.count()
