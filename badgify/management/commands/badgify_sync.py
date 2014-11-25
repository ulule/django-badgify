# -*- coding: utf-8 -*-
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from badgify import commands


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

        make_option('--auto-denormalize',
            action='store',
            dest='auto_denormalize',
            type='string'),

        make_option('--award-post-save',
            action='store',
            dest='award_post_save',
            type='string'),

        make_option('--update',
            action='store_true',
            dest='update'),

        make_option('--exclude-badges',
            action='store',
            dest='exclude_badges',
            type='string'),
    )

    def handle(self, *args, **options):
        options = self.sanitize_options(options)
        cmds = ('badges', 'awards', 'users_count')
        if not len(args):
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
        switchers = [
            'auto_denormalize',
            'award_post_save',
        ]

        multiple_options = [
            'badges',
            'exclude_badges',
        ]

        for option in switchers:
            value = options[option]
            if value:
                if value not in ('on', 'off'):
                    raise CommandError('Option "%s" only takes "on" or "off"' % option)
                options[option] = True if value == 'on' else False

        for option in multiple_options:
            value = options[option]
            if value:
                options[option] = [v for v in value.split(' ') if v]

        return options
