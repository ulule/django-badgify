# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

from .models import Award

logger = logging.getLogger('badgify')


@receiver(post_save, sender=Award, dispatch_uid='badgify.award.post_save.increment_badge_users_count')
def increment_badge_users_count(sender, instance, created, **kwargs):
    from django.db.models import F
    from .settings import AUTO_DENORMALIZE

    if created and AUTO_DENORMALIZE:
        instance.badge.users_count = F('users_count') + 1
        instance.badge.save()


@receiver(pre_delete, sender=Award, dispatch_uid='badgify.award.pre_delete.decrement_badge_users_count')
def decrement_badge_users_count(sender, instance, **kwargs):
    from django.db.models import F
    from .settings import AUTO_DENORMALIZE

    if AUTO_DENORMALIZE and instance.badge.users_count >= 1:
        instance.badge.users_count = F('users_count') - 1
        instance.badge.save()
