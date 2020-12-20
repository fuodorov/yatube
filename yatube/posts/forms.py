from django.forms import ModelForm

from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group")
        labels = {"text": "Текст заметки*", "group": "Группа"}
        help_texts = {"text": (
            "Напишите здесь текст заметки. "
            "Это могут быть ваши мысли или просто наблюдения."),
            "group": (
            "Выберите группу, к которой будет принадлежать ваш пост.")
            }
