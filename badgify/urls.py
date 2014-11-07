# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from .views import BadgeListView, BadgeDetailView


urlpatterns = patterns(
    '',

    url(r'^$',
        BadgeListView.as_view(),
        name='badge_list'),

    url(r'^(?P<slug>[\w-]+)/$',
        BadgeDetailView.as_view(),
        name='badge_detail'),
)
