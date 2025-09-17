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


@pytest.fixture
def form_data():
    return {'text': COMMENT_TEXT}


@pytest.fixture
def new_form_data():
    return {'text': NEW_COMMENT_TEXT}


@pytest.fixture
def bad_words_data():
    return {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}


def test_anonymous_user_cant_create_comment(client, detail_url, form_data):
    client.post(detail_url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(
        author_client, detail_url, comments_url, form_data, news, author):
    response = author_client.post(detail_url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == comments_url

    comments_count = Comment.objects.count()
    assert comments_count == 1

    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, detail_url, bad_word):
    bad_words_data = {'text': f'Какой-то текст, {bad_word}, еще текст'}
    response = author_client.post(detail_url, data=bad_words_data)
    form = response.context['form']
    assert form.errors['text'] == [WARNING]

    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_edit_comment(
        author_client, edit_url, comments_url, new_form_data, comment):
    original_news = comment.news
    original_author = comment.author
    original_created = comment.created

    response = author_client.post(edit_url, data=new_form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == comments_url

    comment.refresh_from_db()

    assert comment.text == NEW_COMMENT_TEXT
    assert comment.news == original_news
    assert comment.author == original_author
    assert comment.created == original_created


def test_user_cant_edit_comment_of_another_user(
        reader_client, edit_url, new_form_data, comment):
    original_text = comment.text
    original_news = comment.news
    original_author = comment.author
    original_created = comment.created

    response = reader_client.post(edit_url, data=new_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND

    comment.refresh_from_db()

    assert comment.text == original_text
    assert comment.news == original_news
    assert comment.author == original_author
    assert comment.created == original_created


def test_author_can_delete_comment(
        author_client, delete_url, comments_url, comment):
    comments_count_before = Comment.objects.count()
    response = author_client.post(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == comments_url
    assert Comment.objects.count() == comments_count_before - 1


def test_user_cant_delete_comment_of_another_user(
        reader_client, delete_url, comment):
    comments_count_before = Comment.objects.count()
    response = reader_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_count_before
