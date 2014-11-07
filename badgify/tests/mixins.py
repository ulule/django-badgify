# -*- coding: utf-8 -*_
from __future__ import unicode_literals

from random import randrange

from django.utils.text import slugify

from random_words import RandomNicknames

from ..recipe import BaseRecipe
from ..models import Badge

from .models import BadgifyUser as User


class UserFixturesMixin(object):
    """
    User fixtures mixin.
    """

    def create_users(self):
        self.user1 = User.objects.create_user(
            'johndoe',
            'john@example.com',
            'secret')
        self.user2 = User.objects.create_user(
            'mikedavis',
            'mike@example.com',
            'secret')
        self.user3 = User.objects.create_user(
            'banana',
            'banana@example.com',
            'secret')

    def get_dummy_users(self, count=20):
        rn = RandomNicknames()
        users, usernames = [], []
        for name in rn.random_nicks(count=count):
            name = '%s #%d' % (name, randrange(99))
            username = slugify(name)
            usernames.append(username)
            users.append(User(
                username=username,
                email='%s@example.com' % username,
                password='secret'))
        return (users, usernames)


class BadgeFixturesMixin(object):
    """
    Badge fixtures mixin.
    """

    def get_dummy_badges(self, count=20):
        rn = RandomNicknames()
        badges, slugs = [], []
        for name in rn.random_nicks(count=count):
            name = '%s #%d' % (name, randrange(99))
            slug = slugify(name)
            slugs.append(slug)
            badges.append(Badge(name=name, slug=slug, description=name))
        return badges, slugs


class RecipeFixturesMixin(object):
    """
    Recipe fixtures mixin.
    """

    def get_dummy_recipes(self, count=50):
        rn = RandomNicknames()
        recipes, slugs = [], []
        for name in rn.random_nicks(count=count):
            slug = slugify(name)
            slugs.append(slug)
            name = name.encode('ascii', 'ignore')
            attrs = dict(
                name=name,
                slug=slug,
                description=name,
                image=name,
                user_queryset=User.objects.none())
            recipes.append(type(name, (BaseRecipe,), attrs))
        return (recipes, slugs)
