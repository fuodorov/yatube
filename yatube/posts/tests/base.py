import os
import shutil
from collections import namedtuple

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse, reverse_lazy

from posts.forms import PostForm
from posts.models import Follow, Group, Post, User

FIRST_GROUP_NAME = "test-group-1"
FIRST_GROUP_SLUG = "test-slug-1"
FIRST_GROUP_DESCRIPTION = "test-description-1"
SECOND_GROUP_NAME = "test-group-2"
SECOND_GROUP_SLUG = "test-slug-2"
SECOND_GROUP_DESCRIPTION = "test-description-2"
USERNAME = "test-user"
FOLLOWER = "test-follower"
POST_TEXT = "test-post"
COMMENT_TEXT = "test-comment"
FIRST_IMG_NAME = "img-1"
SECOND_IMG_NAME = "img-2"

INDEX_URL = reverse("index")
SIGNUP_URL = reverse_lazy("login")
NEW_POST_URL = reverse("new_post")
FOLLOW_INDEX_URL = reverse("follow_index")
AUTHOR_URL = reverse("about:author")
TECH_URL = reverse("about:tech")
PAGE_NOT_FOUND_URL = reverse("404")
SERVER_ERROR_URL = reverse("500")

FIRST_GROUP_URL = reverse("group", args=[FIRST_GROUP_SLUG])
SECOND_GROUP_URL = reverse("group", args=[SECOND_GROUP_SLUG])
PROFILE_URL = reverse("profile", args=[USERNAME])
FOLLOWER_URL = reverse("profile", args=[FOLLOWER])
PROFILE_FOLLOW_URL = reverse("profile_follow", args=[USERNAME])
PROFILE_UNFOLLOW_URL = reverse("profile_unfollow", args=[USERNAME])

NOT_URL = "not" + PAGE_NOT_FOUND_URL

FIRST_IMG = (b"\x47\x49\x46\x38\x39\x61\x02\x00"
             b"\x01\x00\x80\x00\x00\x00\x00\x00"
             b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
             b"\x00\x00\x00\x2C\x00\x00\x00\x00"
             b"\x02\x00\x01\x00\x00\x02\x02\x0C"
             b"\x0A\x00\x3B")
SECOND_IMG = (b"\x48\x49\x46\x38\x39\x61\x02\x00"
              b"\x01\x00\x80\x00\x00\x00\x00\x00"
              b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
              b"\x00\x00\x00\x2C\x00\x00\x00\x00"
              b"\x02\x00\x01\x00\x00\x02\x02\x0C"
              b"\x0A\x00\x3B")

Page = namedtuple("Page", {
    "url",
    "client",
    "end_url",
    "template",
    "expected_code"
})


class BaseTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        settings.MEDIA_ROOT = os.path.join(settings.MEDIA_ROOT, "media")
        cls.user = User.objects.create(username=USERNAME)
        cls.follower = User.objects.create(username=FOLLOWER)
        cls.guest = Client()
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        cls.authorized_follower = Client()
        cls.authorized_follower.force_login(cls.follower)
        Follow.objects.get_or_create(author=cls.user, user=cls.follower)
        cls.first_group = Group.objects.create(
            title=FIRST_GROUP_NAME,
            slug=FIRST_GROUP_SLUG,
            description=FIRST_GROUP_DESCRIPTION
        )
        cls.second_group = Group.objects.create(
            title=SECOND_GROUP_NAME,
            slug=SECOND_GROUP_SLUG,
            description=SECOND_GROUP_DESCRIPTION
        )
        cls.form = PostForm()
        cls.uploaded_first_img = SimpleUploadedFile(
            name=FIRST_IMG_NAME,
            content=FIRST_IMG,
            content_type="image/jpeg"
        )
        cls.uploaded_second_img = SimpleUploadedFile(
            name=SECOND_IMG_NAME,
            content=SECOND_IMG,
            content_type="image/jpeg"
        )
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
            group=cls.first_group,
            image=cls.uploaded_first_img
        )
        cls.ADD_COMMENT_URL = reverse("add_comment",
                                      args=[cls.user.username, cls.post.id])
        cls.POST_EDIT_URL = reverse("post_edit",
                                    args=[cls.user.username, cls.post.id])
        cls.POST_URL = reverse("post", args=[cls.user.username, cls.post.id])

        cls.list_pages = [
            Page(INDEX_URL, cls.authorized_user, INDEX_URL,
                 "index.html", 200),
            Page(INDEX_URL, cls.guest, INDEX_URL, "index.html", 200),
            Page(PROFILE_URL, cls.authorized_user, PROFILE_URL,
                 "posts/profile.html", 200),
            Page(PROFILE_URL, cls.guest, PROFILE_URL,
                 "posts/profile.html", 200),
            Page(FIRST_GROUP_URL, cls.authorized_user, FIRST_GROUP_URL,
                 "posts/group.html", 200),
            Page(FIRST_GROUP_URL, cls.guest, FIRST_GROUP_URL,
                 "posts/group.html", 200),
            Page(FOLLOW_INDEX_URL, cls.authorized_follower,
                 FOLLOW_INDEX_URL, "posts/follow.html", 200),
            Page(FOLLOW_INDEX_URL, cls.guest,
                 SIGNUP_URL, "registration/login.html", 302),
            Page(AUTHOR_URL, cls.authorized_user, AUTHOR_URL,
                 "about/author.html", 200),
            Page(AUTHOR_URL, cls.guest, AUTHOR_URL,
                 "about/author.html", 200),
            Page(TECH_URL, cls.authorized_user, TECH_URL,
                 "about/tech.html", 200),
            Page(TECH_URL, cls.guest, TECH_URL,
                 "about/tech.html", 200),
            Page(cls.POST_URL, cls.authorized_user, cls.POST_URL,
                 "posts/post.html", 200),
            Page(cls.POST_URL, cls.guest, cls.POST_URL,
                 "posts/post.html", 200),
            Page(cls.POST_EDIT_URL, cls.authorized_user, cls.POST_URL,
                 "posts/new_post.html", 200),
            Page(cls.POST_EDIT_URL, cls.guest, SIGNUP_URL,
                 "registration/login.html", 302),
            Page(NEW_POST_URL, cls.authorized_user, NEW_POST_URL,
                 "posts/new_post.html", 200),
            Page(NEW_POST_URL, cls.guest, SIGNUP_URL,
                 "registration/login.html", 302),
            Page(NOT_URL, cls.guest, PAGE_NOT_FOUND_URL,
                 "misc/404.html", 404)
        ]

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        cache.clear()
