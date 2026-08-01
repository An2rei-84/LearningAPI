from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from lms.models import Course
from users.models import Payment
from unittest.mock import patch, Mock


class UserBaseTestCase(APITestCase):
    """
    Базовый тестовый класс для приложения users.
    Настраивает тестовых пользователей и курсы.
    """

    def setUp(self):
        self.User = get_user_model()

        # Создаем тестовых пользователей
        self.user = self.User.objects.create_user(
            email="user@example.com", password="password", is_active=True
        )
        self.owner = self.User.objects.create_user(
            email="owner@example.com", password="password", is_active=True
        )
        self.moderator = self.User.objects.create_user(
            email="moderator@example.com", password="password", is_active=True
        )
        # Создаем группу модераторов, если ее нет
        self.moderators_group, created = Group.objects.get_or_create(name="moderators")
        self.moderator.groups.add(self.moderators_group)

        # Создаем тестовый курс
        self.course = Course.objects.create(
            title="Тестовый курс для оплаты",
            description="Описание курса",
            owner=self.owner,
            price=150.00,
        )

        # URL-адреса для API
        self.payment_create_url = reverse("users:payment_create")
        self.payment_retrieve_url = lambda pk: reverse("users:payment_retrieve", args=[pk])


class PaymentCreateTestCase(UserBaseTestCase):
    """
    Тесты для создания платежей через Stripe.
    """

    @patch("stripe.Product.create")
    @patch("stripe.Price.create")
    @patch("stripe.checkout.Session.create")
    def test_payment_create_stripe(self, mock_session_create, mock_price_create, mock_product_create):
        """
        Тест успешного создания платежа через Stripe.
        """
        # Мокируем ответы Stripe API
        mock_product_create.return_value.id = "prod_test_id"
        mock_price_create.return_value.id = "price_test_id"
        mock_session_create.return_value.id = "cs_test_id"
        mock_session_create.return_value.url = "https://checkout.stripe.com/test_session"

        self.client.force_authenticate(user=self.user)
        data = {"paid_course": self.course.id}
        response = self.client.post(self.payment_create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("stripe_payment_link", response.data)
        self.assertEqual(response.data["stripe_payment_link"], "https://checkout.stripe.com/test_session")

        # Проверяем, что Payment объект был создан в нашей базе
        payment = Payment.objects.get(paid_course=self.course, user=self.user)
        self.assertIsNotNone(payment)
        self.assertEqual(payment.stripe_session_id, "cs_test_id")
        self.assertEqual(payment.stripe_payment_link, "https://checkout.stripe.com/test_session")
        self.assertEqual(payment.amount, self.course.price)
        self.assertEqual(payment.payment_method, "stripe")

        # Проверяем вызовы Stripe API
        mock_product_create.assert_called_once_with(name=self.course.title)
        mock_price_create.assert_called_once_with(product="prod_test_id", unit_amount=int(self.course.price * 100), currency="rub")
        mock_session_create.assert_called_once_with(
            success_url="https://example.com/success",
            line_items=[{"price": "price_test_id", "quantity": 1}],
            mode="payment",
        )

    def test_payment_create_unauthenticated(self):
        """
        Тест попытки создания платежа неаутентифицированным пользователем.
        """
        data = {"paid_course": self.course.id}
        response = self.client.post(self.payment_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Payment.objects.count(), 0)

    def test_payment_create_invalid_course(self):
        """
        Тест попытки создания платежа с несуществующим курсом.
        """
        self.client.force_authenticate(user=self.user)
        data = {"paid_course": 999}  # Несуществующий ID курса
        response = self.client.post(self.payment_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("paid_course", response.data)
        self.assertEqual(Payment.objects.count(), 0)


class PaymentRetrieveTestCase(UserBaseTestCase):
    """
    Тесты для получения информации о платеже и его статусе.
    """

    def setUp(self):
        super().setUp()
        # Создаем платеж для проверки статуса
        self.payment = Payment.objects.create(
            user=self.user,
            paid_course=self.course,
            amount=self.course.price,
            payment_method="stripe",
            stripe_session_id="cs_test_id_retrieved",
            stripe_payment_link="https://checkout.stripe.com/test_session_retrieved",
        )

    @patch("stripe.checkout.Session.retrieve")
    def test_payment_retrieve_status(self, mock_session_retrieve):
        """
        Тест получения статуса платежа из Stripe.
        """
        # Мокируем ответ Stripe API
        mock_session_retrieve.return_value = Mock(payment_status="paid")

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.payment_retrieve_url(self.payment.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("stripe_payment_status", response.data)
        self.assertEqual(response.data["stripe_payment_status"], "paid")
        mock_session_retrieve.assert_called_once_with("cs_test_id_retrieved")

    def test_payment_retrieve_unauthenticated(self):
        """
        Тест попытки получения статуса платежа неаутентифицированным пользователем.
        """
        response = self.client.get(self.payment_retrieve_url(self.payment.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_payment_retrieve_other_user_fails(self):
        """
        Тест, что другой пользователь не может получить статус чужого платежа.
        """
        self.client.force_authenticate(user=self.moderator)  # Модератор не владелец
        response = self.client.get(self.payment_retrieve_url(self.payment.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
