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

    def get_missing_user_ids(self):
        """
        Returns a tuple of missing unique user IDs and number of IDS for the given
        QuerySet list and badge.
        """
        from django.db import connections
        existing_ids = self.badge.users.using(self.db_read).values_list('id', flat=True)
        logger.debug(
            "→ Badge %s: %d users already awarded (fetched from db '%s')",
            self.slug,
            len(existing_ids),
            self.db_read)

        current_ids = self.user_ids.using(self.db_read)
        logger.debug(
            "→ Badge %s: %d users to check (fetched from db '%s')",
            self.slug,
            len(current_ids),
            self.db_read)

        missing_ids = list(set(current_ids) - set(existing_ids))
        logger.debug(
            '→ Badge %s: %d users need to be awarded',
            self.slug, len(missing_ids))

        return list(set(current_ids) - set(existing_ids))

    def get_award_objects(self):
        """
        Returns a list of ``Award`` objects ready to be saved.
        """
        User = get_user_model()
        ids = self.get_missing_user_ids()
        ids_limit = self.user_ids_limit
        ids_count = len(ids)
        if not ids:
            return
        awards = []
        done_ids = 0
        for user_ids in chunks(ids, ids_limit):
            done_ids += ids_limit
            logger.debug(
                "→ Badge %s: building award objects -- fetching %d of %d users "
                "(db '%s')",
                self.slug,
                done_ids,
                ids_count,
                self.db_read)
            for user in User.objects.using(self.db_read).filter(id__in=user_ids):
                awards.append(Award(user=user, badge=self.badge))
        return awards

    def create_awards(self):
        """
        Create awards.
        """
        logger.debug('✓ Badge %s: finding awards...', self.badge.slug)

        awards = self.get_award_objects() or []

        if not awards:
            return

        count = len(awards)
        batch_size = self.award_batch_size

        try:
            Award.objects.bulk_create(awards, batch_size=batch_size)
            logger.debug('✓ Badge %s: created %d awards (%d items by insert)',
                self.slug,
                count,
                batch_size)
            for obj in awards:
                signals.post_save.send(
                    sender=obj.__class__,
                    instance=obj,
                    created=True,
                    raw=True)
        except IntegrityError:
            logger.error('✘ Badge %s: IntegrityError for %d awards', self.slug, count)
