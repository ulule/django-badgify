# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractUser


class BadgifyUser(AbstractUser):
    love_python = models.BooleanField(default=False)
    love_js = models.BooleanField(default=False)
    love_java = models.BooleanField(default=False)
