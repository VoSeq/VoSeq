# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import voseq

version = voseq.__version__

requirements = [
    'biopython',
    'Django',
    'pyprind',
    'elasticsearch',
    'Unipath',
    'psycopg2',
    'dataset',
    'django-haystack',
    'django-debug-toolbar',
    'pytz',
    'django-suit',
]

test_requirements = [
    'coverage',
    'nose',
    'pep8',
    'coveralls',
    'Sphinx',
]

setup(
    name='VoSeq',
    version=version,
    author='Carlos Pena, Tobias Malm, Victor Mezarino',
    author_email='carlosp420@gmail.com',
    packages=[
        'voseq',
    ],
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    scripts=['voseq/manage.py'],
    test_require=test_requirements,
)
