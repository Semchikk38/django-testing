from http import HTTPStatus
import pytest

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'client_fixture_name, url_fixture_name, expected_status',
    [
        ('client', 'home_url', HTTPStatus.OK),
        ('client', 'login_url', HTTPStatus.OK),
        ('client', 'signup_url', HTTPStatus.OK),
        ('client', 'detail_url', HTTPStatus.OK),

        ('author_client', 'edit_url', HTTPStatus.OK),
        ('author_client', 'delete_url', HTTPStatus.OK),

        ('reader_client', 'edit_url', HTTPStatus.NOT_FOUND),
        ('reader_client', 'delete_url', HTTPStatus.NOT_FOUND),

        ('client', 'edit_url', HTTPStatus.FOUND),
        ('client', 'delete_url', HTTPStatus.FOUND),
    ]
)
def test_all_pages_status_codes(
        request, client_fixture_name, url_fixture_name, expected_status):
    client_obj = request.getfixturevalue(client_fixture_name)
    url = request.getfixturevalue(url_fixture_name)

    response = client_obj.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_fixture_name, redirect_url_fixture_name',
    [
        ('edit_url', 'redirect_url_for_edit'),
        ('delete_url', 'redirect_url_for_delete'),
    ]
)
def test_redirect_urls(
        client, request, url_fixture_name, redirect_url_fixture_name):
    url = request.getfixturevalue(url_fixture_name)
    expected_redirect = request.getfixturevalue(redirect_url_fixture_name)

    response = client.get(url)
    assert response.url == expected_redirect
