"""
Настройка URL-адресов для приложения LMS.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

from lms.apps import LmsConfig
from lms.views import (
    CourseViewSet,
    LessonListCreateAPIView,
    LessonRetrieveUpdateDestroyAPIView,
)

app_name = LmsConfig.name

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="courses")

urlpatterns = [
    path("lessons/", LessonListCreateAPIView.as_view(), name="lesson_list_create"),
    path(
        "lessons/<int:pk>/",
        LessonRetrieveUpdateDestroyAPIView.as_view(),
        name="lesson_retrieve_update_destroy",
    ),
]

urlpatterns += router.urls
