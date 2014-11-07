# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.files.storage
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Award',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('awarded_at', models.DateTimeField(auto_now_add=True, verbose_name='awarded at')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'award',
                'verbose_name_plural': 'awards',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='The badge name', max_length=255, verbose_name='name')),
                ('slug', models.SlugField(max_length=255, blank=True, help_text='The badge slug (auto-generated if empty)', unique=True, verbose_name='slug')),
                ('description', models.TextField(help_text='The badge description', verbose_name='description', blank=True)),
                ('image', models.ImageField(storage=django.core.files.storage.FileSystemStorage(base_url=b'/media/uploads/', location=b'/vagrant/badgify/tests/media/uploads'), upload_to=b'', blank=True, help_text='Please, upload an image for this badge', null=True, verbose_name='image')),
                ('users', models.ManyToManyField(help_text='Users that earned this badge', to=settings.AUTH_USER_MODEL, verbose_name='users', through='badgify.Award')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'badge',
                'verbose_name_plural': 'badges',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='award',
            name='badge',
            field=models.ForeignKey(related_name='awards', verbose_name='badge', to='badgify.Badge'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='award',
            name='user',
            field=models.ForeignKey(related_name='badges', verbose_name='user', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='award',
            unique_together=set([('user', 'badge')]),
        ),
    ]
