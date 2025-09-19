from http import HTTPStatus

import pytest
from news.models import Comment
from news.forms import BAD_WORDS, WARNING


TEXT = 'Текст комментария'
BAD_WORDS_DATA = [
    {'text': f'Какой-то текст, {bad_word}, еще текст'}
    for bad_word in BAD_WORDS
]


pytestmark = pytest.mark.django_db


def test_anonym_cant_create_comment(client, detail_url):
    client.post(detail_url, data={'text': TEXT})
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
        author_client, detail_url, comments_url, news, author):
    response = author_client.post(detail_url, data={'text': TEXT})
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == comments_url

    assert Comment.objects.count() == 1

    comment = Comment.objects.get()
    assert comment.text == TEXT
    assert comment.news == news
    assert comment.author == author


@pytest.mark.parametrize('bad_words_data', BAD_WORDS_DATA)
def test_user_cant_use_bad_words(author_client, detail_url, bad_words_data):
    response = author_client.post(detail_url, data=bad_words_data)
    form = response.context['form']
    assert form.errors['text'] == [WARNING]
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
        author_client, edit_url, comments_url, comment):
    new_text = 'Обновлённый комментарий'
    response = author_client.post(edit_url, data={'text': new_text})
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == comments_url

    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == new_text
    assert updated_comment.news == comment.news
    assert updated_comment.author == comment.author
    assert updated_comment.created == comment.created


def test_user_cant_edit_comment_of_another_user(
        reader_client, edit_url, comment):
    new_text = 'Обновлённый комментарий'
    response = reader_client.post(edit_url, data={'text': new_text})
    assert response.status_code == HTTPStatus.NOT_FOUND

    unchanged_comment = Comment.objects.get(id=comment.id)
    assert unchanged_comment.text == comment.text
    assert unchanged_comment.news == comment.news
    assert unchanged_comment.author == comment.author
    assert unchanged_comment.created == comment.created


def test_author_can_delete_comment(
        author_client, delete_url, comments_url, comment):
    response = author_client.post(delete_url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == comments_url
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
        reader_client, delete_url, comment):
    response = reader_client.post(delete_url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1

    unchanged_comment = Comment.objects.get(id=comment.id)
    assert unchanged_comment.text == comment.text
    assert unchanged_comment.news == comment.news
    assert unchanged_comment.author == comment.author
