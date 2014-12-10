# -*- coding: utf-8 -*-
import django
from django.conf import settings

__all__ = ['get_user_model']


AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


def get_user_model():
    if django.VERSION >= (1, 5):
        from django.contrib.auth import get_user_model as _get_user_model
        User = _get_user_model()
    else:
        from django.contrib.auth.models import User
    return User
