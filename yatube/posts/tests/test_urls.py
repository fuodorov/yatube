import os
import shutil

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

import posts.tests.constants as consts
from posts.models import Follow, Group, Post, User


class StaticURLTests(TestCase):
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
        cls.group = Group.objects.create(
            title=consts.FIRST_GROUP_NAME,
            slug=consts.FIRST_GROUP_SLUG,
            description=consts.FIRST_GROUP_DESCRIPTION
        )
        cls.second_group = Group.objects.create(
            title=consts.SECOND_GROUP_NAME,
            slug=consts.SECOND_GROUP_SLUG,
            description=consts.SECOND_GROUP_DESCRIPTION
        )
        cls.UPLOADED_IMG = SimpleUploadedFile(
            name=consts.FIRST_IMG_NAME,
            content=consts.FIRST_IMG,
            content_type="image/jpeg"
        )
        cls.post = Post.objects.create(
            text=consts.POST_TEXT,
            author=cls.user,
            group=cls.group,
            image=cls.UPLOADED_IMG
        )
        cls.ADD_COMMENT_URL = reverse("add_comment",
                                      args=[cls.user.username, cls.post.id])
        cls.POST_EDIT_URL = reverse("post_edit",
                                    args=[cls.user.username, cls.post.id])
        cls.POST_URL = reverse("post", args=[cls.user.username, cls.post.id])

        cls.POST_EDIT_GUEST_TARGET_URL = (consts.SIGNUP_URL +
                                          "?next=" + cls.POST_EDIT_URL)
        cls.POST_EDIT_FOLLOWER_TARGET_URL = cls.POST_URL
        cls.COMMENT_GUEST_TARGET_URL = (consts.SIGNUP_URL +
                                        "?next=" + cls.ADD_COMMENT_URL)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_pages_redirect(self):
        guest = self.guest
        user, follower = self.authorized_user, self.authorized_follower
        CHECK_REDIRECT = {
            "new_guest": (consts.NEW_POST_URL, guest,
                          consts.NEW_GUEST_TARGET_URL),
            "follow_index_guest": (consts.FOLLOW_INDEX_URL, guest,
                                   consts.FOLLOW_INDEX_GUEST_TARGET_URL),
            "post_edit_follower": (self.POST_EDIT_URL, follower,
                                   self.POST_EDIT_FOLLOWER_TARGET_URL),
            "post_edit_guest": (self.POST_EDIT_URL, guest,
                                self.POST_EDIT_GUEST_TARGET_URL),
            "comment_guest": (self.ADD_COMMENT_URL, guest,
                              self.COMMENT_GUEST_TARGET_URL),
            "follow_guest": (consts.PROFILE_FOLLOW_URL, guest,
                             consts.PROFILE_FOLLOW_GUEST_TARGET_URL),
            "follow_user": (consts.PROFILE_FOLLOW_URL, user,
                            consts.PROFILE_FOLLOW_USER_TARGET_URL),
            "follow_follower": (consts.PROFILE_FOLLOW_URL, follower,
                                consts.PROFILE_FOLLOW_USER_TARGET_URL),
            "unfollow_guest": (consts.PROFILE_UNFOLLOW_URL, guest,
                               consts.PROFILE_UNFOLLOW_GUEST_TARGET_URL),
            "unfollow_follower": (consts.PROFILE_UNFOLLOW_URL, follower,
                                  consts.PROFILE_UNFOLLOW_FOLLOWER_TARGET_URL)
        }
        for name, (url, client, target_url) in CHECK_REDIRECT.items():
            with self.subTest(url=url, msg=name):
                self.assertRedirects(client.get(url, follow=True), target_url)

    def test_pages_template(self):
        user = self.authorized_user
        CHECK_TEMPLATE = {
            "index": (consts.INDEX_URL, consts.INDEX_TEMPLATE),
            "new": (consts.NEW_POST_URL, consts.NEW_POST_TEMPLATE),
            "follow": (consts.FOLLOW_INDEX_URL, consts.FOLLOW_INDEX_TEMPLATE),
            "group": (consts.FIRST_GROUP_URL, consts.GROUP_TEMPLATE),
            "profile": (consts.PROFILE_URL, consts.PROFILE_TEMPLATE),
            "post": (self.POST_URL, consts.POST_TEMPLATE),
            "post_edit": (self.POST_EDIT_URL, consts.POST_EDIT_TEMPLATE),
            "page_404": (consts.NOT_URL, consts.PAGE_NOT_FOUND_TEMPLATE),
            "about_author": (consts.AUTHOR_URL, consts.AUTHOR_TEMPLATE),
            "about_tech": (consts.TECH_URL, consts.TECH_TEMPLATE),
        }
        for name, (url, template) in CHECK_TEMPLATE.items():
            with self.subTest(url=url, msg=name):
                self.assertTemplateUsed(user.get(url), template)

    def test_pages_expected_code(self):
        guest = self.guest
        user, follower = self.authorized_user, self.authorized_follower
        CHECK_EXPECTED_CODE = {
            "index_guest": (consts.INDEX_URL, guest, 200),
            "new_guest": (consts.NEW_POST_URL, guest, 302),
            "new_user": (consts.NEW_POST_URL, user, 200),
            "follow_index_guest": (consts.FOLLOW_INDEX_URL, guest, 302),
            "follow_index_user": (consts.FOLLOW_INDEX_URL, user, 200),
            "group_guest": (consts.FIRST_GROUP_URL, guest, 200),
            "profile_guest": (consts.PROFILE_URL, guest, 200),
            "post_guest": (self.POST_URL, guest, 200),
            "post_edit_guest": (self.POST_EDIT_URL, guest, 302),
            "post_edit_user": (self.POST_EDIT_URL, user, 200),
            "post_edit_follower": (self.POST_EDIT_URL, follower, 302),
            "comment_guest": (self.ADD_COMMENT_URL, guest, 302),
            "comment_user": (self.ADD_COMMENT_URL, user, 200),
            "follow_guest": (consts.PROFILE_FOLLOW_URL, guest, 302),
            "follow_user": (consts.PROFILE_FOLLOW_URL, user, 302),
            "follow_follower": (consts.PROFILE_FOLLOW_URL, follower, 302),
            "unfollow_guest": (consts.PROFILE_UNFOLLOW_URL, guest, 302),
            "unfollow_user": (consts.PROFILE_UNFOLLOW_URL, user, 404),
            "unfollow_follower": (consts.PROFILE_UNFOLLOW_URL, follower, 302),
            "page_404_guest": (consts.NOT_URL, guest, 404),
            "about_author_guest": (consts.AUTHOR_URL, guest, 200),
            "about_tech_guest": (consts.TECH_URL, guest, 200)
        }
        for name, (url, client, expected_code) in CHECK_EXPECTED_CODE.items():
            with self.subTest(url=url, msg=name):
                self.assertEqual(client.get(url).status_code, expected_code)
