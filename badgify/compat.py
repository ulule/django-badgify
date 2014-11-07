# -*- coding: utf-8 -*-
import django
from django.conf import settings

__all__ = ['get_user_model', 'get_image_field']


AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


def get_user_model():
    if django.VERSION >= (1, 5):
        from django.contrib.auth import get_user_model as _get_user_model
        User = _get_user_model()
    else:
        from django.contrib.auth.models import User
    return User


def get_image_field():
    from django.db import models
    from django.utils.translation import ugettext_lazy as _
    from . import settings as app_settings
    kwargs = dict(
        null=True,
        blank=True,
        verbose_name=_('image'),
        help_text=_('Please, upload an image for this badge'))
    if django.VERSION >= (1, 7):
        kwargs['storage'] = app_settings.BADGE_IMAGE_UPLOAD_STORAGE
    else:
        kwargs['upload_to'] = app_settings.BADGE_IMAGE_UPLOAD_ROOT
    return models.ImageField(**kwargs)
