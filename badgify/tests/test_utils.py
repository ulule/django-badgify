# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.query import QuerySet
from django.test import TestCase

from .. import utils
from ..models import Badge, Award

from .mixins import UserFixturesMixin
from .models import BadgifyUser as User


class DummyModel(models.Model):
    name = models.CharField(max_length=255)


class UtilsTestCase(TestCase, UserFixturesMixin):
    """
    Utils test case.
    """

    def test_get_queryset_list(self):
        func = utils.get_queryset_list
        goods = [
            DummyModel.objects.all(),
            DummyModel.objects.none(),
            [DummyModel.objects.all(), DummyModel.objects.all()],
            [DummyModel.objects.none(), DummyModel.objects.all()],
            [DummyModel.objects.none(), DummyModel.objects.none()],
            (DummyModel.objects.all(), DummyModel.objects.all()),
            (DummyModel.objects.none(), DummyModel.objects.all()),
            (DummyModel.objects.none(), DummyModel.objects.none()),
        ]
        bads = [
            'oops',
            ['oops', 'bad'],
            [123, 10.2, 'very bad'],
        ]
        for good in goods:
            self.assertTrue(func(good))
            result = func(good)
            self.assertTrue(isinstance(result, (list, tuple)))
        for bad in bads:
            self.assertRaises(Exception, func, bad)

    def test_get_user_ids_for_badge(self):
        func = utils.get_user_ids_for_badge
        users, usernames = self.get_dummy_users(count=20)
        for user in users:
            user.save()
        Badge.objects.create(name='badge', slug='badge')
        badge = Badge.objects.get(slug='badge')
        self.assertEqual(User.objects.count(), 20)
        self.assertEqual(Badge.objects.count(), 1)
        self.assertEqual(Award.objects.count(), 0)
        # First, without awards
        result = func(badge=badge, user_querysets=User.objects.none())
        self.assertEqual(result, ([], 0))
        result = func(badge=badge, user_querysets=User.objects.all())
        self.assertEqual(result, (list(User.objects.values_list('id', flat=True)), 20))
        # Then, let's create award
        for user in users:
            Award.objects.create(user=user, badge=badge)
        result = func(badge=badge, user_querysets=User.objects.none())
        self.assertEqual(result, ([], 0))
        result = func(badge=badge, user_querysets=User.objects.all())
        self.assertEqual(result, ([], 0))

    def test_get_award_objects_for_badge(self):
        func = utils.get_award_objects_for_badge
        users, usernames = self.get_dummy_users(count=20)
        for user in users:
            user.save()
        Badge.objects.create(name='badge', slug='badge')
        badge = Badge.objects.get(slug='badge')
        user_ids = User.objects.values_list('id', flat=True)
        result = func(badge=badge, user_ids=user_ids)
        self.assertEqual(len(result), 20)
        for obj in result:
            self.assertTrue(isinstance(obj, Award))

    def test_chunk_user_queryset_for_ids(self):
        func = utils.chunk_user_queryset_for_ids
        users, usernames = self.get_dummy_users(count=50)
        for user in users:
            user.save()
        ids = User.objects.values_list('id', flat=True)
        result = func(ids=ids, batch_size=10)
        self.assertEqual(len(result), 5)
        for qs in result:
            self.assertTrue(isinstance(qs, QuerySet))
        result = func(ids=ids, batch_size=50)
        self.assertEqual(len(result), 1)
