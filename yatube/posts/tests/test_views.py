import os
import shutil

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

import posts.tests.constants as consts
from posts.forms import PostForm
from posts.models import Follow, Group, Post, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = os.path.join(settings.MEDIA_ROOT, "media")
        cls.user = User.objects.create(username=consts.USERNAME)
        cls.follower = User.objects.create(username=consts.FOLLOWER)
        cls.guest = Client()
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        cls.authorized_follower = Client()
        cls.authorized_follower.force_login(cls.follower)
        Follow.objects.create(author=cls.user, user=cls.follower)
        cls.first_group = Group.objects.create(
            title=consts.FIRST_GROUP_NAME,
            slug=consts.FIRST_GROUP_SLUG,
            description=consts.FIRST_GROUP_DESCRIPTION
        )
        cls.second_group = Group.objects.create(
            title=consts.SECOND_GROUP_NAME,
            slug=consts.SECOND_GROUP_SLUG,
            description=consts.SECOND_GROUP_DESCRIPTION
        )
        cls.form = PostForm()
        cls.UPLOADED_FIRST_IMG = SimpleUploadedFile(
            name=consts.FIRST_IMG_NAME,
            content=consts.FIRST_IMG,
            content_type="image/jpeg"
        )
        cls.post = Post.objects.create(
            text=consts.POST_TEXT,
            author=cls.user,
            group=cls.first_group,
            image=cls.UPLOADED_FIRST_IMG
        )
        cls.POST_EDIT_URL = reverse("post_edit",
                                    args=[cls.user.username, cls.post.id])
        cls.POST_URL = reverse("post", args=[cls.user.username, cls.post.id])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_post_content_on_all_pages(self):
        guest, follower = self.guest, self.authorized_follower
        CHECK_CONTENT = {
            "index_guest": (consts.INDEX_URL, guest),
            "post_guest": (self.POST_URL, guest),
            "follow_index_follower": (consts.FOLLOW_INDEX_URL, follower),
            "group_guest": (consts.FIRST_GROUP_URL, guest),
            "profile_guest": (consts.PROFILE_URL, guest),
        }
        for name, (url, client) in CHECK_CONTENT.items():
            with self.subTest(url=url, msg=name):
                context = client.get(url).context
                if "post" in context:
                    post = context["post"]
                else:
                    self.assertEqual(len(context["page"]), 1)
                    post = context["page"][0]
                self.assertTrue(self.post == post)

    def test_post_on_another_group(self):
        context = self.authorized_user.get(consts.SECOND_GROUP_URL).context
        self.assertNotIn(self.post, context["page"])

    def test_cache_index_page(self):
        response_before = self.authorized_user.get(consts.INDEX_URL)
        self.post.text = consts.POST_NEW_TEXT
        self.post.save()
        response_before = self.authorized_user.get(consts.INDEX_URL)
        self.assertEqual(response_before.content, response_before.content)
        cache.clear()
        response_after = self.authorized_user.get(consts.INDEX_URL)
        self.assertNotEqual(response_before.content, response_after.content)
