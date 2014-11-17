# -*- coding: utf-8 -*-
from . import registry


def sync_badges(**kwargs):
    """
    Iterates over registered recipes and creates missing ``Badge`` objects.
    """
    registry.syncdb()


def sync_counts(**kwargs):
    """
    Iterates over registered recipes and denormalizes the awarded users count
    into ``Badge.users_count`` field to reduce database queries.
    """
    registry.sync_users_count()


def sync_awards(**kwargs):
    """
    Iterates over registered recipes and possibly creates awards.

    Takes three optional arguments:

        * ``connection``: the database alias passed to each recipe User QuerySet
        * ``batch_size``: how many ``Award`` object to create in a single query
        * ``badges``: only creates awards for the given badge slugs (separated by a space)

    """
    registry.sync_awards(
        connection=_get_option_connection(kwargs),
        batch_size=_get_option_batch_size(kwargs),
        badges=_get_option_badges(kwargs))


def _get_option_connection(kwargs):
    """
    Takes a kwargs dictionary, looks for ``connection`` key and returns either
    the ``connection`` key value if defined or ``django.db.DEFAULT_DB_ALIAS``.
    """
    from django.db import DEFAULT_DB_ALIAS
    connection = kwargs.get('connection', None)
    return connection if connection else DEFAULT_DB_ALIAS


def _get_option_batch_size(kwargs):
    """
    Takes a kwargs dictionary, looks for ``batch_size`` key and returns either the
    ``batch_size`` key value if defined or ``BADGIFY_AWARD_BULK_CREATE_BATCH_SIZE``
    setting value.
    """
    from .settings import AWARD_BULK_CREATE_BATCH_SIZE
    batch_size = kwargs.get('batch_size', None)
    return batch_size if batch_size else AWARD_BULK_CREATE_BATCH_SIZE


def _get_option_badges(kwargs):
    """
    Takes a kwargs dictionary, looks for ``badges`` key and returns
    either the normalized slugs from ``badges`` key value if defined or ``None``.
    """
    badges = kwargs.get('badges', None)
    if badges:
        badges = [b for b in badges.split(' ') if b]
    return badges
