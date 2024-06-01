from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUp(cls):
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='User')
        cls.data_with_slug = {
            'title': 'Title',
            'text': 'Text',
            'slug': 'Slug',
        }
        cls.data_without_slug = {
            'title': 'Title',
            'text': 'Text',
        }
        cls.url = reverse('notes:add')
        cls.redirect_url = reverse('notes:success')

    def check_note_equal(self, note: Note, data: dict, user):
        self.assertEqual(note.title, data['title'])
        self.assertEqual(note.text, data['text'])
        self.assertEqual(note.slug, data['slug'])
        self.assertEqual(note.author, user)

    def test_unauthorized_user_cant_create_note(self):
        self.client.post(self.url, data=self.data_with_slug)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_authorized_user_can_create_note(self):
        response = self.auth_client.post(self.url, data=self.data_with_slug)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.check_note_equal(note, self.data_with_slug, self.user)

    def test_authorized_user_cant_use_same_slug(self):
        self.note = Note.objects.create(
            title='Title',
            text='Text',
            author=self.user,
        )
        new_data = {
            'title': 'Title2',
            'text': 'Text2',
            'author': self.user,
            'slug': self.note.slug,
        }
        response = self.auth_client.post(self.url, data=new_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(self.note.slug + WARNING),
        )
        notes_count = Note.objects.count()
        self.assertNotEqual(notes_count, 2)

    def test_authorized_user_dont_fill_in_slug_field(self):
        response = self.auth_client.post(self.url, self.data_without_slug)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        made_up_slug = slugify(self.data_without_slug['title'])
        self.assertEqual(note.slug, made_up_slug)


class TestNoteEditdelete(TestCase):

    @classmethod
    def setUp(cls):
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.auth_user_client = Client()
        cls.auth_user_client.force_login(cls.auth_user)

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.auth_user = User.objects.create(username='Random user')
        cls.note = Note.objects.create(
            title='Title',
            text='Text',
            author=cls.author,
            slug='Slug',
        )
        cls.new_data = {
            'title': 'Updated title',
            'text': 'Updated text',
            'slug': 'Updated_slug',
        }
        cls.note_url = reverse(
            'notes:detail',
            kwargs={'slug': cls.note.slug}
        )
        cls.note_delete_url = reverse(
            'notes:delete',
            kwargs={'slug': cls.note.slug}
        )
        cls.note_edit_url = reverse(
            'notes:edit',
            kwargs={'slug': cls.note.slug}
        )
        cls.redirect_url = reverse('notes:success')

    def check_note_equal(self, note: Note, data: dict):
        self.assertEqual(note.title, data['title'])
        self.assertEqual(note.text, data['text'])
        self.assertEqual(note.slug, data['slug'])

    def check_note_not_equal(self, note: Note, data: dict):
        self.assertNotEqual(note.title, data['title'])
        self.assertNotEqual(note.text, data['text'])
        self.assertNotEqual(note.slug, data['slug'])

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.note_edit_url, self.new_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.redirect_url)
        self.note.refresh_from_db()
        self.check_note_equal(self.note, self.new_data)

    def test_authorized_user_cant_edit_note_of_another_author(self):
        response = self.auth_user_client.post(
            self.note_edit_url,
            self.new_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.check_note_not_equal(self.note, self.new_data)

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.note_delete_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_author_cant_delete_note_of_another_author(self):
        response = self.auth_user_client.delete(self.note_delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
