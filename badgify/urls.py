from django.urls import re_path as url

from .views import BadgeListView, BadgeDetailView


urlpatterns = [
    url(r'^$', BadgeListView.as_view(), name='badge_list'),
    url(r'^(?P<slug>[\w-]+)/$', BadgeDetailView.as_view(), name='badge_detail'),
]
