import shutil
import tempfile
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
#from django.core.cache import cache
from ..models import Group, Post, Comment, Follow

TEST_OF_POST: int = 13
User = get_user_model()
FIRST_OF_POSTS: int = 10
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

class PaginatorViewsTest(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='author')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание'
        )
        bulk_posts: list = []
        for i in range(TEST_OF_POST):
            bulk_posts.append(Post(
                text=f'Тестовый текст {i}',
                group=self.group,
                author=self.user)
            )
        Post.objects.bulk_create(bulk_posts)

    def test_number_of_posts_per_page(self):
        '''Проверка количества постов на первой и второй страницах. '''
        pages: tuple = (
            reverse('posts:index'),
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}),
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'})
        )
        for page in pages:
            response1 = self.guest_client.get(page)
            response2 = self.guest_client.get(page + '?page=2')
            count_posts1 = len(
                response1.context['page_obj'])
            count_posts2 = len(
                response2.context['page_obj'])
            error_name1 = (
                f'Ошибка: {count_posts1} постов,'
                f' должно {FIRST_OF_POSTS}'
            )
            error_name2 = (
                f'Ошибка: {count_posts2} постов,'
                f'должно {TEST_OF_POST - FIRST_OF_POSTS}'
            )
            self.assertEqual(
                count_posts1,
                FIRST_OF_POSTS,
                error_name1
            )
            self.assertEqual(
                count_posts2,
                TEST_OF_POST - FIRST_OF_POSTS,
                error_name2
            )

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author1')
        cls.user2 = User.objects.create_user(username='author2')
    
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
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group')
        self.post = Post.objects.create(
            text='Тестовый текст',
            group=self.group,
            author=self.user,
            image=self.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_views_correct_template(self):
        '''URL-адрес использует соответствующий шаблон.'''
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug':
                            f'{self.group.slug}'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username':
                            f'{self.user.username}'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post.id}'}):
                        'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id':
                            self.post.id}): 'posts/create_post.html'}
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template, 'ERROR_IN_THE_TEMPLATE')

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        post_text_0 = {
            response.context['post'].text: 'Тестовый пост',
            response.context['post'].group: self.group,
            response.context['post'].author: PostViewsTest.user
        }
        for value, expected in post_text_0.items():
            self.assertEqual(post_text_0[value], expected)

    def test_post_create_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertTrue(response.context.get('is_edit'))

    def test_post_added_correct(self):
        """Пост при создании добавлен корректно"""
        post = Post.objects.create(
            text='Тестовый текст проверка добавления поста',
            author=self.user,
            group=self.group,
            image=self.uploaded
        )
        response_index = self.authorized_client.get(
            reverse('posts:index'))
        response_group = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}))
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))
        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        profile = response_profile.context['page_obj']
        self.assertIn(post, index, 'поста нет на главной')
        self.assertIn(post, group, 'поста нет в профиле')
        self.assertIn(post, profile, 'поста нет в группе')
        various_group = response_group.context['group']
        various_profile = response_profile.context['author']
        self.assertEqual(post.group, various_group, ' нет переменной группы')
        self.assertEqual(
            post.author,
            various_profile, ' нет переменной автора'
        )

    def test_post_added_correct_user2(self):
        """Пост при создании не добавляется другому пользователю
        Но виден на главной странице и в группе"""
        group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_group2'
        )
        posts_count = Post.objects.filter(group=self.group).count()
        post = Post.objects.create(
            text='Тестовый пост от другого автора',
            author=self.user2,
            group=group2)
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))
        group = Post.objects.filter(group=self.group).count()
        profile = response_profile.context['page_obj']
        self.assertEqual(group, posts_count, 'поста нет в другой группе')
        self.assertNotIn(
            post, profile,
            'поста нет в группе другого пользователя'
        )

# def test_cache_context(self):
#         '''Проверка кэширования страницы index'''
#         before_create_post = self.authorized_client.get(
#             reverse('posts:index'))
#         first_item_before = before_create_post.content
#         Post.objects.create(
#             author=self.user,
#             text='Проверка кэша',
#             group=self.group)
#         after_create_post = self.authorized_client.get(reverse('posts:index'))
#         first_item_after = after_create_post.content
#         self.assertEqual(first_item_after, first_item_before)
#         cache.clear()
#         after_clear = self.authorized_client.get(reverse('posts:index'))
#         self.assertNotEqual(first_item_after, after_clear)

# от однокурсников, проверить
# def test_cache_index(self):
#         """Проверка хранения и очищения кэша для index."""
#         response = self.authorized_author.get(reverse('posts:index'))
#         posts = response.content
#         Post.objects.create(
#             text='test_new_post',
#             author=self.author,
#         )
#         response_old = self.authorized_author.get(reverse('posts:index'))
#         old_posts = response_old.content
#         self.assertEqual(old_posts, posts)
#         cache.clear()
#         response_new = self.authorized_author.get(reverse('posts:index'))
#         new_posts = response_new.content
#         self.assertNotEqual(old_posts, new_posts)

class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author1')
        cls.user2 = User.objects.create_user(username='author2')
        cls.author = User.objects.create_user(username='someauthor')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

    def test_post_when_subscribing(self):
        '''Доступность постов нужного автора.
        Увеличение подписок автора'''
        count_follow = Follow.objects.filter(
            user=FollowViewsTest.user).count()
        data_follow = {'user': FollowViewsTest.user,
                    'author': FollowViewsTest.author}
        url_redirect = reverse(
            'posts:profile',
            kwargs={'username': FollowViewsTest.author.username})
        response = self.authorized_client.post(
            reverse('posts:profile_follow', kwargs={
                'username': FollowViewsTest.author.username}),
            data=data_follow, follow=True)
        new_count_follow = Follow.objects.filter(
            user=FollowViewsTest.user).count()
        self.assertTrue(
            Follow.objects.filter(
                        user=FollowViewsTest.user,
                        author=FollowViewsTest.author).exists())
        self.assertRedirects(response, url_redirect)
        self.assertEqual(count_follow + 1, new_count_follow)

    def test_no_subscription_no_post(self):
        '''Недоступность постов при отсутствии подписки на автора.
        Увеличения подписок нет'''
        count_follow = Follow.objects.filter(
            user=FollowViewsTest.user).count()
        data_follow = {'user': FollowViewsTest.user,
                    'author': FollowViewsTest.author}
        url_redirect = ('/auth/login/?next=/profile/'
                        f'{self.author.username}/unfollow/')
        response = self.guest_client.post(
            reverse('posts:profile_unfollow', kwargs={
                'username': FollowViewsTest.author}),
            data=data_follow, follow=True)
        new_count_follow = Follow.objects.filter(
            user=FollowViewsTest.user).count()
        self.assertFalse(Follow.objects.filter(
            user=FollowViewsTest.user,
            author=FollowViewsTest.author).exists())
        self.assertRedirects(response, url_redirect)
        self.assertEqual(count_follow, new_count_follow)

    def test_displaying_new_posts(self):
        '''У подписанного на избранного автора появляется новый пост.
        У неподписанного на выбранного автора новый пост отсутствует.'''
        new_post_follower = Post.objects.create(
            author=FollowViewsTest.author,
            text='Текстовый текст')
        Follow.objects.create(
            user=FollowViewsTest.user,
            author=FollowViewsTest.author)
        response_follower = self.authorized_client.get(
            reverse('posts:follow_index'))
        new_posts = response_follower.context['page_obj']
        self.assertIn(new_post_follower, new_posts)


class CommentTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author1')
        cls.user2 = User.objects.create_user(username='author2')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group')
        self.post = Post.objects.create(
            text='Тестовый текст',
            group=self.group,
            author=self.user)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с
        правильным контекстом комментария."""
        self.comment = Comment.objects.create(
            post_id=self.post.id,
            author=self.user,
            text='Тестовый коммент')
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        comments = {response.context['comments'][0].text: 'Тестовый коммент',
                    response.context['comments'][0].author: self.user.username
                    }
        for value, expected in comments.items():
            self.assertEqual(comments[value], expected)
        self.assertTrue(response.context['form'], 'форма получена')
