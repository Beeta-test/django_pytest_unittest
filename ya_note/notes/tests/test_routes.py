from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Создает тестовых пользователей и заметку."""
        cls.author = User.objects.create(username='BIBA')
        cls.reader = User.objects.create(username='BOBA')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author
        )

    def setUp(self):
        """Логинит клиенты для каждого теста."""
        super().setUp()
        self.author_client = Client()
        self.reader_client = Client()
        self.author_client.force_login(self.author)
        self.reader_client.force_login(self.reader)

    def test_availability_page(self):
        """Проверяет доступность страниц для анонимного пользователя."""
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_authenticated_user(self):
        """Проверяет доступность страниц для
        аутентифицированного пользователя.
        """
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        """
        Проверяет доступность страниц редактирования, удаления и просмотра
        заметки для автора и другого пользователя.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND)
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """
        Проверяет перенаправление анонимного пользователя на страницу логина
        при попытке доступа к страницам.
        """
        login_url = reverse('users:login')
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
