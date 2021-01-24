import os
import shutil

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

import posts.tests.constants as const

from posts.models import Follow, Group, Post, User


class StaticURLTests(TestCase):
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
        cls.group = Group.objects.create(
            title=const.FIRST_GROUP_NAME,
            slug=const.FIRST_GROUP_SLUG,
            description=const.FIRST_GROUP_DESCRIPTION
        )
        cls.second_group = Group.objects.create(
            title=const.SECOND_GROUP_NAME,
            slug=const.SECOND_GROUP_SLUG,
            description=const.SECOND_GROUP_DESCRIPTION
        )
        cls.uploaded_img = SimpleUploadedFile(
            name=const.FIRST_IMG_NAME,
            content=const.FIRST_IMG,
            content_type="image/jpeg"
        )
        cls.post = Post.objects.create(
            text=const.POST_TEXT,
            author=cls.user,
            group=cls.group,
            image=cls.uploaded_img
        )
        cls.ADD_COMMENT_URL = reverse("add_comment",
                                      args=[cls.user.username, cls.post.id])
        cls.POST_EDIT_URL = reverse("post_edit",
                                    args=[cls.user.username, cls.post.id])
        cls.POST_URL = reverse("post", args=[cls.user.username, cls.post.id])

        cls.POST_EDIT_GUEST_TARGET_URL = (const.SIGNUP_URL +
                                          "?next=" + cls.POST_EDIT_URL)
        cls.POST_EDIT_FOLLOWER_TARGET_URL = cls.POST_URL
        cls.COMMENT_GUEST_TARGET_URL = (const.SIGNUP_URL +
                                        "?next=" + cls.ADD_COMMENT_URL)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_pages_redirect(self):
        guest = self.guest
        user, follower = self.authorized_user, self.authorized_follower
        CHECK_EXPECTED_CODE = {
            "new_guest": (const.NEW_POST_URL, guest,
                          const.NEW_GUEST_TARGET_URL),
            "follow_index_guest": (const.FOLLOW_INDEX_URL, guest,
                                   const.FOLLOW_INDEX_GUEST_TARGET_URL),
            "post_edit_follower": (self.POST_EDIT_URL, follower,
                                   self.POST_EDIT_FOLLOWER_TARGET_URL),
            "post_edit_guest": (self.POST_EDIT_URL, guest,
                                self.POST_EDIT_GUEST_TARGET_URL),
            "comment_guest": (self.ADD_COMMENT_URL, guest,
                              self.COMMENT_GUEST_TARGET_URL),
            "follow_guest": (const.PROFILE_FOLLOW_URL, guest,
                             const.PROFILE_FOLLOW_GUEST_TARGET_URL),
            "follow_user": (const.PROFILE_FOLLOW_URL, user,
                            const.PROFILE_FOLLOW_USER_TARGET_URL),
            "follow_follower": (const.PROFILE_FOLLOW_URL, follower,
                                const.PROFILE_FOLLOW_USER_TARGET_URL),
            "unfollow_guest": (const.PROFILE_UNFOLLOW_URL, guest,
                               const.PROFILE_UNFOLLOW_GUEST_TARGET_URL),
            "unfollow_user": (const.PROFILE_UNFOLLOW_URL, user,
                              const.PROFILE_UNFOLLOW_USER_TARGET_URL),
            "unfollow_follower": (const.PROFILE_UNFOLLOW_URL, follower,
                                  const.PROFILE_UNFOLLOW_FOLLOWER_TARGET_URL)
        }
        for name, (url, client, target_url) in CHECK_EXPECTED_CODE.items():
            with self.subTest(url=url, msg=name):
                self.assertRedirects(client.get(url, follow=True), target_url)

    def test_pages_template(self):
        user = self.authorized_user
        CHECK_TEMPLATE = {
            "index": (const.INDEX_URL, const.INDEX_TEMPLATE),
            "new": (const.NEW_POST_URL, const.NEW_POST_TEMPLATE),
            "follow": (const.FOLLOW_INDEX_URL, const.FOLLOW_INDEX_TEMPLATE),
            "group": (const.FIRST_GROUP_URL, const.GROUP_TEMPLATE),
            "profile": (const.PROFILE_URL, const.PROFILE_TEMPLATE),
            "post": (self.POST_URL, const.POST_TEMPLATE),
            "post_edit": (self.POST_EDIT_URL, const.POST_EDIT_TEMPLATE),
            "page_404": (const.NOT_URL, const.PAGE_NOT_FOUND_TEMPLATE),
            "about_author": (const.AUTHOR_URL, const.AUTHOR_TEMPLATE),
            "about_tech": (const.TECH_URL, const.TECH_TEMPLATE),
        }
        for name, (url, template) in CHECK_TEMPLATE.items():
            with self.subTest(url=url, msg=name):
                self.assertTemplateUsed(user.get(url), template)

    def test_pages_expected_code(self):
        guest = self.guest
        user, follower = self.authorized_user, self.authorized_follower
        CHECK_EXPECTED_CODE = {
            "index_guest": (const.INDEX_URL, guest, 200),
            "index_user": (const.INDEX_URL, user, 200),
            "new_guest": (const.NEW_POST_URL, guest, 302),
            "new_user": (const.NEW_POST_URL, user, 200),
            "follow_index_guest": (const.FOLLOW_INDEX_URL, guest, 302),
            "follow_index_user": (const.FOLLOW_INDEX_URL, user, 200),
            "follow_index_follower": (const.FOLLOW_INDEX_URL, follower, 200),
            "group_guest": (const.FIRST_GROUP_URL, guest, 200),
            "group_user": (const.FIRST_GROUP_URL, user, 200),
            "profile_guest": (const.PROFILE_URL, guest, 200),
            "profile_user": (const.PROFILE_URL, user, 200),
            "post_guest": (self.POST_URL, guest, 200),
            "post_user": (self.POST_URL, user, 200),
            "post_edit_guest": (self.POST_EDIT_URL, guest, 302),
            "post_edit_user": (self.POST_EDIT_URL, user, 200),
            "post_edit_follower": (self.POST_EDIT_URL, follower, 302),
            "comment_guest": (self.ADD_COMMENT_URL, guest, 302),
            "comment_user": (self.ADD_COMMENT_URL, user, 200),
            "follow_guest": (const.PROFILE_FOLLOW_URL, guest, 302),
            "follow_user": (const.PROFILE_FOLLOW_URL, user, 302),
            "follow_follower": (const.PROFILE_FOLLOW_URL, follower, 302),
            "unfollow_guest": (const.PROFILE_UNFOLLOW_URL, guest, 302),
            "unfollow_user": (const.PROFILE_UNFOLLOW_URL, user, 302),
            "unfollow_follower": (const.PROFILE_UNFOLLOW_URL, follower, 302),
            "page_404_guest": (const.NOT_URL, guest, 404),
            "page_404_user": (const.NOT_URL, user, 404),
            "about_author_guest": (const.AUTHOR_URL, guest, 200),
            "about_author_user": (const.AUTHOR_URL, user, 200),
            "about_tech_guest": (const.TECH_URL, guest, 200),
            "about_tech_user": (const.TECH_URL, user, 200)
        }
        for name, (url, client, expected_code) in CHECK_EXPECTED_CODE.items():
            with self.subTest(url=url, msg=name):
                self.assertEqual(client.get(url).status_code, expected_code)
