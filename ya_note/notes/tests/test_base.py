from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from http import HTTPStatus

from notes.models import Note
from .test_constants import NOTE_SLUG, NOTE_ADD_URL

User = get_user_model()


class BaseTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Не автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug=NOTE_SLUG,
            author=cls.author,
        )
        cls.author_client = cls.client_class()
        cls.not_author_client = cls.client_class()
        cls.author_client.force_login(cls.author)
        cls.not_author_client.force_login(cls.not_author)

        cls.home_url = reverse('notes:home')
        cls.login_url = reverse('users:login')
        cls.signup_url = reverse('users:signup')
        cls.success_url = reverse('notes:success')
        cls.detail_url = reverse('notes:detail', args=(NOTE_SLUG,))
        cls.edit_url = reverse('notes:edit', args=(NOTE_SLUG,))
        cls.delete_url = reverse('notes:delete', args=(NOTE_SLUG,))
        cls.expected_redirect_url = f'{cls.login_url}?next={NOTE_ADD_URL}'

        cls.OK = HTTPStatus.OK
        cls.NOT_FOUND = HTTPStatus.NOT_FOUND
        cls.FOUND = HTTPStatus.FOUND
