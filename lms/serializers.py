"""
Сериализаторы для моделей Course и Lesson в приложении LMS.
"""

from rest_framework import serializers

from lms.models import Course, Lesson, Subscription
from lms.validators import validate_youtube_link


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Lesson.
    """

    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    video_link = serializers.URLField(
        validators=[validate_youtube_link], required=False, allow_null=True
    )

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
        exclude = (
            "course",
            "owner",
        )


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Course.
    """

    # Добавляем поле для отображения количества уроков в курсе
    lesson_count = serializers.SerializerMethodField()
    # Добавляем поле для вывода списка уроков, связанных с курсом
    lessons = LessonInCourseSerializer(many=True, read_only=True)
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "preview",
            "description",
            "lesson_count",
            "lessons",
            "owner",
            "is_subscribed",
        )

    def get_lesson_count(self, obj):
        """
        Возвращает количество уроков, связанных с данным курсом.
        """
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """
        Возвращает True, если текущий пользователь подписан на курс, иначе False.
        """
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, course=obj).exists()
        return False
