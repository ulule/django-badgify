# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import signals
from django.test import TestCase

from .. import settings
from ..recipe import bulk_create_awards
from ..compat import get_user_model
from ..models import Badge, Award


class SignalsTestCase(TestCase):
    """
    Signals test case.
    """

    def setUp(self):
        reload(settings)
        self.user = get_user_model().objects.create_user('user', 'user@example.com', '$ecret')
        self.badge = Badge.objects.create(name='badge', slug='badge')
        self.post_save_count = 0
        signals.post_save.connect(self._award_post_save_receiver, sender=Award)

    def tearDown(self):
        self.post_save_count = 0
        signals.post_save.disconnect(self._award_post_save_receiver, sender=Award)

    def _award_post_save_receiver(self, *args, **kwargs):
        self.post_save_count += 1

    def create_award(self):
        return Award.objects.create(user=self.user, badge=self.badge)

    def test_award_post_save(self):
        self.assertEqual(self.post_save_count, 0)
        self.create_award()
        self.assertEqual(self.post_save_count, 1)

    def test_auto_denormalize_disabled(self):
        settings.AUTO_DENORMALIZE = False
        badge = Badge.objects.get(slug='badge')
        self.assertEqual(badge.users_count, 0)
        self.assertEqual(self.post_save_count, 0)
        self.create_award()
        self.assertEqual(self.post_save_count, 1)
        badge = Badge.objects.get(slug='badge')
        self.assertEqual(badge.users_count, 0)

    def test_auto_denormalize_enabled(self):
        settings.AUTO_DENORMALIZE = True
        badge = Badge.objects.get(slug='badge')
        self.assertEqual(badge.users_count, 0)
        self.assertEqual(self.post_save_count, 0)
        self.create_award()
        self.assertEqual(self.post_save_count, 1)
        badge = Badge.objects.get(slug='badge')
        self.assertEqual(badge.users_count, 1)

    def test_award_bulk_create_post_save_disabled(self):
        settings.AUTO_DENORMALIZE = True
        badge = Badge.objects.get(slug='badge')
        self.assertEqual(badge.users_count, 0)
        self.assertEqual(self.post_save_count, 0)
        awards = [Award(user=self.user, badge=self.badge)]
        bulk_create_awards(objects=awards, post_save_signal=False)
        self.assertEqual(self.post_save_count, 0)
        badge = Badge.objects.get(slug='badge')
        self.assertEqual(badge.users_count, 0)

    def test_award_bulk_create_post_save_enabled(self):
        settings.AUTO_DENORMALIZE = True
        badge = Badge.objects.get(slug='badge')
        self.assertEqual(badge.users_count, 0)
        self.assertEqual(self.post_save_count, 0)
        awards = [Award(user=self.user, badge=self.badge)]
        bulk_create_awards(objects=awards, post_save_signal=True)
        self.assertEqual(self.post_save_count, 1)
        badge = Badge.objects.get(slug='badge')
        self.assertEqual(badge.users_count, 1)
