#!/usr/bin/env python
import os
from distutils.core import setup

data_dir = os.path.join(os.getcwd(), 'embellish/defaults')
setup(
    name='embellish',
    version='0.9',
    author='Bosco Ho',
    author_email='boscoh@gmail.com',
    url='http://github.com/boscoh/embellish',
    description='Static site generator',
    long_description=
        "Embellish is a static website generator. It turns a pile of templates, "
        "content, and resources (like CSS and images) into a neat stack of "
        "plain HTML. You run it on your local computer, and it generates a "
        "directory of web files that you can upload to your web server, or "
        "serve directly.",
    requires=['pyyaml', 'jinja2', 'Markdown', 'Flask', 'jinja2_hamlpy', 'hamlpy'],
    packages=['embellish',],
    package_data={"embellish": ['defaults/default.haml',]},
    scripts=['bin/embellish', 'bin/monitor'],
)