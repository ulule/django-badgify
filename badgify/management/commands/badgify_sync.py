# -*- coding: utf-8 -*-
import collections
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from badgify.commands import sync_badges, sync_awards, sync_counts
from badgify import settings


COMMANDS = collections.OrderedDict([
    ('badges', sync_badges),
    ('awards', sync_awards),
    ('counts', sync_counts),
])


class Command(BaseCommand):
    """
    Command that synchronizes badges, awards and counts.
    """
    help = u'Synchronizes badges, awards and counts.'

    option_list = BaseCommand.option_list + (
        make_option('--batch-size',
            action='store',
            dest='batch_size',
            type='int'),
        make_option('--badges',
            action='store',
            dest='badges'),
        make_option('--connection',
            action='store',
            dest='connection'))

    def handle(self, *args, **options):
        if not len(args):
            if settings.ENABLE_BADGE_USERS_COUNT_SIGNAL:
                del COMMANDS['counts']
            for cmd in COMMANDS.itervalues():
                cmd(**options)
            return
        if len(args) > 1:
            raise CommandError('This command only accepts: %s' % ', '.join(COMMANDS))
        if len(args) == 1:
            arg = args[0]
            if arg not in COMMANDS.keys():
                raise CommandError('"%s" is not a valid command. Use: %s' % (
                    arg,
                    ', '.join(COMMANDS)))
            COMMANDS[arg](**options)
