# -*- coding: utf-8 -*-
import collections


class BadgifyRegistry(object):
    """
    Badge recipes registry.
    """

    def __init__(self):
        """
        Initializes a new registry.
        """
        self._registry = {}

    def register(self, recipe):
        """
        Registers a new recipe class.
        """
        if isinstance(recipe, collections.Iterable):
            for item in recipe:
                recipe = self._recipe_instance(item)
                self._registry[recipe.slug] = recipe
        else:
            recipe = self._recipe_instance(recipe)
            self._registry[recipe.slug] = recipe

    def unregister(self, recipe):
        """
        Unregisters a given recipe class.
        """
        recipe = self._recipe_instance(recipe)
        if recipe.slug in self._registry:
            del self._registry[recipe.slug]

    def clear(self):
        self._registry = {}

    def _recipe_instance(self, klass):
        """
        Returns recipe instance from class.
        """
        from .recipe import BaseRecipe
        assert issubclass(klass, BaseRecipe)
        return klass()

    @property
    def recipes(self):
        """
        Returns registered recipes.
        """
        return self._registry


def _autodiscover(recipes):
    import copy
    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule
    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        try:
            before_import_recipes = copy.copy(recipes)
            import_module('%s.badgify_recipes' % app)
        except:
            recipes = before_import_recipes
            if module_has_submodule(mod, 'badgify_recipes'):
                raise


registry = BadgifyRegistry()


def autodiscover():
    _autodiscover(registry)


def register(*args, **kwargs):
    return registry.register(*args, **kwargs)
