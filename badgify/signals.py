# -*- coding: utf-8 -*-
import logging

from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

from .models import Award

logger = logging.getLogger('badgify')


@receiver(post_save, sender=Award)
def increment_badge_users_count(sender, instance, created, **kwargs):
    from django.db.models import F
    from .settings import AUTO_DENORMALIZE

    if created and AUTO_DENORMALIZE:
        instance.badge.users_count = F('users_count') + 1

        logger.debug('✓ Badge %s: incremented users_count field (now: %d)',
                     instance.badge.slug,
                     instance.badge.users_count)

        instance.badge.save()


@receiver(pre_delete, sender=Award)
def decrement_badge_users_count(sender, instance, **kwargs):
    from django.db.models import F
    from .settings import AUTO_DENORMALIZE

    if AUTO_DENORMALIZE:
        instance.badge.users_count = F('users_count') - 1

        logger.debug('✓ Badge %s: decremented users_count field (now: %d)',
                     instance.badge.slug,
                     instance.badge.users_count)

        instance.badge.save()
