# -*- coding: utf-8 -*-
import collections
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from badgify import settings, registry


class Command(BaseCommand):
    """
    Command that synchronizes badges, awards and counts.
    """
    help = u'Synchronizes badges, awards and counts.'

    option_list = BaseCommand.option_list + (
        make_option('--badges',
            action='store',
            dest='badges',
            type='string'),)

    def handle(self, *args, **options):
        self.options = options
        self._sanitize_options()
        commands = collections.OrderedDict([
            ('badges', self.sync_badges),
            ('awards', self.sync_awards),
            ('users_count', self.sync_users_count),
        ])
        if not len(args):
            if settings.ENABLE_BADGE_USERS_COUNT_SIGNAL:
                del commands['users_count']
            for cmd in commands.itervalues():
                cmd()
            return
        if len(args) > 1:
            raise CommandError('This command only accepts: %s' % ', '.join(commands))
        if len(args) == 1:
            arg = args[0]
            if arg not in commands.keys():
                raise CommandError('"%s" is not a valid command. Use: %s' % (
                    arg,
                    ', '.join(commands)))
            commands[arg]()

    def sync_badges(self):
        registry.sync_badges(**self.options)

    def sync_users_count(self):
        registry.sync_users_count(**self.options)

    def sync_awards(self):
        registry.sync_awards(**self.options)

    def _sanitize_options(self):
        self._sanitize_badges()

    def _sanitize_badges(self):
        badges = self.options.get('badges')
        if badges:
            self.options['badges'] = [b for b in badges.split(' ') if b]
