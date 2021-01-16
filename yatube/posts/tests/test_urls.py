from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(username="Leo")
        cls.group = Group.objects.create(
            title="Заголовок группы",
            slug="test",
            description="Тестовый текст"
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый текст"
        )
        cls.list_pages_client = {
            reverse("new_post"): "posts/new_post.html",
            reverse("post_edit", args=[cls.user, 1]): "posts/new_post.html",
        }
        cls.list_pages_guest = {
            reverse("index"): "index.html",
            reverse("post", args=[cls.user, 1]): "posts/post.html",
            reverse("profile", args=[cls.user]): "posts/profile.html",
            reverse("group",
                    kwargs={"slug": cls.group.slug}): "posts/group.html",
            reverse("about:author"): "about/author.html",
            reverse("about:tech"): "about/tech.html"
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def test_pages_guest(self):
        for page, template in self.list_pages_guest.items():
            with self.subTest(url=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, 200,
                                 f"Страница {page} не отвечает")

    def test_pages_client(self):
        for page, template in self.list_pages_client.items():
            with self.subTest(url=page):
                response = self.authorized_user.get(page)
                self.assertEqual(response.status_code, 200,
                                 f"Страница {page} не отвечает")

    def test_pages_guest_templates(self):
        for page, template in self.list_pages_guest.items():
            with self.subTest(url=page):
                response = self.guest_client.get(page)
                self.assertTemplateUsed(response, template,
                                        f"Шаблон {template} не работает")

    def test_pages_client_templates(self):
        for page, template in self.list_pages_client.items():
            with self.subTest(url=page):
                response = self.authorized_user.get(page)
                self.assertTemplateUsed(response, template,
                                        f"Шаблон {template} не работает")

    def test_guest_redirect(self):
        for page, template in self.list_pages_client.items():
            with self.subTest(url=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, 302)

    def test_404(self):
        for page, template in self.list_pages_guest.items():
            with self.subTest(url=page):
                not_page = "not_" + page
                response = self.client.get(not_page)
                self.assertEqual(response.status_code, 404)
