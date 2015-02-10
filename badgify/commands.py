# -*- coding: utf-8 -*-
from django.db import reset_queries

from . import registry
from . import settings
from .utils import log_queries


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
