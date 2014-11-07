# -*- coding: utf-8 -*-
import django

from .. import settings
from ..utils import load_class


Badge = load_class(settings.BADGE_MODEL)
Award = load_class(settings.AWARD_MODEL)


if settings.ENABLE_BADGE_USERS_COUNT_SIGNAL:
    from django.db.models import signals
    from ..signals import increment_badge_users_count
    signals.post_save.connect(
        increment_badge_users_count,
        sender=Award,
        dispatch_uid='increment_badge_users_count')


if django.VERSION < (1, 7):
    from .. import autodiscover
    autodiscover()
