# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.db import DEFAULT_DB_ALIAS, IntegrityError
from django.db.models import signals
from django.utils.functional import cached_property

from . import settings
from .compat import get_user_model
from .models import Badge, Award
from .utils import chunks

logger = logging.getLogger('badgify')

PRE_DELETE_UID = 'badgify.award.pre_delete.decrement_badge_users_count'


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

    # How many awards to create at once
    batch_size = settings.BATCH_SIZE

    @property
    def image(self):
        raise NotImplementedError('Image must be implemented')

    @property
    def user_ids(self):
        pass

    @property
    def badge(self):
        return self.cached_badge or self.uncached_badge

    @cached_property
    def cached_badge(self):
        return self.get_badge()

    @property
    def uncached_badge(self):
        return self.get_badge()

    def get_badge(self):
        """
        The related ``Badge`` object.
        """
        try:
            obj = Badge.objects.using(self.db_read).get(slug=self.slug)
            logger.debug('✓ Badge %s: fetched from db (%s)', obj.slug, self.db_read)
        except Badge.DoesNotExist:
            obj = None
        return obj

    def create_badge(self, update=False):
        """
        Saves the badge in the database (or updates it if ``update`` is ``True``).
        Returns a tuple: ``badge`` (the badge object) and ``created`` (``True``, if
        badge has been created).
        """
        badge, created = self.badge, False
        if badge:
            logger.debug('✓ Badge %s: already created', badge.slug)
            if update:
                to_update = {}
                for field in ('name', 'slug', 'description', 'image'):
                    attr = getattr(self, field)
                    badge_attr = getattr(badge, field)
                    if attr != badge_attr:
                        to_update[field] = attr
                        logger.debug('✓ Badge %s: updated "%s" field', self.slug, field)
                Badge.objects.filter(id=badge.id).update(**to_update)
        else:
            kwargs = {'name': self.name, 'image': self.image}
            optional_fields = ['slug', 'description']
            for field in optional_fields:
                value = getattr(self, field)
                if value is not None:
                    kwargs[field] = value
            badge = Badge.objects.create(**kwargs)
            created = True
            logger.debug('✓ Badge %s: created', badge.slug)
        return (badge, created)

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

    def update_badge_users_count(self):
        """
        Denormalizes ``Badge.users.count()`` into ``Bagdes.users_count`` field.
        """
        logger.debug('→ Badge %s: syncing users count...', self.slug)

        badge, updated = self.badge, False

        if not badge:
            logger.debug(
                '✘ Badge %s: does not exist in the database (run badgify_sync badges)',
                self.slug)
            return (self.slug, updated)

        old_value, new_value = badge.users_count, badge.users.count()

        if old_value != new_value:
            badge = Badge.objects.get(slug=self.slug)
            badge.users_count = new_value
            badge.save()
            updated = True

        if updated:
            logger.debug('✓ Badge %s: updated users count (from %d to %d)',
                         self.slug,
                         old_value,
                         new_value)
        else:
            logger.debug('✓ Badge %s: users count up-to-date (%d)',
                         self.slug,
                         new_value)

        return (badge, updated)

    def get_already_awarded_user_ids(self, db_read=None, show_log=True):
        """
        Returns already awarded user ids and the count.
        """

        db_read = db_read or self.db_read

        already_awarded_ids = self.badge.users.using(db_read).values_list('id', flat=True)
        already_awarded_ids_count = len(already_awarded_ids)

        if show_log:
            logger.debug(
                "→ Badge %s: %d users already awarded (fetched from db '%s')",
                self.slug,
                already_awarded_ids_count,
                db_read)

        return already_awarded_ids

    def get_current_user_ids(self, db_read=None):
        """
        Returns current user ids and the count.
        """
        db_read = db_read or self.db_read

        return self.user_ids.using(db_read)

    def get_unawarded_user_ids(self, db_read=None):
        """
        Returns unawarded user ids (need to be saved) and the count.
        """
        db_read = db_read or self.db_read

        already_awarded_ids = self.get_already_awarded_user_ids(db_read=db_read)
        current_ids = self.get_current_user_ids(db_read=db_read)
        unawarded_ids = list(set(current_ids) - set(already_awarded_ids))
        unawarded_ids_count = len(unawarded_ids)

        logger.debug(
            '→ Badge %s: %d users need to be awarded',
            self.slug,
            unawarded_ids_count)

        return (unawarded_ids, unawarded_ids_count)

    def get_obsolete_user_ids(self, db_read=None):
        """
        Returns obsolete users IDs to unaward.
        """
        db_read = db_read or self.db_read

        already_awarded_ids = self.get_already_awarded_user_ids(db_read=db_read, show_log=False)
        current_ids = self.get_current_user_ids(db_read=db_read)
        obsolete_ids = list(set(already_awarded_ids) - set(current_ids))
        obsolete_ids_count = len(obsolete_ids)

        logger.debug(
            '→ Badge %s: %d users need to be unawarded',
            self.slug,
            obsolete_ids_count)

        return (obsolete_ids, obsolete_ids_count)

    def create_awards(self, db_read=None, batch_size=None,
                      post_save_signal=True):
        """
        Create awards.
        """
        if not self.can_perform_awarding():
            return

        User = get_user_model()

        db_read = db_read or self.db_read
        batch_size = batch_size or self.batch_size

        unawarded_ids, unawarded_ids_count = self.get_unawarded_user_ids(db_read=db_read)
        obsolete_ids, obsolete_ids_count = self.get_obsolete_user_ids(db_read=db_read)

        if obsolete_ids:
            for user_ids in chunks(obsolete_ids, batch_size):
                obsolete_users = User.objects.using(db_read).in_bulk(user_ids).values()

                signals.pre_delete.disconnect(sender=Award, dispatch_uid=PRE_DELETE_UID)
                Award.objects.filter(user__in=user_ids).delete()

                logger.debug("→ Badge %s (db_read: %s): unawarded %s",
                             self.slug,
                             db_read,
                             ' '.join(['%s' % user for user in obsolete_users]))

        if unawarded_ids:
            for user_ids in chunks(unawarded_ids, batch_size):
                unwarded_users = User.objects.using(db_read).in_bulk(user_ids).values()
                objects = [Award(user_id=user_id, badge=self.badge) for user_id in user_ids]

                bulk_create_awards(objects=objects,
                                   batch_size=batch_size,
                                   post_save_signal=post_save_signal)

                logger.debug("→ Badge %s (db_read: %s): awarded %s",
                             self.slug,
                             db_read,
                             ' '.join(['%s' % user for user in unwarded_users]))


def bulk_create_awards(objects, batch_size=500, post_save_signal=True):
    """
    Saves award objects.
    """
    count = len(objects)
    if not count:
        return
    badge = objects[0].badge
    try:
        Award.objects.bulk_create(objects, batch_size=batch_size)
        if post_save_signal:
            for obj in objects:
                signals.post_save.send(sender=obj.__class__, instance=obj, created=True)
    except IntegrityError:
        logger.error('✘ Badge %s: IntegrityError for %d awards', badge.slug, count)
