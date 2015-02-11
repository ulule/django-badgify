# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from badgify.commands import reset_awards


class Command(BaseCommand):
    """
    Commands that resets awards.
    """
    help = 'Resets awards.'

    def handle(self, *args, **options):
        reset_awards(**options)
