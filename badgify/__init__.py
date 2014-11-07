# -*- coding: utf-8 -*-
from .registry import registry, register, autodiscover

__all__ = ['registry', 'register', 'autodiscover']


default_app_config = 'badgify.apps.BadgifyConfig'
