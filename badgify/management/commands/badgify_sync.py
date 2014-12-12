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

        make_option('--db-read',
            action='store',
            dest='db_read',
            type='string'),

        make_option('--disable-signals',
            action='store_true',
            dest='disable_signals'),

        make_option('--batch-size',
            action='store',
            dest='batch_size',
            type='int'),

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

    @staticmethod
    def sanitize_options(options):
        multiples = ['badges', 'exclude_badges']
        for option in multiples:
            value = options[option]
            if value:
                options[option] = [v for v in value.split(' ') if v]
        return options
