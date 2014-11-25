# -*- coding: utf-8 -*-
import collections
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from badgify import settings, commands


class Command(BaseCommand):
    """
    Command that synchronizes badges, awards and counts.
    """
    help = u'Synchronizes badges, awards and counts.'

    option_list = BaseCommand.option_list + (
        make_option('--badges',
            action='store',
            dest='badges',
            type='string'),
        make_option('--update',
            action='store_true',
            dest='update'),
        make_option('--exclude-badges',
            action='store',
            dest='exclude_badges',
            type='string'))

    def handle(self, *args, **options):
        options = self.sanitize_options(options)
        cmds = ('badges', 'awards', 'users_count')
        if not len(args):
            if settings.ENABLE_BADGE_USERS_COUNT_SIGNAL:
                del cmds['users_count']
            for cmd in cmds:
                getattr(commands, 'sync_%s' % cmd)(**options)
            return
        if len(args) > 1:
            raise CommandError('This command only accepts: %s' % ', '.join(cmds))
        if len(args) == 1:
            arg = args[0]
            if arg not in cmds:
                raise CommandError('"%s" is not a valid command. Use: %s' % (
                    arg,
                    ', '.join(cmds)))
            getattr(commands, 'sync_%s' % arg)(**options)

    @staticmethod
    def sanitize_options(options):
        for option in ('badges', 'exclude_badges'):
            badges = options[option]
            if badges:
                options[option] = [b for b in badges.split(' ') if b]
        return options
