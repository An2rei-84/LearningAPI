"""
Модели для приложения пользователей.
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """
    Кастомный менеджер модели пользователя, где email является уникальным идентификатором
    для аутентификации вместо имени пользователя.
    """

    def _create_user(self, email, password, **extra_fields):
        """
        Создает и сохраняет пользователя с заданным email и паролем.
        """
        if not email:
            raise ValueError("Email должен быть установлен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Создает и сохраняет пользователя с заданным email и паролем.
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Создает и сохраняет суперпользователя с заданным email и паролем.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Кастомная модель пользователя, расширяющая стандартную AbstractUser.
    Использует email для авторизации вместо username.
    """

    username = None  # Отключаем стандартное поле username
    email = models.EmailField(unique=True, verbose_name="email")

    phone = models.CharField(
        max_length=35, verbose_name="телефон", blank=True, null=True
    )
    city = models.CharField(max_length=100, verbose_name="город", blank=True, null=True)
    avatar = models.ImageField(
        upload_to="users/avatars/",
        verbose_name="аватар",
        blank=True,
        null=True,
    )

    USERNAME_FIELD = "email"  # Устанавливаем email как поле для авторизации
    REQUIRED_FIELDS = []  # Убираем REQUIRED_FIELDS, так как email уже unique=True

    objects = UserManager()  # Присваиваем кастомный менеджер

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        """
        Возвращает строковое представление пользователя (email).
        """
        return self.email


class Payment(models.Model):
    """
    Модель, представляющая платежи пользователей за курсы или уроки.
    """

    PAYMENT_METHOD_CHOICES = [
        ("cash", "Наличные"),
        ("transfer", "Перевод на счет"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="пользователь",
    )
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="дата оплаты")
    paid_course = models.ForeignKey(
        "lms.Course",
        on_delete=models.CASCADE,
        verbose_name="оплаченный курс",
        blank=True,
        null=True,
    )
    paid_lesson = models.ForeignKey(
        "lms.Lesson",
        on_delete=models.CASCADE,
        verbose_name="оплаченный урок",
        blank=True,
        null=True,
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="сумма оплаты"
    )
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHOD_CHOICES,
        default="transfer",
        verbose_name="способ оплаты",
    )

    class Meta:
        verbose_name = "платеж"
        verbose_name_plural = "платежи"

    def __str__(self):
        """
        Возвращает строковое представление платежа.
        """
        if self.paid_course:
            return (
                f"Платеж от {self.user.email} за курс "
                f"'{self.paid_course.title}' на сумму {self.amount}"
            )
        elif self.paid_lesson:
            return (
                f"Платеж от {self.user.email} за урок "
                f"'{self.paid_lesson.title}' на сумму {self.amount}"
            )
        return f"Платеж от {self.user.email} на сумму {self.amount}"
