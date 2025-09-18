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
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def signup_url():
    """Фикстура получения URL страницы регистрации."""
    return reverse('users:signup')


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
def redirect_url_for_edit(edit_url, login_url):
    return f'{login_url}?next={edit_url}'


@pytest.fixture
def redirect_url_for_delete(delete_url, login_url):
    return f'{login_url}?next={delete_url}'


@pytest.mark.parametrize(
    'url_fixture, expected_status',
    [
        ('home_url', HTTPStatus.OK),
        ('login_url', HTTPStatus.OK),
        ('signup_url', HTTPStatus.OK),
        ('detail_url', HTTPStatus.OK),
    ]
)
def test_public_pages_availability(
        client, request, url_fixture, expected_status):
    url = request.getfixturevalue(url_fixture)
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'user_fixture, url_fixture, expected_status',
    [
        ('author', 'edit_url', HTTPStatus.OK),
        ('author', 'delete_url', HTTPStatus.OK),
        ('reader', 'edit_url', HTTPStatus.NOT_FOUND),
        ('reader', 'delete_url', HTTPStatus.NOT_FOUND),
    ]
)
def test_comment_pages_availability(
        client, request, user_fixture, url_fixture, expected_status):
    user = request.getfixturevalue(user_fixture)
    url = request.getfixturevalue(url_fixture)

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == expected_status
    client.logout()


@pytest.mark.parametrize(
    'url_fixture, redirect_url_fixture',
    [
        ('edit_url', 'redirect_url_for_edit'),
        ('delete_url', 'redirect_url_for_delete'),
    ]
)
def test_redirect_for_anonymous_client(
        client, request, url_fixture, redirect_url_fixture):
    url = request.getfixturevalue(url_fixture)
    expected_redirect = request.getfixturevalue(redirect_url_fixture)

    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_redirect
