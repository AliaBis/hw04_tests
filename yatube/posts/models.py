from django.contrib.auth import get_user_model
from django.db import models
from core.models import CreatedModel

User = get_user_model()
LEN_OF_POSTS = 15


class Post(CreatedModel):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, относительно поста'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )

    def __str__(self):
        return self.text[:LEN_OF_POSTS]


class Meta:
    verbose_name = 'Пост'
    verbose_name_plural = 'Посты'
    ordering = ('-pub_date', 'author')


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Жанр',
        help_text='Укажите жанр'
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name='Параметр',
        help_text='Адрес'
    )
    description = models.TextField(
        verbose_name='Содержание',
        help_text='Содержание'
    )

    def __str__(self):
        return self.title


class Meta:
    verbose_name = 'Жанр'
    verbose_name_plural = 'Жанры'
    ordering = ('title',)
