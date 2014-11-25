# -*- coding: utf-8 -*-
import django

from .. import settings
from ..utils import load_class


Badge = load_class(settings.BADGE_MODEL)
Award = load_class(settings.AWARD_MODEL)

if django.VERSION < (1, 7):
    from .. import autodiscover
    autodiscover()

from ..signals import *   # noqa
