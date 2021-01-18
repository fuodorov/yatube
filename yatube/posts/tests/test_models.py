from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post


class TestModelGroup(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title="Название группы",
            slug="test_slug",
            description="Текст"
        )
        cls.group = Group.objects.first()

    def test_verbose_name(self):
        group_field = self.group
        field_verbose = {
            "title": "Название группы: ",
            "slug": "Адрес в интернете: ",
            "description": "Информация об авторе: "
        }
        for value, expect in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group_field._meta.get_field(value).verbose_name,
                    expect,
                    "Неправильное поле verbose_name"
                )

    def test_help_text(self):
        group_field = self.group
        field_help_text = {
            "title": "Напишите название группы.",
            "slug": "Укажите адрес сообщества в интернете.",
            "description": "Напишите что-нибудь об авторе."
        }
        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group_field._meta.get_field(value).help_text,
                    expected,
                    "Неправильное поле help_text"
                )

    def test_str(self):
        value = self.group.__str__()
        expected = self.group.title
        self.assertEqual(value, expected, "Метод __str__() не работает")


class TestModelPost(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = get_user_model().objects.create_user(username="Alex")
        group = Group.objects.create(
            title="Название группы",
            slug="test_slug",
            description="Текст"
        )
        Post.objects.create(
            text="Текст",
            author=user,
            group=group
        )
        cls.post = Post.objects.get(id=1)

    def test_verbose_name(self):
        post_fields = self.post
        field_verbose = {
            "text": "Текст заметки: ",
            "author": "Автор заметки: ",
            "group": "Группа: "
        }
        for value, expected in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post_fields._meta.get_field(value).verbose_name,
                    expected,
                    "Неправильное поле verbose_name"
                )

    def test_help_text(self):
        post_fields = self.post
        field_verbose = {
            "text": "Напишите здесь текст заметки.",
            "author": "Это пользователь, опубликовавший заметку.",
            "group": "Выберите группу, к которой будет принадлежать пост."
        }
        for value, expected in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post_fields._meta.get_field(value).help_text,
                    expected,
                    "Неправильное поле help_text"
                )

    def test_str(self):
        value = TestModelGroup.group.__str__()
        expected = TestModelGroup.group.title
        self.assertEqual(value, expected, "Метод __str__() не работает")
