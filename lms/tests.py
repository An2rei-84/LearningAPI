from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from lms.models import Course, Lesson, Subscription


class LmsTestCase(APITestCase):
    """
    Базовый тестовый класс для LMS-приложения.
    Настраивает тестовых пользователей, группы, курсы и уроки.
    """

    def setUp(self):
        self.User = get_user_model()

        # Создаем группы модераторов
        self.moderators_group, created = Group.objects.get_or_create(name="moderators")

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
        self.moderator.groups.add(self.moderators_group)

        # Создаем тестовые курсы
        self.course1 = Course.objects.create(
            title="Тестовый курс 1", description="Описание курса 1", owner=self.owner
        )
        self.course2 = Course.objects.create(
            title="Тестовый курс 2", description="Описание курса 2", owner=self.user
        )

        # Создаем тестовые уроки
        self.lesson1 = Lesson.objects.create(
            title="Тестовый урок 1",
            description="Описание урока 1",
            course=self.course1,
            owner=self.owner,
            video_link="https://www.youtube.com/watch?v=video1",
        )
        self.lesson2 = Lesson.objects.create(
            title="Тестовый урок 2",
            description="Описание урока 2",
            course=self.course2,
            owner=self.user,
            video_link="https://www.youtube.com/watch?v=video2",
        )

        # URL-адреса для API
        self.lessons_list_url = reverse("lms:lessons-list")
        self.lesson_detail_url = lambda pk: reverse("lms:lessons-detail", args=[pk])
        self.courses_list_url = reverse("lms:courses-list")
        self.course_detail_url = lambda pk: reverse("lms:courses-detail", args=[pk])
        self.subscription_toggle_url = reverse("lms:subscription_toggle")


class LessonCRUDTestCase(LmsTestCase):
    """
    Тесты для CRUD операций с уроками.
    """

    def test_lesson_create(self):
        """
        Тест создания урока.
        """
        self.client.force_authenticate(user=self.owner)
        data = {
            "title": "Новый урок",
            "description": "Описание нового урока",
            "course": self.course1.id,
            "video_link": "https://www.youtube.com/watch?v=new_video",
        }
        response = self.client.post(self.lessons_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 3)
        self.assertEqual(Lesson.objects.get(title="Новый урок").owner, self.owner)

    def test_lesson_create_by_moderator_fails(self):
        """
        Тест, что модератор не может создать урок.
        """
        self.client.force_authenticate(user=self.moderator)
        data = {
            "title": "Урок от модератора",
            "description": "Описание",
            "course": self.course1.id,
            "video_link": "https://www.youtube.com/watch?v=mod_video",
        }
        response = self.client.post(self.lessons_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_lesson_list(self):
        """
        Тест получения списка уроков.
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.lessons_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Владелец видит только свои уроки (lesson1)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], self.lesson1.title)

    def test_lesson_list_moderator(self):
        """
        Тест получения списка уроков модератором (видит все).
        """
        self.client.force_authenticate(user=self.moderator)
        response = self.client.get(self.lessons_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_lesson_retrieve(self):
        """
        Тест получения деталей урока.
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.lesson_detail_url(self.lesson1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.lesson1.title)

    def test_lesson_retrieve_other_owner_fails(self):
        """
        Тест, что пользователь не может получить детали чужого урока.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.lesson_detail_url(self.lesson1.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_update(self):
        """
        Тест обновления урока владельцем.
        """
        self.client.force_authenticate(user=self.owner)
        updated_data = {"title": "Обновленный урок 1"}
        response = self.client.patch(
            self.lesson_detail_url(self.lesson1.id), updated_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson1.refresh_from_db()
        self.assertEqual(self.lesson1.title, "Обновленный урок 1")

    def test_lesson_update_moderator(self):
        """
        Тест обновления урока модератором.
        """
        self.client.force_authenticate(user=self.moderator)
        updated_data = {"title": "Урок 1 (обновлен модератором)"}
        response = self.client.patch(
            self.lesson_detail_url(self.lesson1.id), updated_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson1.refresh_from_db()
        self.assertEqual(self.lesson1.title, "Урок 1 (обновлен модератором)")

    def test_lesson_update_other_user_fails(self):
        """
        Тест, что другой пользователь не может обновить урок.
        """
        self.client.force_authenticate(user=self.user)
        updated_data = {"title": "Попытка обновления"}
        response = self.client.patch(
            self.lesson_detail_url(self.lesson1.id), updated_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_delete(self):
        """
        Тест удаления урока владельцем.
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.lesson_detail_url(self.lesson1.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_lesson_delete_moderator_fails(self):
        """
        Тест, что модератор не может удалить урок.
        """
        self.client.force_authenticate(user=self.moderator)
        response = self.client.delete(self.lesson_detail_url(self.lesson1.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_lesson_delete_other_user_fails(self):
        """
        Тест, что другой пользователь не может удалить урок.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.lesson_detail_url(self.lesson1.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_video_link_validator_success(self):
        """
        Тест валидатора ссылки на YouTube (успех).
        """
        self.client.force_authenticate(user=self.owner)
        data = {
            "title": "Урок с YouTube",
            "description": "Описание",
            "course": self.course1.id,
            "video_link": "https://www.youtube.com/watch?v=valid_link",
        }
        response = self.client.post(self.lessons_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 3)

    def test_video_link_validator_fail(self):
        """
        Тест валидатора ссылки (провал, не YouTube).
        """
        self.client.force_authenticate(user=self.owner)
        data = {
            "title": "Урок с не YouTube",
            "description": "Описание",
            "course": self.course1.id,
            "video_link": "https://vimeo.com/some_video",
        }
        response = self.client.post(self.lessons_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Ссылка должна вести на youtube.com", str(response.data))
        self.assertEqual(Lesson.objects.count(), 2)


class SubscriptionTestCase(LmsTestCase):
    """
    Тесты для функционала подписки.
    """

    def test_toggle_subscription_add(self):
        """
        Тест добавления подписки.
        """
        self.client.force_authenticate(user=self.user)
        data = {"course_id": self.course1.id}
        response = self.client.post(self.subscription_toggle_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка добавлена")
        self.assertTrue(
            Subscription.objects.filter(
                user=self.user, course=self.course1
            ).exists()
        )

    def test_toggle_subscription_remove(self):
        """
        Тест удаления подписки.
        """
        Subscription.objects.create(user=self.user, course=self.course1)
        self.client.force_authenticate(user=self.user)
        data = {"course_id": self.course1.id}
        response = self.client.post(self.subscription_toggle_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка удалена")
        self.assertFalse(
            Subscription.objects.filter(
                user=self.user, course=self.course1
            ).exists()
        )

    def test_is_subscribed_field(self):
        """
        Тест поля is_subscribed в сериализаторе курса.
        """
        # Сначала пользователь не подписан на course1
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.course_detail_url(self.course2.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_subscribed"])

        # Пользователь подписывается на course2
        Subscription.objects.create(user=self.user, course=self.course2)
        response = self.client.get(self.course_detail_url(self.course2.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_subscribed"])


class PaginationTestCase(LmsTestCase):
    """
    Тесты для пагинации.
    """

    def test_lesson_pagination(self):
        """
        Тест пагинации списка уроков.
        """
        # Создаем много уроков для одного владельца
        for i in range(15):
            Lesson.objects.create(
                title=f"Урок {i}",
                description="Описание",
                course=self.course1,
                owner=self.owner,
                video_link="https://www.youtube.com/watch?v=pag_video",
            )
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.lessons_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertEqual(len(response.data["results"]), 10)  # page_size = 10
        self.assertEqual(response.data["count"], 16)  # 15 новых + lesson1

        # Тестирование page_size_query_param
        response = self.client.get(f"{self.lessons_list_url}?page_size=5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 5)

    def test_course_pagination(self):
        """
        Тест пагинации списка курсов.
        """
        # Создаем много курсов
        for i in range(15):
            Course.objects.create(
                title=f"Тестовый курс {i + 3}",
                description="Описание",
                owner=self.user,
            )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.courses_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertEqual(len(response.data["results"]), 10)  # page_size = 10
        self.assertEqual(response.data["count"], 16)  # 15 новых + course2
