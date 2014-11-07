# -*- coding: utf-8 -*-
from django.apps import AppConfig


class BadgifyConfig(AppConfig):
    name = 'badgify'
    verbose_name = 'Badgify'

    def ready(self):
        super(BadgifyConfig, self).ready()
        self.module.autodiscover()
