#!/usr/bin/env python
from __future__ import print_function
import sys
import os
import pprint

import stasis
import embellish

usage = '''
Runs the local static web server for a website that
uses embellish.py to regenerate the website when the
content changes.

monitor.py web_dir|site.yaml

- web_dir: runs default embellish in flat-file mode
           as the regeneration function
- site.yaml: runs the web-server from the output directory
             specified in the yaml file
'''


if len(sys.argv) == 1:
  print(usage)
  sys.exit(1)

arg = os.path.abspath(sys.argv[1])
if os.path.isdir(arg):
  site = embellish.default_site
  config_dir = arg
elif os.path.isfile(arg):
  site = embellish.read_config_yaml(arg)
  config_dir = os.path.dirname(arg)
else:
  print('Can\'t figure out {0}'.format(arg))
  sys.exit(1)

site_dir = os.path.join(config_dir, site['output_dir'])

for key in site.keys():
  if key.endswith('_dir') or key.startswith('cache'):
    site[key] = os.path.abspath(os.path.join(site_dir, site[key]))

regenerate = lambda: embellish.generate_site_incrementally(site)

monitor_keys = ['content_dir', 'template_dir', 'media_dir']
monitor_dirs = [site[k] for k in monitor_keys]

pprint.pprint(site)

stasis.run(site_dir, monitor_dirs, regenerate)

