from http import HTTPStatus
from django.urls import reverse
import pytest


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_page_availability_for_anonymous_user(client, name):
    """
    Тестирует, что страницы главной, логина, логаута и регистрации
    доступны для анонимного пользователя.
    """
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_news_detail_page_for_anonymous_user(client, news):
    """
    Тестирует, что страница с подробной информацией о новости
    доступна для анонимного пользователя.
    """
    url = reverse('news:detail', args=[news.pk])
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_comment_edit_delete_pages_for_author(author_client, comment):
    """
    Тестирует, что автор комментария может получить доступ к страницам
    редактирования и удаления своего комментария.
    """
    edit_url = reverse('news:edit', args=[comment.pk])
    delete_url = reverse('news:delete', args=[comment.pk])
    response_edit = author_client.get(edit_url)
    response_delete = author_client.get(delete_url)
    assert response_edit.status_code == HTTPStatus.OK
    assert response_delete.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('edit', 'delete')
)
def test_anonymous_user_redirect_to_login(client, comment, name):
    """
    Тестирует, что анонимный пользователь при попытке доступа
    к страницам редактирования и удаления комментария
    перенаправляется на страницу логина.
    """
    url = reverse(f'news:{name}', args=[comment.pk])
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url.startswith(reverse('users:login'))


@pytest.mark.django_db
def test_reader_cant_edit_delete_comment(reader_client, comment):
    """
    Тестирует, что обычный пользователь не может получить доступ
    к страницам редактирования и удаления чужого комментария.
    """
    edit_url = reverse('news:edit', args=[comment.pk])
    delete_url = reverse('news:delete', args=[comment.pk])
    response_edit = reader_client.get(edit_url)
    response_delete = reader_client.get(delete_url)
    assert response_edit.status_code == HTTPStatus.NOT_FOUND
    assert response_delete.status_code == HTTPStatus.NOT_FOUND
