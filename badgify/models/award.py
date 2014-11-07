# -*- coding: utf-8 -*-
from . import base


class Award(base.Award):
    class Meta(base.Award.Meta):
        abstract = False
