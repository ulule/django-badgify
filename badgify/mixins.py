# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import collections
import logging

logger = logging.getLogger('badgify')


class RegistryDatabaseOpsMixin(object):
    """
    Registry mixin that adds database operations.
    """

    def syncdb(self):
        """
        Iterates over registered recipes and creates missing badges.
        """
        from django.db import IntegrityError
        from .models import Badge

        created, failed = [], []

        for instance in self.get_recipe_instances():
            try:
                Badge.objects.get(slug=instance.slug)
            except Badge.DoesNotExist:
                try:
                    badge = Badge.objects.create(
                        name=instance.name,
                        slug=instance.slug,
                        description=instance.description,
                        image=instance.image)
                    created.append(badge)
                    logger.debug('✓ Badge %s: created', badge.slug)
                except IntegrityError:
                    failed.append(instance.slug)

        if failed:
            for badge in failed:
                logger.error('✘ Badge %s: IntegrityError', badge)

        return (created, failed)

    def sync_users_count(self, connection=None):
        """
        Iterates over registered recipes and denormalizes ``Badge.users.count()``
        into ``Badge.users_count`` field.
        """
        updated, unchanged = [], []

        for instance in self.get_recipe_instances():

            badge = self.get_recipe_instance_badge(instance)
            if not badge:
                continue

            logger.debug('→ Badge %s: syncing counts...', badge.slug)

            old_value, new_value = badge.users_count, badge.users.count()
            if old_value != new_value:
                badge.users_count = new_value
                badge.save()
                updated.append(badge)
                logger.debug('✓ Badge %s: updated users count (from %d to %d)',
                    badge.slug, old_value, new_value)
                continue

            unchanged.append(badge)
            logger.debug('✓ Badge %s: users count up-to-date (%d)', badge.slug, new_value)

        return (updated, unchanged)

    def sync_awards(self, connection=None, batch_size=None, badges=None):
        """
        Iterates over registered recipes and possibly creates awards.
        """
        from django.db import IntegrityError
        from django.db.models import signals

        from .models import Award
        from .utils import get_user_ids_for_badge, get_award_objects_for_badge

        for instance in self.get_recipe_instances(badges=badges):

            badge = self.get_recipe_instance_badge(instance)
            if not badge:
                continue

            logger.debug('→ Badge %s: syncing awards...', badge.slug)

            user_ids, user_ids_count = get_user_ids_for_badge(
                badge=badge,
                user_querysets=instance.user_queryset,
                connection=connection)

            if not user_ids_count:
                logger.debug('✓ Badge %s: no new awards', badge.slug)
                continue

            logger.debug('→ Badge %s: found %d awards to save', badge.slug, user_ids_count)

            objects = get_award_objects_for_badge(
                badge=badge,
                user_ids=user_ids,
                connection=connection,
                batch_size=batch_size)

            try:
                Award.objects.bulk_create(objects, batch_size=batch_size)
                logger.debug('✓ Badge %s: created %d awards', badge.slug, user_ids_count)
                for obj in objects:
                    signals.post_save.send(
                        sender=obj.__class__,
                        instance=obj,
                        created=True,
                        raw=True)
            except IntegrityError:
                logger.error('✘ Badge %s: IntegrityError for %d awards', badge.slug, user_ids_count)
