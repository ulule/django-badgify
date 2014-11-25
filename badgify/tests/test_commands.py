# -*- coding: utf-8 -*-
from django.test import TestCase

from .. import registry
from .. import commands
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
        Recipe1.name = 'Howdy'
        commands.sync_badges(update=False)
        self.assertEqual(Badge.objects.get(slug='recipe1').name, 'Recipe 1')
        commands.sync_badges(update=True)
        self.assertEqual(Badge.objects.get(slug='recipe1').name, 'Howdy')
        Recipe1.name = 'Recipe 1'

    def test_sync_users_count(self):
        user = get_user_model().objects.create_user('user', 'user@example.com', '$ecret')
        registry.register([Recipe1, Recipe2])
        commands.sync_badges()
        updated, unchanged = commands.sync_users_count()
        self.assertEqual(len(updated), 0)
        self.assertEqual(len(unchanged), 2)
        Award.objects.create(user=user, badge=Badge.objects.get(slug='recipe1'))
        updated, unchanged = commands.sync_users_count()
        self.assertEqual(len(updated), 1)
        self.assertEqual(len(unchanged), 1)
        self.assertEqual(updated[0].users_count, 1)
        Award.objects.all().delete()
        updated, unchanged = commands.sync_users_count()
        self.assertEqual(len(updated), 1)
        self.assertEqual(len(unchanged), 1)
        self.assertEqual(updated[0].users_count, 0)

    def test_sync_awards(self):
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
