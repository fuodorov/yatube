from django.test import TestCase

import posts.tests.constants as const
from posts.models import Group, Post, User


class TestModelGroup(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title=const.FIRST_GROUP_NAME,
            slug=const.FIRST_GROUP_SLUG,
            description=const.FIRST_GROUP_DESCRIPTION
        )

    def test_verbose_name(self):
        field_verbose = {
            "title": Group._meta.get_field("title").verbose_name,
            "slug": Group._meta.get_field("slug").verbose_name,
            "description": Group._meta.get_field("description").verbose_name
        }
        for value, expect in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.group._meta.get_field(value).verbose_name, expect)

    def test_help_text(self):
        field_help_text = {
            "title": Group._meta.get_field("title").help_text,
            "slug": Group._meta.get_field("slug").help_text,
            "description": Group._meta.get_field("description").help_text
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
        user = User.objects.create_user(username=const.USERNAME)
        group = Group.objects.create(
            title=const.FIRST_GROUP_NAME,
            slug=const.FIRST_GROUP_SLUG,
            description=const.FIRST_GROUP_DESCRIPTION
        )
        cls.post = Post.objects.create(
            text=const.POST_TEXT,
            author=user,
            group=group
        )

    def test_verbose_name(self):
        field_verbose = {
            "text": Post._meta.get_field("text").verbose_name,
            "author": Post._meta.get_field("author").verbose_name,
            "group": Post._meta.get_field("group").verbose_name
        }
        for value, expected in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        field_verbose = {
            "text": Post._meta.get_field("text").help_text,
            "author": Post._meta.get_field("author").help_text,
            "group": Post._meta.get_field("group").help_text
        }
        for value, expected in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).help_text, expected)

    def test_str(self):
        value = TestModelGroup.group.__str__()
        expected = TestModelGroup.group.title
        self.assertEqual(value, expected)
