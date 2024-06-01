from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUp(cls):
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.auth_user_client = Client()
        cls.auth_user_client.force_login(cls.auth_user)

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(
            username='Author',
        )
        cls.auth_user = User.objects.create(
            username='Random user',
        )
        cls.note = Note.objects.create(
            title='Title',
            text='Text',
            author=cls.author,
        )

    def test_not_authorized_user_has_no_form(self):
        urls = (
            ('notes:edit', self.note.slug),
            ('notes:detail', self.note.slug),
        )

        for name, kwargs in urls:
            with self.subTest(name=name):
                response = self.client.get(name, kwargs=kwargs)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
                self.assertNotIn('form', response.context)

    def test_create_note_form_available_for_authorized_users(self):
        url = reverse('notes:add')
        response = self.auth_user_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_edit_note_form_available_for_author(self):
        url = reverse('notes:edit', kwargs={'slug': self.note.slug})
        response = self.author_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('note', response.context)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_note_in_list_for_author(self):
        url = reverse('notes:list')
        response = self.author_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        object_list = response.context['object_list']
        assert self.note in object_list

    def test_note_not_in_list_for_authorized_user(self):
        url = reverse('notes:list')
        response = self.auth_user_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        object_list = response.context['object_list']
        assert self.note not in object_list
