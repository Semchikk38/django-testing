from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .test_constants import (
    NOTE_ADD_URL, NOTE_SLUG, NOTE_TITLE, NOTE_TEXT, FORM_DATA
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
        cls.form_data = FORM_DATA
        cls.author_client = cls.client_class()
        cls.not_author_client = cls.client_class()
        cls.author_client.force_login(cls.author)
        cls.not_author_client.force_login(cls.not_author)


class TestLogic(BaseTest):

    def test_author_can_create_note(self):
        notes_before = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(NOTE_ADD_URL, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_after = set(Note.objects.values_list('id', flat=True))
        new_notes = notes_after - notes_before
        self.assertEqual(len(new_notes), 1)
        new_note = Note.objects.get(id=new_notes.pop())
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        notes_before = set(Note.objects.values_list('id', flat=True))
        response = self.client.post(NOTE_ADD_URL, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={NOTE_ADD_URL}'
        self.assertRedirects(response, expected_url)
        notes_after = set(Note.objects.values_list('id', flat=True))
        self.assertEqual(notes_before, notes_after)

    def test_not_unique_slug(self):
        notes_before = set(Note.objects.values_list('id', flat=True))
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(NOTE_ADD_URL, data=self.form_data)
        form = response.context['form']
        self.assertIn('slug', form.errors)
        self.assertIn(self.note.slug + WARNING, form.errors['slug'])
        notes_after = set(Note.objects.values_list('id', flat=True))
        self.assertEqual(notes_before, notes_after)

    def test_empty_slug(self):
        notes_before = set(Note.objects.values_list('id', flat=True))
        form_data_without_slug = {
            'title': self.form_data['title'],
            'text': self.form_data['text']
        }
        response = self.author_client.post(
            NOTE_ADD_URL, data=form_data_without_slug
        )
        self.assertRedirects(response, reverse('notes:success'))
        notes_after = set(Note.objects.values_list('id', flat=True))
        new_notes = notes_after - notes_before
        self.assertEqual(len(new_notes), 1)
        new_note = Note.objects.get(id=new_notes.pop())
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_author_can_edit_note(self):
        original_note_data = {
            'title': self.note.title,
            'text': self.note.text,
            'slug': self.note.slug,
            'author': self.note.author
        }
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(self.note.author, original_note_data['author'])

    def test_not_author_cant_edit_note(self):
        original_note_data = {
            'title': self.note.title,
            'text': self.note.text,
            'slug': self.note.slug,
            'author': self.note.author
        }
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.not_author_client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, original_note_data['title'])
        self.assertEqual(self.note.text, original_note_data['text'])
        self.assertEqual(self.note.slug, original_note_data['slug'])
        self.assertEqual(self.note.author, original_note_data['author'])

    def test_author_can_delete_note(self):
        notes_before = set(Note.objects.values_list('id', flat=True))
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.author_client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        notes_after = set(Note.objects.values_list('id', flat=True))
        self.assertEqual(len(notes_before) - len(notes_after), 1)
        self.assertNotIn(self.note.id, notes_after)

    def test_not_author_cant_delete_note(self):
        notes_before = set(Note.objects.values_list('id', flat=True))
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.not_author_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_after = set(Note.objects.values_list('id', flat=True))
        self.assertEqual(notes_before, notes_after)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, NOTE_TITLE)
        self.assertEqual(self.note.text, NOTE_TEXT)
        self.assertEqual(self.note.slug, NOTE_SLUG)
        self.assertEqual(self.note.author, self.author)
