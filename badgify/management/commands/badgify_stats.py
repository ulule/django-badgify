# -*- coding: utf-8 -*-
from optparse import make_option

from django.core.management.base import BaseCommand

from badgify.commands import show_stats


class Command(BaseCommand):
    """
    Commands that shows badge stats.
    """
    help = 'Shows badge stats.'

    option_list = BaseCommand.option_list + (
        make_option('--db-read',
            action='store',
            dest='db_read',
            type='string'),
    )

    def handle(self, *args, **options):
        show_stats(**options)
