import os
import shutil

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

import posts.tests.constants as const

from posts.forms import PostForm
from posts.models import Comment, Follow, Group, Post, User


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
        cls.uploaded_first_img = SimpleUploadedFile(
            name=const.FIRST_IMG_NAME,
            content=const.FIRST_IMG,
            content_type="image/jpeg"
        )
        cls.uploaded_second_img = SimpleUploadedFile(
            name=const.SECOND_IMG_NAME,
            content=const.FIRST_IMG,
            content_type="image/jpeg"
        )
        cls.post = Post.objects.create(
            text=const.POST_TEXT,
            author=cls.user,
            group=cls.first_group,
            image=cls.uploaded_first_img
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

    def test_authorized_user_new_post(self):
        form_data = {
            "group": self.first_group.id,
            "text": const.POST_TEXT,
            "image": self.uploaded_first_img
        }
        self.authorized_user.post(
            const.NEW_POST_URL,
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(text=const.POST_TEXT).exists() and
            Post.objects.filter(group=self.first_group.id).exists() and
            const.FIRST_IMG_NAME in self.post.image.name
        )

    def test_guest_new_post(self):
        cash_count = Post.objects.count()
        form_data = {
            "group": self.first_group.id,
            "text": const.POST_TEXT,
            "image": self.uploaded_first_img
        }
        response = self.guest.post(
            const.NEW_POST_URL,
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), cash_count)
        self.assertEqual(response.status_code, 200)

    def test_user_new_comment(self):
        self.authorized_user.post(
            self.ADD_COMMENT_URL,
            {"text": const.COMMENT_TEXT},
            follow=True
        )
        self.assertTrue(
            Comment.objects.filter(text=const.COMMENT_TEXT).exists()
        )

    def test_author_edit_post(self):
        cashed_post = self.post
        form_data = {
            "text": const.POST_NEW_TEXT,
            "group": self.second_group.id
        }
        self.authorized_user.post(self.POST_EDIT_URL, data=form_data, follow=True)
        self.post.refresh_from_db()
        self.assertNotEqual(self.post, cashed_post)

    def test_anonym_edit_post(self):
        cashed_post = self.post
        CHECK_ANONYM = (self.authorized_follower, self.guest)
        form_data = {
            "text": const.POST_NEW_TEXT,
            "group": self.second_group.id,
            "image": self.uploaded_second_img
        }
        for anonym in CHECK_ANONYM:
            with self.subTest(msg=anonym):
                anonym.post(self.POST_EDIT_URL, data=form_data, follow=True)
                self.assertEqual(self.post, cashed_post)
