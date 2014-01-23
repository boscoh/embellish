#!/usr/bin/env python
from setuptools import setup

# This is to disable the 'black magic' surrounding versioned repositories... Terrible!
from setuptools.command import sdist
del sdist.finders[:]

description = \
"""Embellish is a low-friction static website generator.

Docs at http://github.com/boscoh/embellish.
"""

# hamlpy dev version requires a bit of rejigging
# http://stackoverflow.com/questions/3472430/how-can-i-make-setuptools-install-a-package-thats-not-on-pypi/3481388#3481388

setup(
    name='embellish',
    version='0.9',
    author='Bosco Ho',
    author_email='boscoh@gmail.com',
    url='http://github.com/boscoh/embellish',
    description='Static site generator',
    long_description=description,
    license='BSD',
    dependency_links = [
        'https://api.github.com/repos/jessemiller/HamlPy/zipball/acb79e14381ce46e6d1cb64e7cb154751ae02dfe#egg=hamlpy-0.82.2'],
    install_requires=[
        'hamlpy',
        'markdown',
        'PyYaml',
        'jinja2', 
        'python-dateutil',
        'sassin',
        'flask',
    ],
    packages=['embellish',],
    package_data={"embellish": ['defaults/default.haml',]},
    scripts=['bin/embellish'],
)