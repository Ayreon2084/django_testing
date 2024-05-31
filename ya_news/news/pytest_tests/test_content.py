from http import HTTPStatus

from django.conf import settings
from django.urls import reverse
import pytest

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, list_of_news):
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, list_of_news):
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    news_list = list(response.context['object_list'])
    sorted_news = sorted(
        news_list,
        key=lambda news: news.date,
        reverse=True
    )
    assert sorted_news == news_list


@pytest.mark.django_db
def test_comments_order(client, news, list_of_comments):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    news = response.context['news']
    comments_list = list(news.comment_set.all())
    sorted_comments = sorted(
        comments_list,
        key=lambda comments: comments.created
    )
    assert sorted_comments == comments_list


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, form_in_list',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False)
    )
)
def test_unauthorized_client_has_no_form(
    parametrized_client,
    form_in_list,
    comment
):
    url = reverse('news:detail', args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert ('form' in response.context) is form_in_list
    if 'form' in response.context:
        assert isinstance(response.context['form'], CommentForm)
