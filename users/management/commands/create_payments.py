from django.core.management.base import BaseCommand
from users.models import User, Payment
from lms.models import Course, Lesson
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    """
    Кастомная команда для создания тестовых пользователей, курсов, уроков и платежей.
    """

    help = "Создает тестовые данные: пользователей, курсы, уроки и платежи."

    def handle(self, *args, **options):
        """
        Логика выполнения команды.
        """
        self.stdout.write("Удаление старых тестовых данных...")
        User.objects.filter(is_superuser=False).delete()
        Course.objects.all().delete()
        Lesson.objects.all().delete()
        Payment.objects.all().delete()

        self.stdout.write("Создание тестовых пользователей...")
        users_to_create = [
            {"email": "user1@example.com", "first_name": "Иван", "last_name": "Иванов"},
            {"email": "user2@example.com", "first_name": "Петр", "last_name": "Петров"},
            {
                "email": "user3@example.com",
                "first_name": "Анна",
                "last_name": "Сидорова",
            },
        ]
        test_users = []
        for user_data in users_to_create:
            user = User.objects.create_user(
                email=user_data["email"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                password="password123",
            )
            test_users.append(user)
        self.stdout.write(f"Создано {len(test_users)} пользователей.")

        self.stdout.write("Создание тестовых курсов...")
        course1 = Course.objects.create(
            title="Основы Python", description="Базовый курс по Python."
        )
        course2 = Course.objects.create(
            title="Продвинутый Django",
            description="Глубокое погружение в Django и DRF.",
        )
        test_courses = [course1, course2]
        self.stdout.write(f"Создано {len(test_courses)} курсов.")

        self.stdout.write("Создание тестовых уроков...")
        lesson1_c1 = Lesson.objects.create(
            title="Введение в Python",
            description="Первые шаги в программировании на Python.",
            video_link="http://example.com/video1",
            course=course1,
        )
        lesson2_c1 = Lesson.objects.create(
            title="Типы данных Python",
            description="Изучение основных типов данных.",
            video_link="http://example.com/video2",
            course=course1,
        )
        lesson1_c2 = Lesson.objects.create(
            title="DRF: Сериализаторы",
            description="Основы работы с сериализаторами в DRF.",
            video_link="http://example.com/drf_video1",
            course=course2,
        )
        test_lessons = [lesson1_c1, lesson2_c1, lesson1_c2]
        self.stdout.write(f"Создано {len(test_lessons)} уроков.")

        self.stdout.write("Создание тестовых платежей...")
        payment_methods = ["cash", "transfer"]
        now = datetime.now()
        test_payments = []

        # Платежи за курсы
        for user in test_users:
            for course in test_courses:
                payment_date = now - timedelta(days=random.randint(1, 30))
                payment = Payment.objects.create(
                    user=user,
                    payment_date=payment_date,
                    paid_course=course,
                    amount=random.randint(100, 500) * 100,
                    payment_method=random.choice(payment_methods),
                )
                test_payments.append(payment)

        # Платежи за уроки
        for user in test_users:
            for lesson in test_lessons:
                if (
                    random.random() > 0.5
                ):  # Некоторые уроки могут быть оплачены отдельно
                    payment_date = now - timedelta(days=random.randint(1, 30))
                    payment = Payment.objects.create(
                        user=user,
                        payment_date=payment_date,
                        paid_lesson=lesson,
                        amount=random.randint(10, 50) * 100,
                        payment_method=random.choice(payment_methods),
                    )
                    test_payments.append(payment)

        self.stdout.write(f"Создано {len(test_payments)} платежей.")
        self.stdout.write(self.style.SUCCESS("Тестовые данные успешно созданы!"))
