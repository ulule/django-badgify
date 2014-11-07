# -*- coding: utf-8 -*-
from django.db.models import F


def increment_badge_users_count(sender, instance, created, **kwargs):
    if created:
        instance.badge.users_count = F('users_count') + 1
        instance.badge.save()
