# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from voseq import voseq


version = voseq.__version__

requirements = [
    'amas==0.2',
    'biopython==1.66',
    'Django==1.9',
    'Pillow==3.0.0',
    'pyprind==2.9.3',
    'elasticsearch==1.4',
    'Unipath==1.1',
    'psycopg2==2.6.1',
    'dataset>=0.5.6',
    'pytz>=2015.4',
    'django-crispy-forms==1.4.0',
    'django-import-export==0.3.1',
    'django-registration-redux==1.2',
    'django-debug-toolbar>=1.3.2',
    'django-suit>=0.2.13',
    'django-haystack==2.4.0',
    'easy-thumbnails==2.2',
    'flickrapi==2.0',
    'dataset-creator==0.3.10',
    'seqrecord-expanded==0.2.4',
    'degenerate-dna==0.0.9',
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
    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    zip_safe=False,
    scripts=['voseq/manage.py'],
    test_require=test_requirements,
)
