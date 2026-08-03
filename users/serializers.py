"""
Сериализаторы для моделей приложения пользователей.
"""

from rest_framework import serializers

from users.models import User, Payment
from lms.models import Course, Lesson
from users.services import retrieve_stripe_session


class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Payment.
    """

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    paid_course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), required=False
    )
    paid_lesson = serializers.PrimaryKeyRelatedField(
        queryset=Lesson.objects.all(), required=False
    )

    class Meta:
        model = Payment
        fields = (
            "id",
            "user",
            "payment_date",
            "paid_course",
            "paid_lesson",
            "amount",
            "payment_method",
            "stripe_session_id",
            "stripe_payment_link",
        )
        read_only_fields = ("amount", "stripe_session_id", "stripe_payment_link")


class PaymentRetrieveSerializer(PaymentSerializer):
    """
    Сериализатор для детального просмотра платежа, включая статус из Stripe.
    """

    stripe_payment_status = serializers.SerializerMethodField()

    class Meta(PaymentSerializer.Meta):
        fields = PaymentSerializer.Meta.fields + ("stripe_payment_status",)

    def get_stripe_payment_status(self, obj):
        """
        Получает статус платежа из Stripe по ID сессии.
        """
        if obj.stripe_session_id:
            session = retrieve_stripe_session(obj.stripe_session_id)
            return session.payment_status
        return "N/A"  # или None, если сессии нет


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User, который включает поле пароля для записи
    и обрабатывает хеширование пароля при создании и обновлении.
    """

    payments = PaymentSerializer(many=True, read_only=True)
    password = serializers.CharField(write_only=True)  # Добавляем поле пароля

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar",
            "payments",
            "password",  # Включаем пароль для записи
        )

    def create(self, validated_data):
        """
        Создает нового пользователя, хешируя его пароль.
        """
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """
        Обновляет пользователя, хешируя новый пароль, если он предоставлен.
        """
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class UserPublicSerializer(serializers.ModelSerializer):
    """
    Сериализатор для публичного отображения модели User,
    исключая конфиденциальные данные.
    """

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "phone",
            "city",
            "avatar",
        )
