from http import HTTPStatus
import pytest
from pytest_lazyfixture import lazy_fixture as lf

pytestmark = pytest.mark.django_db

OK = HTTPStatus.OK
NOT_FOUND = HTTPStatus.NOT_FOUND
FOUND = HTTPStatus.FOUND


@pytest.mark.parametrize(
    'client_fixture_name, url_fixture_name, expected_status',
    [
        (lf('client'), lf('home_url'), OK),
        (lf('client'), lf('login_url'), OK),
        (lf('client'), lf('signup_url'), OK),
        (lf('client'), lf('detail_url'), OK),

        (lf('author_client'), lf('edit_url'), OK),
        (lf('author_client'), lf('delete_url'), OK),

        (lf('reader_client'), lf('edit_url'), NOT_FOUND),
        (lf('reader_client'), lf('delete_url'), NOT_FOUND),

        (lf('client'), lf('edit_url'), FOUND),
        (lf('client'), lf('delete_url'), FOUND),
    ]
)
def test_all_pages_status_codes(
        client_fixture_name, url_fixture_name, expected_status):
    response = client_fixture_name.get(url_fixture_name)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_fixture_name, redirect_url_fixture_name',
    [
        (lf('edit_url'), lf('redirect_url_for_edit')),
        (lf('delete_url'), lf('redirect_url_for_delete')),
    ]
)
def test_redirect_urls(client, url_fixture_name, redirect_url_fixture_name):
    response = client.get(url_fixture_name)
    assert response.url == redirect_url_fixture_name
