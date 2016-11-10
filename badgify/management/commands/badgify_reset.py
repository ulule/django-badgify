# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from badgify.commands import reset_awards
from badgify.utils import sanitize_command_options


class Command(BaseCommand):
    """
    Commands that resets awards.
    """
    help = 'Resets awards'

    def add_arguments(self, parser):
        """
        Command arguments.
        """
        parser.add_argument('--badges',
                            action='store',
                            dest='badges',
                            type=str)

        parser.add_argument('--exclude-badges',
                            action='store',
                            dest='exclude_badges',
                            type=str)

    def handle(self, **options):
        """
        Command handler.
        """
        reset_awards(**sanitize_command_options(options))
