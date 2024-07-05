import pytest
from http import HTTPStatus
from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_cant_comment(client, news):
    """
    Тестирует, что анонимный пользователь
    не может отправить комментарий.
    """
    url = reverse('news:detail', args=[news.pk])
    response = client.post(url, {'text': 'Test comment'})
    assert Comment.objects.count() == 0
    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db
def test_reader_can_submit_comment(reader_client, news):
    """
    Тестирует, что авторизованный пользователь
    может отправить комментарий.
    """
    url = reverse('news:detail', args=[news.pk])
    response = reader_client.post(url, {'text': 'Test comment'})
    assert Comment.objects.count() == 1
    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db
def test_comment_with_bad_words(reader_client, news):
    """Тестирует, что комментарий с запрещенными словами не добавляется."""
    url = reverse('news:detail', args=[news.pk])
    response = reader_client.post(url, {'text': BAD_WORDS})
    assert Comment.objects.count() == 0
    form_errors = response.context['form'].errors
    assert 'text' in form_errors
    assert WARNING in form_errors['text']


@pytest.mark.django_db
def test_author_edit_delete_comment(author_client, comment):
    """
    Тестирует, что автор комментария может
    редактировать и удалять свой комментарий.
    """
    edit_url = reverse('news:edit', args=[comment.pk])
    delete_url = reverse('news:delete', args=[comment.pk])
    response_edit = author_client.post(edit_url, {'text': 'Updated text'})
    response_delete = author_client.post(delete_url)
    assert response_edit.status_code == HTTPStatus.FOUND
    assert response_delete.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(pk=comment.pk).exists()


@pytest.mark.django_db
def test_reader_cant_edit_delete_comment(reader_client, comment):
    """
    Тестирует, что обычный пользователь не может
    редактировать или удалять комментарии других пользователей.
    """
    edit_url = reverse('news:edit', args=[comment.pk])
    delete_url = reverse('news:delete', args=[comment.pk])
    response_edit = reader_client.post(edit_url, {'text': 'Updated text'})
    response_delete = reader_client.post(delete_url)
    assert response_edit.status_code == HTTPStatus.NOT_FOUND
    assert response_delete.status_code == HTTPStatus.NOT_FOUND
