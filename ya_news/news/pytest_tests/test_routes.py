from http import HTTPStatus

import pytest
from pytest_lazyfixture import lazy_fixture as lf

pytestmark = pytest.mark.django_db

OK = HTTPStatus.OK
NOT_FOUND = HTTPStatus.NOT_FOUND
FOUND = HTTPStatus.FOUND

CLIENT = lf('client')
AUTHOR_CLIENT = lf('author_client')
READER_CLIENT = lf('reader_client')

HOME_URL = lf('home_url')
LOGIN_URL = lf('login_url')
SIGNUP_URL = lf('signup_url')
DETAIL_URL = lf('detail_url')
EDIT_URL = lf('edit_url')
DELETE_URL = lf('delete_url')
REDIRECT_URL_FOR_EDIT = lf('redirect_url_for_edit')
REDIRECT_URL_FOR_DELETE = lf('redirect_url_for_delete')


@pytest.mark.parametrize(
    'client_fixture_name, url_fixture_name, expected_status',
    [
        (CLIENT, HOME_URL, OK),
        (CLIENT, LOGIN_URL, OK),
        (CLIENT, SIGNUP_URL, OK),
        (CLIENT, DETAIL_URL, OK),

        (AUTHOR_CLIENT, EDIT_URL, OK),
        (AUTHOR_CLIENT, DELETE_URL, OK),

        (READER_CLIENT, EDIT_URL, NOT_FOUND),
        (READER_CLIENT, DELETE_URL, NOT_FOUND),

        (CLIENT, EDIT_URL, FOUND),
        (CLIENT, DELETE_URL, FOUND),
    ]
)
def test_all_pages_status_codes(
        client_fixture_name, url_fixture_name, expected_status):
    response = client_fixture_name.get(url_fixture_name)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_fixture_name, redirect_url_fixture_name',
    [
        (EDIT_URL, REDIRECT_URL_FOR_EDIT),
        (DELETE_URL, REDIRECT_URL_FOR_DELETE),
    ]
)
def test_redirect_urls(client, url_fixture_name, redirect_url_fixture_name):
    response = client.get(url_fixture_name)
    assert response.url == redirect_url_fixture_name
