# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.db import DEFAULT_DB_ALIAS, IntegrityError
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

    # The default Badge QuerySet used to retrieve the related badge
    badge_queryset = Badge.objects.all()

    # The database on which to perform read-only queries for Badge model
    badge_db_read = DEFAULT_DB_ALIAS

    # The database on which to perform write queries for Badge model
    badge_db_write = DEFAULT_DB_ALIAS

    # Maximum number of User IDs to retrieve by query (for SELECT IN)
    # Example: User.objects.filter(id__in=MAX_NUMBER)
    # The queryset will be chunked into multiple querysets of n max IDs.
    user_ids_limit = settings.USER_IDS_LIMIT

    # The database on which to perform user read-only queries
    user_db_read = DEFAULT_DB_ALIAS

    # The database on which to perform Award write queries
    award_db_write = DEFAULT_DB_ALIAS

    # How many awards to create in a single query
    award_batch_size = settings.AWARD_BULK_CREATE_BATCH_SIZE

    @property
    def image(self):
        raise NotImplementedError('Image must be implemented')

    @property
    def user_ids(self):
        pass

    @cached_property
    def badge(self):
        obj = None
        try:
            obj = self.badge_queryset.using(self.badge_db_read).get(slug=self.slug)
        except Badge.DoesNotExist:
            pass
        return obj

    @classmethod
    def chunk_user_queryset(cls, ids):
        """
        Returns a list of multiple User QuerySet.
        """
        User = get_user_model()
        return [User.objects.using(cls.user_db_read).filter(id__in=ids)
                for chunked_ids in chunks(ids, cls.user_ids_limit)]

    def get_user_querysets(self):
        ids = self.user_ids
        if isinstance(self.user_ids, QuerySet):
            ids = list(ids)
        if ids:
            return self.chunk_user_queryset(ids=ids)

    def get_missing_user_ids(self):
        """
        Returns a tuple of missing unique user IDs and number of IDS for the given
        QuerySet list and badge.
        """
        querysets = self.get_user_querysets() or []
        querysets_count = len(querysets)
        user_db = self.user_db_read
        existing_ids = self.badge.users.values_list('id', flat=True)
        ids = []
        if querysets:
            logger.debug('→ Badge %s: retrieving user ids (user querysets count:%d, user db: %s)',
                self.slug,
                querysets_count,
                user_db)
        for qs in querysets:
            qs_ids = qs.using(user_db).values_list('id', flat=True)
            missing_ids = list(set(qs_ids) - set(existing_ids))
            ids = ids + missing_ids
        return list(set(ids))

    def get_award_objects(self):
        """
        Returns a list of ``Award`` objects ready to be saved.
        """
        User = get_user_model()
        user_ids = self.get_missing_user_ids()
        user_ids_limit = self.user_ids_limit
        user_ids_count = len(user_ids)
        user_db = self.user_db_read
        if not user_ids:
            logger.debug('→ Badge %s: no awards', self.slug)
            return
        logger.debug("→ Badge %s: building award objects (user ids count: %d, user ids limit: %d, user db:%s)",
            self.slug,
            user_ids_count,
            user_ids_limit,
            user_db)
        return [Award(user=user, badge=self.badge)
                       for ids in chunks(user_ids, user_ids_limit)
                       for user in User.objects.using(user_db).filter(id__in=user_ids)]

    def create_awards(self):
        """
        Create awards.
        """
        awards = self.get_award_objects() or []
        count = len(awards)
        db = self.award_db_write
        batch_size = self.award_batch_size
        if not awards:
            return
        try:
            Award.objects.using(db).bulk_create(awards, batch_size=batch_size)
            logger.debug('✓ Badge %s: created %d awards (batch size: %d, award db: %s)',
                self.slug,
                count,
                db)
            for obj in awards:
                signals.post_save.send(
                    sender=obj.__class__,
                    instance=obj,
                    created=True,
                    raw=True)
        except IntegrityError:
            logger.error('✘ Badge %s: IntegrityError for %d awards',
                self.slug,
                count)
