import os
import shutil

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

import posts.tests.constants as const
from posts.forms import PostForm
from posts.models import Follow, Group, Post, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = os.path.join(settings.MEDIA_ROOT, "media")
        cls.user = User.objects.create(username=const.USERNAME)
        cls.follower = User.objects.create(username=const.FOLLOWER)
        cls.guest = Client()
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        cls.authorized_follower = Client()
        cls.authorized_follower.force_login(cls.follower)
        Follow.objects.create(author=cls.user, user=cls.follower)
        cls.first_group = Group.objects.create(
            title=const.FIRST_GROUP_NAME,
            slug=const.FIRST_GROUP_SLUG,
            description=const.FIRST_GROUP_DESCRIPTION
        )
        cls.second_group = Group.objects.create(
            title=const.SECOND_GROUP_NAME,
            slug=const.SECOND_GROUP_SLUG,
            description=const.SECOND_GROUP_DESCRIPTION
        )
        cls.form = PostForm()
        cls.UPLOADED_FIRST_IMG = SimpleUploadedFile(
            name=const.FIRST_IMG_NAME,
            content=const.FIRST_IMG,
            content_type="image/jpeg"
        )
        cls.UPLOADED_SECOND_IMG = SimpleUploadedFile(
            name=const.SECOND_IMG_NAME,
            content=const.FIRST_IMG,
            content_type="image/jpeg"
        )
        cls.post = Post.objects.create(
            text=const.POST_TEXT,
            author=cls.user,
            group=cls.first_group,
            image=cls.UPLOADED_FIRST_IMG
        )
        cls.ADD_COMMENT_URL = reverse("add_comment",
                                      args=[cls.user.username, cls.post.id])
        cls.POST_EDIT_URL = reverse("post_edit",
                                    args=[cls.user.username, cls.post.id])
        cls.POST_URL = reverse("post", args=[cls.user.username, cls.post.id])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_post_content_on_all_pages(self):
        for url, client, end_url, template, expected_code in self.list_pages:
            condition = (
                url in self.post_check_urls and
                url != const.INDEX_URL and
                200 == expected_code
            )
            if condition:
                with self.subTest(url=url):
                    self.assertTrue(
                        self.post == client.get(url).context["post"]
                    )
            elif url == const.INDEX_URL:
                with self.subTest(url=url):
                    self.assertTrue(
                        self.post == client.get(url).context["page"][0]
                    )

    def test_cache_index_page(self):
        response_before = self.authorized_user.get(const.INDEX_URL)
        page_before_clear_cache = response_before.content
        post = Post.objects.latest("id")
        post.text = "Update" + post.text
        post.save()
        response_before = self.authorized_user.get(const.INDEX_URL)
        page_before_clear_cache_refresh = response_before.content
        self.assertEqual(page_before_clear_cache,
                         page_before_clear_cache_refresh)
        cache.clear()
        response_after = self.authorized_user.get(const.INDEX_URL)
        page_after_clear_cache = response_after.content
        self.assertNotEqual(page_before_clear_cache, page_after_clear_cache)


class PaginatorViewsTest(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for post_item in range(2 * POSTS_PER_PAGE):
            Post.objects.create(
                text=POST_TEXT,
                author=cls.user,
                group=cls.first_group
            )

    def test_paginator_first_page(self):
        response = self.guest.get(INDEX_URL)
        self.assertEqual(
            len(response.context["page"]),
            POSTS_PER_PAGE
        )

    def test_paginator_second_page(self):
        response = self.guest.get(INDEX_URL + "?page=2")
        self.assertEqual(
            len(response.context["page"]),
            POSTS_PER_PAGE
        )


class FollowTests(BaseTestCase):
    def test_follow(self):
        Follow.objects.filter(
            author=self.user, user=self.follower).delete()
        self.authorized_follower.get(PROFILE_FOLLOW_URL)
        self.assertTrue(
            Follow.objects.filter(author=self.user,
                                  user=self.follower).exists())

    def test_unfollow(self):
        self.authorized_follower.get(PROFILE_UNFOLLOW_URL)
        self.assertFalse(
            Follow.objects.filter(author=self.user,
                                  user=self.follower).exists())
