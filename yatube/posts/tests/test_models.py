from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Post

User = get_user_model()
LEN_OF_POSTS = 15

class PostModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовое описание поста',
        )

    def test_models_have_correct_object_names(self):
        '''Проверка длины __str__ post'''
        error_name = f"Вывод не имеет {LEN_OF_POSTS} символов"
        self.assertEqual(self.post.__str__(),
                        self.post.text[:LEN_OF_POSTS],
                        error_name)

    def test_title_label(self):
        '''Проверка заполнения verbose_name'''
        field_verboses = {'text': 'Текст поста',
                        'pub_date': 'Дата публикации',
                        'group': 'Группа',
                        'author': 'Автор'}
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                error_name = f'Поле {field} ожидало значение {expected_value}'
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value, error_name)

    def test_title_help_text(self):
        '''Проверка заполнения help_text'''
        field_help_texts = {'text': 'Введите текст поста',
                            'group': 'Группа для размещения поста'}
                            
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                error_name = f'Поле {field} ожидало значение {expected_value}'
                self.assertEqual(
                    self.post._meta.get_field(field).help_text,
                    expected_value, error_name)