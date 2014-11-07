# -*- coding: utf-8 -*-
from django.core import exceptions
from django.utils.importlib import import_module

from . import settings


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
    if not isinstance(class_path, basestring):
        try:
            class_path, app_label = class_path
        except:
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
    except ImportError, e:
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
    setting_name = 'BADGIFY_%s_MODEL' % model_name.upper().replace('_', '')
    class_path = getattr(settings, setting_name, None)
    if not class_path:
        return 'badgify.%s' % model_name
    elif isinstance(class_path, basestring):
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
        except:
            raise exceptions.ImproperlyConfigured(CLASS_PATH_ERROR % (
                setting_name, setting_name))
    return '%s.%s' % (app_label, model_name)


def chunks(l, n):
    """
    Yields successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def get_queryset_list(querysets):
    """
    Gets a QuerySet or a list of QuerySet, performs validation and return a
    list of QuerySet.
    """
    from django.db.models.query import QuerySet, EmptyQuerySet
    if not isinstance(querysets, (list, tuple)):
        querysets = [querysets]
    for qs in querysets:
        if not isinstance(qs, (QuerySet, EmptyQuerySet)):
            raise Exception('The supposed QuerySet is not a valid QuerySet. '
                            'Must be an instance of QuerySet or EmptyQuerySet.')
    return querysets


def get_user_ids_for_badge(badge, user_querysets):
    """
    Returns a tuple of missing unique user IDs and number of IDS for the given
    QuerySet list and badge.
    """
    from django.db.models.query import EmptyQuerySet
    user_querysets = get_queryset_list(user_querysets)
    existing_ids = badge.users.values_list('id', flat=True)
    ids = []
    for qs in user_querysets:
        if isinstance(qs, EmptyQuerySet):
            continue
        qs_ids = qs.values_list('id', flat=True)
        missing_ids = list(set(qs_ids) - set(existing_ids))
        ids = ids + missing_ids
    ids = list(set(ids))
    return (ids, len(ids))


def get_award_objects_for_badge(badge, user_ids, batch_size=500):
    """
    Returns a list of ``Award`` objects for the given ``Badge`` object and
    ``User`` IDs (and optionally chuncked with the ``batch_size``).
    """
    from .models import Award
    from .compat import get_user_model
    User = get_user_model()
    return [Award(user=user, badge=badge)
                   for ids in chunks(user_ids, batch_size)
                   for user in User.objects.filter(id__in=ids)]


def chunk_user_queryset_for_ids(ids, batch_size=500):
    """
    Returns a list of multiple User QuerySet chunked from ``ids`` (user IDs)
    and ``batch_size`` (how many ids to give to ``SELECT IN``).
    """
    from .compat import get_user_model
    User = get_user_model()
    return [User.objects.filter(id__in=ids) for chunked_ids in chunks(ids, batch_size)]
