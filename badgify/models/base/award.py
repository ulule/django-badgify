# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from badgify import compat
from badgify.utils import get_model_string


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
