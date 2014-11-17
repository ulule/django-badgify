# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import collections
import logging

from .mixins import RegistryDatabaseOpsMixin

logger = logging.getLogger('badgify')


class BadgifyRegistry(RegistryDatabaseOpsMixin):
    """
    Badge recipes registry.
    """

    def __init__(self):
        """
        Initializes a new registry.
        """
        self._registry = {}

    @property
    def recipes(self):
        """
        Returns all registered recipes (keys are recipe's badge slugs and values
        are recipe instances.
        """
        return self._registry

    def register(self, recipe):
        """
        Registers a new recipe class.
        """
        if isinstance(recipe, collections.Iterable):
            for item in recipe:
                recipe = self.get_recipe_instance_from_class(item)
                self._registry[recipe.slug] = recipe
        else:
            recipe = self.get_recipe_instance_from_class(recipe)
            self._registry[recipe.slug] = recipe

    def unregister(self, recipe):
        """
        Unregisters a given recipe class.
        """
        recipe = self.get_recipe_instance_from_class(recipe)
        if recipe.slug in self._registry:
            del self._registry[recipe.slug]

    def clear(self):
        """
        Clears the registry (removes all registered classes).
        """
        self._registry = {}

    def get_recipe_instance(self, badge):
        """
        Returns the recipe instance for the given badge slug.
        If badge has not been registered, raises ``exceptions.BadgeNotFound``.
        """
        from .exceptions import BadgeNotFound
        if self._registry.has_key(badge):
            return self.recipes[badge]
        raise BadgeNotFound()

    def get_recipe_instances(self, badges=None):
        """
        Returns all recipe instances or just those for the given badges.
        """
        if badges:
            valid, invalid = self.get_recipe_instances_for_badges(badges=badges)
            return valid
        return self.recipes.itervalues()

    def get_recipe_instances_for_badges(self, badges):
        """
        Takes a list of badge slugs and returns a tuple: ``(valid, invalid)``.

            ``valid``
                A list containing valid recipe instances (badges exist).

            ``invalid``
                A list containing invalid badge slugs (badges do not exist).

        """
        from .exceptions import BadgeNotFound

        valid, invalid = [], []

        if not isinstance(badges, collections.Iterable):
            badges = [badges]

        for badge in badges:
            try:
                recipe = self.get_recipe_instance(badge)
                valid.append(recipe)
            except BadgeNotFound:
                logger.error('✘ Badge "%s" has not been registered', badge)
                invalid.append(badge)

        return (valid, invalid)

    def get_recipe_instance_from_class(self, klass):
        """
        Returns recipe instance from the given class ``klass``.
        """
        from .recipe import BaseRecipe
        assert issubclass(klass, BaseRecipe)
        return klass()

    def get_recipe_instance_badge(self, instance):
        """
        Takes a recipe instance, checks if the related ``Badge`` model instance
        exists. If it exists, returns it. Otherwise, returns ``None``.
        """
        badge = None
        try:
            badge = instance.badge
        except instance.badge.model.DoesNotExist:
            logger.debug("✘ Badge %s: does not exist (run badgify_sync badges)",
                         instance.slug)
        return badge


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
