from collections import namedtuple

from posts.tests.base import (AUTHOR_URL, FIRST_GROUP_URL, INDEX_URL,
                              NEW_POST_URL, PROFILE_URL, SIGNUP_URL, TECH_URL,
                              BaseTestCase, NOT_URL, PAGE_NOT_FOUND_URL)


class StaticURLTests(BaseTestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        set = {"url", "client", "end_url", "template", "expected_code"}
        Page = namedtuple("Page", set)
        self.list_pages = [
            Page(INDEX_URL, self.authorized_user, INDEX_URL,
                 "index.html", 200),
            Page(INDEX_URL, self.guest, INDEX_URL, "index.html", 200),
            Page(PROFILE_URL, self.authorized_user, PROFILE_URL,
                 "posts/profile.html", 200),
            Page(PROFILE_URL, self.guest, PROFILE_URL,
                 "posts/profile.html", 200),
            Page(FIRST_GROUP_URL, self.authorized_user, FIRST_GROUP_URL,
                 "posts/group.html", 200),
            Page(FIRST_GROUP_URL, self.guest, FIRST_GROUP_URL,
                 "posts/group.html", 200),
            Page(AUTHOR_URL, self.authorized_user, AUTHOR_URL,
                 "about/author.html", 200),
            Page(AUTHOR_URL, self.guest, AUTHOR_URL,
                 "about/author.html", 200),
            Page(TECH_URL, self.authorized_user, TECH_URL,
                 "about/tech.html", 200),
            Page(TECH_URL, self.guest, TECH_URL,
                 "about/tech.html", 200),
            Page(self.POST_URL, self.authorized_user, self.POST_URL,
                 "posts/post.html", 200),
            Page(self.POST_URL, self.guest, self.POST_URL,
                 "posts/post.html", 200),
            Page(self.POST_EDIT_URL, self.authorized_user, self.POST_URL,
                 "posts/new_post.html", 200),
            Page(self.POST_EDIT_URL, self.guest, SIGNUP_URL,
                 "registration/login.html", 302),
            Page(NEW_POST_URL, self.authorized_user, NEW_POST_URL,
                 "posts/new_post.html", 200),
            Page(NEW_POST_URL, self.guest, SIGNUP_URL,
                 "registration/login.html", 302),
            Page(NOT_URL, self.guest, PAGE_NOT_FOUND_URL,
                 "misc/404.html", 404),
        ]

    def test_pages_redirect(self):
        for url, client, end_url, template, expected_code in self.list_pages:
            with self.subTest(url=url):
                if 302 == expected_code:
                    target_url = end_url + '?next=' + url
                    self.assertRedirects(
                        client.get(url, follow=True),
                        target_url,
                        status_code=302
                    )

    def test_pages_template(self):
        for url, client, end_url, template, expected_code in self.list_pages:
            with self.subTest(url=url):
                self.assertTemplateUsed(client.get(url, follow=True), template)

    def test_pages_expected_code(self):
        for url, client, end_url, template, expected_code in self.list_pages:
            with self.subTest(url=url):
                self.assertEqual(client.get(url).status_code, expected_code)
