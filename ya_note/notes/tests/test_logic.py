from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .test_base import (
    BaseTest, NOTE_ADD_URL, EDIT_URL,
    DELETE_URL, SUCCESS_URL, REDIRECT_NOTE_ADD_URL
)


class TestLogic(BaseTest):

    def test_author_can_create_note(self):
        initial_notes_ids = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(NOTE_ADD_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)

        final_notes_ids = set(Note.objects.values_list('id', flat=True))
        new_notes_ids = final_notes_ids - initial_notes_ids
        self.assertEqual(len(new_notes_ids), 1)
        new_note = Note.objects.get(id=new_notes_ids.pop())
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        initial_notes_ids = set(Note.objects.values_list('id', flat=True))
        response = self.client.post(NOTE_ADD_URL, data=self.form_data)
        self.assertRedirects(response, REDIRECT_NOTE_ADD_URL)
        self.assertEqual(
            set(Note.objects.values_list('id', flat=True)), initial_notes_ids)

    def test_not_unique_slug(self):
        self.form_data['slug'] = self.note.slug
        initial_notes_ids = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(NOTE_ADD_URL, data=self.form_data)
        form = response.context['form']
        self.assertIn('slug', form.errors)
        self.assertIn(self.note.slug + WARNING, form.errors['slug'])
        self.assertEqual(
            set(Note.objects.values_list('id', flat=True)), initial_notes_ids)

    def test_empty_slug(self):
        del self.form_data['slug']
        initial_notes_ids = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(NOTE_ADD_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)

        final_notes_ids = set(Note.objects.values_list('id', flat=True))
        new_notes_ids = final_notes_ids - initial_notes_ids
        self.assertEqual(len(new_notes_ids), 1)

        new_note = Note.objects.get(id=new_notes_ids.pop())
        self.assertEqual(new_note.slug, slugify(self.form_data['title']))
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_author_can_edit_note(self):
        response = self.author_client.post(EDIT_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)

        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, self.form_data['title'])
        self.assertEqual(updated_note.text, self.form_data['text'])
        self.assertEqual(updated_note.slug, self.form_data['slug'])
        self.assertEqual(updated_note.author, self.note.author)

    def test_not_author_cant_edit_note(self):
        response = self.not_author_client.post(
            EDIT_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        unchanged_note = Note.objects.get(id=self.note.id)
        self.assertEqual(unchanged_note.title, self.note.title)
        self.assertEqual(unchanged_note.text, self.note.text)
        self.assertEqual(unchanged_note.slug, self.note.slug)
        self.assertEqual(unchanged_note.author, self.note.author)

    def test_author_can_delete_note(self):
        initial_count = Note.objects.count()
        response = self.author_client.post(DELETE_URL)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), initial_count - 1)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_not_author_cant_delete_note(self):
        initial_notes_ids = set(Note.objects.values_list('id', flat=True))
        response = self.not_author_client.post(DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(
            set(Note.objects.values_list('id', flat=True)), initial_notes_ids)

        existing_note = Note.objects.get(id=self.note.id)
        self.assertEqual(existing_note.title, self.note.title)
        self.assertEqual(existing_note.text, self.note.text)
        self.assertEqual(existing_note.slug, self.note.slug)
        self.assertEqual(existing_note.author, self.note.author)
