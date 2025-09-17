import pytest
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from news.models import Comment, News

User = get_user_model()


@pytest.mark.django_db
class TestRoutes:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.news = News.objects.create(title='Заголовок', text='Текст')
        self.author = User.objects.create(username='Лев Толстой')
        self.reader = User.objects.create(username='Читатель простой')
        self.comment = Comment.objects.create(
            news=self.news,
            author=self.author,
            text='Текст комментария'
        )

    @pytest.mark.parametrize(
        'name,args',
        [
            ('news:home', None),
            ('news:detail', lambda self: (self.news.id,)),
            ('users:login', None),
            ('users:signup', None),
        ]
    )
    def test_pages_availability(self, client, name, args):
        if callable(args):
            args = args(self)
        url = reverse(name, args=args)
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK

    @pytest.mark.parametrize('name', ['news:edit', 'news:delete'])
    def test_availability_for_comment_edit_and_delete_author(
        self, client, name
    ):
        client.force_login(self.author)
        url = reverse(name, args=(self.comment.id,))
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK

    @pytest.mark.parametrize('name', ['news:edit', 'news:delete'])
    def test_availability_for_comment_edit_and_delete_reader(
        self, client, name
    ):
        client.force_login(self.reader)
        url = reverse(name, args=(self.comment.id,))
        response = client.get(url)
        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize('name', ['news:edit', 'news:delete'])
    def test_redirect_for_anonymous_client(self, client, name):
        login_url = reverse('users:login')
        url = reverse(name, args=(self.comment.id,))
        redirect_url = f'{login_url}?next={url}'
        response = client.get(url)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == redirect_url
