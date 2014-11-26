# -*- coding: utf-8 -*-
from django.db.models import signals
from django.test import TestCase

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
        reload(settings)
        registry.clear()
        self.post_save_count = 0
        signals.post_save.connect(self._award_post_save_receiver, sender=Award)

    def tearDown(self):
        registry.clear()
        signals.post_save.disconnect(self._award_post_save_receiver, sender=Award)

    def _award_post_save_receiver(self, *args, **kwargs):
        self.post_save_count += 1

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

    def test_sync_awards_auto_denormalize_false(self):
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
        self.assertEqual(recipe.badge.users_count, 0)
        self.assertEqual(self.post_save_count, 1)

    def test_sync_awards_auto_denormalize_true(self):
        settings.AUTO_DENORMALIZE = True
        user = get_user_model().objects.create_user('user', 'user@example.com', '$ecret')
        registry.register(Recipe1)
        commands.sync_badges()
        recipe = registry.get_recipe_instance('recipe1')
        user.love_python = True
        user.save()
        commands.sync_awards()
        self.assertEqual(recipe.badge.users.count(), 1)
        self.assertEqual(recipe.badge.users_count, 1)
        self.assertEqual(self.post_save_count, 1)

    def test_sync_awards_disable_signals(self):
        settings.AUTO_DENORMALIZE = True
        user = get_user_model().objects.create_user('user', 'user@example.com', '$ecret')
        registry.register(Recipe1)
        created = commands.sync_badges()
        recipe = registry.get_recipe_instance('recipe1')
        self.assertEqual(len(created), 1)
        self.assertEqual(self.post_save_count, 0)
        self.assertEqual(recipe.badge.users_count, 0)
        user.love_python = True
        user.save()
        commands.sync_awards(**{'disable_signals': True})
        self.assertEqual(recipe.badge.users_count, 0)
        self.assertEqual(self.post_save_count, 0)
