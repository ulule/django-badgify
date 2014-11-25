# -*- coding: utf-8 -*-
import logging

from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import Award

logger = logging.getLogger('badgify')


@receiver(post_save, sender=Award)
def increment_badge_users_count(sender, instance, created, **kwargs):
    from django.db.models import F
    from .settings import AUTO_DENORMALIZE
    if created and AUTO_DENORMALIZE:
        logger.debug('✓ Badge %s: updated users_count field', instance.badge.slug)
        instance.badge.users_count = F('users_count') + 1
        instance.badge.save()
