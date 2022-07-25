from django.forms import ModelForm
from django.core.exceptions import ValidationError
from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        help_text = {
            'text': 'Текст поста',
            'group': 'Группа',
            'image': 'Изображение'
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text', )
    
    def clean_data(self):
        text = self.cleaned_data['text']
        if not text:
            raise ValidationError('Пост не может быть без текста')
        return text
