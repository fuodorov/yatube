import os

from django.conf import settings
from django.test import Client, TestCase

import posts.tests.constants as consts
from posts.models import Follow, Post, User


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
        cls.post = Post.objects.create(text=consts.POST_TEXT, author=cls.user)

    def test_follow(self):
        self.authorized_follower.get(consts.PROFILE_FOLLOW_URL)
        self.assertTrue(
            Follow.objects.filter(author=self.user,
                                  user=self.follower).exists())

    def test_unfollow(self):
        self.authorized_follower.get(consts.PROFILE_FOLLOW_URL)
        self.authorized_follower.get(consts.PROFILE_UNFOLLOW_URL)
        self.assertFalse(
            Follow.objects.filter(author=self.user,
                                  user=self.follower).exists())

    def test_post_is_not_on_follow_index(self):
        context = self.authorized_user.get(consts.FOLLOW_INDEX_URL).context
        self.assertNotIn(self.post, context["page"])
