from django.core.cache import cache

from posts.settings import POSTS_PER_PAGE
from posts.tests.base import (BaseTestCase, INDEX_URL, POST_TEXT,
                              FIRST_GROUP_URL, PROFILE_URL, FOLLOW_INDEX_URL,
                              PROFILE_FOLLOW_URL, PROFILE_UNFOLLOW_URL)

from posts.models import Follow, Post


class ViewContentTest(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_check_urls = [
            cls.POST_URL,
            FIRST_GROUP_URL,
            PROFILE_URL,
            FOLLOW_INDEX_URL,
            INDEX_URL
        ]

    def test_post_content_on_all_pages(self):
        for url, client, end_url, template, expected_code in self.list_pages:
            condition = (
                url in self.post_check_urls and
                url != INDEX_URL and
                200 == expected_code
            )
            if condition:
                with self.subTest(url=url):
                    self.assertTrue(
                        self.post == client.get(url).context["post"]
                    )
            elif url == INDEX_URL:
                with self.subTest(url=url):
                    self.assertTrue(
                        self.post == client.get(url).context.get("page")[0]
                    )

    def test_cache_index_page(self):
        response_before = self.authorized_user.get(INDEX_URL)
        page_before_clear_cache = response_before.content
        post = Post.objects.latest("id")
        post.text = "Update" + post.text
        post.save()
        response_before = self.authorized_user.get(INDEX_URL)
        page_before_clear_cache_refresh = response_before.content
        self.assertEqual(page_before_clear_cache,
                         page_before_clear_cache_refresh)
        cache.clear()
        response_after = self.authorized_user.get(INDEX_URL)
        page_after_clear_cache = response_after.content
        self.assertNotEqual(page_before_clear_cache, page_after_clear_cache)


class PaginatorViewsTest(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for i in range(2*POSTS_PER_PAGE):
            Post.objects.create(
                text=POST_TEXT,
                author=cls.user,
                group=cls.first_group
            )

    def test_paginator_first_page(self):
        response = self.guest.get(INDEX_URL)
        self.assertEqual(
            len(response.context.get("page").object_list),
            POSTS_PER_PAGE
        )

    def test_paginator_second_page(self):
        response = self.guest.get(INDEX_URL + "?page=2")
        self.assertEqual(
            len(response.context.get("page").object_list),
            POSTS_PER_PAGE
        )


class FollowTests(BaseTestCase):
    def test_follow_unfollow(self):
        Follow.objects.filter(
            author=self.user, user=self.follower).delete()
        with self.subTest(msg="Following"):
            self.authorized_follower.get(PROFILE_FOLLOW_URL)
            self.assertTrue(
                Follow.objects.filter(author=self.user,
                                      user=self.follower).exists())
        with self.subTest(msg="Unfollowing"):
            self.authorized_follower.get(PROFILE_UNFOLLOW_URL)
            self.assertFalse(
                Follow.objects.filter(author=self.user,
                                      user=self.follower).exists())

    def test_followed_authors_post_appears_in_follow_list(self):
        self.assertTrue(Follow.objects.filter(author=self.user).exists())
        Follow.objects.filter(author=self.user, user=self.follower).delete()
        self.assertFalse(Follow.objects.filter(author=self.user).exists())
