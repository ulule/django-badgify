from django.apps import AppConfig


class BadgifyConfig(AppConfig):
    name = 'badgify'
    verbose_name = 'Badgify'

    def ready(self):
        super().ready()
        self.module.autodiscover()
