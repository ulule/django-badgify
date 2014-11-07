# -*- coding: utf-8 -*-
from django.template import Template, Context
from django.test import TestCase

from ..models import Award
from ..templatetags.badgify_tags import badgify_badges as badges_tag

from .models import BadgifyUser as User
from .mixins import BadgeFixturesMixin, UserFixturesMixin


class BadgesTagTestCase(TestCase, BadgeFixturesMixin, UserFixturesMixin):
    """
    ``badgify_badges`` templatetag test case.
    """

    def setUp(self):
        self.badges = []
        badges, slugs = self.get_dummy_badges()
        for badge in badges:
            badge.save()
            self.badges.append(badge)
        self.users = self.create_users()
        self.badge = self.badges[0]
        self.user = User.objects.get(username='johndoe')
        self.award = Award.objects.create(badge=self.badge, user=self.user)

    def test_no_args(self):
        badges = badges_tag()
        self.assertEqual(len(badges), 20)
        template = Template('''
            {% load badgify_tags %}
            {% badgify_badges as badges %}
            {% for badge in badges %}{{ badge.name }} {{ badge.slug }}{% endfor %}
        ''')
        rendered = template.render(Context({}))
        for badge in self.badges:
            self.assertIn(badge.name, rendered)
            self.assertIn(badge.slug, rendered)

    def test_with_username(self):
        badges = badges_tag(**{'username': 'johndoe'})
        self.assertEqual(len(badges), 1)
        template = Template('''
            {% load badgify_tags %}
            {% badgify_badges username="johndoe" as badges %}
            {% for badge in badges %}{{ badge.name }} {{ badge.slug }}{% endfor %}
        ''')
        rendered = template.render(Context({}))
        self.assertIn(self.badge.name, rendered)
        self.assertIn(self.badge.slug, rendered)

    def test_with_user(self):
        badges = badges_tag(**{'user': self.user})
        self.assertEqual(len(badges), 1)
        template = Template('''
            {% load badgify_tags %}
            {% badgify_badges user=user as badges %}
            {% for badge in badges %}{{ badge.name }} {{ badge.slug }}{% endfor %}
        ''')
        rendered = template.render(Context({'user': self.user}))
        self.assertIn(self.badge.name, rendered)
        self.assertIn(self.badge.slug, rendered)
