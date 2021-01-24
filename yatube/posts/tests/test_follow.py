import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase

import posts.tests.constants as const
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
        cls.UPLOADED_FIRST_IMG = SimpleUploadedFile(
            name=const.FIRST_IMG_NAME,
            content=const.FIRST_IMG,
            content_type="image/jpeg"
        )
        cls.post = Post.objects.create(
            text=const.POST_TEXT,
            author=cls.user,
            group=cls.first_group,
            image=cls.UPLOADED_FIRST_IMG
        )

    def test_follow(self):
        Follow.objects.filter(
            author=self.user, user=self.follower).delete()
        self.authorized_follower.get(const.PROFILE_FOLLOW_URL)
        self.assertTrue(
            Follow.objects.filter(author=self.user,
                                  user=self.follower).exists())

    def test_unfollow(self):
        self.authorized_follower.get(const.PROFILE_UNFOLLOW_URL)
        self.assertFalse(
            Follow.objects.filter(author=self.user,
                                  user=self.follower).exists())
