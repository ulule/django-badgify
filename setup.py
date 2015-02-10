# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

root = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(root, 'README.rst')) as f:
    README = f.read()

setup(
    name='django-badgify',
    version='0.1.4',
    description='Badges app for Django',
    long_description=README,
    author='Gilles Fabio',
    author_email='gilles.fabio@gmail.com',
    url='http://github.com/ulule/django-badgify',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'Pillow==2.4.0',
        'pytz',
    ],
    tests_require=['coverage', 'RandomWords'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ]
)
