django-badgify
==============

This Django application will help you to create your own badge system on your website.

It has been used on `Ulule <http://www.ulule.com>`_ to create our own `badge mechanism <http://www.ulule.com/badges/>`_.

.. image:: https://secure.travis-ci.org/ulule/django-badgify.png?branch=master
    :alt: Build Status
    :target: http://travis-ci.org/ulule/django-badgify

Installation
------------

.. code-block:: bash

    $ pip install django-badgify

Usage
-----

Add ``badgify`` to your ``INSTALLED_APPS`` in ``settings.py``:

.. code-block:: python

    INSTALLED_APPS = (
        # ...
        'badgify',
    )

Synchronize the database:

.. code-block:: bash

    # Django < 1.7
    $ python manage.py syncdb

    # Django >= 1.7
    $ python manage.py migrate

Create a ``badgify_recipes.py`` file in your Django application:

.. code-block:: bash

    $ cd path/to/your/django/app
    $ touch badgify_recipes.py

Open this file and import `badgify.recipe.BaseRecipe` class and `badgify` module:

.. code-block:: python

    from badgify.recipe import BaseRecipe
    import badgify

Create and register your recipe classes:

.. code-block:: python

    class PythonLoverRecipe(BaseRecipe):
        pass


    class JSLoverRecipe(BaseRecipe):
        pass


    # Per class
    badgify.register(PythonLoverRecipe)
    badgify.register(JSLoverRecipe)

    # All at once in a list
    badgify.register([PythonLoverRecipe, JSLoverRecipe])

A recipe class must implement:

* ``name`` class attribute
    The badge name (humanized).

* ``image`` property
    The badge image/logo as a file object.

A recipe class may implement:

* ``slug`` class attribute
    The badge slug (used internally and in URLs).
    If not provided, it will be auto-generated based on the badge name.

* ``description`` class attribute
    The badge description (short).
    It not provided, value will be blank.

* ``user_ids`` property
    ``QuerySet`` returning User IDs likely to be awarded. You must return a
    ``QuerySet`` and not just a Python list or tuple. You can use
    ``values_list('id', flat=True)``.

* ``db_read`` class attribute
    The database alias on which to perform read queries.
    Defaults to ``django.db.DEFAULT_DB_ALIAS``.

* ``batch_size`` class attribute
    How many ``Award`` objects to create at once.
    Defaults to ``BADGIFY_BATCH_SIZE`` (``500``).

Example:

.. code-block:: python

    from django.contrib.staticfiles.storage import staticfiles_storage

    from badgify.recipe import BaseRecipe
    import badgify

    from .models import MyCustomUser


    class PythonLoverRecipe(BaseRecipe):
        """
        People loving Python.
        """
        name = 'Python Lover'
        slug = 'python-lover'
        description = 'People loving Python programming language'

        @property
        def image(self):
            return staticfiles_storage.open('python-lover.png')

        @property
        def user_ids(self):
            return (MyCustomUser.objects.filter(love_python=True)
                                        .values_list('id', flat=True))


    class JSLoverRecipe(BaseRecipe):
        """
        People loving JS.
        """
        name = 'JS Lover'
        slug = 'js-lover'
        description = 'People loving JS programming language'

        @property
        def image(self):
            return staticfiles_storage.open('js-lover.png')

        @property
        def user_ids(self):
            return (MyCustomUser.objects.filter(love_js=True)
                                        .values_list('id', flat=True))


    class JavaLoverRecipe(BaseRecipe):
        """
        People loving Java.
        """
        name = 'JS Lover'
        slug = 'js-lover'
        description = 'People loving JS programming language'

        @property
        def image(self):
            return staticfiles_storage.open('js-lover.png')


    badgify.register([
        PythonLoverRecipe,
        JSLoverRecipe,
        JavaLoverRecipe,
    ])

Once you have implemented and registered your recipe classes, you can invoke
available commands bellow:

.. code-block:: bash

    # Create badges from recipes
    $ python manage.py badgify_sync badges

    # Update badges from recipes
    $ python manage.py badgify_sync badges --update

    # Create awards
    $ python manage.py badgify_sync awards

    # Create awards bypassing signals (improve performances)
    $ python manage.py badgify_sync awards --disable-signals

    # Only create awards for "python" badge
    $ python manage.py badgify_sync awards --badges python

    # Only create awards for "python" and "go" badges
    $ python manage.py badgify_sync awards --badges "python go"

    # Create awards for all badges, except "php"
    $ python manage.py badgify_sync awards --exclude-badges php

    # Create awards for all badges, except "php" and "java"
    $ python manage.py badgify_sync awards --exclude-badges "php java"

    # Denormalize Badge.users.count() into Badge.users_count field
    $ python manage.py badgify_sync counts

    # Only denormalize counts for "python" badge
    $ python manage.py badgify_sync counts --badges python

    # Denormalize counts for all badges, except "php"
    $ python manage.py badgify_sync counts --exclude-badges php

    # Denormalize counts for all badges, except "php" and "java"
    $ python manage.py badgify_sync counts --exclude-badges "php java"

    # Typical workflow for best performances
    $ python manage.py badgify_sync badges
    $ python manage.py badgify_sync awards --disable-signals
    $ python manage.py badgify_sync counts

    # WARNING: if you delete awards to start again with a fresh table
    # don't forget to update Badge.users_count field. Or use this command:
    $ python manage.py badgify_reset

    # Typical workflow for best performances if you want to recompute awards
    $ python manage.py badgify_reset
    $ python manage.py badgify_sync awards --disable-signals
    $ python manage.py badgify_sync counts

Templatetags
------------

badgify_badges
..............

Takes two optional arguments:

* ``user``: a ``User`` object
* ``username``: a ``User`` username

Without any argument, displays all badges. Otherwise, badges awarded by the given user.

.. code-block:: html+django

    {% load badgify_tags %}

    {% badgify_badges as badges %}
    {% badgify_badges username="johndoe" as badges %}
    {% badgify_badges user=user as badges %}

    {% for badge in badges %}
        {{ badge.name }}
    {% endfor %}

Custom Models
-------------

**django-badgify** lets you define your own model classes for ``Badge`` and ``Award``
models. That can be pretty useful for i18n stuff
(example: `django-transmetta <https://github.com/Yaco-Sistemas/django-transmeta/>`_ support),
adding custom fields, methods or properties.

Your models must inherit from ``badgify.models.base`` model classes:

.. code-block:: python

    # yourapp.models

    from badgify.models import base


    class Badge(base.Badge):
        # you own fields / logic here
        class Meta(base.Badge.Meta):
            abstract = False


    class Award(base.Award):
        # you own fields / logic here
        class Meta(base.Award.Meta):
            abstract = False


Then tell the application to use them in place of default ones in your ``settings.py`` module:

.. code-block:: python

    # yourapp.settings

    BADGIFY_BADGE_MODEL = 'yourapp.models.Badge'
    BADGIFY_AWARD_MODEL = 'yourapp.models.Award'

Settings
--------

You can altere the application behavior by defining settings in your ``settings.py``
module.

All application settings are prefixed with ``BADGIFY_``.

``BADGIFY_BADGE_IMAGE_UPLOAD_ROOT``
...................................

The root path for ``Badge``  model ``ImageField``.

``BADGIFY_BADGE_IMAGE_UPLOAD_URL``
..................................

The URL ``Badge``  model ``ImageField``.

``BADGIFY_BADGE_IMAGE_UPLOAD_STORAGE``
......................................

Your own ``django.core.files.storage`` storage instance.

``BADGIFY_BADGE_LIST_VIEW_PAGINATE_BY``
.......................................

Number of badges to display on the badge list page.

``BADGIFY_BADGE_DETAIL_VIEW_PAGINATE_BY``
.........................................

Number of awarded users to display on the badge detail page.

``BADGIFY_BADGE_MODEL``
.......................

Your own concrete ``Badge`` model class as module path.

Example: ``yourapp.models.Badge``.

``BADGIFY_AWARD_MODEL``
.......................

Your own concrete ``Award`` model class as module path.

Example: ``yourapp.models.Award``.

``BADGIFY_BATCH_SIZE``
......................

Maximum number of ``Award`` objects to create at once.

Defaults to ``500``.

Contribute
----------

.. code-block:: bash

    # Don't have pip?
    $ sudo easy_install pip

    # Don't already have virtualenv?
    $ sudo pip install virtualenv

    # Clone and install dependencies
    $ git clone https://github.com/ulule/django-badgify.git
    $ cd django-badgify
    $ make install

    # Launch tests
    $ make test

    # Launch example project
    $ make serve

Compatibility
-------------

- Python 2.6: Django 1.5, 1.6
- python 2.7: Django 1.5, 1.6, 1.7, 1.8
- Python 3.3: Django 1.5, 1.6, 1.7, 1.8
- Python 3.4: Django 1.5, 1.6, 1.7, 1.8
