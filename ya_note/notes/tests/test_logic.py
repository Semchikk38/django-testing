from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .test_base import BaseTest, NOTE_ADD_URL


class TestLogic(BaseTest):

    def test_author_can_create_note(self):
        initial_note_ids = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(NOTE_ADD_URL, data=self.form_data)
        self.assertRedirects(response, self.success_url)

        final_note_ids = set(Note.objects.values_list('id', flat=True))
        new_note_ids = final_note_ids - initial_note_ids
        self.assertEqual(len(new_note_ids), 1)

        new_note = Note.objects.get(id=new_note_ids.pop())
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        initial_note_ids = set(Note.objects.values_list('id', flat=True))
        response = self.client.post(NOTE_ADD_URL, data=self.form_data)
        self.assertRedirects(response, self.expected_redirect_url)
        self.assertEqual(
            set(Note.objects.values_list('id', flat=True)), initial_note_ids)

    def test_not_unique_slug(self):
        self.form_data['slug'] = self.note.slug
        initial_note_ids = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(NOTE_ADD_URL, data=self.form_data)
        form = response.context['form']
        self.assertIn('slug', form.errors)
        self.assertIn(self.note.slug + WARNING, form.errors['slug'])
        self.assertEqual(
            set(Note.objects.values_list('id', flat=True)), initial_note_ids)

    def test_empty_slug(self):
        del self.form_data['slug']
        initial_note_ids = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(NOTE_ADD_URL, data=self.form_data)
        self.assertRedirects(response, self.success_url)

        final_note_ids = set(Note.objects.values_list('id', flat=True))
        new_note_ids = final_note_ids - initial_note_ids
        self.assertEqual(len(new_note_ids), 1)

        new_note = Note.objects.get(id=new_note_ids.pop())
        self.assertEqual(new_note.slug, slugify(self.form_data['title']))
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_author_can_edit_note(self):
        original_author = self.note.author
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)

        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, self.form_data['title'])
        self.assertEqual(updated_note.text, self.form_data['text'])
        self.assertEqual(updated_note.slug, self.form_data['slug'])
        self.assertEqual(updated_note.author, original_author)

    def test_not_author_cant_edit_note(self):
        original_title = self.note.title
        original_text = self.note.text
        original_slug = self.note.slug
        original_author = self.note.author

        response = self.not_author_client.post(
            self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        unchanged_note = Note.objects.get(id=self.note.id)
        self.assertEqual(unchanged_note.title, original_title)
        self.assertEqual(unchanged_note.text, original_text)
        self.assertEqual(unchanged_note.slug, original_slug)
        self.assertEqual(unchanged_note.author, original_author)

    def test_author_can_delete_note(self):
        initial_note_ids = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(
            len(set(Note.objects.values_list('id', flat=True))),
            len(initial_note_ids) - 1)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_not_author_cant_delete_note(self):
        initial_note_ids = set(Note.objects.values_list('id', flat=True))
        response = self.not_author_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(
            set(Note.objects.values_list('id', flat=True)), initial_note_ids)

        existing_note = Note.objects.get(id=self.note.id)
        self.assertEqual(existing_note.title, self.note.title)
        self.assertEqual(existing_note.text, self.note.text)
        self.assertEqual(existing_note.slug, self.note.slug)
        self.assertEqual(existing_note.author, self.note.author)
