from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

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
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='unique',
            author=cls.author
        )

    def test_note_in_list_for_author(self):
        '''Заметка передаётся на страницу со списком заметок.'''
        url = reverse('notes:list')
        response = self.author_client.get(url)
        notes = response.context['object_list']
        self.assertIn(self.note, notes)

    def test_note_not_in_list_for_another_user(self):
        '''Заметки нет в списке другого польз-ля.'''
        url = reverse('notes:list')
        response = self.reader_client.get(url)
        notes = response.context['object_list']
        self.assertNotIn(self.note, notes)

    def test_create_note_page_contains_form(self):
        '''На страницы создания и ред-ния заметки передаются формы.'''
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
