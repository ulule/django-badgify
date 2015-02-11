# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.db import reset_queries, DEFAULT_DB_ALIAS
from django.db.models import Count, signals

from . import registry
from . import settings
from .models import Badge, Award
from .utils import log_queries

logger = logging.getLogger('badgify')


def sync_badges(**kwargs):
    """
    Iterates over registered recipes and creates missing badges.
    """
    update = kwargs.get('update', False)
    created_badges = []
    instances = registry.get_recipe_instances()

    for instance in instances:
        reset_queries()
        badge, created = instance.create_badge(update=update)
        if created:
            created_badges.append(badge)
        log_queries(instance)

    return created_badges


def sync_counts(**kwargs):
    """
    Iterates over registered recipes and denormalizes ``Badge.users.count()``
    into ``Badge.users_count`` field.
    """
    badges = kwargs.get('badges')
    excluded = kwargs.get('exclude_badges')

    instances = registry.get_recipe_instances(badges=badges, excluded=excluded)
    updated_badges, unchanged_badges = [], []

    for instance in instances:
        reset_queries()
        badge, updated = instance.update_badge_users_count()
        if updated:
            updated_badges.append(badge)
        else:
            unchanged_badges.append(badge)
        log_queries(instance)

    return (updated_badges, unchanged_badges)


def sync_awards(**kwargs):
    """
    Iterates over registered recipes and possibly creates awards.
    """
    badges = kwargs.get('badges')
    excluded = kwargs.get('exclude_badges')
    disable_signals = kwargs.get('disable_signals')
    batch_size = kwargs.get('batch_size', None)
    db_read = kwargs.get('db_read', None)

    award_post_save = True

    if disable_signals:
        settings.AUTO_DENORMALIZE = False
        award_post_save = False

    instances = registry.get_recipe_instances(badges=badges, excluded=excluded)

    for instance in instances:
        reset_queries()
        instance.create_awards(
            batch_size=batch_size,
            db_read=db_read,
            post_save_signal=award_post_save)
        log_queries(instance)


def show_stats(**kwargs):
    """
    Shows badges stats.
    """
    db_read = kwargs.get('db_read', DEFAULT_DB_ALIAS)

    badges = (Badge.objects.using(db_read)
                           .all()
                           .annotate(u_count=Count('users'))
                           .order_by('u_count'))

    for badge in badges:
        logger.info('{:<20} {:>10} users awarded | users_count: {})'.format(
            badge.name,
            badge.u_count,
            badge.users_count))


def reset_awards(**kwargs):
    """
    Resets badges stats.
    """
    filter_badges = kwargs.get('badges', None)
    exclude_badges = kwargs.get('exclude_badges', None)

    for option in [filter_badges, exclude_badges]:
        if option:
            if not isinstance(option, (list, tuple)):
                option = [option]

    signals.pre_delete.disconnect(sender=Award,
                                  dispatch_uid='badgify.award.pre_delete.decrement_badge_users_count')

    award_qs = Award.objects.all()
    badge_qs = Badge.objects.all()

    if filter_badges:
        award_qs = award_qs.filter(badge__slug__in=filter_badges)
        badge_qs = badge_qs.filter(slug__in=filter_badges)

    if exclude_badges:
        award_qs = award_qs.exclude(badge__slug__in=exclude_badges)
        badge_qs = badge_qs.exclude(slug__in=exclude_badges)

    awards_count = award_qs.count()
    award_qs.delete()
    logger.info('✓ Deleted %d awards', awards_count)

    badges_count = badge_qs.count()
    badge_qs.update(users_count=0)
    logger.info('✓ Reseted Badge.users_count field of %d badge(s)', badges_count)
