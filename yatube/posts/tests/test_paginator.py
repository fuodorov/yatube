from django.test import Client, TestCase

import posts.tests.constants as consts
from posts.models import Post, User
from posts.settings import POSTS_PER_PAGE


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=consts.USERNAME)
        cls.guest = Client()
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        for post_item in range(2 * POSTS_PER_PAGE):
            Post.objects.create(text=consts.POST_TEXT, author=cls.user)

    def test_paginator_first_page(self):
        response = self.guest.get(consts.INDEX_URL)
        self.assertEqual(len(response.context["page"]), POSTS_PER_PAGE)

    def test_paginator_second_page(self):
        response = self.guest.get(consts.INDEX_URL + "?page=2")
        self.assertEqual(len(response.context["page"]), POSTS_PER_PAGE)
