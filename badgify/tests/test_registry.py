# -*- coding: utf-8 -*-
from django.test import TestCase

from ..registry import BadgifyRegistry
from ..recipe import BaseRecipe


class BadRecipe(object):
    pass


class NotImplementedRecipe(BaseRecipe):
    pass


class GoodRecipe(BaseRecipe):
    name = 'Foo'
    slug = 'foo'
    description = 'Foo description'

    @property
    def image(self):
        return 'image'

    @property
    def user_queryset(self):
        return []


class RegistryTestCase(TestCase):
    """
    Registry test case.
    """

    def test_register(self):
        registry = BadgifyRegistry()
        self.assertRaises(AssertionError, registry.register, BadRecipe)
        self.assertIsNone(registry.register(GoodRecipe))
        self.assertEqual(len(registry.recipes), 1)

    def test_register_recipe_list(self):
        registry = BadgifyRegistry()
        Recipe1 = type('Recipe1', (BaseRecipe,), dict(name='r1', slug='r1'))
        Recipe2 = type('Recipe2', (BaseRecipe,), dict(name='r2', slug='r2'))
        registry.register([Recipe1, Recipe2])
        self.assertEqual(len(registry.recipes), 2)

    def test_unregister(self):
        registry = BadgifyRegistry()
        registry.register(GoodRecipe)
        self.assertEqual(len(registry.recipes), 1)
        registry.unregister(GoodRecipe)
        self.assertEqual(len(registry.recipes), 0)
