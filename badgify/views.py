# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.views.generic import ListView

from .models import Badge
from . import settings


class BadgeListView(ListView):
    """
    Badge list view.
    """
    model = Badge
    context_object_name = 'badges'
    template_name = 'badgify/badge_list.html'
    paginate_by = settings.BADGE_LIST_VIEW_PAGINATE_BY


class BadgeDetailView(ListView):
    """
    Badge detail view.
    """
    model = Badge
    template_name = 'badgify/badge_detail.html'
    context_object_name = 'awarded_users'
    paginate_by = settings.BADGE_DETAIL_VIEW_PAGINATE_BY

    @cached_property
    def badge(self):
        return get_object_or_404(self.model, slug=self.kwargs.get('slug', None))

    def get_queryset(self):
        return self.badge.users.all()

    def get_context_data(self, **kwargs):
        context = super(BadgeDetailView, self).get_context_data(**kwargs)
        context['badge'] = self.badge
        return context
