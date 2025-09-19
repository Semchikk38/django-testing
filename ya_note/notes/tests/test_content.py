from .test_base import BaseTest, NOTES_LIST_URL, NOTE_ADD_URL, EDIT_URL


class TestContent(BaseTest):

    def test_note_in_list_for_author(self):
        response = self.author_client.get(NOTES_LIST_URL)
        notes = response.context['object_list']
        self.assertIn(self.note, notes)

        author_note = notes.get(id=self.note.id)
        self.assertEqual(author_note.title, self.note.title)
        self.assertEqual(author_note.text, self.note.text)
        self.assertEqual(author_note.slug, self.note.slug)
        self.assertEqual(author_note.author, self.note.author)

    def test_note_not_in_list_for_another_user(self):
        response = self.not_author_client.get(NOTES_LIST_URL)
        notes = response.context['object_list']
        self.assertNotIn(self.note, notes)

    def test_pages_contain_form(self):
        urls_to_check = [
            (NOTE_ADD_URL, 'страницы создания'),
            (EDIT_URL, 'страницы редактирования'),
        ]

        for url, description in urls_to_check:
            with self.subTest(url=url, description=description):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
