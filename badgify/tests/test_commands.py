# -*- coding: utf-8 -*-
from django.db.models import signals
from django.test import TestCase

import badgify

from ..commands import sync_badges, sync_awards, sync_counts

from ..models import Badge, Award
from ..recipe import BaseRecipe

from .models import BadgifyUser as User
from .mixins import UserFixturesMixin, RecipeFixturesMixin


class BaseTestCase(TestCase):
    """
    Base test case.
    """

    def register_recipes(self):
        from .badgify_recipes import PythonLoverRecipe, JSLoverRecipe, JavaLoverRecipe
        recipes = [PythonLoverRecipe, JSLoverRecipe, JavaLoverRecipe]
        badgify.register(recipes)

    def unregister_recipes(self):
        badgify.registry.clear()


class SyncBadgesCommandTestCase(BaseTestCase, RecipeFixturesMixin):
    """
    ``badgify_sync badges`` command test case.
    """

    def setUp(self):
        badgify.registry.clear()

    def tearDown(self):
        badgify.registry.clear()

    def test_command(self):
        recipes, slugs = self.get_dummy_recipes(count=50)
        for recipe in recipes:
            badgify.register(recipe)
        sync_badges()
        self.assertEqual(Badge.objects.count(), 50)
        # check integrity
        recipes = []
        for slug in slugs:
            name = slug.encode('ascii', 'ignore')
            name += name
            attrs = dict(
                name=name,
                description=name,
                slug=slug,
                image=name,
                user_querset=User.objects.none())
            recipes.append(type(name, (BaseRecipe,), attrs))
        for slug in slugs[:5]:
            slug += slug
            name = slug.encode('ascii', 'ignore')
            name += name
            attrs = dict(
                name=name,
                slug=slug,
                description=name,
                image=name,
                user_querset=User.objects.none())
            recipes.append(type(name, (BaseRecipe,), attrs))
        for recipe in recipes:
            badgify.register(recipe)
        sync_badges()
        self.assertEqual(Badge.objects.count(), 55)


class SyncAwardsCommandTestCase(BaseTestCase, UserFixturesMixin):
    """
    ``badgify_sync awards`` command test case.
    """

    def setUp(self):
        self.register_recipes()
        self.created_count = 0
        self.signals_count = 0
        signals.post_save.connect(self._post_save_listener, sender=Award)

    def tearDown(self):
        signals.post_save.disconnect(self._post_save_listener, sender=Award)
        self.unregister_recipes()

    def _post_save_listener(self, *args, **kwargs):
        self.signals_count += 1
        created = kwargs.get('created', False)
        if created:
            self.created_count += 1

    def test_command(self):
        sync_badges()
        users, usernames = self.get_dummy_users(count=30)
        lovers = {'python': users[:15], 'java': users[15:20], 'js': users[20:30]}
        for lover, users in lovers.items():
            for user in users:
                setattr(user, 'love_%s' % lover, True)
                user.save()
        sync_awards()
        self.assertEqual(Award.objects.count(), 25)
        self.assertEqual(self.signals_count, 25)
        self.assertEqual(self.created_count, 25)
        self.assertEqual(Award.objects.filter(badge__slug='python-lover').count(), 15)
        self.assertEqual(Award.objects.filter(badge__slug='js-lover').count(), 10)
        self.assertEqual(Award.objects.filter(badge__slug='java-lover').count(), 0)
        User.objects.filter(love_python=True).update(love_python=False, love_js=True)
        sync_awards()
        self.assertEqual(Award.objects.filter(badge__slug='python-lover').count(), 15)
        self.assertEqual(Award.objects.filter(badge__slug='js-lover').count(), 25)
        self.assertEqual(Award.objects.filter(badge__slug='java-lover').count(), 0)


class SyncCountsCommandTestCase(BaseTestCase, UserFixturesMixin):
    """
    ``badgify_sync counts`` command test case.
    """

    def setUp(self):
        self.register_recipes()

    def tearDown(self):
        self.unregister_recipes()

    def test_command(self):
        sync_badges()
        users, usernames = self.get_dummy_users(count=30)
        lovers = {'python': users[:15], 'java': users[15:20], 'js': users[20:30]}
        for lover, users in lovers.items():
            for user in users:
                setattr(user, 'love_%s' % lover, True)
                user.save()
        sync_awards()
        self.assertEqual(Award.objects.count(), 25)
        sync_counts()
        self.assertEqual(Badge.objects.get(slug='python-lover').users_count, 15)
        self.assertEqual(Badge.objects.get(slug='js-lover').users_count, 10)
        self.assertEqual(Badge.objects.get(slug='java-lover').users_count, 0)
