from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(
            username='Author',
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.auth_user = User.objects.create(
            username='Random user',
        )
        cls.auth_user_client = Client()
        cls.auth_user_client.force_login(cls.auth_user)
        cls.note = Note.objects.create(
            title='Title',
            text='Text',
            author=cls.author,
        )

    def test_pages_availability_for_everyone(self):
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

    def test_availability_for_authorized_user(self):
        urls = (
            'notes:add',
            'notes:list',
            'notes:success',
        )

        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.auth_user_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_delete_detail(self):
        urls = (
            ('notes:edit', self.note.slug),
            ('notes:detail', self.note.slug),
            ('notes:delete', self.note.slug),
        )

        user_statuses = (
            (self.author, self.author_client, HTTPStatus.OK),
            (self.auth_user, self.auth_user_client, HTTPStatus.NOT_FOUND),
        )

        for user, client, status in user_statuses:
            for name, kwargs in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, kwargs={'slug': kwargs})
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects_for_unauthorized_user(self):
        login_url = settings.LOGIN_URL
        urls = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:edit', {'slug': self.note.slug}),
            ('notes:detail', {'slug': self.note.slug}),
            ('notes:delete', {'slug': self.note.slug}),
        )

        for name, kwargs in urls:
            with self.subTest(name=name):
                url = reverse(name, kwargs=kwargs)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
