from django.urls import reverse

NOTES_LIST_URL = reverse('notes:list')
NOTE_ADD_URL = reverse('notes:add')

NOTE_SLUG = 'note-slug'
NEW_NOTE_SLUG = 'new-slug'
NOTE_TITLE = 'Заголовок'
NOTE_TEXT = 'Текст заметки'
NEW_NOTE_TITLE = 'Новый заголовок'
NEW_NOTE_TEXT = 'Новый текст'

FORM_DATA = {
    'title': NEW_NOTE_TITLE,
    'text': NEW_NOTE_TEXT,
    'slug': NEW_NOTE_SLUG
}
