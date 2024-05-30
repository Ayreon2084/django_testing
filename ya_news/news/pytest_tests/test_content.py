from django.conf import settings
from django.urls import reverse
import pytest

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, list_of_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, list_of_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert sorted_dates == all_dates


@pytest.mark.django_db
def test_comments_order(client, news, list_of_comments):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    object_list = response.context['news']
    comments = object_list.comment_set.all()
    all_dates = [comment.created for comment in comments]
    sorted_dates = sorted(all_dates)
    assert all_dates == sorted_dates

@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, form_in_list',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False)
    )
)
def test_anonymous_client_has_no_form(
    parametrized_client,
    form_in_list,
    comment
):
    url = reverse('news:detail', args=(comment.id,))
    response = parametrized_client.get(url)
    print(response.context)
    assert ('form' in response.context) is form_in_list
