from django.contrib.auth import get_user_model

from .test_base import BaseTest, NOTES_LIST_URL, NOTE_ADD_URL
from .test_base import (
    REDIRECT_NOTES_LIST_URL, REDIRECT_NOTE_ADD_URL,
    REDIRECT_SUCCESS_URL, REDIRECT_DETAIL_URL,
    REDIRECT_EDIT_URL, REDIRECT_DELETE_URL
)

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
            (NOTES_LIST_URL, REDIRECT_NOTES_LIST_URL),
            (NOTE_ADD_URL, REDIRECT_NOTE_ADD_URL),
            (self.success_url, REDIRECT_SUCCESS_URL),
            (self.detail_url, REDIRECT_DETAIL_URL),
            (self.edit_url, REDIRECT_EDIT_URL),
            (self.delete_url, REDIRECT_DELETE_URL),
        ]

        for url, expected_url in urls_to_check:
            with self.subTest(url=url):
                self.assertRedirects(self.client.get(url), expected_url)
