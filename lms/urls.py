"""
Настройка URL-адресов для приложения LMS.
"""

from rest_framework.routers import DefaultRouter

from lms.apps import LmsConfig
from lms.views import (
    CourseViewSet,
    LessonViewSet,
)

app_name = LmsConfig.name

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="courses")
router.register(r"lessons", LessonViewSet, basename="lessons")

urlpatterns = []

urlpatterns += router.urls
