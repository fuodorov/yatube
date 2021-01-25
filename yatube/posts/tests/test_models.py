from django.test import TestCase

import posts.tests.constants as consts
from posts.models import Group, Post, User


class TestModelGroup(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title=consts.FIRST_GROUP_NAME,
            slug=consts.FIRST_GROUP_SLUG,
            description=consts.FIRST_GROUP_DESCRIPTION
        )

    def test_verbose_name(self):
        get_field = Group._meta.get_field
        field_verbose = {
            "title": get_field("title").verbose_name,
            "slug": get_field("slug").verbose_name,
            "description": get_field("description").verbose_name
        }
        for value, expect in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.group._meta.get_field(value).verbose_name, expect)

    def test_help_text(self):
        get_field = Group._meta.get_field
        field_help_text = {
            "title": get_field("title").help_text,
            "slug": get_field("slug").help_text,
            "description": get_field("description").help_text
        }
        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.group._meta.get_field(value).help_text, expected)

    def test_str(self):
        value = self.group.__str__()
        expected = self.group.title
        self.assertEqual(value, expected)


class TestModelPost(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create_user(username=consts.USERNAME)
        group = Group.objects.create(
            title=consts.FIRST_GROUP_NAME,
            slug=consts.FIRST_GROUP_SLUG,
            description=consts.FIRST_GROUP_DESCRIPTION
        )
        cls.post = Post.objects.create(
            text=consts.POST_TEXT,
            author=user,
            group=group
        )

    def test_verbose_name(self):
        get_field = Post._meta.get_field
        field_verbose = {
            "text": get_field("text").verbose_name,
            "author": get_field("author").verbose_name,
            "group": get_field("group").verbose_name
        }
        for value, expected in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        get_field = Post._meta.get_field
        field_verbose = {
            "text": get_field("text").help_text,
            "author": get_field("author").help_text,
            "group": get_field("group").help_text
        }
        for value, expected in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).help_text, expected)

    def test_str(self):
        value = TestModelGroup.group.__str__()
        expected = TestModelGroup.group.title
        self.assertEqual(value, expected)
