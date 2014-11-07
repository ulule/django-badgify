# -*- coding: utf-8 -*-
import logging
import random
from optparse import make_option

from django.core import management
from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS, IntegrityError
from django.utils.text import slugify
from random_words import RandomNicknames
from badgify.models import Badge, Award

from example.models import User

logger = logging.getLogger('example.fixtures')


class Command(BaseCommand):
    """
    Creates fixtures.
    """
    help = u'Create fixtures'

    option_list = BaseCommand.option_list + (
        make_option('--flushdb',
            action='store_true',
            dest='flushdb'),)

    def handle(self, *args, **options):
        self.flushdb = options.get('flushdb')
        self._pre_tasks()
        self._create_users()
        self._create_badges()
        self._create_awards()

    def _pre_tasks(self):
        if self.flushdb:
            management.call_command('flush', verbosity=0, interactive=False)
            logger.info('Flushed database')

    def _create_users(self):
        rn = RandomNicknames()
        for name in rn.random_nicks(count=50):
            username = '%s%d' % (slugify(name), random.randrange(1, 99))
            user = User.objects.create_user(
                username=username,
                email='%s@example.com' % username,
                password='secret')
            logger.info('Created user: %s', user.username)

    def _create_badges(self):
        rn = RandomNicknames()
        for name in rn.random_nicks(count=20):
            slug = slugify(name)
            badge = Badge.objects.create(
                name=name,
                slug=slug,
                description='Lorem ipsum dolor sit amet, consectetur adipisicing elit')
            logger.info('Created badge: %s', badge.name)

    def _create_awards(self):
        users = User.objects.all()
        for user in users:
            everyone_badge = Badge.objects.last()
            badge = Badge.objects.order_by('?')[0]
            try:
                award = Award.objects.create(user=user, badge=badge)
                everyone_award = Award.objects.create(user=user, badge=everyone_badge)
                logger.info('%s --- %s', award, everyone_award)
            except IntegrityError:
                pass
