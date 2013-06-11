#!/usr/bin/env python
from __future__ import print_function
import sys
import os
import shutil
import codecs
import datetime
from hashlib import md5
import re
import pprint
from unicodedata import normalize

import yaml

from rapydcss import SASStoSCSS
import StringIO
import scss

from jinja2 import Environment, FileSystemLoader
from jinja2_hamlpy import HamlPyExtension

from markdown import markdown

version = '0.9'

usage = '''
==================================================
Embellish: a low friction static website generator
==================================================
Looks for markdown files (*markdown, *mkd, *md, *txt) and
converts them into HTML pages. 

Metadata in the markdown files can invoke HAML/jinja2
templates (*haml), or jinja2 templates(any other extension).

usage: embellish.py web_dir|site.yaml 
'''


# utility functions

def get_dict_val(my_dict, *keys):
  "Returns None if key is not found. Extra keys for nested dicts"
  for key in keys:
    if key not in my_dict:
      return None
    val = my_dict[key]  
    my_dict = val    
  return val


def has_extensions(fname, *exts):
  for ext in exts:
    if fname.endswith(ext):
      return True
  return False


def relpath(path, mother_path=None):
  if mother_path is None:
    mother_path = os.getcwd()
  relpath = os.path.relpath(
      os.path.abspath(path),  os.path.abspath(mother_path))
  if relpath.startswith('./'):
    relpath = relpath[2:]
  return relpath


def write_text(fname, text):
  "Writes text to file in utf-8 and creates directory if needed."
  dirname = os.path.dirname(fname)
  if dirname and not os.path.isdir(dirname):
    os.makedirs(dirname)
  with codecs.open(fname, 'w', encoding='utf-8') as f:
    f.write(text)


def read_text(fname):
  "Reads in utf-8 encoding (includes ascii)"
  with codecs.open(fname, encoding='utf-8') as f:
    text = f.read()
  return text


def read_page(fname):
  page = {
    'template': 'default.haml',  # name of template file
    'filename': fname,  # name of markdown file
    'modified': os.path.getmtime(fname),  # unix time number of file  
    'checksum': '', # checksum used to check final output to avoid redundant writes
    'excerpt': '', # text to put in excerpt, no tags please!
    'content': '',  # main text of article
    'title': '',  # title for indexing and for large display
    'category': '',  # category of article for indexing 
    'rel_site_url': '',  # the top site directory relative to this page
    'date': None,  # published date
    'slug': None,  # url-safe name of article used to make url and files
    'url': '',   # relative url used for links in index files
    'target': '',    # target filename, maybe different to url due to redirection
    'index': False,   # indicates if this is an indexing page
    'sort_key': None,  # the field on which to sort under in indexing
    'sort_reverse': True,  # ascending or descing order for sorting
    'subpages': [],   # in indexing, pages belonging to the index placed here
    'max_subpages': None,  # a maximum limit of files to put in subpages
  }
  text = read_text(fname)
  parts = text.split('\n---\n')
  if len(parts) > 1:
    page.update(yaml.load(parts[0]))
  if len(parts) > 2:
    page['excerpt'] = parts[1]
  page['content'] = parts[-1]
  return page


def convert_markdown(text):
  return markdown(text, extensions=['codehilite'])


# from http://flask.pocoo.org/snippets/5/
_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
def slugify(text, delim=u'-'):
    """Generates an slightly worse ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))


# default 'parse_page_fn' used in 'read_page'
def parse_metadata(page, site):
  # markdown conversion here
  if not get_dict_val(page, 'title'):
    page['title'] = ''

  if not get_dict_val(page, 'excerpt'):
    strip_tags_str = re.sub(
        r'\<.+?\>', '', page['content'], flags=re.DOTALL)
    words = strip_tags_str.split()
    page['excerpt'] = ' '.join(words[:50])
    if len(words) > 50:
      page['excerpt'] += ' ...'

  if not get_dict_val(page, 'slug'):
    basename = os.path.splitext(os.path.basename(page['filename']))[0]
    page['slug'] = slugify(unicode(basename))

  if not get_dict_val(page, 'url'):
    dirname = os.path.dirname(page['filename'])
    full_url = os.path.join(dirname, page['slug'] + site['ext'])
    page['url'] = relpath(full_url, site['content_dir'])

  if not get_dict_val(page, 'target'):
    page['target'] = page['url']

  if not get_dict_val(page, 'date'):
    page['date'] = datetime.datetime.fromtimestamp(page['modified'])

  if isinstance(page['date'], datetime.date):
    page['date'] = datetime.datetime.combine(
         page['date'], datetime.time(0, 0))

  if not get_dict_val(page, 'template'):
    page['template'] = 'default.haml'


def get_pages(
    site, convert_content_fn=convert_markdown, 
    parse_metadata_fn=parse_metadata):

  cached_pages = { p['filename']:p for p in site['pages'] }
  site['pages'] = []
  top_dir = os.path.abspath(site['content_dir'])
  for root, dirs, fnames in os.walk(top_dir):
    for f in fnames:
      if has_extensions(f, '.mkd', '.markdown', '.md', '.txt'):
        f = os.path.join(root, f)
        if f in cached_pages and \
            cached_pages[f]['modified'] >= os.path.getmtime(f):
          page = cached_pages[f]
        else:
          page = read_page(f)
          page['content'] = convert_content_fn(page['content'])
          parse_metadata_fn(page, site)
        site['pages'].append(page)


# Writing file functions

def get_category_subpages(index_page, site):
  category = get_dict_val(index_page, 'category')

  subpages = []
  for subpage in site['pages']:
    if not get_dict_val(subpage, 'index'):
      if category:
        if get_dict_val(subpage, 'category') != category:
          continue
      subpages.append(subpage)

  sort_key = get_dict_val(index_page, 'sort_key')
  if sort_key:
    sort_reverse = get_dict_val(index_page, 'sort_reverse')
    if sort_reverse is None:
      sort_reverse = False
    subpages = filter(lambda p: get_dict_val(p, sort_key), subpages)
    subpages.sort(key=lambda p: p[sort_key], reverse=sort_reverse)

  n_subpage = get_dict_val(index_page, 'max_subpages')
  if n_subpage is not None:
    subpages = subpages[:n_subpage]

  return subpages


def get_jinjahaml_template(fname):
  dirname, basename = os.path.split(fname)
  jinja2_env = Environment(
    loader=FileSystemLoader(dirname), 
    extensions=[HamlPyExtension])
  return jinja2_env.get_template(basename)


# default 'render_template_fn' used in 'write_pages'
def render_jinjahaml_template(
    page, site, template_fname, cached_templates):
  "Returns html string from template in page"
  if template_fname not in cached_templates:
    template = get_jinjahaml_template(template_fname)
    cached_templates[template_fname] = template
  else:
    template = cached_templates[template_fname]
  return template.render(page=page, site=site)


def write_pages(site, render_template_fn=render_jinjahaml_template):
  output_dir = site['output_dir']

  # clearing the cached_templates here is quite important because
  # when run in persistent mode, you want the templates
  # freshly loaded for each call of 'write_pages'
  cached_templates = {}

  for page in site['pages']:
    out_f = os.path.join(output_dir, page['target'])
    dir_of_f = os.path.dirname(out_f)
    page['rel_site_url'] = relpath(output_dir, dir_of_f)

    if get_dict_val(page, 'index'):
      page['subpages'] = get_category_subpages(page, site)

    template_dirs = [
      os.path.dirname(page['filename']),
      site['template_dir'],
      os.path.join(os.path.dirname(__file__), 'defaults')
    ]
    for template_dir in template_dirs:
      template_fname = os.path.join(
          template_dir, page['template'])
      if os.path.isfile(template_fname):
        break
    else:
      print('Error: can\'t find template {0} in {1}'.format(
          page['template'], page['filename']))
      continue

    final_text = render_template_fn(
        page, site, template_fname, cached_templates)

    if get_dict_val(page, 'subpages'):
      # clean up after render so don't have to cache later
      del page['subpages']

    checksum = md5(final_text.encode('utf-8')).digest()
    if checksum == get_dict_val(page, 'checksum'):
      if os.path.isfile(out_f):
        continue

    write_text(out_f, final_text)
    page['checksum'] = checksum
    print("{0} -> {1}".format(page['filename'], out_f))


# transfer functions to copy the static directory
_scss_compiler = scss.Scss()

def scss_to_css(src, dst): 
  if src.endswith('.sass'):
    scss_buffer = StringIO.StringIO()
    SASStoSCSS.parse_file(src, scss_buffer)
    scss_text = scss_buffer.getvalue()
  elif src.endswith('.scss'):
    scss_text = read_text(src)
  else:
    return 'Can\'t recognize SCSS file {}'.format(src)
  css_text = _scss_compiler.compile(scss_text)
  write_text(dst, css_text)


def jinjahaml_to_html(src, dst): 
  try:
    template = get_jinjahaml_template(src)
    text = template.render()
  except:
    print('Couldn\'t parse HAML file', src)
    return
  write_text(dst, text)


# default 'copy_file_fn' used in 'transfer_media_files'
def copy_or_process_sass_and_haml(src, dst):
  """
  Copies and/or processes in file transfer.
  Returns (src, dst) or None if skip.
  """

  transfer_fn = shutil.copy2

  if has_extensions(src, '.sass', '.scss'):
    dst = os.path.splitext(dst)[0] + '.css'
    transfer_fn = scss_to_css

  if src.endswith('.haml'):
    # check if it's pure haml and not a haml/jinja template
    text = read_text(src)
    if not ('{{' in text and '}}' in text):
      dst = dst.replace('.haml', '.html')
      transfer_fn = jinjahaml_to_html

  if src == dst:
    return None

  if os.path.isfile(dst):
    if os.path.getmtime(dst) >= os.path.getmtime(src):
      return None

  print('{0} -> {1}'.format(src, dst))
  transfer_fn(src, dst)


def transfer_media_files(site, copy_file_fn=copy_or_process_sass_and_haml):

  def copy_tree(src, dst):
    """
    Walks directory 'src' to copy file to 'dst'.
    Calls copy_file_fn to do actual file transfer.
    """
    if not os.path.isdir(dst):
      os.makedirs(dst)
    errors = []
    for name in os.listdir(src):
      srcname = os.path.join(src, name)
      dstname = os.path.join(dst, name)
      if os.path.isdir(srcname):
        copy_tree(srcname, dstname)
      else:
        copy_file_fn(srcname, dstname)

  copy_tree(relpath(site['media_dir']), relpath(site['output_dir']))


# main function

def generate_site(
    site,
    convert_content_fn=convert_markdown,
    parse_metadata_fn=parse_metadata,
    render_template_fn=render_jinjahaml_template,
    copy_file_fn=copy_or_process_sass_and_haml):

  print(">>> Scanning pages")
  get_pages(site, convert_content_fn, parse_metadata_fn)

  print(">>> Processing template rendering")
  write_pages(site, render_template_fn)
  
  print(">>> Processing media files")
  transfer_media_files(site, copy_file_fn)



def generate_site_incrementally(
    site,
    convert_content_fn=convert_markdown,
    parse_metadata_fn=parse_metadata,
    render_template_fn=render_jinjahaml_template,
    copy_file_fn=copy_or_process_sass_and_haml):
  """
  A wrapper around 'generate_site' that caches
  the `pages` data structure for incremental updates.
  """
  cached_pages = get_dict_val(site, 'cached_pages')
  if os.path.isfile(cached_pages):
    print(">>> Loading cached pages")
    site['pages'] = eval(read_text(cached_pages))
  generate_site(
    site, convert_content_fn, parse_metadata_fn,
    render_template_fn, copy_file_fn)
  if cached_pages:
    print(">>> Caching pages")
    write_text(cached_pages, repr(site['pages']))



default_site = {
  'url': 'http://boscoh.com', # if '' then use relative urls
  'content_dir': '.',  # look for markdown files
  'template_dir': '.',  # look for templates
  'output_dir': '.',  # generated files and static files put here
  'media_dir': '.',  # files to be correctly directly into the output file
  'cached_pages': 'site.cache',  # if not empty, caching file to spend updates
  'ext': '.html',
  'pages': [],  # stores all the processed pages found in 'content_dir'
}


def read_config_yaml(config):
  load_site = yaml.load(read_text(config))
  for key in load_site:
    if load_site[key] is None:
      load_site[key] = ''
  print('>>> Site configuration:')
  pprint.pprint(load_site)
  site = default_site
  site.update(load_site)
  return site


if __name__ == "__main__":
  if len(sys.argv) == 1:
    print(usage)
  else:
    if os.path.isfile(sys.argv[1]):
      site = read_config_yaml(sys.argv[1])
    else:
      os.chdir(sys.argv[1])
      site = default_site
    generate_site_incrementally(site)

  
