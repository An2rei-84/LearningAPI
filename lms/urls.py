"""
Настройка URL-адресов для приложения LMS.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from lms.apps import LmsConfig
from lms.views import (
    CourseViewSet,
    LessonViewSet,
    SubscriptionAPIView,
)

app_name = LmsConfig.name

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="courses")
router.register(r"lessons", LessonViewSet, basename="lessons")

urlpatterns = [
    path("subscriptions/toggle/", SubscriptionAPIView.as_view(), name="subscription_toggle"),
]

urlpatterns += router.urls
