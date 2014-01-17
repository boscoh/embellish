#!/usr/bin/env python
from __future__ import print_function
import os
import glob
import stat
import logging
import sys
import string
import random
import webbrowser
import threading 

# import gevent
# import gevent.monkey
# from gevent.pywsgi import WSGIServer
# gevent.monkey.patch_all()

from flask import Flask, request, Response, redirect, send_from_directory


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


def is_something_changed():
  if app.regenerate is None:
    return False
  if app.monitor_dirs:
    checksum = 0
    for check_dir in app.monitor_dirs:
      for root, dirs, files in os.walk(check_dir + '/'):
        fnames = [os.path.join(root, f) for f in files]
        checksum += sum(map(os.path.getmtime, fnames))
    # no changes in directories:
    if app.checksum == None:
      app.checksum = checksum
    if checksum == app.checksum:
      return False
    app.checksum = checksum
  return True


def regenerate_site_if_changed():
  if is_something_changed():
    app.regenerate()


# def event_stream():
#     count = 0
#     while True:
#         gevent.sleep(2)
#         if is_something_changed():
#           app.regenerate()
#           yield 'data: %s\n\n' % count
#         count += 1


# @app.route('/my_event_source')
# def sse_request():
#     return Response(
#             event_stream(),
#             mimetype='text/event-stream')


def send_fname(fname):
  app.logger.info('FETCHING: {0}'.format(fname))
  if fname.endswith('.html'):
    regenerate_site_if_changed()
  return send_from_directory(*os.path.split(fname))


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
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


def run(site_dir, monitor_dirs, regenerate_fn):
  app.regenerate = regenerate_fn
  app.site_dir = site_dir
  app.monitor_dirs = list(set(monitor_dirs))
  app.checksum = None
  port = random.randint(5000, 65535)
  url = 'http://127.0.0.1:{}/'.format(port)
  home = os.path.join(app.site_dir, 'index.html')
  if not os.path.isfile(home):
    htmls = glob.glob(os.path.join(app.site_dir, '*html'))
    if htmls:
      url += os.path.basename(htmls[0])
  print('Will try to open', url)
  wait = 2
  threading.Timer(wait, lambda: webbrowser.open(url), ()).start()
  app.run(port=port)


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print(usage)
  else:
    site_dir = os.path.abspath(sys.argv[1])
    run(site_dir, [], None)

