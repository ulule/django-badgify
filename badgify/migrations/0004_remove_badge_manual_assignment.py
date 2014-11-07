# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('badgify', '0003_badge_users_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='badge',
            name='manual_assignment',
        ),
    ]
