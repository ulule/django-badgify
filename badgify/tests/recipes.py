# -*- coding: utf-8 -*-
from ..recipe import BaseRecipe
from ..compat import get_user_model


class BadRecipe(object):
    pass


class NotImplementedRecipe(BaseRecipe):
    pass


class Recipe1(BaseRecipe):
    name = 'Recipe 1'
    slug = 'recipe1'
    description = 'Recipe 1 description'

    @property
    def image(self):
        return 'image'

    @property
    def user_ids(self):
        return (get_user_model().objects.filter(love_python=True)
                                .values_list('id', flat=True))


class Recipe2(BaseRecipe):
    name = 'Recipe 2'
    slug = 'recipe2'
    description = 'Recipe 2 description'

    @property
    def image(self):
        return 'image'

    @property
    def user_ids(self):
        return []
