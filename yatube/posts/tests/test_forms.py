from django.urls import reverse

from posts.models import Comment, Post, Follow
from posts.tests.base import (COMMENT_TEXT, FIRST_IMG_NAME, NEW_POST_URL,
                              POST_TEXT, BaseTestCase)


class PostFormTests(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
            group=cls.first_group,
            image=cls.uploaded_first_img
        )

    def test_authorized_user_new_post(self):
        form_data = {
            "group": self.first_group.id,
            "text": POST_TEXT,
            "image": self.uploaded_first_img
        }
        self.authorized_user.post(
            NEW_POST_URL,
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(text=POST_TEXT).exists() and
            Post.objects.filter(group=self.first_group.id).exists() and
            FIRST_IMG_NAME in self.post.image.name
        )

    def test_guest_new_post(self):
        cash_count = Post.objects.count()
        form_data = {
            "group": self.first_group.id,
            "text": POST_TEXT,
            "image": self.uploaded_first_img
        }
        response = self.guest.post(
            NEW_POST_URL,
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), cash_count)
        self.assertEqual(response.status_code, 200)

    def test_authorized_user_new_comment(self):
        self.authorized_user.post(
            reverse("add_comment", args=[self.user.username, self.post.id]),
            {"text": COMMENT_TEXT},
            follow=True
        )
        self.assertTrue(Comment.objects.filter(text=COMMENT_TEXT).exists())

    def test_edit_post(self):
        self.authorized_user.post(
            reverse("post_edit", args=[self.user.username, self.post.id]),
            {"text": "not" + POST_TEXT, "group": self.second_group.id},
            follow=True
        )
        self.post.refresh_from_db()
        self.assertNotEqual(self.post.text, POST_TEXT)
        self.assertNotEqual(self.post.group, self.first_group)

    def test_not_author_edit_post(self):
        self.authorized_follower.post(
            reverse("post_edit", args=[self.user.username, self.post.id]),
            {"text": "not" + POST_TEXT, "group": self.second_group.id},
            follow=True
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, POST_TEXT)
        self.assertEqual(self.post.group, self.first_group)

    def test_guest_edit_post(self):
        self.guest.post(
            reverse("post_edit", args=[self.user.username, self.post.id]),
            {"text": "not" + POST_TEXT, "group": self.second_group.id},
            follow=True
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, POST_TEXT)
        self.assertEqual(self.post.group, self.first_group)

    def test_followed_authors_post_appears_in_follow_list(self):
        Follow.objects.get_or_create(author=self.user, user=self.follower)
        self.assertTrue(Follow.objects.filter(author=self.user).exists())
        Follow.objects.filter(author=self.user, user=self.follower).delete()
        self.assertFalse(Follow.objects.filter(author=self.user).exists())
