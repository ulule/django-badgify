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

    auto_denormalize = kwargs.get('auto_denormalize')
    award_post_save = kwargs.get('award_post_save')

    if auto_denormalize is None:
        auto_denormalize = settings.AUTO_DENORMALIZE

    if award_post_save is None:
        award_post_save = settings.AWARD_POST_SAVE

    settings.AUTO_DENORMALIZE = False if not auto_denormalize else True

    instances = registry.get_recipe_instances(badges=badges, excluded=excluded)

    for instance in instances:
        reset_queries()
        instance.create_awards(post_save_signal=award_post_save)
        log_queries(instance)
