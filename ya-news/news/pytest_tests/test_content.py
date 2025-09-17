import pytest
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from news.forms import CommentForm
from news.models import Comment, News

User = get_user_model()


@pytest.mark.django_db
class TestHomePage:
    HOME_URL = reverse('news:home')

    @pytest.fixture(autouse=True)
    def setup(self):
        today = datetime.today()
        all_news = [
            News(
                title=f'Новость {index}',
                text='Просто текст.',
                date=today - timedelta(days=index)
            )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        ]
        News.objects.bulk_create(all_news)

    def test_news_count(self, client):
        response = client.get(self.HOME_URL)
        object_list = response.context['object_list']
        news_count = object_list.count()
        assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE

    def test_news_order(self, client):
        response = client.get(self.HOME_URL)
        object_list = response.context['object_list']
        all_dates = [news.date for news in object_list]
        sorted_dates = sorted(all_dates, reverse=True)
        assert all_dates == sorted_dates


@pytest.mark.django_db
class TestDetailPage:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.news = News.objects.create(
            title='Тестовая новость', text='Просто текст.'
        )
        self.detail_url = reverse('news:detail', args=(self.news.id,))
        self.author = User.objects.create(username='Комментатор')
        now = timezone.now()
        for index in range(10):
            comment = Comment.objects.create(
                news=self.news, author=self.author, text=f'Tекст {index}',
            )
            comment.created = now + timedelta(days=index)
            comment.save()

    def test_comments_order(self, client):
        response = client.get(self.detail_url)
        assert 'news' in response.context
        news = response.context['news']
        all_comments = news.comment_set.all()
        all_timestamps = [comment.created for comment in all_comments]
        sorted_timestamps = sorted(all_timestamps)
        assert all_timestamps == sorted_timestamps

    def test_anonymous_client_has_no_form(self, client):
        response = client.get(self.detail_url)
        assert 'form' not in response.context

    def test_authorized_client_has_form(self, client):
        client.force_login(self.author)
        response = client.get(self.detail_url)
        assert 'form' in response.context
        assert isinstance(response.context['form'], CommentForm)
