# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('badgify', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='badge',
            name='manual_assignment',
            field=models.BooleanField(default=False, help_text='Bypass the award creation command to manually assign awards', verbose_name='manual assignment'),
            preserve_default=True,
        ),
    ]
