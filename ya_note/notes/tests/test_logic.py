from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

url_add = reverse('notes:add')
User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.form_data_note = {
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'unique',
        }
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'unique'
        }

    def test_anonymous_cant_create_note(self):
        '''Анонимный польз-тель не может создать заметку.'''
        note_before = Note.objects.count()
        self.client.post(url_add, data=self.form_data_note)
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={url_add}'
        response = self.client.get(url_add)
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Note.objects.count(), note_before)

    def test_user_can_create_note(self):
        '''Авторизованный польз-тель может создать заметку.'''
        note_before = Note.objects.count()
        self.author_client.post(url_add, data=self.form_data_note)
        self.assertEqual(Note.objects.count(), note_before + 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.form_data_note['text'])
        self.assertEqual(note.title, self.form_data_note['title'])
        self.assertEqual(note.slug, self.form_data_note['slug'])
        self.assertEqual(note.author, self.author)

    def test_not_unique_slug(self):
        '''Невозможно создать две заметки с одинаковым slug.'''
        response = self.author_client.post(url_add, data=self.form_data)
        response = self.author_client.post(url_add, data=self.form_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.form_data_note['slug'] + WARNING)
        )

    def test_empty_slug(self):
        '''Создание заметки без slug - slug формируется автоматически.'''
        note_before = Note.objects.count()
        self.form_data.pop('slug')
        response = self.author_client.post(url_add, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), note_before + 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        assert new_note.slug == expected_slug
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_delete_note(self):
        '''Автор может удалить свою запись.'''
        note_before = Note.objects.count()
        response = self.author_client.post(url_add, data=self.form_data_note)
        url = reverse('notes:delete', args=(self.form_data_note['slug'],))
        response = self.author_client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), note_before)

    def test_author_can_edit_note(self):
        '''Автор может редактировать свою запись.'''
        self.author_client.post(url_add, data=self.form_data_note)
        note_before = Note.objects.count()
        url = reverse('notes:edit', args=(self.form_data_note['slug'],))
        response = self.author_client.post(url, data=self.form_data)
        self.assertEqual(Note.objects.count(), note_before)
        update_note = Note.objects.get()
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(update_note.title, self.form_data['title'])
        self.assertEqual(update_note.slug, self.form_data['slug'])
        self.assertEqual(update_note.text, self.form_data['text'])
        self.assertEqual(update_note.author, self.author)

    def test_user_cant_delete_another_note(self):
        '''Польз-ель не может удалить чужую запись.'''
        response = self.author_client.post(url_add, data=self.form_data_note)
        note_before = Note.objects.count()
        url = reverse('notes:delete', args=(self.form_data_note['slug'],))
        response = self.reader_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), note_before)

    def test_user_cant_edit_another_note(self):
        '''Польз-ель не может ред-ть чужую запись.'''
        self.author_client.post(url_add, data=self.form_data_note)
        note_before = Note.objects.count()
        url = reverse('notes:edit', args=(self.form_data_note['slug'],))
        response = self.reader_client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), note_before)
        update_note = Note.objects.get()
        self.assertEqual(update_note.title, self.form_data_note['title'])
        self.assertEqual(update_note.text, self.form_data_note['text'])
        self.assertEqual(update_note.slug, self.form_data_note['slug'])
        self.assertEqual(update_note.author, self.author)
