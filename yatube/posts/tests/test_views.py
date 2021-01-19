import shutil

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse
from django.test import Client, TestCase

from posts.constants import POSTS_PER_PAGE

from ..models import Comment, Follow, Group, Post, User


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
        cls.small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        cls.uploaded = SimpleUploadedFile(
            name="small.gif",
            content=cls.small_gif,
            content_type="image/gif"
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый текст",
            group=cls.group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)
        cache.clear()

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

    def test_cache_index_page(self):
        response_before = self.authorized_user.get(reverse("index"))
        page_before_clear_cache = response_before.content
        post = Post.objects.latest("id")
        post.text = "Update" + post.text
        post.save()
        response_before = self.authorized_user.get(reverse("index"))
        page_before_clear_cache_refresh = response_before.content
        self.assertEqual(page_before_clear_cache,
                         page_before_clear_cache_refresh)
        cache.clear()
        response_after = self.authorized_user.get(reverse("index"))
        page_after_clear_cache = response_after.content
        self.assertNotEqual(page_before_clear_cache, page_after_clear_cache)


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


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.unfollow_user = User.objects.create(
            username="unfollow_username",
            email="unfollow_username@testmail.com",
        )
        cls.user = User.objects.create(
            username="test_username",
            email="test_username@testmail.com",
        )
        cls.author = User.objects.create(
            username="test_author",
            email="test_author@testmail.com",
        )
        cls.group = Group.objects.create(
            title="Тестовое сообщество",
            slug="test-slug",
            description="test description"
        )
        cls.post = Post.objects.create(
            text="Заголовок тестовой записи",
            author=cls.author,
            group=cls.group,
        )
        cls.post_id = cls.post.id

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(FollowTests.user)
        self.authorized_unfollow_client = Client()
        self.authorized_unfollow_client.force_login(FollowTests.unfollow_user)
        self.guest_client = Client()
        cache.clear()

    def test_client_follow_users(self):
        followers_before = Follow.objects.filter(
            author=FollowTests.author).count()
        self.authorized_client.post(
            reverse("profile_follow", kwargs={"username": FollowTests.author}))
        followers_after = Follow.objects.filter(
            author=FollowTests.author).count()

        self.assertEqual(followers_before + 1, followers_after)

    def test_client_unfollow_users(self):
        followers_before = Follow.objects.filter(
            author=FollowTests.author).count()
        self.authorized_client.post(
            reverse("profile_follow", kwargs={"username": FollowTests.author}))
        self.authorized_client.post(
            reverse("profile_unfollow",
                    kwargs={"username": FollowTests.author}))
        followers_after_delete = Follow.objects.filter(
            author=FollowTests.author).count()
        self.assertEqual(followers_before, followers_after_delete)

    def test_new_post_followers(self):
        Follow.objects.create(
            user=FollowTests.user,
            author=FollowTests.author
        )
        response_follower = self.authorized_client.get(
            reverse("follow_index"))
        page_before_new_post = len(response_follower.context.get("page"))
        Post.objects.create(
            text="Новый пост от автора",
            author=FollowTests.author
        )
        cache.clear()
        response_follower = self.authorized_client.get(
            reverse("follow_index"))
        page_after_new_post = len(response_follower.context.get("page"))
        self.assertEqual(page_before_new_post + 1, page_after_new_post)

    def test_new_post_unfollowers(self):
        Follow.objects.create(
            user=FollowTests.user,
            author=FollowTests.author
        )
        response_unfollow = self.authorized_unfollow_client.get(
            reverse("follow_index"))
        page_unfollow_user_before = response_unfollow.content
        Post.objects.create(
            text="Новый пост от автора",
            author=FollowTests.author
        )
        cache.clear()
        response_unfollow = self.authorized_unfollow_client.get(
            reverse("follow_index"))
        page_unfollow_user_after = response_unfollow.content
        self.assertEqual(page_unfollow_user_before, page_unfollow_user_after)

    def test_client_comment_on_posts(self):
        form_data = {
            "text": "test_text",
            "author": FollowTests.user,
            "post": FollowTests.post,
        }
        comments_count_before = Comment.objects.count()
        self.authorized_client.post(
            reverse("add_comment", kwargs={
                "username": FollowTests.post.author.username,
                "post_id": FollowTests.post_id
            }), data=form_data, follow=True, )
        self.guest_client.post(
            reverse("add_comment", kwargs={
                "username": FollowTests.post.author.username,
                "post_id": FollowTests.post_id
            }), data=form_data, follow=True, )
        comments_count_after = Comment.objects.count()
        self.assertEqual(comments_count_before + 1, comments_count_after)
