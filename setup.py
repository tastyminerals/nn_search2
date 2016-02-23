#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Setup script for nn-search2.

Usage:
    python setup.py install

"""
# always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    windows=['nn-search2.pyw'],
    console = ['nn-search2.pyw'],
    name='nn-search2',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='2.0.0',

    description='nn-search2 -- POS-tags searching tool',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/tastyminerals/nn-search.git',

    # Author details
    author=['Pavel Shkadzko'],

    author_email=['tastyminerals@gmail.com'],

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        # Development Status :: 3 - Alpha
        # Development Status :: 4 - Beta
        'Development Status :: 5 - Production/Stable',
        # Development Status :: 6 - Mature
        # Indicate who your project is intended for
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Education',
        'Topic :: Text Processing :: Linguistic',
        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only'
    ],

    # What does your project relate to?
    keywords='part-of-speech tagging',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'unittests']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html

    # these are only dependencies that can be installed via pip
    install_requires=['matplotlib>=1.5.1', 'Pillow>=3.1.0', 'nltk>=3.1',
                      'textblob>=0.11.0', 'textblob-aptagger>=0.2.0',
                      'docx>=0.2.4', 'hunspell>=0.3.3', 'pdfminer>=20140328'],

    # other dependencies are: Tk 8.6.4-1,

    data_files=[
      ('penn', ['/nn-search/data/penn_tags.csv']),
      ('icons', [
                    'nn-search/data/icons/cog.png',
                    'nn-search/data/icons/copy.png',
                    'nn-search/data/icons/cross.png',
                    'nn-search/data/icons/cup.png',
                    'nn-search/data/icons/cut.png',
                    'nn-search/data/icons/disk.png',
                    'nn-search/data/icons/error.png',
                    'nn-search/data/icons/exit.png',
                    'nn-search/data/icons/help.png',
                    'nn-search/data/icons/info.png',
                    'nn-search/data/icons/load.png',
                    'nn-search/data/icons/page_save.png',
                    'nn-search/data/icons/paste.png',
                    'nn-search/data/icons/pos-tagging.png',
                    'nn-search/data/icons/proc.png',
                    'nn-search/data/icons/redo.png',
                    'nn-search/data/icons/sad.png',
                    'nn-search/data/icons/search.png',
                    'nn-search/data/icons/stats2.png',
                    'nn-search/data/icons/stats3.png',
                    'nn-search/data/icons/stats.png',
                    'nn-search/data/icons/undo.png',
                    'nn-search/data/icons/view1.png',
                    'nn-search/data/icons/view2.png',
                    'nn-search/data/icons/view3.png',
                    'nn-search/data/icons/wand.png',
                    'nn-search/data/icons/warning.png'
                 ])
    ],

    setup_requires=['pytest-runner'],
    tests_require=['pytest']
)
