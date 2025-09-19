import pytest
from django.conf import settings

from news.forms import CommentForm


pytestmark = pytest.mark.django_db


def test_news_count(client, home_url, news_batch):
    response = client.get(home_url)
    news = response.context['object_list']
    assert news.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, home_url, news_batch):
    response = client.get(home_url)
    news = response.context['object_list']
    all_dates = [one_news.date for one_news in news]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_order(client, detail_url, comments_batch):
    response = client.get(detail_url)
    news_obj = response.context['news']
    comments = news_obj.comment_set.all()
    all_timestamps = [comment.created for comment in comments]
    assert all_timestamps == sorted(all_timestamps)


def test_anonymous_client_has_no_form(client, detail_url):
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, detail_url):
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
