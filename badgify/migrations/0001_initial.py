# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Award',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('awarded_at', models.DateTimeField(verbose_name='awarded at', auto_now_add=True)),
            ],
            options={
                'abstract': False,
                'verbose_name_plural': 'awards',
                'verbose_name': 'award',
            },
        ),
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(verbose_name='name', help_text='The badge name', max_length=255)),
                ('slug', models.SlugField(verbose_name='slug', unique=True, help_text='The badge slug (auto-generated if empty)', blank=True, max_length=255)),
                ('description', models.TextField(verbose_name='description', blank=True, help_text='The badge description')),
                ('image', models.ImageField(verbose_name='Image', help_text='Please, upload an image for this badge', upload_to='badges', null=True, blank=True)),
                ('users_count', models.IntegerField(editable=False, default=0, verbose_name='users count')),
                ('users', models.ManyToManyField(verbose_name='users', to=settings.AUTH_USER_MODEL, help_text='Users that earned this badge', through='badgify.Award')),
            ],
            options={
                'abstract': False,
                'verbose_name_plural': 'badges',
                'verbose_name': 'badge',
            },
        ),
        migrations.AddField(
            model_name='award',
            name='badge',
            field=models.ForeignKey(verbose_name='badge', to='badgify.Badge', related_name='awards'),
        ),
        migrations.AddField(
            model_name='award',
            name='user',
            field=models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL, related_name='badges'),
        ),
        migrations.AlterUniqueTogether(
            name='award',
            unique_together=set([('user', 'badge')]),
        ),
    ]
