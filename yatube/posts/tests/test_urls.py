from posts.tests.base import BaseTestCase


class StaticURLTests(BaseTestCase):
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
