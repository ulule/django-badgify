# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import IntegrityError
from django.test import TestCase

from ..models import Badge, Award
from .mixins import UserFixturesMixin


class BadgeTestCase(TestCase):
    """
    Badge model test case.
    """

    def test_autocreate_slug(self):
        badge = Badge.objects.create(name='Super Chouette')
        self.assertEqual(badge.slug, 'super-chouette')


class AwardTestCase(TestCase, UserFixturesMixin):
    """
    Award model test case.
    """

    def setUp(self):
        self.create_users()

    def test_create(self):
        badge = Badge.objects.create(name='Super Chouette')
        Award.objects.create(user=self.user1, badge=badge)
        Award.objects.create(user=self.user2, badge=badge)
        self.assertEqual(badge.users.count(), 2)
        self.assertRaises(IntegrityError, Award.objects.create, **{
            'user': self.user1,
            'badge': badge
        })
