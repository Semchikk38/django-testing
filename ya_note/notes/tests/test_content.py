from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .test_base import BaseTest
from .test_constants import NOTE_ADD_URL, NOTE_SLUG


class TestContent(BaseTest):

    def test_author_can_create_note(self):
        form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        notes_count_before = Note.objects.count()
        response = self.author_client.post(NOTE_ADD_URL, data=form_data)
        self.assertRedirects(response, self.success_url)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after - notes_count_before, 1)
        new_note = Note.objects.latest('id')
        self.assertEqual(new_note.title, form_data['title'])
        self.assertEqual(new_note.text, form_data['text'])
        self.assertEqual(new_note.slug, form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        notes_count_before = Note.objects.count()
        response = self.client.post(NOTE_ADD_URL, data=form_data)
        self.assertRedirects(response, self.expected_redirect_url)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_before, notes_count_after)

    def test_not_unique_slug(self):
        form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': self.note.slug
        }
        notes_count_before = Note.objects.count()
        response = self.author_client.post(NOTE_ADD_URL, data=form_data)
        form = response.context['form']
        self.assertIn('slug', form.errors)
        self.assertIn(self.note.slug + WARNING, form.errors['slug'])
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_before, notes_count_after)

    def test_empty_slug(self):
        form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст'
        }
        notes_count_before = Note.objects.count()
        response = self.author_client.post(NOTE_ADD_URL, data=form_data)
        self.assertRedirects(response, self.success_url)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after - notes_count_before, 1)
        new_note = Note.objects.latest('id')
        expected_slug = slugify(form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)
        self.assertEqual(new_note.title, form_data['title'])
        self.assertEqual(new_note.text, form_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_author_can_edit_note(self):
        form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        original_author = self.note.author
        response = self.author_client.post(self.edit_url, data=form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, form_data['title'])
        self.assertEqual(self.note.text, form_data['text'])
        self.assertEqual(self.note.slug, form_data['slug'])
        self.assertEqual(self.note.author, original_author)

    def test_not_author_cant_edit_note(self):
        form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        original_title = self.note.title
        original_text = self.note.text
        original_slug = self.note.slug
        original_author = self.note.author

        response = self.not_author_client.post(self.edit_url, data=form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        unchanged_note = Note.objects.get(id=self.note.id)
        self.assertEqual(unchanged_note.title, original_title)
        self.assertEqual(unchanged_note.text, original_text)
        self.assertEqual(unchanged_note.slug, original_slug)
        self.assertEqual(unchanged_note.author, original_author)

    def test_author_can_delete_note(self):
        notes_count_before = Note.objects.count()
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, self.success_url)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_before - notes_count_after, 1)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_not_author_cant_delete_note(self):
        notes_count_before = Note.objects.count()
        response = self.not_author_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_before, notes_count_after)
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())
        unchanged_note = Note.objects.get(id=self.note.id)
        self.assertEqual(unchanged_note.title, 'Заголовок')
        self.assertEqual(unchanged_note.text, 'Текст заметки')
        self.assertEqual(unchanged_note.slug, NOTE_SLUG)
        self.assertEqual(unchanged_note.author, self.author)
