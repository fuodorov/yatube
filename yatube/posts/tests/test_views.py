from django import forms
from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import Client, TestCase

from posts.constants import POSTS_PER_PAGE

from ..models import Group, Post


class ViewContentTest(TestCase):
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
            text="Тестовый текст",
            group=cls.group,
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def test_index_content(self):
        response = self.guest_client.get(reverse("index"))
        content = self.post
        expected_content = response.context.get("page")[0]
        self.assertEqual(content, expected_content,
                         "Контент index.html не верен")

    def test_group_content(self):
        response = self.guest_client.get(
            reverse("group", args=["test"])
        )
        content = self.post
        expected_content = response.context.get("post")
        self.assertEqual(content, expected_content,
                         "Контент group.html не верен")

    def test_post_content(self):
        response = self.authorized_user.get(
            reverse("post_edit", kwargs={"username": self.user, "post_id": 1}))
        content = self.post
        expected_content = response.context.get("post")
        self.assertEqual(content, expected_content,
                         "Контент post.html не верен")

    def test_new_post_form(self):
        fields_list = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        response = self.authorized_user.get(reverse("new_post"))
        for field, field_widget in fields_list.items():
            form_field = response.context.get("form").fields.get(field)
            self.assertIsInstance(form_field, field_widget)

    def test_post_edit_form(self):
        fields_list = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        response = self.authorized_user.get(
            reverse("post_edit", args=["Leo", self.post.id]))
        for field, field_widget in fields_list.items():
            form_field = response.context.get("form").fields.get(field)
            self.assertIsInstance(form_field, field_widget)

    def test_create_content_index(self):
        new_post = Post.objects.create(
            text="Тестовый текст",
            author=self.user,
            group=self.group,
            image=self.post.image
        )
        response = self.authorized_user.get(
            reverse("index"))
        self.assertContains(response, new_post)

    def test_create_content_group(self):
        new_post = Post.objects.create(
            text="Тестовый текст",
            author=self.user,
            group=self.group,
            image=self.post.image
        )
        response = self.authorized_user.get(
            reverse("group", args=[self.group.slug]))
        self.assertContains(response, new_post)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user("Alex")
        cls.group = Group.objects.create(
            title="Заголовок группы",
            slug="test",
            description="Тестовый текст"
        )
        for i in range(2*POSTS_PER_PAGE):
            Post.objects.create(
                text=f"тестовый текст {i}",
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        self.guest_client = Client()

    def test_paginator_first_page(self):
        response = self.guest_client.get(reverse("index"))
        self.assertEqual(
            len(response.context.get("page").object_list),
            POSTS_PER_PAGE
        )

    def test_paginator_second_page(self):
        response = self.guest_client.get(reverse("index") + "?page=2")
        self.assertEqual(
            len(response.context.get("page").object_list),
            POSTS_PER_PAGE
        )
