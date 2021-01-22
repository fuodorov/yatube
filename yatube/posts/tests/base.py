import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, User

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


class BaseTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create(username=USERNAME)
        cls.follower = User.objects.create(username=FOLLOWER)
        cls.guest = Client()
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        cls.authorized_follower = Client()
        cls.authorized_follower.force_login(cls.follower)
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

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()
