# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify

from .. import compat
from ..utils import get_model_string
from . import settings


@python_2_unicode_compatible
class Badge(models.Model):
    """
    A Badge.
    """
    name = models.CharField(
        max_length=255,
        verbose_name=_('name'),
        help_text=_('The badge name'))

    slug = models.SlugField(
        max_length=255,
        blank=True,
        unique=True,
        verbose_name=_('slug'),
        help_text=_('The badge slug (auto-generated if empty)'))

    description = models.TextField(
        blank=True,
        verbose_name=_('description'),
        help_text=_('The badge description'))

    image = models.ImageField(null=True, blank=True,
                              verbose_name=_('Image'),
                              help_text=_('Please, upload an image for this badge'),
                              upload_to=settings.BADGE_IMAGE_UPLOAD_ROOT)

    users = models.ManyToManyField(
        compat.AUTH_USER_MODEL,
        through='Award',
        verbose_name=_('users'),
        help_text=_('Users that earned this badge'))

    users_count = models.IntegerField(
        default=0,
        verbose_name=_('users count'),
        editable=False)

    class Meta:
        abstract = True
        app_label = 'badgify'
        verbose_name = _('badge')
        verbose_name_plural = _('badges')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('badge_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super(Badge, self).save(*args, **kwargs)


@python_2_unicode_compatible
class Award(models.Model):
    """
    An Award.
    """
    user = models.ForeignKey(
        compat.AUTH_USER_MODEL,
        verbose_name=_('user'),
        related_name='badges')

    badge = models.ForeignKey(
        get_model_string('Badge'),
        verbose_name=_('badge'),
        related_name='awards')

    awarded_at = models.DateTimeField(
        verbose_name=_('awarded at'),
        auto_now_add=True)

    class Meta:
        abstract = True
        app_label = 'badgify'
        verbose_name = _('award')
        verbose_name_plural = _('awards')
        unique_together = (('user', 'badge'),)

    def __str__(self):
        return '%s earned %s' % (self.user, self.badge.name)
