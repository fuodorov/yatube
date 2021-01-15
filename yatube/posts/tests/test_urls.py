from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post, User


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create(
            username="eva",
            first_name="eva",
            last_name="eva"
        )
        cls.user2 = User.objects.create(
            username="bob",
            first_name="bob",
            last_name="bob"
        )
        cls.group = Group.objects.create(
            title="Заголовок",
            slug="test_slug",
            description="Текст"
        )
        cls.post = Post.objects.create(
            text="Текст",
            author=cls.user1,
            group=cls.group
        )
        cls.guest_client = Client()
        cls.creator_user = Client()
        cls.creator_user.force_login(cls.user1)
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user2)
        cls.list_pages_client = {
            reverse("new_post"): "posts/new_post.html",
        }
        cls.list_pages_guest = {
            reverse("index"): "index.html",
            reverse("group",
                    kwargs={"slug": cls.group.slug}): "posts/group.html",
        }

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
                response = self.client.get(page, follow=True)
                login_page = reverse("login")
                self.assertRedirects(
                    response, (f'{login_page}?next={page}')
                )

    def test_404(self):
        for page, template in self.list_pages_guest.items():
            with self.subTest(url=page):
                not_page = "not_" + page
                response = self.client.get(not_page)
                self.assertEqual(response.status_code, 404)
