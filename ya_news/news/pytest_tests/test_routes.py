from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_lazyfixture import lazy_fixture
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:detail', lazy_fixture('pk_news')),
    ),
)
def test_page_availability_for_anonymous_user(
    client, name, args
):
    """
    Тестирует, что страницы главной, логина, логаута и регистрации
    доступны для анонимного пользователя.
    """
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', lazy_fixture('pk_comment')),
        ('news:delete', lazy_fixture('pk_comment')),
    )
)
def test_comment_edit_delete_pages_for_author(author_client, name, args):
    """
    Тестирует, что автор комментария может получить доступ к страницам
    редактирования и удаления своего комментария.
    """
    url = reverse(name, args=args)
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', lazy_fixture('pk_comment')),
        ('news:delete', lazy_fixture('pk_comment'))
    )
)
def test_anonymous_user_redirect_to_login(client, args, name):
    """
    Тестирует, что анонимный пользователь при попытке доступа
    к страницам редактирования и удаления комментария
    перенаправляется на страницу логина.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', lazy_fixture('pk_comment')),
        ('news:delete', lazy_fixture('pk_comment')),
    )
)
def test_reader_cant_edit_delete_comment(reader_client, name, args):
    """
    Тестирует, что обычный пользователь не может получить доступ
    к страницам редактирования и удаления чужого комментария.
    """
    url = reverse(name, args=args)
    response = reader_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
