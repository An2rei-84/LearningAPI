"""
Сериализаторы для моделей приложения пользователей.
"""
from rest_framework import serializers

from users.models import User, Payment


class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Payment.
    """

    user = serializers.SlugRelatedField(slug_field="email", read_only=True)
    paid_course = serializers.SlugRelatedField(
        slug_field="title", read_only=True
    )
    paid_lesson = serializers.SlugRelatedField(
        slug_field="title", read_only=True
    )

    class Meta:
        model = Payment
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User, исключая поле password.
    """

    payments = PaymentSerializer(many=True, read_only=True)

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
        )
