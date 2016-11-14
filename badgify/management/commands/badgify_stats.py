# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from badgify.commands import show_stats


class Command(BaseCommand):
    """
    Commands that shows badge stats.
    """
    help = 'Shows badge stats'

    def add_arguments(self, parser):
        """
        Command arguments.
        """
        parser.add_argument('--db-read',
                            action='store',
                            dest='db_read',
                            type=str)

    def handle(self, **options):
        """
        Command handler.
        """
        show_stats(**options)
