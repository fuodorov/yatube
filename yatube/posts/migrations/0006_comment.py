# Generated by Django 3.1.3 on 2021-01-16 07:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0005_post_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='Текст комментария.', verbose_name='Текст')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Дата комментария')),
                ('author', models.ForeignKey(help_text='Автор комментария.', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='Автор: ')),
                ('post', models.ForeignKey(help_text='Пост, к которому оставлен комментарий.', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='posts.post', verbose_name='Заметка: ')),
            ],
            options={
                'ordering': ('-created',),
            },
        ),
    ]
