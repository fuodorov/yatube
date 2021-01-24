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
        guest = self.guest
        user, follower = self.authorized_user, self.authorized_follower
        CHECK_CONTENT = {
            "index_guest": (const.INDEX_URL, guest),
            "index_user": (const.INDEX_URL, user),
            "post_guest": (self.POST_URL, guest),
            "post_user": (self.POST_URL, user),
            "follow_index_follower": (const.FOLLOW_INDEX_URL, follower),
            "group_guest": (const.FIRST_GROUP_URL, guest),
            "group_user": (const.FIRST_GROUP_URL, user),
            "profile_guest": (const.PROFILE_URL, guest),
            "profile_user": (const.PROFILE_URL, user),
        }
        for name, (url, client) in CHECK_CONTENT.items():
            with self.subTest(url=url, msg=name):
                context = client.get(url).context
                if context.get("post"):
                    post = context.get("post")
                else:
                    post = context["page"][0]
                self.assertTrue(self.post == post)

    def test_cache_index_page(self):
        response_before = self.authorized_user.get(const.INDEX_URL)
        page_before_clear_cache = response_before.content
        post = Post.objects.get(id=self.post.id)
        post.text = const.POST_NEW_TEXT
        post.save()
        response_before = self.authorized_user.get(const.INDEX_URL)
        page_before_clear_cache_refresh = response_before.content
        self.assertEqual(page_before_clear_cache,
                         page_before_clear_cache_refresh)
        cache.clear()
        response_after = self.authorized_user.get(const.INDEX_URL)
        page_after_clear_cache = response_after.content
        self.assertNotEqual(page_before_clear_cache, page_after_clear_cache)
