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
    paid_course = serializers.SlugRelatedField(slug_field="title", read_only=True)
    paid_lesson = serializers.SlugRelatedField(slug_field="title", read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"


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
