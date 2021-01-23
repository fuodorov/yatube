from django.contrib.auth import get_user_model
from django.db import models

from posts.settings import LETTERS_PER_STR

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name="Название группы: ",
        max_length=200,
        help_text="Напишите название группы."
    )
    slug = models.SlugField(
        verbose_name="Ключ для составления адреса: ",
        max_length=100,
        unique=True,
        help_text="Укажите адрес сообщества в интернете."
    )
    description = models.TextField(
        verbose_name="Информация об авторе: ",
        help_text="Напишите что-нибудь об авторе."
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name="Текст заметки: ",
        help_text="Напишите здесь текст заметки."
    )
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор заметки: ",
        help_text="Это пользователь, опубликовавший заметку."
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="posts",
        verbose_name="Группа: ",
        help_text="Можете выбрать группу, к которой будет принадлежать пост."
    )
    image = models.ImageField(
        upload_to="posts/",
        blank=True,
        null=True,
        verbose_name="Изображение: ",
        help_text="Можете выбрать картинку к посту."
    )

    class Meta:
        ordering = ("-pub_date", )

    def __str__(self):
        return self.text[:LETTERS_PER_STR]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Заметка: ",
        help_text="Пост, к которому оставлен комментарий."
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор: ",
        help_text="Автор комментария."
    )
    text = models.TextField("Текст", help_text="Текст комментария.")
    created = models.DateTimeField(
        "Дата комментария", auto_now_add=True
    )

    class Meta:
        ordering = ("-created", )

    def __str__(self):
        return self.text[:LETTERS_PER_STR]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик: ",
        help_text="Подписчик."
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор: ",
        help_text="Автор."
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("user", "author"),
                name="follow_pair"
            )
        ]
