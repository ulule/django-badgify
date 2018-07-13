# -*- coding: utf-8 -*-
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from .models import Badge, Award
from . import settings


class BadgeAdmin(admin.ModelAdmin):
    """
    Badge model admin options.
    """
    list_display = ('name', 'description', 'link', 'image_thumbnail')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug', 'description')

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{0}" width="80">', obj.image.url)
        return '<img src="http://placehold.it/80x80">'
    image_thumbnail.short_description = _('image')
    image_thumbnail.allow_tags = True

    def link(self, obj):
        return format_html('<a href="{0}">{1}</a>',
                           self.view_on_site(obj),
                           self.view_on_site(obj))
    link.short_description = _('link')
    link.allow_tags = True

    def view_on_site(self, obj):
        return reverse('badge_detail', kwargs={'slug': obj.slug})


class AwardAdmin(admin.ModelAdmin):
    """
    Award model admin options.
    """
    list_display = ('user', 'badge', 'awarded_at')
    date_hierarchy = 'awarded_at'
    list_filter = ('badge',)
    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__email',
        'badge__name',
        'badge__slug',
        'badge__description')


if settings.REGISTER_ADMIN:
    admin.site.register(Badge, BadgeAdmin)
    admin.site.register(Award, AwardAdmin)
