from .test_base import BaseTest, NOTES_LIST_URL, NOTE_ADD_URL


class TestContent(BaseTest):

    def test_note_in_list_for_author(self):
        response = self.author_client.get(NOTES_LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_for_another_user(self):
        response = self.not_author_client.get(NOTES_LIST_URL)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_create_note_page_contains_form(self):
        response = self.author_client.get(NOTE_ADD_URL)
        self.assertIn('form', response.context)

    def test_edit_note_page_contains_form(self):
        response = self.author_client.get(self.edit_url)
        self.assertIn('form', response.context)
