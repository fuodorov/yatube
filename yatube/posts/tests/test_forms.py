from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.test_user = User.objects.create(
            username="test_user"
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.test_user)
        cls.test_group = Group.objects.create(
            title="Тестовое сообщество",
            slug="test_group",
            description="test_group",
        )

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            "text": "Создаем новую запись в группе",
            "group": self.test_group.id,
        }
        response = self.authorized_client.post(
            reverse("new_post"),
            data=form_data
        )
        self.assertEqual(Post.objects.count(), posts_count+1)
        self.assertEqual(response.status_code, 302)
        last_object = Post.objects.last()
        self.assertEqual(last_object.text, form_data["text"])
        self.assertEqual(last_object.group, self.test_group)
        self.assertEqual(last_object.author, self.test_user)

    def test_edit_post(self):
        form_data_edit = {
            "text": "Исправленный тестовый текст записи",
            "group": self.test_group.id,
        }
        test_post = Post.objects.create(
            text="Тестовый текст записи",
            author=self.test_user,
        )
        kwargs = {'username': 'test_user', 'post_id': test_post.id}
        response = self.authorized_client.post(
            reverse('post_edit', kwargs=kwargs),
            data=form_data_edit
        )
        test_post.refresh_from_db()
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(test_post.text, form_data_edit["text"])
        self.assertEqual(test_post.group, self.test_group)
        self.assertEqual(test_post.author, self.test_user)

    def test_create_post_guest(self):
        form_data = {
            "text": "Гость пытается создать новую запись в группе",
            "group": self.test_group.id,
        }
        response = self.client.post(
            reverse("new_post"),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_edit_post_guest(self):
        form_data_edit = {
            "text": "Исправленный гостем текст записи",
            "group": self.test_group.id,
        }
        test_post = Post.objects.create(
            text="Тестовый текст записи",
            author=self.test_user,
            group=self.test_group,
        )
        test_post.refresh_from_db()
        self.assertNotEqual(test_post.text, form_data_edit["text"])
        self.assertEqual(test_post.group, self.test_group)
        self.assertEqual(test_post.author, self.test_user)

    def test_edit_post_not_author(self):
        form_data_edit = {
            "text": "Исправленный не автором текст записи",
            "group": self.test_group.id,
        }
        test_post = Post.objects.create(
            text="Тестовый текст записи",
            author=self.test_user,
            group=self.test_group,
        )
        not_author_user = User.objects.create(
            username="not_author"
        )
        not_author_client = Client()
        not_author_client.force_login(not_author_user)
        test_post.refresh_from_db()
        self.assertNotEqual(test_post.text, form_data_edit["text"])
        self.assertEqual(test_post.group, self.test_group)
        self.assertEqual(test_post.author, self.test_user)
