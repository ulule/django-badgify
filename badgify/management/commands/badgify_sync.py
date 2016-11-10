# -*- coding: utf-8 -*-
from django.core.management.base import CommandError, LabelCommand

from badgify import commands
from badgify.utils import sanitize_command_options


class Command(LabelCommand):
    """
    Command that synchronizes badges, awards and counts.
    """
    help = 'Synchronizes badges, awards and counts'

    def add_arguments(self, parser):
        """
        Command arguments.
        """
        super(Command, self).add_arguments(parser)

        parser.add_argument('--badges',
                            action='store',
                            dest='badges',
                            type=str)

        parser.add_argument('--db-read',
                            action='store',
                            dest='db_read',
                            type=str)

        parser.add_argument('--disable-signals',
                            action='store_true',
                            dest='disable_signals')

        parser.add_argument('--batch-size',
                            action='store',
                            dest='batch_size',
                            type=int)

        parser.add_argument('--update',
                            action='store_true',
                            dest='update')

        parser.add_argument('--exclude-badges',
                            action='store',
                            dest='exclude_badges',
                            type=str)

    def handle_label(self, label, **options):
        """
        Command handler.
        """
        if not hasattr(commands, 'sync_%s' % label):
            raise CommandError('"%s" is not a valid command.' % label)

        getattr(commands, 'sync_%s' % label)(**sanitize_command_options(options))
