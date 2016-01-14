# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Award',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('awarded_at', models.DateTimeField(auto_now_add=True, verbose_name='awarded at')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'award',
                'verbose_name_plural': 'awards',
            },
        ),
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The badge name', max_length=255, verbose_name='name')),
                ('slug', models.SlugField(blank=True, help_text='The badge slug (auto-generated if empty)', max_length=255, unique=True, verbose_name='slug')),
                ('description', models.TextField(blank=True, help_text='The badge description', verbose_name='description')),
                ('image', models.ImageField(blank=True, help_text='Please, upload an image for this badge', null=True, upload_to=b'badges', verbose_name='Image')),
                ('users_count', models.IntegerField(default=0, editable=False, verbose_name='users count')),
                ('users', models.ManyToManyField(help_text='Users that earned this badge', through='badgify.Award', to=settings.AUTH_USER_MODEL, verbose_name='users')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'badge',
                'verbose_name_plural': 'badges',
            },
        ),
        migrations.AddField(
            model_name='award',
            name='badge',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='awards', to='badgify.Badge', verbose_name='badge'),
        ),
        migrations.AddField(
            model_name='award',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='badges', to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.AlterUniqueTogether(
            name='award',
            unique_together=set([('user', 'badge')]),
        ),
    ]
