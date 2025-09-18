from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .test_base import BaseTest, NOTE_ADD_URL


class TestLogic(BaseTest):

    def test_author_can_create_note(self):
        form_data = self.get_form_data()
        initial_notes = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(NOTE_ADD_URL, data=form_data)
        self.assertRedirects(response, self.success_url)

        final_notes = set(Note.objects.values_list('id', flat=True))
        new_notes = final_notes - initial_notes
        self.assertEqual(len(new_notes), 1)

        new_note = Note.objects.get(id=new_notes.pop())
        self.assertEqual(new_note.title, form_data['title'])
        self.assertEqual(new_note.text, form_data['text'])
        self.assertEqual(new_note.slug, form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        form_data = self.get_form_data()
        initial_notes = set(Note.objects.values_list('id', flat=True))
        response = self.client.post(NOTE_ADD_URL, data=form_data)
        self.assertRedirects(response, self.expected_redirect_url)

        final_notes = set(Note.objects.values_list('id', flat=True))
        self.assertEqual(initial_notes, final_notes)

    def test_not_unique_slug(self):
        form_data = self.get_form_data(slug=self.note.slug)
        initial_notes = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(NOTE_ADD_URL, data=form_data)
        form = response.context['form']
        self.assertIn('slug', form.errors)
        self.assertIn(self.note.slug + WARNING, form.errors['slug'])

        final_notes = set(Note.objects.values_list('id', flat=True))
        self.assertEqual(initial_notes, final_notes)

    def test_empty_slug(self):
        form_data = self.get_form_data()
        form_data.pop('slug')
        initial_notes = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(NOTE_ADD_URL, data=form_data)
        self.assertRedirects(response, self.success_url)

        final_notes = set(Note.objects.values_list('id', flat=True))
        new_notes = final_notes - initial_notes
        self.assertEqual(len(new_notes), 1)

        new_note = Note.objects.get(id=new_notes.pop())
        expected_slug = slugify(form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)
        self.assertEqual(new_note.title, form_data['title'])
        self.assertEqual(new_note.text, form_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_author_can_edit_note(self):
        form_data = self.get_form_data()
        original_note_data = {
            'title': self.note.title,
            'text': self.note.text,
            'slug': self.note.slug,
            'author': self.note.author
        }

        response = self.author_client.post(self.edit_url, data=form_data)
        self.assertRedirects(response, self.success_url)

        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, form_data['title'])
        self.assertEqual(updated_note.text, form_data['text'])
        self.assertEqual(updated_note.slug, form_data['slug'])
        self.assertEqual(updated_note.author, original_note_data['author'])

    def test_not_author_cant_edit_note(self):
        form_data = self.get_form_data()
        original_note_data = {
            'title': self.note.title,
            'text': self.note.text,
            'slug': self.note.slug,
            'author': self.note.author
        }

        response = self.not_author_client.post(self.edit_url, data=form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        unchanged_note = Note.objects.get(id=self.note.id)
        self.assertEqual(unchanged_note.title, original_note_data['title'])
        self.assertEqual(unchanged_note.text, original_note_data['text'])
        self.assertEqual(unchanged_note.slug, original_note_data['slug'])
        self.assertEqual(unchanged_note.author, original_note_data['author'])

    def test_author_can_delete_note(self):
        initial_notes = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, self.success_url)

        final_notes = set(Note.objects.values_list('id', flat=True))
        self.assertEqual(len(initial_notes) - len(final_notes), 1)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_not_author_cant_delete_note(self):
        initial_notes = set(Note.objects.values_list('id', flat=True))
        response = self.not_author_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        final_notes = set(Note.objects.values_list('id', flat=True))
        self.assertEqual(initial_notes, final_notes)
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())
