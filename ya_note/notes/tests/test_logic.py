from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create(username='Читатель')
        cls.author = User.objects.create(username='Автор')
        cls.form_data_note = {
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'unique',
            'author': cls.author
        }
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'unique'
        }

    def test_anonymous_cant_create_note(self):
        '''Анонимный польз-тель не может создать заметку.'''
        url = reverse('notes:add')
        self.client.post(url, data=self.form_data_note)
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={url}'
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_can_create_note(self):
        '''Авторизованный польз-тель может создать заметку.'''
        self.client.force_login(self.author)
        url = reverse('notes:add')
        self.client.post(url, data=self.form_data_note)
        self.assertEqual(Note.objects.count(), 1)

    def test_not_unique_slug(self):
        '''Невозможно создать две заметки с одинаковым slug.'''
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        response = self.client.post(url, data=self.form_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.form_data_note['slug'] + WARNING)
        )

    def test_empty_slug(self):
        '''Создание заметки без slug - slug формируется автоматически.'''
        self.client.force_login(self.author)
        self.form_data.pop('slug')
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        assert new_note.slug == expected_slug
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_delete_note(self):
        '''Автор может удалить свою запись.'''
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data_note)
        url = reverse('notes:delete', args=(self.form_data_note['slug'],))
        response = self.client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_author_can_edit_note(self):
        '''Автор может редактировать свою запись.'''
        self.client.force_login(self.author)
        url = reverse('notes:add')
        self.client.post(url, data=self.form_data_note)
        url = reverse('notes:edit', args=(self.form_data_note['slug'],))
        response = self.client.post(url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 1)
        update_note = Note.objects.get()
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(update_note.title, self.form_data['title'])

    def test_user_cant_delete_another_note(self):
        '''Польз-ель не может удалить чужую запись.'''
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data_note)
        self.client.force_login(self.reader)
        url = reverse('notes:delete', args=(self.form_data_note['slug'],))
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_user_cant_edit_another_note(self):
        '''Польз-ель не может ред-ть чужую запись.'''
        self.client.force_login(self.author)
        url = reverse('notes:add')
        self.client.post(url, data=self.form_data_note)
        self.client.force_login(self.reader)
        url = reverse('notes:edit', args=(self.form_data_note['slug'],))
        response = self.client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
