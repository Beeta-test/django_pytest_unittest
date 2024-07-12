from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_cant_comment(client, news, comment_form):
    """
    Тестирует, что анонимный пользователь
    не может отправить комментарий.
    """
    url = reverse('news:detail', args=[news.pk])
    response = client.post(url, comment_form)
    assert Comment.objects.count() == 0
    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db
def test_reader_can_submit_comment(reader_client, news, comment_form):
    """
    Тестирует, что авторизованный пользователь
    может отправить комментарий.
    """
    url = reverse('news:detail', args=[news.pk])
    response = reader_client.post(url, comment_form)
    assert Comment.objects.count() == 1
    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db
@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_comment_with_bad_words(reader_client, news, bad_word):
    """Тестирует, что комментарий с запрещенными словами не добавляется."""
    url = reverse('news:detail', args=[news.pk])
    response = reader_client.post(url, {'text': bad_word})
    assert Comment.objects.count() == 0
    assertFormError(response, 'form', 'text', WARNING)


@pytest.mark.django_db
def test_author_delete_comment(author_client, comment):
    """
    Тестирует, что автор комментария может
    удалять свой комментарий.
    """
    url = reverse('news:delete', args=[comment.pk])
    delete = author_client.post(url)
    assert delete.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_edit_comment(author_client, comment, comment_form):
    url = reverse('news:edit', args=[comment.pk])
    response = author_client.post(url, comment_form)
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == comment_form['text']


@pytest.mark.django_db
def test_reader_cant_delete_comment(reader_client, comment):
    """
    Тестирует, что обычный пользователь не может
    редактировать или удалять комментарии других пользователей.
    """
    url = reverse('news:delete', args=[comment.pk])
    response = reader_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_reader_cant_edit_comment(reader_client, comment, comment_form):
    original_text = comment.text
    url = reverse('news:edit', args=[comment.pk])
    response = reader_client.post(url, comment_form)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == original_text
