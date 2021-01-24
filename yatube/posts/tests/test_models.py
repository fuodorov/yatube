from django.test import TestCase

from posts.models import Group, Post, User


class TestModelGroup(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title="Название группы",
            slug="test_slug",
            description="Текст"
        )

    def test_verbose_name(self):
        group_field = self.group
        field_verbose = {
            "title": "Название группы: ",
            "slug": "Ключ для составления адреса: ",
            "description": "Информация об авторе: "
        }
        for value, expect in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group_field._meta.get_field(value).verbose_name, expect)

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
                    group_field._meta.get_field(value).help_text, expected)

    def test_str(self):
        value = self.group.__str__()
        expected = self.group.title
        self.assertEqual(value, expected)


class TestModelPost(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create_user(username="Alex")
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
                    post_fields._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        post_fields = self.post
        field_verbose = {
            "text": "Напишите здесь текст заметки.",
            "author": "Это пользователь, опубликовавший заметку.",
            "group": ("Можете выбрать группу, "
                      "к которой будет принадлежать пост.")
        }
        for value, expected in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post_fields._meta.get_field(value).help_text, expected)

    def test_str(self):
        value = TestModelGroup.group.__str__()
        expected = TestModelGroup.group.title
        self.assertEqual(value, expected)
