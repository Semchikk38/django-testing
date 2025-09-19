from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

NOTES_LIST_URL = reverse('notes:list')
NOTE_ADD_URL = reverse('notes:add')
NOTE_SLUG = 'note-slug'
HOME_URL = reverse('notes:home')
LOGIN_URL = reverse('users:login')
SIGNUP_URL = reverse('users:signup')
SUCCESS_URL = reverse('notes:success')
DETAIL_URL = reverse('notes:detail', args=(NOTE_SLUG,))
EDIT_URL = reverse('notes:edit', args=(NOTE_SLUG,))
DELETE_URL = reverse('notes:delete', args=(NOTE_SLUG,))

REDIRECT_NOTES_LIST_URL = f'{LOGIN_URL}?next={NOTES_LIST_URL}'
REDIRECT_NOTE_ADD_URL = f'{LOGIN_URL}?next={NOTE_ADD_URL}'
REDIRECT_SUCCESS_URL = f'{LOGIN_URL}?next={SUCCESS_URL}'
REDIRECT_DETAIL_URL = f'{LOGIN_URL}?next={DETAIL_URL}'
REDIRECT_EDIT_URL = f'{LOGIN_URL}?next={EDIT_URL}'
REDIRECT_DELETE_URL = f'{LOGIN_URL}?next={DELETE_URL}'


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

        cls.home_url = HOME_URL
        cls.login_url = LOGIN_URL
        cls.signup_url = SIGNUP_URL
        cls.success_url = SUCCESS_URL
        cls.detail_url = DETAIL_URL
        cls.edit_url = EDIT_URL
        cls.delete_url = DELETE_URL
        cls.expected_redirect_url = REDIRECT_NOTE_ADD_URL

        cls.redirect_notes_list_url = REDIRECT_NOTES_LIST_URL
        cls.redirect_note_add_url = REDIRECT_NOTE_ADD_URL
        cls.redirect_success_url = REDIRECT_SUCCESS_URL
        cls.redirect_detail_url = REDIRECT_DETAIL_URL
        cls.redirect_edit_url = REDIRECT_EDIT_URL
        cls.redirect_delete_url = REDIRECT_DELETE_URL

        cls.OK = HTTPStatus.OK
        cls.NOT_FOUND = HTTPStatus.NOT_FOUND
        cls.FOUND = HTTPStatus.FOUND

        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def setUp(self):
        self.redirect_urls = {
            NOTES_LIST_URL: REDIRECT_NOTES_LIST_URL,
            NOTE_ADD_URL: REDIRECT_NOTE_ADD_URL,
            self.success_url: REDIRECT_SUCCESS_URL,
            self.detail_url: REDIRECT_DETAIL_URL,
            self.edit_url: REDIRECT_EDIT_URL,
            self.delete_url: REDIRECT_DELETE_URL,
        }
