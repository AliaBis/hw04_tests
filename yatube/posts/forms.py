from django.forms import ModelForm
from django.core.exceptions import ValidationError
from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group']
        help_text = {
            'text': 'Текст поста',
            'group': 'Группа'
        }

    def clean_data(self):
        text = self.cleaned_data['text']
        if not text:
            raise ValidationError('Пост не может быть без текста')
        return text
