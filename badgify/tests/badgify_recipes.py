# -*- coding: utf-8 -*-
from django.contrib.staticfiles.storage import staticfiles_storage

import badgify
from ..recipe import BaseRecipe
from .models import BadgifyUser as User


class PythonLoverRecipe(BaseRecipe):
    """
    People loving Python.
    """
    name = 'Python Lover'
    slug = 'python-lover'
    description = 'People loving Python programming language'

    @property
    def image(self):
        return staticfiles_storage.open('python-lover.png')

    @property
    def user_ids(self):
        return User.objects.filter(love_python=True).values_list('id', flat=True)


class JSLoverRecipe(BaseRecipe):
    """
    People loving JS.
    """
    name = 'JS Lover'
    slug = 'js-lover'
    description = 'People loving JS programming language'

    @property
    def image(self):
        return staticfiles_storage.open('js-lover.png')

    @property
    def user_ids(self):
        return User.objects.filter(love_js=True).values_list('id', flat=True)


class JavaLoverRecipe(BaseRecipe):
    """
    People loving Java.
    """
    name = 'Java Lover'
    slug = 'java-lover'
    description = 'People loving Java programming language'

    @property
    def image(self):
        return staticfiles_storage.open('js-lover.png')


badgify.register([
    PythonLoverRecipe,
    JSLoverRecipe,
    JavaLoverRecipe,
])
