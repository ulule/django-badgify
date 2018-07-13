# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify

from badgify import compat, settings


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
