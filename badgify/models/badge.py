# -*- coding: utf-8 -*-
from . import base


class Badge(base.Badge):
    class Meta(base.Badge.Meta):
        abstract = False
