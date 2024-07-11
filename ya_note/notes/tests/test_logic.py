from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create(username='BIBA')
        cls.url = reverse('notes:add')
        cls.author_client = Client()
        cls.author_client.force_login(cls.user)
        cls.form_data = {
            'title': 'New Note',
            'text': 'Some text',
            'slug': 'new-note'
        }

    def test_anonymous_user_cant_create_note(self):
        """Аннонимный пользователь не может создавать заметки."""
        initial_count = Note.objects.count()
        self.client.post(self.url, data=self.form_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, initial_count)

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        initial_count = Note.objects.count()
        response = self.author_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))

        self.assertEqual(Note.objects.count(), initial_count + 1)
        note = Note.objects.last()
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])

    def test_slug_notes(self):
        """Пользователь не может создавать заметки с одинаковыми slug."""
        note = Note.objects.create(
            author=self.user,
            title='Note title',
            text='New next',
            slug='new-note'
        )
        initial_count = Note.objects.count()
        response = self.author_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=f'{note.slug}{WARNING}'
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, initial_count)

    def test_slug_auto_generation(self):
        """Slug формируется автоматически, если он не заполнен."""
        initial_count = Note.objects.count()
        del self.form_data['slug']
        response = self.author_client.post(
            self.url,
            data=self.form_data
        )
        self.assertRedirects(response, reverse('notes:success'))

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, initial_count + 1)

        note = Note.objects.get(title=self.form_data['title'])
        self.assertEqual(note.slug, slugify(self.form_data['title']))


class TestNoteEditDelete(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='AMOGUS')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='WILLI')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author
        )
        cls.url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')
        cls.form_data = {
            'title': 'New Note',
            'text': 'Some text',
            'slug': 'new-note'
        }

    def test_author_note_delete(self):
        """Автор может удалить свою заметку."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_reader_cant_note_delete(self):
        """Читатель не может удалить чужую заметку."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_note_edit(self):
        """Автор может изменять свои заметки."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])

    def test_reader_cant_edit_note(self):
        """Читалеть не может редактировать чужую заметку."""
        original_slug = self.note.slug
        original_title = self.note.title
        original_text = self.note.text
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.slug, original_slug)
        self.assertEqual(self.note.title, original_title)
        self.assertEqual(self.note.text, original_text)
