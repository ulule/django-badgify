# -*- coding: utf-8 -*-
from django.db import reset_queries

from . import registry
from .utils import log_queries


def sync_badges(**kwargs):
    """
    Iterates over registered recipes and creates missing badges.
    """
    created_badges, failed_badges = [], []
    instances = registry.get_recipe_instances()

    for instance in instances:
        reset_queries()
        badge, created, failed = instance.create_badge()
        if created:
            created_badges.append(badge)
        if failed:
            failed_badges.append(instance.slug)
        log_queries(instance)

    return (created_badges, failed_badges)


def sync_users_count(**kwargs):
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

    instances = registry.get_recipe_instances(badges=badges, excluded=excluded)

    for instance in instances:
        reset_queries()
        instance.create_awards()
        log_queries(instance)
