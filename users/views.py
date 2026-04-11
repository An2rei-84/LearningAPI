"""
API-представления (Views) для модели User в приложении users.
"""
from rest_framework import viewsets, generics
from django_filters.rest_framework import DjangoFilterBackend

from users.models import User, Payment
from users.serializers import UserSerializer, PaymentSerializer
from users.filters import PaymentFilter


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели User, предоставляющий полный набор CRUD-операций
    для управления профилями пользователей.
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()


class PaymentListAPIView(generics.ListAPIView):
    """
    APIView для вывода списка платежей с возможностями фильтрации и сортировки.
    """

    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PaymentFilter
    ordering_fields = ("payment_date",)
