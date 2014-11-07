# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.db import IntegrityError
from django.db.models import signals

from . import registry
from . import settings
from .models import Badge, Award
from .utils import get_user_ids_for_badge, get_award_objects_for_badge

logger = logging.getLogger(__name__)


def sync_badges(**kwargs):
    """
    Synchronizes badges from recipes.
    """
    badges = Badge.objects.all()
    new_badges = []

    for slug in registry.recipes:
        recipe = registry.recipes[slug]
        try:
            badges.get(slug=slug)
        except Badge.DoesNotExist:
            try:
                badge = badges.create(
                    name=recipe.name,
                    slug=slug,
                    description=recipe.description,
                    image=recipe.image)
                new_badges.append(badge)
            except IntegrityError:
                logger.debug('✘ IntegrityError for badge: %s', slug)

    if len(new_badges):
        for badge in new_badges:
            logger.debug('✓ Created new badge: %s', badge.name)


def sync_awards(**kwargs):
    """
    Loads registered recipes and synchronizes awards.
    """
    batch_size = kwargs.get('batch_size', None)

    if batch_size is None:
        batch_size = settings.AWARD_BULK_CREATE_BATCH_SIZE

    for slug in registry.recipes:

        recipe = registry.recipes[slug]
        badge = recipe.badge
        user_querysets = recipe.user_queryset

        user_ids, user_ids_count = get_user_ids_for_badge(
            badge=badge,
            user_querysets=user_querysets)

        if not user_ids_count:
            logger.debug('✓ No new awards for badge %s', badge.name)
            continue

        logger.debug('→ Found %s awards to save for badge %s...',
            user_ids_count,
            badge.name)

        objects = get_award_objects_for_badge(
            badge=badge,
            user_ids=user_ids,
            batch_size=batch_size)

        try:
            Award.objects.bulk_create(objects, batch_size=batch_size)
            logger.debug('✓ Created %d awards for badge %s', user_ids_count, badge.name)
            for obj in objects:
                signals.post_save.send(
                    sender=obj.__class__,
                    instance=obj,
                    created=True,
                    raw=True)
        except IntegrityError:
            logger.error('✘ IntegrityError for %d awards', user_ids_count)


def sync_counts(**kwargs):
    """
    Synchronizes badge counts.
    """
    for slug in registry.recipes:

        recipe = registry.recipes[slug]
        badge = recipe.badge
        logger.debug('→ Start computing counts for badge %s...', badge.name)

        old_value = badge.users_count
        new_value = badge.users.count()

        if old_value != new_value:
            badge.users_count = new_value
            badge.save()
            logger.debug('✓ Updated users count for badge %s (from %d to %d)',
                badge.name,
                old_value,
                new_value)
            continue

        logger.debug('✓ Users count for badge %s is already up-to-date (%d)',
            badge.name,
            new_value)
