from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from .test_constants import (
    NOTES_LIST_URL, NOTE_ADD_URL, NOTE_SLUG, NOTE_TITLE, NOTE_TEXT
)

User = get_user_model()


class BaseTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Не автор')
        cls.note = Note.objects.create(
            title=NOTE_TITLE,
            text=NOTE_TEXT,
            slug=NOTE_SLUG,
            author=cls.author,
        )
        cls.author_client = cls.client_class()
        cls.not_author_client = cls.client_class()
        cls.anonymous_client = cls.client_class()
        cls.author_client.force_login(cls.author)
        cls.not_author_client.force_login(cls.not_author)


class TestRoutes(BaseTest):

    def test_pages_availability(self):

        test_cases = [
            (self.anonymous_client, reverse('notes:home'), HTTPStatus.OK),
            (self.anonymous_client, reverse('users:login'), HTTPStatus.OK),
            (self.anonymous_client, reverse('users:signup'), HTTPStatus.OK),

            (self.not_author_client, NOTES_LIST_URL, HTTPStatus.OK),
            (self.not_author_client, NOTE_ADD_URL, HTTPStatus.OK),
            (self.not_author_client, reverse('notes:success'), HTTPStatus.OK),

            (self.author_client, reverse(
                'notes:detail', args=(NOTE_SLUG,)), HTTPStatus.OK),
            (self.author_client, reverse(
                'notes:edit', args=(NOTE_SLUG,)), HTTPStatus.OK),
            (self.author_client, reverse(
                'notes:delete', args=(NOTE_SLUG,)), HTTPStatus.OK),
            (self.not_author_client, reverse(
                'notes:detail', args=(NOTE_SLUG,)), HTTPStatus.NOT_FOUND),
            (self.not_author_client, reverse(
                'notes:edit', args=(NOTE_SLUG,)), HTTPStatus.NOT_FOUND),
            (self.not_author_client, reverse(
                'notes:delete', args=(NOTE_SLUG,)), HTTPStatus.NOT_FOUND),
        ]
        for client, url, expected_status in test_cases:
            with self.subTest(url=url, client=client, status=expected_status):
                self.assertEqual(client.get(url).status_code, expected_status)

    def test_redirects_for_anonymous_user(self):

        login_url = reverse('users:login')

        urls_to_check = [
            NOTES_LIST_URL,
            NOTE_ADD_URL,
            reverse('notes:success'),
            reverse('notes:detail', args=(NOTE_SLUG,)),
            reverse('notes:edit', args=(NOTE_SLUG,)),
            reverse('notes:delete', args=(NOTE_SLUG,)),
        ]

        for url in urls_to_check:
            with self.subTest(url=url):
                expected_url = f'{login_url}?next={url}'
                response = self.anonymous_client.get(url)
                self.assertRedirects(response, expected_url)
