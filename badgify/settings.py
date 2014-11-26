# -*- coding: utf-8 -*-
import os

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

from django.conf import settings
from django.core.files.storage import FileSystemStorage


APP_NAMESPACE = 'BADGIFY'


BADGE_IMAGE_UPLOAD_ROOT = getattr(
    settings,
    '%s_IMAGE_UPLOAD_ROOT' % APP_NAMESPACE,
    os.path.join(getattr(settings, 'MEDIA_ROOT', 'media/'), 'uploads'))

BADGE_IMAGE_UPLOAD_URL = getattr(
    settings,
    '%s_MEDIA_URL' % APP_NAMESPACE,
    urljoin(getattr(settings, 'MEDIA_URL', '/media/'), 'uploads/'))

BADGE_IMAGE_UPLOAD_STORAGE = getattr(
    settings,
    '%s_BADGE_IMAGE_UPLOAD_STORAGE' % APP_NAMESPACE,
    FileSystemStorage(
        location=BADGE_IMAGE_UPLOAD_ROOT,
        base_url=BADGE_IMAGE_UPLOAD_URL))

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

MAX_AWARDS_PER_CREATE = getattr(
    settings,
    '%s_MAX_AWARDS_PER_CREATE' % APP_NAMESPACE,
    500)

AUTO_DENORMALIZE = getattr(
    settings,
    '%s_AUTO_DENORMALIZE' % APP_NAMESPACE,
    True)
