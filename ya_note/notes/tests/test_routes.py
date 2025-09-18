from django.contrib.auth import get_user_model

from .test_base import BaseTest
from .test_constants import NOTES_LIST_URL, NOTE_ADD_URL

User = get_user_model()


class TestRoutes(BaseTest):

    def test_pages_availability(self):
        test_cases = [
            (self.client, self.home_url, self.OK),
            (self.client, self.login_url, self.OK),
            (self.client, self.signup_url, self.OK),

            (self.not_author_client, NOTES_LIST_URL, self.OK),
            (self.not_author_client, NOTE_ADD_URL, self.OK),
            (self.not_author_client, self.success_url, self.OK),

            (self.author_client, self.detail_url, self.OK),
            (self.author_client, self.edit_url, self.OK),
            (self.author_client, self.delete_url, self.OK),

            (self.not_author_client, self.detail_url, self.NOT_FOUND),
            (self.not_author_client, self.edit_url, self.NOT_FOUND),
            (self.not_author_client, self.delete_url, self.NOT_FOUND),

            (self.client, NOTES_LIST_URL, self.FOUND),
            (self.client, NOTE_ADD_URL, self.FOUND),
            (self.client, self.success_url, self.FOUND),
            (self.client, self.detail_url, self.FOUND),
            (self.client, self.edit_url, self.FOUND),
            (self.client, self.delete_url, self.FOUND),
        ]

        for client, url, expected_status in test_cases:
            with self.subTest(url=url, client=client, status=expected_status):
                self.assertEqual(client.get(url).status_code, expected_status)

    def test_redirects_for_anonymous_user(self):
        urls_to_check = [
            (NOTES_LIST_URL, f'{self.login_url}?next={NOTES_LIST_URL}'),
            (NOTE_ADD_URL, f'{self.login_url}?next={NOTE_ADD_URL}'),
            (self.success_url, f'{self.login_url}?next={self.success_url}'),
            (self.detail_url, f'{self.login_url}?next={self.detail_url}'),
            (self.edit_url, f'{self.login_url}?next={self.edit_url}'),
            (self.delete_url, f'{self.login_url}?next={self.delete_url}'),
        ]

        for url, expected_url in urls_to_check:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)
