# -*- coding: utf-8 -*-
from django.conf import settings


APP_NAMESPACE = 'BADGIFY'

REGISTER_ADMIN = getattr(
    settings,
    '%s_REGISTER_ADMIN' % APP_NAMESPACE,
    True)


BADGE_IMAGE_UPLOAD_ROOT = getattr(
    settings,
    '%s_IMAGE_UPLOAD_ROOT' % APP_NAMESPACE,
    'badges')

BADGE_LIST_VIEW_PAGINATE_BY = getattr(
    settings,
    '%s_BADGE_LIST_VIEW_PAGINATE_BY' % APP_NAMESPACE,
    20)

BADGE_DETAIL_VIEW_PAGINATE_BY = getattr(
    settings,
    '%s_BADGE_DETAIL_VIEW_PAGINATE_BY' % APP_NAMESPACE,
    20)

BADGE_MODEL = getattr(
    settings,
    '%s_BADGE_MODEL' % APP_NAMESPACE,
    'badgify.models.badge.Badge')

AWARD_MODEL = getattr(
    settings,
    '%s_AWARD_MODEL' % APP_NAMESPACE,
    'badgify.models.award.Award')

BATCH_SIZE = getattr(
    settings,
    '%s_BATCH_SIZE' % APP_NAMESPACE,
    500)

AUTO_DENORMALIZE = getattr(
    settings,
    '%s_AUTO_DENORMALIZE' % APP_NAMESPACE,
    True)
