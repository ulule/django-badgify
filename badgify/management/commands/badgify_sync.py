# -*- coding: utf-8 -*-
from optparse import make_option

from django.core.management.base import LabelCommand, CommandError

from badgify import commands


class Command(LabelCommand):
    """
    Command that synchronizes badges, awards and counts.
    """
    help = u'Synchronizes badges, awards and counts.'

    option_list = LabelCommand.option_list + (

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

    def handle_label(self, label, **options):
        options = self.sanitize_options(options)
        if not hasattr(commands, 'sync_%s' % label):
            raise CommandError('"%s" is not a valid command.' % label)
        getattr(commands, 'sync_%s' % label)(**options)

    def sanitize_options(self, options):
        options = self.sanitize_multiples(options)
        options = self.sanitize_switchers(options)
        return options

    @staticmethod
    def sanitize_multiples(options):
        multiples = ['badges', 'exclude_badges']
        for option in multiples:
            value = options[option]
            if value:
                options[option] = [v for v in value.split(' ') if v]
        return options

    @staticmethod
    def sanitize_switchers(options):
        switchers = ['auto_denormalize', 'award_post_save']
        for option in switchers:
            value = options[option]
            if value:
                if value not in ('on', 'off'):
                    raise CommandError('Option "%s" only takes "on" or "off"' % option)
                options[option] = True if value == 'on' else False
        return options
