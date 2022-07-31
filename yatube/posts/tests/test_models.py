from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Post, Group

User = get_user_model()
STRING_LENGTH = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовое описание поста',
        )

    def test_models_have_correct_str_post(self):
        '''Проверка длины __str__ post'''
        INCORRECT_OUTPUT = f"Вывод не имеет {STRING_LENGTH} символов"
        self.assertEqual(
            self.post.__str__(),
            self.post.text[:STRING_LENGTH],
            INCORRECT_OUTPUT
        )

    def test_title_label(self):
        '''Проверка заполнения verbose_name'''
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'group': 'Группа',
            'author': 'Автор',
            'image': 'Картинка'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                INVALID_VALUE = f'Поле {field}'
                f'ожидало значение {expected_value}'
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value, INVALID_VALUE)

    def test_title_help_text(self):
        '''Проверка заполнения help_text'''
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, относительно поста',
            'image': 'Картинка'
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                INVALID_VALUE = f'Поле {field}'
                f'ожидало значение {expected_value}'
                self.assertEqual(
                    self.post._meta.get_field(field).help_text,
                    expected_value, INVALID_VALUE)


class GroupModelTest(TestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Группа',
            slug='Адрес',
            description='описание',
        )

    def test_models_have_correct_title_names(self):
        '''Проверка заполнения str group'''
        group = GroupModelTest.group
        title = group.__str__()
        self.assertEqual(title, group.title)

    def test_title_label(self):
        '''Проверка заполнения verbose_name'''
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Жанр',
            'slug': 'Параметр',
            'description': 'Содержание'
            }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

    def test_title_help_text(self):
        '''Проверка заполнения help_text'''
        group = GroupModelTest.group
        field_help_texts = {
            'title': 'Укажите жанр',
            'slug': 'Адрес',
            'description': 'Содержание'
            }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value)