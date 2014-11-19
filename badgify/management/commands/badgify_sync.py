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
        commands = collections.OrderedDict([
            ('badges', self.sync_badges),
            ('awards', self.sync_awards),
            ('users_count', self.sync_users_count),
        ])
        if not len(args):
            if settings.ENABLE_BADGE_USERS_COUNT_SIGNAL:
                del commands['users_count']
            for cmd in commands.itervalues():
                cmd(**options)
            return
        if len(args) > 1:
            raise CommandError('This command only accepts: %s' % ', '.join(commands))
        if len(args) == 1:
            arg = args[0]
            if arg not in commands.keys():
                raise CommandError('"%s" is not a valid command. Use: %s' % (
                    arg,
                    ', '.join(commands)))
            commands[arg](**options)

    def sync_badges(self, **options):
        """
        Synchronizes badges.
        """
        registry.sync_badges(**options)

    def sync_users_count(self, **options):
        """
        Denormalizes ``Badge.users.count()`` into ``badge.users_count`` field.
        """
        registry.sync_users_count(**options)

    def sync_awards(self, **options):
        """
        Synchronizes awards.
        """
        registry.sync_awards(**options)

    def _get_option_badges(kwargs):
        """
        Takes a kwargs dictionary, looks for ``badges`` key and returns
        either the normalized slugs from ``badges`` key value if defined or ``None``.
        """
        badges = kwargs.get('badges', None)
        if badges:
            badges = [b for b in badges.split(' ') if b]
        return badges
