from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name ='Название группы', 
        max_length=200
        )
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name ='Тестовое описание')

    def __str__(self):
        return self.title
class Meta:
    verbose_name = 'Название группы'
    ordering = ('title',)

class Post(models.Model):
    text = models.TextField(
    help_text='Введите текст поста', verbose_name ='Текст поста')
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name = 'Дата публикации' )
    author = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='posts',
        help_text='Группа для размещения поста', verbose_name='Группа')

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Post'
    def __str__(self):
        return self.text[:15]


