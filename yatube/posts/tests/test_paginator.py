from django.test import Client, TestCase

import posts.tests.constants as const
from posts.models import Group, Post, User
from posts.settings import POSTS_PER_PAGE


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=const.USERNAME)
        cls.guest = Client()
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        cls.first_group = Group.objects.create(
            title=const.FIRST_GROUP_NAME,
            slug=const.FIRST_GROUP_SLUG,
            description=const.FIRST_GROUP_DESCRIPTION
        )
        for post_item in range(2 * POSTS_PER_PAGE):
            Post.objects.create(
                text=const.POST_TEXT,
                author=cls.user,
                group=cls.first_group
            )

    def test_paginator_first_page(self):
        response = self.guest.get(const.INDEX_URL)
        self.assertEqual(len(response.context["page"]), POSTS_PER_PAGE)

    def test_paginator_second_page(self):
        response = self.guest.get(const.INDEX_URL + "?page=2")
        self.assertEqual(len(response.context["page"]), POSTS_PER_PAGE)
