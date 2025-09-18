from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .test_base import BaseTest
from .test_constants import NOTE_ADD_URL


class TestLogic(BaseTest):

    def test_author_can_create_note(self):
        form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        initial_count = Note.objects.count()
        response = self.author_client.post(NOTE_ADD_URL, data=form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), initial_count + 1)
        new_note = Note.objects.get(slug=form_data['slug'])
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
        initial_count = Note.objects.count()
        response = self.client.post(NOTE_ADD_URL, data=form_data)
        self.assertRedirects(response, self.expected_redirect_url)
        self.assertEqual(Note.objects.count(), initial_count)

    def test_not_unique_slug(self):
        form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': self.note.slug
        }
        initial_count = Note.objects.count()
        response = self.author_client.post(NOTE_ADD_URL, data=form_data)
        form = response.context['form']
        self.assertIn('slug', form.errors)
        self.assertIn(self.note.slug + WARNING, form.errors['slug'])
        self.assertEqual(Note.objects.count(), initial_count)

    def test_empty_slug(self):
        form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст'
        }
        initial_count = Note.objects.count()
        response = self.author_client.post(NOTE_ADD_URL, data=form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), initial_count + 1)
        new_note = Note.objects.exclude(pk=self.note.pk).get()
        expected_slug = slugify(form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        response = self.author_client.post(self.edit_url, data=form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, form_data['title'])
        self.assertEqual(self.note.text, form_data['text'])
        self.assertEqual(self.note.slug, form_data['slug'])

    def test_other_user_cant_edit_note(self):
        form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        initial_count = Note.objects.count()
        response = self.not_author_client.post(self.edit_url, data=form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(Note.objects.count(), initial_count)

    def test_author_can_delete_note(self):
        initial_count = Note.objects.count()
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), initial_count - 1)

    def test_other_user_cant_delete_note(self):
        initial_count = Note.objects.count()
        response = self.not_author_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), initial_count)
