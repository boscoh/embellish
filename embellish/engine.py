#!/usr/bin/env python


from __future__ import print_function
import sys
import os
import shutil
import codecs
import datetime
from hashlib import md5
import re
from unicodedata import normalize
import logging

logger = logging.getLogger('embellish')

# third-party libraries
import dateutil.parser
import yaml
import sassin
from markdown import markdown
import scss
import coffeescript
from jinja2 import Environment, FileSystemLoader
try:
  from hamlpy.ext import HamlPyExtension
except:
  try:
    from jinja2_hamlpy import HamlPyExtension
  except:
    logger.error('Couldn\'t load the Hamlpy extension for jinja2')



# utility functions

def get_dict_val(my_dict, *keys):
  """
  Returns the value of a dictionary and if key is not found,
  will return None.
  """
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
  """
  Returns the relative path in a safe format to use for
  other file operations.
  """
  if mother_path is None:
    mother_path = os.getcwd()
  relpath = os.path.relpath(
      os.path.abspath(path),  os.path.abspath(mother_path))
  if relpath.startswith('./'):
    relpath = relpath[2:]
  return relpath


def write_text(fname, text):
  """
  Writes text to file in utf-8 and creates directory if needed.
  """
  dirname = os.path.dirname(fname)
  if dirname and not os.path.isdir(dirname):
    os.makedirs(dirname)
  with codecs.open(fname, 'w', encoding='utf-8') as f:
    f.write(text)


def read_text(fname):
  """
  Reads text in utf-8 encoding (includes ascii).
  """
  with codecs.open(fname, encoding='utf-8') as f:
    text = f.read()
  return text


def is_uptodate(src, dst):
  """
  Evaluates if .src has been modified afte the time of .dst.
  """
  return os.path.isfile(dst) and os.path.getmtime(dst) >= os.path.getmtime(src)


####


def read_page(fname):
  """
  Returns a page dictionary with text from fname, and fields 
  overriden by metadata found in fname.
  """
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
  try:
    text = read_text(fname)
  except Exception, e:
    logger.error('error reading "{}"'.format(relpath(fname)))
    logger.error('codecs:' + str(e))
    raise e

  # a little hack to allow adjacent --- to denote sections
  parts = ['']
  for line in text.splitlines():
    if len(parts) < 3:
      if line.startswith('---') and line.strip() == '---':
        parts.append('')
        continue
    parts[-1] += line + '\n'

  if len(parts) > 1:
    try:
      yaml_metadata = yaml.load(parts[0])
    except Exception, e:
      logger.error('YAML:error reading metadata from "{}"'.format(relpath(fname)))
      logger.error('YAML:' + str(e))
      raise e
    page.update(yaml_metadata)
    if isinstance(page['date'], str):
      page['date'] = dateutil.parser.parse(page['date'])
  if len(parts) > 2:
    page['excerpt'] = parts[1]
  page['content'] = parts[-1]
  return page


def convert_markdown(text):
  return markdown(text, extensions=['codehilite(guess_lang=False)'])


# from http://flask.pocoo.org/snippets/5/
_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
def slugify(text, delim=u'-'):
  """
  Returns a converted string that is internet-safe for URLs"
  """
  result = []
  for word in _punct_re.split(text.lower()):
      word = normalize('NFKD', word).encode('ascii', 'ignore')
      if word:
          result.append(word)
  return unicode(delim.join(result))


def parse_metadata(page, site):
  """
  Processes the page metadata into proper Python objects.
  """

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
  """
  Read all text files into site['pages'] with processing of 
  metadata.
  """
  cached_pages = { p['filename']:p for p in site['pages'] }
  site['pages'] = []
  top_dir = os.path.abspath(site['content_dir'])
  for root, dirs, fnames in os.walk(top_dir):
    for f in fnames:
      if site['files']:
        if f not in site['files']:
          continue
      if has_extensions(f, '.mkd', '.markdown', '.md', '.txt'):
        f = os.path.join(root, f)
        if f in cached_pages and \
            cached_pages[f]['modified'] >= os.path.getmtime(f):
          page = cached_pages[f]
        else:
          try:
            page = read_page(f)
          except:
            logger.error('skipping ' + relpath(f))
            continue
          try:
            # markdown conversion happens here
            page['content'] = convert_content_fn(page['content'])
          except Exception, e:
            logger.error('text conversion: error in "{}"'.format(f))
            logger.error('text conversion:' + str(e))
            continue
          parse_metadata_fn(page, site)
        site['pages'].append(page)
    if not site['recursive']:
      break


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
  """
  Returns the rendered html of page using template_fname
  """
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
      logger.error('Can\'t find template "{0}" in "{1}"'.format(
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
    logger.info('compiled .html: "{0}" -> "{1}"'.format(
         relpath(page['filename']), relpath(out_f)))


# transfer functions to copy the static directory

_scss_compiler = scss.Scss(scss_opts={'style':'expanded'})
def scss_to_css(src, dst_dir, site): 
  dst = os.path.join(dst_dir, os.path.basename(src))
  dst = os.path.splitext(dst)[0] + '.css'
  if not has_extensions(src, '.sass', '.scss'):
    return False
  if not site['force'] and is_uptodate(src, dst):
    return False
  if has_extensions(src, '.sass'):
    sass_text = read_text(src)
    scss_text = sassin.compile(sass_text)
  else:
    scss_text = read_text(src)
  try:
    css_text = _scss_compiler.compile(scss_text)
    if os.path.isfile(dst):
      os.remove(dst)
    write_text(dst, css_text)
    logger.info('compiled .sass file: "{0}" -> "{1}"'.format(src, dst))
  except Exception, e:
    logger.error('sassin:in "{0}"'.format(src))
    logger.error('sassin:' + str(e))
  return dst


def jinjahaml_to_html(src, dst_dir, site): 
  """
  Compiles .haml src to a .html file in dst_dir.
  """
  dst = os.path.join(dst_dir, os.path.basename(src))
  dst = os.path.splitext(dst)[0] + '.html'
  if not has_extensions(src, '.haml'):
    return False
  if not site['force'] and is_uptodate(src, dst):
    return False
  # check if it's pure haml and not a haml/jinja template
  text = read_text(src)
  is_haml_jinja = '{{' in text and '}}' in text
  if is_haml_jinja:
    return False
  try:
    template = get_jinjahaml_template(src)
    page = {
      'filename': dst,  # name of markdown file
    }
    text = template.render({'site':site, 'page':page})
    if os.path.isfile(dst):
      os.remove(dst)
    write_text(dst, text)
    logger.info('compiled .haml file: "{0}" -> "{1}"'.format(src, dst))
  except Exception, e:
    logger.error('hamlpy:in file "{0}"'.format(src))
    logger.error('hamlpy:' + str(e))
  return dst


def coffee_compile(src, dst_dir, site): 
  dst = os.path.join(dst_dir, os.path.basename(src))
  dst = os.path.splitext(dst)[0] + '.js'
  if not has_extensions(src, '.coffee'):
    return False
  if not site['force'] and is_uptodate(src, dst):
    return False
  try:
    in_text = read_text(src)
    out_text = coffeescript.compile(in_text)
    if os.path.isfile(out_text):
      os.remove(out_text)
    write_text(dst, out_text)
    logger.info('compiled .coffee file: "{0}" -> "{1}"'.format(src, dst))
  except Exception, e:
    logger.error('coffeescript:in file "{0}"'.format(src))
    logger.error('coffeescript:' + str(e))
  return dst


def direct_copy(src, dst_dir, site):
  dst = os.path.join(dst_dir, os.path.basename(src))
  if not site['force'] and is_uptodate(src, dst):
    return False
  try:
    shutil.copy2(src, dst)
    logger.info('File transfer: {0} -> {1}'.format(src, dst))
  except:
    logger.debug('File transfer: {0} -> {1}'.format(src, dst))


def copy_or_process_sass_and_haml(src, dst_dir, site):
  """
  Default transfer files, will copy or process .sass and .haml
  depending on file extension. 
  """
  # This is recognized by the target transfer fns, which 
  # return True if activated.
  if scss_to_css(src, dst_dir, site):
    return
  if coffee_compile(src, dst_dir, site):
    return
  if jinjahaml_to_html(src, dst_dir, site):
    return
  if direct_copy(src, dst_dir, site):
    return


def transfer_media_files(
    site, copy_file_fn=copy_or_process_sass_and_haml):
  """
  Transfer files found in the media directory to the target
  directory using the copy_file_fn to do the transfer.
  """

  def copy_tree(src, dst):
    """
    Copies files with copy_file_fn from 'src' to 'dst', then 
    recurses over sub-directories.
    """
    if not os.path.isdir(dst):
      os.makedirs(dst)
    errors = []
    for name in os.listdir(src):
      srcname = relpath(os.path.join(src, name))
      dstname = relpath(os.path.join(dst, name))
      if os.path.isdir(srcname):
        if site['recursive']:
          copy_tree(srcname, dstname)
      else:
        copy_file_fn(srcname, dst, site)

  copy_tree(relpath(site['media_dir']), relpath(site['output_dir']))


# main function

def generate_site(
    site,
    convert_content_fn=convert_markdown,
    parse_metadata_fn=parse_metadata,
    render_template_fn=render_jinjahaml_template,
    copy_file_fn=copy_or_process_sass_and_haml):
  """
  Generates static web-site based on markdown files.
  """
  logger.info(">>> Recursion mode:", site['recursive'])
  logger.info(">>> Force mode:", site['force'])
  logger.info(">>> Scanning pages")
  get_pages(site, convert_content_fn, parse_metadata_fn)

  logger.info(">>> Processing template rendering")
  write_pages(site, render_template_fn)
  
  logger.info(">>> Processing media files")
  transfer_media_files(site, copy_file_fn)



def generate_site_incrementally(
    site,
    convert_content_fn=convert_markdown,
    parse_metadata_fn=parse_metadata,
    render_template_fn=render_jinjahaml_template,
    copy_file_fn=copy_or_process_sass_and_haml):
  """
  Generates static website incrementally by caching the main-data
  structure betweend updates.
  """
  cached_pages = get_dict_val(site, 'cached_pages')
  if not get_dict_val(site, 'force'):
    if os.path.isfile(cached_pages):
      logger.info(">>> Loading cached pages")
      site['pages'] = eval(read_text(cached_pages))
  generate_site(
    site, convert_content_fn, parse_metadata_fn,
    render_template_fn, copy_file_fn)
  if cached_pages:
    logger.info(">>> Caching pages")
    write_text(cached_pages, repr(site['pages']))



default_site = {
  'url': 'http://boscoh.com', # if '' then use relative urls
  'content_dir': '.',  # look for markdown files
  'template_dir': '.',  # look for templates
  'output_dir': '.',  # generated files and static files put here
  'media_dir': '.',  # files to be correctly directly into the output file
  'cached_pages': 'site.cache',  # if not empty, caching file to spend updates
  'files': [],
  'ext': '.html',
  'recursive': False,
  'force': False,
  'pages': [],  # stores all the processed pages found in 'content_dir'
}


def read_config_yaml(config):
  """
  Returns a dictionary read from a config file in YAML.
  """
  load_site = yaml.load(read_text(config))
  for key in load_site:
    if load_site[key] is None:
      load_site[key] = ''
  site = default_site
  site.update(load_site)
  return site


  
