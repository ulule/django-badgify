import logging

from importlib import import_module

from django.core import exceptions
from django.db import connection

import six

from . import settings

logger = logging.getLogger(__name__)


CLASS_PATH_ERROR = 'django-badgify is unable to interpret settings value for %s. '\
                   '%s should be in the form of a tupple: '\
                   '(\'path.to.models.Class\', \'app_label\').'


def load_class(class_path, setting_name=None):
    """
    Loads a class given a class_path. The setting value may be a string or a
    tuple. The setting_name parameter is only there for pretty error output, and
    therefore is optional

    Borrowed from: https://github.com/thoas/django-discussions/blob/master/discussions/utils.py
    """
    if not isinstance(class_path, six.string_types):
        try:
            class_path, app_label = class_path
        except Exception:
            if setting_name:
                raise exceptions.ImproperlyConfigured(CLASS_PATH_ERROR % (
                    setting_name, setting_name))
            else:
                raise exceptions.ImproperlyConfigured(CLASS_PATH_ERROR % (
                    'this setting', 'It'))

    try:
        class_module, class_name = class_path.rsplit('.', 1)
    except ValueError:
        if setting_name:
            txt = '%s isn\'t a valid module. Check your %s setting' % (
                class_path, setting_name)
        else:
            txt = '%s isn\'t a valid module.' % class_path
        raise exceptions.ImproperlyConfigured(txt)

    try:
        mod = import_module(class_module)
    except ImportError as e:
        if setting_name:
            txt = 'Error importing backend %s: "%s". Check your %s setting' % (
                class_module, e, setting_name)
        else:
            txt = 'Error importing backend %s: "%s".' % (class_module, e)
        raise exceptions.ImproperlyConfigured(txt)

    try:
        clazz = getattr(mod, class_name)
    except AttributeError:
        if setting_name:
            txt = ('Backend module "%s" does not define a "%s" class. Check'
                   ' your %s setting' % (class_module, class_name,
                                         setting_name))
        else:
            txt = 'Backend module "%s" does not define a "%s" class.' % (
                class_module, class_name)
        raise exceptions.ImproperlyConfigured(txt)
    return clazz


def get_model_string(model_name):
    """
    Returns the model string notation Django uses for lazily loaded ForeignKeys
    (eg 'auth.User') to prevent circular imports.
    This is needed to allow our crazy custom model usage.

    Borrowed from: https://github.com/thoas/django-discussions/blob/master/discussions/utils.py
    """
    setting_name = '%s_MODEL' % model_name.upper().replace('_', '')
    class_path = getattr(settings, setting_name, None)
    if not class_path:
        return 'badgify.%s' % model_name
    elif isinstance(class_path, str):
        parts = class_path.split('.')
        try:
            index = parts.index('models') - 1
        except ValueError:
            raise exceptions.ImproperlyConfigured(CLASS_PATH_ERROR % (
                setting_name, setting_name))
        app_label, model_name = parts[index], parts[-1]
    else:
        try:
            class_path, app_label = class_path
            model_name = class_path.split('.')[-1]
        except Exception:
            raise exceptions.ImproperlyConfigured(CLASS_PATH_ERROR % (
                setting_name, setting_name))
    return '%s.%s' % (app_label, model_name)


def chunks(l, n):
    """
    Yields successive n-sized chunks from l.
    """
    for i in range(0, len(l), n):
        yield l[i:i + n]


def log_queries(recipe):
    """
    Logs recipe instance SQL queries (actually, only time).
    """
    logger.debug(
        '⚐ Badge %s: SQL queries time %.2f second(s)',
        recipe.slug,
        sum([float(q['time']) for q in connection.queries]))


def sanitize_command_options(options):
    """
    Sanitizes command options.
    """
    multiples = [
        'badges',
        'exclude_badges',
    ]

    for option in multiples:
        if options.get(option):
            value = options[option]
            if value:
                options[option] = [v for v in value.split(' ') if v]

    return options
