"""
API-представления (Views) для модели User в приложении users.
"""

from rest_framework import viewsets, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from users.models import User, Payment
from users.serializers import (
    UserSerializer,
    PaymentSerializer,
    UserPublicSerializer,
)  # Импортируем UserPublicSerializer
from users.filters import PaymentFilter
from users.permissions import IsOwner  # Импортируем IsOwner


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели User, предоставляющий полный набор CRUD-операций
    для управления профилями пользователей.
    """

    queryset = User.objects.all()

    def get_permissions(self):
        """
        Устанавливает разрешения для разных действий.
        """
        if self.action == "create":  # Регистрация
            self.permission_classes = [AllowAny]
        elif self.action in [
            "retrieve",
            "update",
            "partial_update",
            "destroy",
        ]:  # Просмотр/Редактирование/Удаление конкретного пользователя
            self.permission_classes = [IsAuthenticated, IsOwner]
        else:  # list action (просмотр списка пользователей)
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        """
        Возвращает соответствующий сериализатор в зависимости от действия.
        """
        if self.action == "retrieve":
            # Если пользователь просматривает свой профиль, или если это его профиль
            if self.request.user == self.get_object():
                return UserSerializer
            # Если просматривает чужой профиль
            return UserPublicSerializer
        return UserSerializer


class PaymentListAPIView(generics.ListAPIView):
    """
    APIView для вывода списка платежей с возможностями фильтрации и сортировки.
    """

    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PaymentFilter
    ordering_fields = ("payment_date",)
