# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('badgify', '0002_badge_manual_assignment'),
    ]

    operations = [
        migrations.AddField(
            model_name='badge',
            name='users_count',
            field=models.IntegerField(default=0, verbose_name='users count', editable=False),
            preserve_default=True,
        ),
    ]
