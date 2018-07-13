# -*- coding: utf-8 -*-
from django.urls import reverse
from django.test import TestCase

from ..models import Badge

from .mixins import BadgeFixturesMixin


class BadgeDetailViewTestCase(TestCase):
    """
    BadgeDetail view test case.
    """

    def setUp(self):
        self.badge = Badge.objects.create(
            name='Djangonaut',
            slug='djangonaut',
            description='Django Developer',
            image=u'')
        self.badge_with_hyphen = Badge.objects.create(
            name='Super Djangonaut',
            slug='super-djangonaut',
            description='Super Django Developer',
            image=u'')

    def test_view(self):
        for badge in [self.badge, self.badge_with_hyphen]:
            res = self.client.get(badge.get_absolute_url())
            self.assertEqual(res.status_code, 200)
            self.assertTemplateUsed(res, 'badgify/badge_detail.html')

    def test_view_404(self):
        res = self.client.get(reverse('badge_detail', kwargs={'slug': 'foobar'}))
        self.assertEqual(res.status_code, 404)


class BadgeListViewTestCase(TestCase, BadgeFixturesMixin):
    """
    BadgeList view test case.
    """

    def setUp(self):
        self.badges = []
        badges, slugs = self.get_dummy_badges()
        for badge in badges:
            badge.save()
            self.badges.append(badge)

    def test_view(self):
        res = self.client.get(reverse('badge_list'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'badgify/badge_list.html')
