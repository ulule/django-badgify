# -*- coding: utf-8 -*-
from .base.award import Award as BaseAward


class Award(BaseAward):
    class Meta(BaseAward.Meta):
        abstract = False
