from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects
import pytest


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_id')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None)
    )
)
def test_pages_availability_for_everyone(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('auth_user_client'), HTTPStatus.NOT_FOUND)
    )
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_id')),
        ('news:delete', pytest.lazy_fixture('comment_id'))
    )
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client,
    expected_status,
    name,
    args
):
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_id')),
        ('news:delete', pytest.lazy_fixture('comment_id'))
    )
)
def test_redirect_for_unauthorized_client(
    client,
    name,
    args
):
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
