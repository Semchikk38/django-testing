import pytest
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from news.models import Comment, News

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def news():
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Лев Толстой')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель простой')


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def public_urls():
    return [
        (reverse('news:home'), HTTPStatus.OK),
        (reverse('users:login'), HTTPStatus.OK),
        (reverse('users:signup'), HTTPStatus.OK),
    ]


@pytest.fixture
def redirect_urls(edit_url, delete_url):
    login_url = reverse('users:login')
    return [
        (edit_url, f'{login_url}?next={edit_url}'),
        (delete_url, f'{login_url}?next={delete_url}'),
    ]


def test_public_pages_availability(client, public_urls, detail_url):
    all_public_urls = public_urls + [(detail_url, HTTPStatus.OK)]

    for url, expected_status in all_public_urls:
        response = client.get(url)
        assert response.status_code == expected_status


def test_comment_edit_delete_availability(
    client, author, reader, edit_url, delete_url
):
    test_cases = [
        (author, edit_url, HTTPStatus.OK),
        (author, delete_url, HTTPStatus.OK),
        (reader, edit_url, HTTPStatus.NOT_FOUND),
        (reader, delete_url, HTTPStatus.NOT_FOUND),
    ]

    for user, url, expected_status in test_cases:
        client.force_login(user)
        response = client.get(url)
        assert response.status_code == expected_status
        client.logout()


def test_redirect_for_anonymous_client(client, redirect_urls):
    for url, expected_redirect in redirect_urls:
        response = client.get(url)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == expected_redirect
