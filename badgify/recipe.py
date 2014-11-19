# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.db import connection, connections, DEFAULT_DB_ALIAS, IntegrityError
from django.db.models import signals
from django.db.models.query import QuerySet
from django.utils.functional import cached_property

from . import settings
from .compat import get_user_model
from .models import Badge, Award
from .utils import chunks

logger = logging.getLogger('badgify')


class BaseRecipe(object):
    """
    Base class for badge recipes.
    """

    # Badge.name
    name = None

    # Badge.slug
    slug = None

    # Badge.description
    description = None

    # The database on which to perform read queries
    db_read = DEFAULT_DB_ALIAS

    # Maximum number of User IDs to retrieve by query (for SELECT IN)
    # Example: User.objects.filter(id__in=MAX_NUMBER)
    # The queryset will be chunked into multiple querysets of n max IDs.
    user_ids_limit = settings.USER_IDS_LIMIT

    # How many awards to create in a single query
    award_batch_size = settings.AWARD_BULK_CREATE_BATCH_SIZE

    @property
    def image(self):
        raise NotImplementedError('Image must be implemented')

    @property
    def user_ids(self):
        pass

    @property
    def badge(self):
        obj = None
        try:
            obj = Badge.objects.get(slug=self.slug)
        except Badge.DoesNotExist:
            pass
        return obj

    def can_perform_awarding(self):
        """
        Checks if we can perform awarding process (is ``user_ids`` property
        defined? Does Badge object exists? and so on). If we can perform db
        operations safely, returns ``True``. Otherwise, ``False``.
        """
        if not self.user_ids:
            logger.debug(
                '✘ Badge %s: no users to check (empty user_ids property)',
                self.slug)
            return False

        if not self.badge:
            logger.debug(
                '✘ Badge %s: does not exist in the database (run badgify_sync badges)',
                self.slug)
            return False

        return True

    def get_already_awarded_user_ids(self):
        """
        Returns already awarded user ids and the count.
        """
        already_awarded_ids = self.badge.users.values_list('id', flat=True)
        already_awarded_ids_count = len(already_awarded_ids)

        logger.debug(
            "→ Badge %s: %d users already awarded (fetched from db '%s')",
            self.slug,
            already_awarded_ids_count,
            self.db_read)

        return already_awarded_ids

    def get_current_user_ids(self):
        """
        Returns current user ids and the count.
        """
        current_ids = self.user_ids.using(self.db_read)
        current_ids_count = len(current_ids)

        logger.debug(
            "→ Badge %s: %d users to check (fetched from db '%s')",
            self.slug,
            current_ids_count,
            self.db_read)

        return current_ids

    def get_unawarded_user_ids(self):
        """
        Returns unawarded user ids (need to be saved) and the count.
        """
        already_awarded_ids = self.get_already_awarded_user_ids()
        current_ids = self.get_current_user_ids()
        unawarded_ids = list(set(current_ids) - set(already_awarded_ids))
        unawarded_ids_count = len(unawarded_ids)

        logger.debug(
            '→ Badge %s: %d users need to be awarded',
            self.slug,
            unawarded_ids_count)

        return (unawarded_ids, unawarded_ids_count)

    def get_award_objects(self):
        """
        Returns a list of ``Award`` objects ready to be saved.
        """
        User = get_user_model()
        unawarded_ids, unawarded_ids_count = self.get_unawarded_user_ids()

        if not unawarded_ids:
            return

        awards = []
        done_ids = 0

        for user_ids in chunks(unawarded_ids, self.user_ids_limit):
            done_ids += self.user_ids_limit
            actual_count = done_ids if done_ids <= unawarded_ids_count else unawarded_ids_count
            logger.debug(
                "→ Badge %s: building award objects -- %d on %d users "
                "(db '%s')",
                self.slug,
                actual_count,
                unawarded_ids_count,
                self.db_read)
            for user in User.objects.using(self.db_read).filter(id__in=user_ids):
                awards.append(Award(user=user, badge=self.badge))

        return awards

    def save_award_objects(self):
        """
        Saves award objects.
        """
        awards = self.get_award_objects()
        if not awards:
            return
        try:
            Award.objects.bulk_create(awards, batch_size=self.award_batch_size)
            logger.debug('✓ Badge %s: created %d awards (%d items by insert)',
                self.slug,
                len(awards),
                self.award_batch_size)
            for obj in awards:
                signals.post_save.send(
                    sender=obj.__class__,
                    instance=obj,
                    created=True,
                    raw=True)
        except IntegrityError:
            logger.error('✘ Badge %s: IntegrityError for %d awards', self.slug, count)

    def create_awards(self):
        """
        Create awards.
        """
        if self.can_perform_awarding():
            return self.save_award_objects()
