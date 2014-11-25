# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.utils import override_settings

from .. import settings
from .. import commands
from .. import registry
from ..models import Badge, Award
from ..compat import get_user_model

from .recipes import Recipe1, Recipe2


class CommandsTestCase(TestCase):
    """
    Commands test case.
    """

    def setUp(self):
        registry.clear()

    def tearDown(self):
        registry.clear()

    def test_sync_badges(self):
        registry.register([Recipe1, Recipe2])
        created = commands.sync_badges()
        self.assertEqual(len(created), 2)

    def test_sync_badges_update(self):
        registry.register([Recipe1, Recipe2])
        commands.sync_badges()
        Recipe1.name = 'Howdy'
        commands.sync_badges(update=True)
        self.assertEqual(Badge.objects.get(slug='recipe1').name, 'Howdy')
        Recipe1.name = 'Recipe 1'

    def test_sync_count(self):
        settings.AUTO_DENORMALIZE = False
        user = get_user_model().objects.create_user('user', 'user@example.com', '$ecret')

        registry.register([Recipe1, Recipe2])
        commands.sync_badges()
        updated, unchanged = commands.sync_counts()
        self.assertEqual(len(updated), 0)
        self.assertEqual(len(unchanged), 2)

        Award.objects.create(user=user, badge=Badge.objects.get(slug='recipe1'))
        updated, unchanged = commands.sync_counts()
        self.assertEqual(len(updated), 1)
        self.assertEqual(len(unchanged), 1)

    def test_sync_awards(self):
        settings.AUTO_DENORMALIZE = False
        user = get_user_model().objects.create_user('user', 'user@example.com', '$ecret')
        registry.register(Recipe1)

        created = commands.sync_badges()
        recipe = registry.get_recipe_instance('recipe1')
        self.assertEqual(len(created), 1)
        self.assertEqual(recipe.badge.users.count(), 0)

        user.love_python = True
        user.save()
        commands.sync_awards()

        self.assertEqual(recipe.badge.users.count(), 1)

    def test_sync_awards_auto_denormalize_setting(self):
        settings.AUTO_DENORMALIZE = True
        user = get_user_model().objects.create_user('user', 'user@example.com', '$ecret')
        registry.register(Recipe1)

        created = commands.sync_badges()
        recipe = registry.get_recipe_instance('recipe1')
        self.assertEqual(len(created), 1)
        self.assertEqual(recipe.badge.users_count, 0)

        user.love_python = True
        user.save()
        commands.sync_awards()

        self.assertEqual(recipe.badge.users_count, 1)

    def test_sync_awards_auto_denormalize_option(self):
        settings.AUTO_DENORMALIZE = True

        user = get_user_model().objects.create_user('user', 'user@example.com', '$ecret')
        registry.register(Recipe1)

        created = commands.sync_badges()
        recipe = registry.get_recipe_instance('recipe1')
        self.assertEqual(len(created), 1)
        self.assertEqual(recipe.badge.users_count, 0)

        user.love_python = True
        user.save()
        commands.sync_awards(**{"auto_denormalize": True})

        self.assertEqual(recipe.badge.users_count, 1)
