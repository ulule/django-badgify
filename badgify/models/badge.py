# -*- coding: utf-8 -*-
from .base.badge import Badge as BaseBadge


class Badge(BaseBadge):
    class Meta(BaseBadge.Meta):
        abstract = False
