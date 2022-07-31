from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Post, Group, Comment
import shutil
from django.conf import settings
import tempfile

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    def setUp(self):
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Описание')
    
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_create_post(self):
        '''Проверка создания поста'''
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small_2.gif',
            content=self.small_gif,
            content_type='image/gif')
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст',
            'group': self.group.id,
            'image': self.uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:create_post'),
            data=form_data,
            follow=True
        )
        POST_NOT_CREATED = 'Пост не создан'
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Post.objects.filter(
            text='Текст записанный в форму',
            image=f'posts/{self.uploaded}',
            group=self.group.id,
            author=self.user
        ).exists(), POST_NOT_CREATED
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count + 1,
            POST_NOT_CREATED
        )

    def test_can_edit_post(self):
        '''Проверка прав редактирования'''
        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
            image=self.uploaded
        )
        self.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test-group2',
            description='Описание')
        form_data = {
            'text': 'Текст',
            'group': self.group2.id
        }
        NOT_ALLOWED = 'У пользователя недостаточно прав'
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Post.objects.filter(
            id=self.post.id,
            group=self.group2.id,
            author=self.user,
            image=f'posts/{self.uploaded}',
            pub_date=self.post.pub_date
        ).exists(), NOT_ALLOWED)
        self.assertNotEqual(self.post.text, form_data['text'], NOT_ALLOWED)
        self.assertNotEqual(self.post.group, form_data['group'], NOT_ALLOWED)

class CommentFormTest(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Описание')
        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group)
        self.comment = Comment.objects.create(
            post_id=self.post.id,
            author=self.user,
            text='Тестовый коммент')

    def test_create_comment(self):
        '''Проверка создания комментария'''
        comment_count = Comment.objects.count()
        form_data = {'post_id': self.post.id,
                    'text': 'Тестовый коммент2'}
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}),
            data=form_data, follow=True)
        error_name1 = 'Данные комментария не совпадают'
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Comment.objects.filter(
                        text='Тестовый коммент2',
                        post=self.post.id,
                        author=self.user
                        ).exists(), error_name1)
        self.assertEqual(
            Comment.objects.count(),
            comment_count + 1,
            'THERE_IS_NO_COMMENT')

    def test_no_edit_comment(self):
        '''Проверка запрета комментирования неавторизованого пользователя'''
        posts_count = Comment.objects.count()
        form_data = {'text': 'Тестовый коммент2'}
        response = self.guest_client.post(
            reverse('posts:add_comment',
            kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(
            Comment.objects.count(),
            posts_count + 1,
            'ERRONEOUS_COMMENT')

    def test_comment_null(self):
        '''Запрет пустого комментария'''
        posts_count = Comment.objects.count()
        form_data = {'text': ''}
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(
            Comment.objects.count(),
            posts_count + 1,
            'ERRONEOUS_COMMENT')    
