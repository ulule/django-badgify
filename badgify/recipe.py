# -*- coding: utf-8 -*-
from django.utils.functional import cached_property

from .models import Badge


class BaseRecipe(object):
    """
    Base class for badge recipes.
    """

    # Badge.name
    name = None

    # Badge.slug
    slug = None

    # Badge.description
    description = None

    # The default Badge QuerySet used to retrieve the related badge
    queryset = Badge.objects.all()

    @property
    def image(self):
        raise NotImplementedError('Image must be implemented')

    @property
    def user_queryset(self):
        raise NotImplementedError('User QuerySet must be implemented or just User.objects.none()')

    @cached_property
    def badge(self):
        return self.queryset.get(slug=self.slug)
