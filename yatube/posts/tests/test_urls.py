from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовое описание поста')
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание')

    def test_urls_guest_client(self):
        """Доступ неавторизованного пользователя"""
        pages: tuple = ('/',
                        f'/group/{self.group.slug}/',
                        f'/profile/{self.user.username}/',
                        f'/posts/{self.post.id}/')
        for page in pages:
            response = self.guest_client.get(page)
            NOT_ALLOWED = f'Ошибка: нет доступа до страницы {page}'
            self.assertEqual(response.status_code, HTTPStatus.OK, NOT_ALLOWED)

    def test_urls_redirect_guest_client(self):
        """Редирект неавторизованного пользователя"""
        url1 = '/auth/login/?next=/create/'
        url2 = f'/auth/login/?next=/posts/{self.post.id}/edit/'
        pages: dict = {
            '/create/': url1,
            f'/posts/{self.post.id}/edit/': url2
        }
        for page, value in pages.items():
            response = self.guest_client.get(page)
            self.assertRedirects(response, value)

    def test_urls_authorized_client(self):
        """Доступ авторизованного пользователя"""
        pages: tuple = (
            '/create/',
            f'/posts/{self.post.id}/edit/')
        for page in pages:
            response = self.authorized_client.get(page)
            NOT_ALLOWED = f'Ошибка: нет доступа до страницы {page}'
            self.assertEqual(response.status_code, HTTPStatus.OK, NOT_ALLOWED)

    def test_urls_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names: dict = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html'
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                INVALID_TEMPLATE = f'Ошибка: {adress} ожидал шаблон {template}'
                self.assertTemplateUsed(response, template, INVALID_TEMPLATE)

    def test_404(self):
        """Запрос несуществующей страницы"""
        response = self.guest_client.get('/test-no-popular', follow=True)
        NO_URL = 'Ошибка: unexisting_url не работает'
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND,
            NO_URL
        )
