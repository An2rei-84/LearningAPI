"""
API-представления (Views) для модели User в приложении users.
"""

from rest_framework import viewsets, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter

from users.models import User, Payment
from users.serializers import (
    UserSerializer,
    PaymentSerializer,
    UserPublicSerializer,
    PaymentRetrieveSerializer,
)
from users.filters import PaymentFilter
from users.permissions import IsOwner

# Импорты, которые были ниже в оригинальном файле, но нужны для классов ниже
from django.urls import reverse
from rest_framework.response import Response
from rest_framework import status
from users import services
from lms.models import Course


@extend_schema(
    tags=["Пользователи"],
    description="Управление профилями пользователей. Предоставляет полный набор CRUD-операций.",
    methods={
        "list": extend_schema(
            summary="Получение списка пользователей",
            description=(
                "Возвращает список всех зарегистрированных пользователей. "
                "Доступно только аутентифицированным пользователям."
            ),
        ),
        "create": extend_schema(
            summary="Регистрация нового пользователя",
            description=(
                "Позволяет зарегистрировать нового пользователя, указав email и пароль. "
                "Доступно всем, без аутентификации."
            ),
        ),
        "retrieve": extend_schema(
            summary="Получение информации о пользователе",
            description=(
                "Возвращает детальную информацию о пользователе по его ID. "
                "Если запрашивается собственный профиль, возвращается полная информация. "
                "При просмотре чужого профиля, возвращается публичная информация "
                "(без конфиденциальных полей). "
                "Доступно владельцу профиля и аутентифицированным пользователям."
            ),
        ),
        "update": extend_schema(
            summary="Полное обновление профиля пользователя",
            description=(
                "Полностью обновляет информацию о текущем пользователе по его ID. "
                "Доступно только владельцу профиля."
            ),
        ),
        "partial_update": extend_schema(
            summary="Частичное обновление профиля пользователя",
            description=(
                "Частично обновляет информацию о текущем пользователе по его ID. "
                "Доступно только владельцу профиля."
            ),
        ),
        "destroy": extend_schema(
            summary="Удаление профиля пользователя",
            description="Удаляет профиль текущего пользователя по его ID. Доступно только владельцу профиля.",
        ),
    },
)
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


@extend_schema(
    tags=["Платежи"],
    summary="Получение списка платежей",
    description=(
        "Возвращает список всех платежей с возможностью фильтрации и сортировки. "
        "Доступно аутентифицированным пользователям."
    ),
    parameters=[
        OpenApiParameter(
            name="paid_course",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Фильтрация по ID оплаченного курса.",
        ),
        OpenApiParameter(
            name="paid_lesson",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Фильтрация по ID оплаченного урока.",
        ),
        OpenApiParameter(
            name="payment_method",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Фильтрация по способу оплаты (например, 'cash', 'transfer', 'stripe').",
        ),
        OpenApiParameter(
            name="ordering",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Сортировка по дате платежа. Доступные значения: 'payment_date', '-payment_date'.",
        ),
    ],
)
class PaymentListAPIView(generics.ListAPIView):
    """
    APIView для вывода списка платежей с возможностями фильтрации и сортировки.
    """

    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PaymentFilter
    ordering_fields = ("payment_date",)


@extend_schema(
    tags=["Платежи"],
    summary="Создание платежа для курса",
    description=(
        "Создает платеж для указанного курса и инициирует процесс оплаты через Stripe. "
        "Возвращает объект платежа, содержащий ссылку на страницу оплаты Stripe."
    ),
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "paid_course": {
                    "type": "integer",
                    "description": "ID курса, который будет оплачен.",
                },
            },
            "required": ["paid_course"],
        }
    },
    responses={
        201: PaymentSerializer,  # Ссылка на сериализатор для подробного ответа
        # Можно добавить дополнительные коды ошибок, если они обрабатываются
    },
)
class PaymentCreateAPIView(generics.CreateAPIView):
    """
    API-представление для создания платежа через Stripe.
    """

    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Создает платеж, интегрируясь со Stripe.
        """
        course_id = self.request.data.get("paid_course")
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response(
                {"error": "Курс не найден."}, status=status.HTTP_404_NOT_FOUND
            )

        amount = course.price

        payment = serializer.save(
            user=self.request.user,
            amount=amount,
            paid_course=course,
            payment_method="stripe",
        )

        stripe_product = services.create_stripe_product(course.title)
        stripe_price = services.create_stripe_price(stripe_product.id, payment.amount)

        success_url = self.request.build_absolute_uri(
            reverse("users:payment_retrieve", kwargs={"pk": payment.pk})
        )
        cancel_url = self.request.build_absolute_uri(reverse("users:payment_list"))

        stripe_session = services.create_stripe_session(
            stripe_price.id, success_url, cancel_url
        )

        payment.stripe_session_id = stripe_session.id
        payment.stripe_payment_link = stripe_session.url
        payment.save()


@extend_schema(
    tags=["Платежи"],
    summary="Получение информацию о платеже и его статусе",
    description=(
        "Возвращает детальную информацию об одном платеже по его ID, "
        "включая актуальный статус платежа, полученный из Stripe. "
        "Доступно владельцу платежа."
    ),
    responses={200: PaymentRetrieveSerializer},
)
class PaymentRetrieveAPIView(generics.RetrieveAPIView):
    """
    API-представление для получения информации о платеже и его статусе в Stripe.
    """

    queryset = Payment.objects.filter(payment_method="stripe")
    serializer_class = PaymentRetrieveSerializer
    permission_classes = [IsAuthenticated, IsOwner]
