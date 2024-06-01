from http import HTTPStatus
from random import choice

from django.urls import reverse
import pytest

from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_unauthorized_user_cant_create_comment(
    client,
    news,
    post_comment
):
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=post_comment)
    response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_authorized_user_can_create_comment(
    auth_user,
    auth_user_client,
    news,
    post_comment
):
    url = reverse('news:detail', args=(news.id,))
    response = auth_user_client.post(url, data=post_comment)
    assert response.status_code == HTTPStatus.FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == post_comment['text']
    assert comment.news == news
    assert comment.author == auth_user


def test_user_cant_use_bad_words(
    auth_user_client,
    news
):
    url = reverse('news:detail', args=(news.id,))
    comment_with_bad_words = {
        'text': f'Tests is the most {choice(BAD_WORDS)} boring topic!'
    }
    response = auth_user_client.post(url, data=comment_with_bad_words)
    assert response.status_code == HTTPStatus.OK
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(
    author_client,
    news,
    comment
):
    detail_url = reverse('news:detail', args=(news.id,))
    delete_comment_url = reverse('news:delete', args=(comment.id,))
    url_to_comment = detail_url + '#comments'
    response = author_client.delete(delete_comment_url)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, url_to_comment)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
    auth_user_client,
    comment
):
    delete_comment_url = reverse('news:delete', args=(comment.id,))
    response = auth_user_client.delete(delete_comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_unauthorized_user_cant_delete_comment(
    client,
    comment
):
    delete_comment_url = reverse('news:delete', args=(comment.id,))
    response = client.delete(delete_comment_url)
    assert response.status_code == HTTPStatus.FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
    author_client,
    comment,
    news,
    post_comment
):
    detail_url = reverse('news:detail', args=(news.id,))
    edit_comment_url = reverse('news:edit', args=(comment.id,))
    url_to_comments = detail_url + '#comments'
    response = author_client.post(edit_comment_url, data=post_comment)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == post_comment['text']


def test_user_cant_edit_comment_of_another_user(
    auth_user_client,
    comment,
    post_comment
):
    edit_comment_url = reverse('news:edit', args=(comment.id,))
    current_comment_text = comment.text
    response = auth_user_client.post(edit_comment_url, data=post_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == current_comment_text


@pytest.mark.django_db
def test_unauthorized_user_cant_edit_comment(
    client,
    comment,
    post_comment
):
    edit_comment_url = reverse('news:edit', args=(comment.id,))
    current_comment_text = comment.text
    response = client.post(edit_comment_url, data=post_comment)
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == current_comment_text
