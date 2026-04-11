"""
Настройка URL-адресов для приложения users.
"""
from rest_framework.routers import DefaultRouter
from django.urls import path

from users.apps import UsersConfig
from users.views import UserViewSet, PaymentListAPIView

app_name = UsersConfig.name

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    path("payments/", PaymentListAPIView.as_view(), name="payment_list"),
]

urlpatterns += router.urls
