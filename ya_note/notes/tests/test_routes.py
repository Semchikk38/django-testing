from django.contrib.auth import get_user_model

from .test_base import BaseTest, NOTES_LIST_URL, NOTE_ADD_URL
from .test_base import (
    REDIRECT_NOTES_LIST_URL, REDIRECT_NOTE_ADD_URL,
    REDIRECT_SUCCESS_URL, REDIRECT_DETAIL_URL,
    REDIRECT_EDIT_URL, REDIRECT_DELETE_URL,
    SUCCESS_URL, DETAIL_URL,
    EDIT_URL, DELETE_URL,
    SIGNUP_URL, LOGIN_URL,
    HOME_URL
)

User = get_user_model()


class TestRoutes(BaseTest):

    def test_pages_availability(self):
        test_cases = [
            (self.client, HOME_URL, self.OK),
            (self.client, LOGIN_URL, self.OK),
            (self.client, SIGNUP_URL, self.OK),

            (self.not_author_client, NOTES_LIST_URL, self.OK),
            (self.not_author_client, NOTE_ADD_URL, self.OK),
            (self.not_author_client, SUCCESS_URL, self.OK),

            (self.author_client, DETAIL_URL, self.OK),
            (self.author_client, EDIT_URL, self.OK),
            (self.author_client, DELETE_URL, self.OK),

            (self.not_author_client, DETAIL_URL, self.NOT_FOUND),
            (self.not_author_client, EDIT_URL, self.NOT_FOUND),
            (self.not_author_client, DELETE_URL, self.NOT_FOUND),

            (self.client, NOTES_LIST_URL, self.FOUND),
            (self.client, NOTE_ADD_URL, self.FOUND),
            (self.client, SUCCESS_URL, self.FOUND),
            (self.client, DETAIL_URL, self.FOUND),
            (self.client, EDIT_URL, self.FOUND),
            (self.client, DELETE_URL, self.FOUND),
        ]

        for client, url, expected_status in test_cases:
            with self.subTest(url=url, client=client, status=expected_status):
                self.assertEqual(client.get(url).status_code, expected_status)

    def test_redirects_for_anonymous_user(self):
        urls_to_check = [
            (NOTES_LIST_URL, REDIRECT_NOTES_LIST_URL),
            (NOTE_ADD_URL, REDIRECT_NOTE_ADD_URL),
            (SUCCESS_URL, REDIRECT_SUCCESS_URL),
            (DETAIL_URL, REDIRECT_DETAIL_URL),
            (EDIT_URL, REDIRECT_EDIT_URL),
            (DELETE_URL, REDIRECT_DELETE_URL),
        ]

        for url, expected_url in urls_to_check:
            with self.subTest(url=url):
                self.assertRedirects(self.client.get(url), expected_url)
