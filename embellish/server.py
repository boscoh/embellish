#!/usr/bin/env python
import os
import glob
import stat
import logging
import sys
import string
import random
import webbrowser
import threading 

from flask import Flask, request, redirect, send_from_directory


usage = '''
STASIS
======
A simple static web-site server.
 - adds trailing / to directories
 - adds implied .html to clean urls
 - has a site regeneration hook 
 - monitors modfiications in directories 

usage: stasis.py static_web_dir
'''


app = Flask(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)  


def check_regeneration():
  if app.regenerate is None:
    return
  if app.monitor_dirs:
    checksum = 0
    for check_dir in app.monitor_dirs:
      for root, dirs, files in os.walk(check_dir):
        fnames = [os.path.join(root, f) for f in files]
        checksum += sum(map(os.path.getmtime, fnames))
    # no changes in directories:
    if app.checksum == None:
      app.checksum = checksum
    if checksum == app.checksum:
      return
    app.checksum = checksum
  app.regenerate()


def send_fname(fname):
  app.logger.info('FETCHING: {0}'.format(fname))
  return send_from_directory(*os.path.split(fname))


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    check_regeneration()
    fname = os.path.join(app.site_dir, path.split('?')[0])
    # handle directory redirects -> index.html
    if os.path.isdir(fname):
      fname = os.path.join(fname, 'index.html')
      if os.path.isfile(fname):
        if path and not path.endswith('/'):
          return redirect(path + '/')
        else:
          return send_fname(fname)
    # found file
    if os.path.isfile(fname):
      return send_fname(fname)
    # assume clean url's, add implied .html extension
    if os.path.isfile(fname + '.html'):
      fname += '.html'
      return send_fname(fname)
    # oops no file found
    return 'Problem interpreting {0} as local file {1}'.format(path, fname)


def open_home_with_delay(url, wait=2, force_refresh=False):
  'Opens site in browser, forces refresh with random query.'
  if force_refresh:
    random_string = ''.join(random.choice(string.lowercase) for i in range(5))
    url += '?force_refresh_with_random_string_' + random_string
  # threading.Timer(wait, lambda: webbrowser.open(url), ()).start()
  webbrowser.open(url)


def run(site_dir, monitor_dirs, regenerate_fn):
  app.regenerate = regenerate_fn
  app.site_dir = site_dir
  app.monitor_dirs = monitor_dirs
  app.checksum = None
  url = 'http://127.0.0.1:5000/'
  home = os.path.join(app.site_dir, 'index.html')
  if not os.path.isfile(home):
    htmls = glob.glob(os.path.join(app.site_dir, '*html'))
    if htmls:
      url += os.path.basename(htmls[0])
  open_home_with_delay(url, force_refresh=True)
  app.debug = False
  app.run()


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print usage
  else:
    site_dir = os.path.abspath(sys.argv[1])
    run(site_dir, [], None)

