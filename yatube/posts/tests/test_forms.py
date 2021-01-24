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
        cls.UPLOADED_FIRST_IMG = SimpleUploadedFile(
            name=const.FIRST_IMG_NAME,
            content=const.FIRST_IMG,
            content_type="image/jpeg"
        )
        cls.UPLOADED_SECOND_IMG = SimpleUploadedFile(
            name=const.SECOND_IMG_NAME,
            content=const.FIRST_IMG,
            content_type="image/jpeg"
        )
        cls.post = Post.objects.create(
            text=const.POST_TEXT,
            author=cls.user,
            group=cls.first_group,
            image=cls.UPLOADED_FIRST_IMG
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
        cash_count = Post.objects.count()
        form_data = {
            "group": self.second_group.id,
            "text": const.POST_NEW_TEXT,
            "image": self.UPLOADED_FIRST_IMG
        }
        response = self.authorized_user.post(
            const.NEW_POST_URL,
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(author=self.user,
                                text=const.POST_NEW_TEXT,
                                group=self.second_group.id).exists()
        )
        self.assertTrue(const.FIRST_IMG_NAME in self.post.image.name)
        self.assertRedirects(response, const.INDEX_URL)
        self.assertEqual(Post.objects.count(), cash_count + 1)
        post = response.context["post"]
        self.assertEqual(post.text, const.POST_NEW_TEXT)
        self.assertEqual(post.group.id, self.second_group.id)
        self.assertEqual(post.author, self.user)

    def test_guest_new_post(self):
        cash_count = Post.objects.count()
        form_data = {
            "group": self.first_group.id,
            "text": const.POST_TEXT,
            "image": self.UPLOADED_FIRST_IMG
        }
        self.guest.post(const.NEW_POST_URL, data=form_data, follow=True)
        self.assertEqual(Post.objects.count(), cash_count)

    def test_user_new_comment(self):
        response = self.authorized_user.post(
            self.ADD_COMMENT_URL,
            {"text": const.COMMENT_TEXT},
            follow=True
        )
        self.assertTrue(
            Comment.objects.filter(author=self.user,
                                   text=const.COMMENT_TEXT,
                                   post=self.post).exists()
        )
        comments = response.context["comments"]
        self.assertEqual(comments[0].text, const.COMMENT_TEXT)

    def test_author_edit_post(self):
        form_data = {
            "text": const.POST_NEW_TEXT,
            "group": self.second_group.id,
            "image": self.UPLOADED_SECOND_IMG
        }
        response = self.authorized_user.post(self.POST_EDIT_URL,
                                             data=form_data, follow=True)
        post = response.context["post"]
        self.assertEqual(post.text, const.POST_NEW_TEXT)
        self.assertEqual(post.group, self.second_group)

    def test_anonym_edit_post(self):
        CHECK_ANONYM = {
            "authorized_no_author": self.authorized_follower,
            "guest": self.guest
        }
        form_data = {
            "text": const.POST_NEW_TEXT,
            "group": self.second_group.id,
            "image": self.UPLOADED_SECOND_IMG
        }
        cashed_post = Post.objects.get(id=self.post.id)
        for name, anonym in CHECK_ANONYM.items():
            with self.subTest(msg=name):
                response = anonym.post(self.POST_EDIT_URL,
                                       data=form_data, follow=True)
                post = response.context.get("post")
                if post:
                    self.assertEqual(post, cashed_post)
