import pytest
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment, News

User = get_user_model()

pytestmark = pytest.mark.django_db

DETAIL_URL = 'news:detail'
EDIT_URL = 'news:edit'
DELETE_URL = 'news:delete'

COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'

FORM_DATA = {'text': COMMENT_TEXT}
NEW_FORM_DATA = {'text': NEW_COMMENT_TEXT}

BAD_WORDS_DATA = [
    {'text': f'Какой-то текст, {bad_word}, еще текст'}
    for bad_word in BAD_WORDS
]


@pytest.fixture
def news():
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор комментария')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text=COMMENT_TEXT
    )


@pytest.fixture
def detail_url(news):
    return reverse(DETAIL_URL, args=(news.id,))


@pytest.fixture
def comments_url(detail_url):
    return f'{detail_url}#comments'


@pytest.fixture
def edit_url(comment):
    return reverse(EDIT_URL, args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse(DELETE_URL, args=(comment.id,))


def test_anonymous_user_cant_create_comment(client, detail_url):
    client.post(detail_url, data=FORM_DATA)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
        author_client, detail_url, comments_url, news, author):
    response = author_client.post(detail_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == comments_url

    assert Comment.objects.count() == 1

    comment = Comment.objects.get()
    assert comment.text == FORM_DATA['text']
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
    original_data = {
        'news': comment.news,
        'author': comment.author,
        'created': comment.created
    }

    response = author_client.post(edit_url, data=NEW_FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == comments_url

    updated_comment = Comment.objects.get(id=comment.id)

    assert updated_comment.text == NEW_FORM_DATA['text']
    assert updated_comment.news == original_data['news']
    assert updated_comment.author == original_data['author']
    assert updated_comment.created == original_data['created']


def test_user_cant_edit_comment_of_another_user(
        reader_client, edit_url, comment):
    original_data = {
        'text': comment.text,
        'news': comment.news,
        'author': comment.author,
        'created': comment.created
    }

    response = reader_client.post(edit_url, data=NEW_FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND

    unchanged_comment = Comment.objects.get(id=comment.id)

    assert unchanged_comment.text == original_data['text']
    assert unchanged_comment.news == original_data['news']
    assert unchanged_comment.author == original_data['author']
    assert unchanged_comment.created == original_data['created']


def test_author_can_delete_comment(
        author_client, delete_url, comments_url, comment):
    comment_id = comment.id
    response = author_client.post(delete_url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == comments_url
    assert not Comment.objects.filter(id=comment_id).exists()


def test_user_cant_delete_comment_of_another_user(
        reader_client, delete_url, comment):
    original_data = {
        'text': comment.text,
        'news': comment.news,
        'author': comment.author
    }

    response = reader_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND

    assert Comment.objects.filter(id=comment.id).exists()

    unchanged_comment = Comment.objects.get(id=comment.id)
    assert unchanged_comment.text == original_data['text']
    assert unchanged_comment.news == original_data['news']
    assert unchanged_comment.author == original_data['author']
