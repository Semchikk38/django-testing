import pytest
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from news.forms import CommentForm
from news.models import Comment, News

User = get_user_model()

pytestmark = pytest.mark.django_db

HOME_URL = reverse('news:home')


@pytest.fixture
def author(django_user_model):
    """Фикстура создания автора комментариев."""
    return django_user_model.objects.create(username='Комментатор')


@pytest.fixture
def news():
    """Фикстура создания новости."""
    return News.objects.create(
        title='Тестовая новость',
        text='Просто текст.'
    )


@pytest.fixture
def detail_url(news):
    """Фикстура получения URL детальной страницы новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def create_news():
    """Фикстура создания множества новостей."""
    def _create_news(count):
        today = datetime.today()
        all_news = [
            News(
                title=f'Новость {index}',
                text='Просто текст.',
                date=today - timedelta(days=index)
            )
            for index in range(count)
        ]
        News.objects.bulk_create(all_news)
    return _create_news


@pytest.fixture
def create_comments(news, author):
    """Фикстура создания множества комментариев."""
    def _create_comments(count):
        now = timezone.now()
        for index in range(count):
            comment = Comment.objects.create(
                news=news,
                author=author,
                text=f'Текст {index}',
            )
            comment.created = now + timedelta(days=index)
            comment.save()
    return _create_comments


def test_news_count(client, create_news):
    """Тест количества новостей на главной странице."""
    create_news(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    response = client.get(HOME_URL)
    news = response.context['object_list']
    assert news.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, create_news):
    """Тест порядка новостей на главной странице."""
    create_news(settings.NEWS_COUNT_ON_HOME_PAGE)
    response = client.get(HOME_URL)
    news = response.context['object_list']
    all_dates = [one_news.date for one_news in news]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, news, detail_url, create_comments):
    """Тест порядка комментариев на странице новости."""
    create_comments(10)
    response = client.get(detail_url)
    news_obj = response.context['news']
    comments = news_obj.comment_set.all()
    all_timestamps = [comment.created for comment in comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, detail_url):
    """Тест отсутствия формы комментария для анонимного пользователя."""
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(client, author, detail_url):
    """Тест наличия формы комментария для авторизованного пользователя."""
    client.force_login(author)
    response = client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
