# -*- coding: utf-8 -*-
from django.test import TestCase

from ..exceptions import BadgeNotFound
from ..recipe import BaseRecipe
from ..registry import BadgifyRegistry as Registry

from .recipes import (
    Recipe1,
    Recipe2,
    BadRecipe)


class RegistryTestCase(TestCase):
    """
    Registry test case.
    """

    def test_recipes(self):
        registry = Registry()
        registry.register(Recipe1)
        self.assertTrue(isinstance(registry.recipes, dict))
        self.assertEqual(len(registry.recipes), 1)

    def test_registered(self):
        registry = Registry()
        registry.register(Recipe1)
        registry.register(Recipe2)
        self.assertTrue(isinstance(registry.registered, list))
        self.assertIn('recipe1', registry.registered)
        self.assertIn('recipe2', registry.registered)

    def test_register(self):
        registry = Registry()
        # With a single class
        self.assertRaises(AssertionError, registry.register, BadRecipe)
        self.assertIsNone(registry.register(Recipe1))
        self.assertEqual(len(registry.recipes), 1)
        # With a list of classes
        registry.clear()
        registry.register([Recipe1, Recipe2])
        self.assertEqual(len(registry.recipes), 2)

    def test_unregister(self):
        registry = Registry()
        registry.register(Recipe1)
        self.assertEqual(len(registry.recipes), 1)
        registry.unregister(Recipe1)
        self.assertEqual(len(registry.recipes), 0)

    def test_clear(self):
        registry = Registry()
        registry.register(Recipe1)
        self.assertEqual(len(registry.recipes), 1)
        registry.clear()
        self.assertTrue(isinstance(registry.recipes, dict))
        self.assertEqual(len(registry.recipes), 0)

    def test_get_recipe_instance(self):
        registry = Registry()
        registry.register(Recipe1)
        instance = registry.get_recipe_instance('recipe1')
        self.assertTrue(isinstance(instance, BaseRecipe))
        self.assertRaises(BadgeNotFound, registry.get_recipe_instance, 'unknown')

    def test_get_recipe_instances(self):
        registry = Registry()
        registry.register([Recipe1, Recipe2])
        # Without passing badges arg
        instances = registry.get_recipe_instances()
        self.assertEqual(len(instances), 2)
        for instance in instances:
            self.assertTrue(isinstance(instance, BaseRecipe))
        # By passing badges arg
        registry = Registry()
        registry.register([Recipe1, Recipe2])
        instances = registry.get_recipe_instances(badges=['recipe1', 'oops'])
        self.assertEqual(len(instances), 1)
        instances = registry.get_recipe_instances(badges=['recipe1', 'recipe2'])
        self.assertEqual(len(instances), 2)
        # By passing excluded arg
        registry = Registry()
        registry.register([Recipe1, Recipe2])
        instances = registry.get_recipe_instances(excluded=['recipe2'])
        self.assertEqual(len(instances), 1)
        self.assertTrue(isinstance(instances[0], Recipe1))

    def test_get_recipe_instances_for_badges(self):
        registry = Registry()
        registry.register([Recipe1, Recipe2])
        valid, invalid = registry.get_recipe_instances_for_badges(badges=['recipe1', 'recipe2', 'oops'])
        self.assertEqual(len(valid), 2)
        self.assertEqual(len(invalid), 1)
        self.assertIn('oops', invalid)
        # Test by passing a string instead of a list
        registry = Registry()
        registry.register(Recipe1)
        valid, invalid = registry.get_recipe_instances_for_badges(badges='recipe1')
        self.assertEqual(len(valid), 1)
        self.assertEqual(len(invalid), 0)

    def test_get_recipe_instance_from_class(self):
        registry = Registry()
        instance = registry.get_recipe_instance_from_class(Recipe1)
        self.assertTrue(isinstance(instance, Recipe1))
        self.assertRaises(AssertionError, registry.get_recipe_instance_from_class, BadRecipe)
