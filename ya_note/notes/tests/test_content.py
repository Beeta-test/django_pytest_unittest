from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm


User = get_user_model()


class TestContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Создает тестовых пользователей и заметку."""
        cls.author = User.objects.create(username='BIBA')
        cls.reader = User.objects.create(username='BOBA')
        cls.author_client = Client()
        cls.reader_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author
        )

    def test_note_in_object_list_and_visibility(self):
        """Проверяет, что заметка отображается в object_list
        только для соответствующего авторизованного пользователя.
        """
        test_cases = [
            (self.author_client, True),
            (self.reader_client, False),
        ]

        for client, expected_in_list in test_cases:
            with self.subTest(
                client=client,
                expected_in_list=expected_in_list
            ):
                url = reverse('notes:list')
                response = client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                object_list = response.context['object_list']
                self.assertIs(self.note in object_list, expected_in_list)

    def test_forms_in_create_and_edit_pages(self):
        """Проверяет, что на страницы создания
        и редактирования заметки передаются формы.
        """
        urls = (
            reverse('notes:add'),
            reverse('notes:edit', args=(self.note.slug,)),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertIn('form', response.context)
                form_obj = response.context['form']
                self.assertIsInstance(form_obj, NoteForm)
