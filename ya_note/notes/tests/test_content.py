from http import HTTPStatus

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestContent(TestCase):
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

    def test_note_in_object_list(self):
        """Проверяет, что отдельная заметка передаётся
        на страницу со списком заметок в object_list.
        """
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(self.note, response.context['object_list'])

    def test_note_not_in_other_user_list(self):
        """Проверяет, что заметки одного пользователя
        не попадают в список заметок другого пользователя.
        """
        self.client.force_login(self.reader)
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotIn(self.note, response.context['object_list'])

    def test_forms_in_create_and_edit_pages(self):
        """Проверяет, что на страницы создания
        и редактирования заметки передаются формы.
        """
        self.client.force_login(self.author)
        urls = (
            reverse('notes:add'),
            reverse('notes:edit', args=(self.note.slug,)),
        )
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertIn('form', response.context)
