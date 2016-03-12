#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Setup script for nn_search2.

Usage:
    python2 setup.py install

"""
import os
import subprocess as sb
from distutils.core import setup
# To use a consistent encoding
import codecs
from os import path
from setuptools.command.install import install


HERE = path.abspath(path.dirname(__file__))


class post_install(install):
    def run(self):
        """Run default install with pos-install script"""
        install.run(self)
        script_path = os.path.join(os.getcwd(), 'post_install.sh')
        sb.call([script_path])


# Get the long description from the README file
with codecs.open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
                 long_description = f.read()

setup(
    name='nn_search2',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='2.0.0',

    description='nn_search2 -- part-of-speech tagging and search tool',
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
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
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

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    # these are only dependencies that can be installed via pip
    install_requires=['matplotlib>=1.5.1',
                      'Pillow>=3.1.0',
                      'nltk>=3.1',
                      'textblob>=0.11.0',
                      'docx>=0.2.4',
                      'hunspell>=0.3.3',
                      'pdfminer>=20140328'],

    # What does your project relate to?
    keywords='part-of-speech tagging',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    # packages=find_packages(exclude=['contrib', 'docs', 'unittests']),
    packages=['nn_search2'],

    package_data={
        'nn_search2': [
            'data/penn_tags.csv',
            'data/icons/*.png',
            'data/icons/*.ico'],
        },

    cmdclass={'install': post_install},
)
