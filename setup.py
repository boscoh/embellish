#!/usr/bin/env python
import os
from setuptools import setup

# This is to disable the 'black magic' surrounding versioned repositories... Terrible!
from setuptools.command import sdist
del sdist.finders[:]

description = \
"""Embellish is a static website generator. It's a low
friction command-line tool that converts markdown text
files into HTML. 

See more at httP;;/github.com/boscoh/embellish.
"""

setup(
    name='embellish',
    version='0.9',
    author='Bosco Ho',
    author_email='boscoh@gmail.com',
    url='http://github.com/boscoh/embellish',
    description='Static site generator',
    long_description=description,
    license='BSD',
    install_requires=[
        'markdown',
        'PyYaml',
        'jinja2', 
        'hamlpy', 
        'jinja2-hamlpy', 
        'flask',
    ],
    packages=['embellish',],
    package_data={"embellish": ['defaults/default.haml',]},
    scripts=['bin/embellish', 'bin/monitor'],
)