#!/usr/bin/env python
from setuptools import setup

version = open('embellish/_version.py').read().split()[-1][1:-1]

setup(
    name='embellish',
    version=version,
    author='Bosco Ho',
    author_email='boscoh@gmail.com',
    url='http://github.com/boscoh/embellish',
    description='a lightweight static website generator',
    long_description='Docs at http://github.com/boscoh/embellish',
    license='BSD',
    # linking hamlpy dev version requires a bit of rejigging
    dependency_links = [
        'https://api.github.com/repos/jessemiller/HamlPy/zipball/acb79e14381ce46e6d1cb64e7cb154751ae02dfe#egg=hamlpy-0.82.2'],
    install_requires=[
        'hamlpy',
        'markdown',
        'PyYaml',
        'jinja2', 
        'jinja2-hamlpy',
        'python-dateutil',
        'coffeescript',
        'sassin',
        'flask',
    ],
    packages=['embellish',],
    package_data={
        "embellish": ['defaults/default.haml',]
    },
    scripts=['bin/embellish'],
)