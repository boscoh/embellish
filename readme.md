
# Embellish

## A low-friction static web-site generator

There are many Python static web generators. Many are opinionated - like how you must name your files - this one is not. `Embellish` is quite happy to convert markdown files in any directory into HTML.

`Embellish` is fast: it incrementally rebuilds my blog of ~300 posts, 6 categories, and 25MB of assets in ~1 second on my Macbook air. 

The data model in `embellish` is transparent. It's not an object, it's a dictionary. Remember those? The YAML metadata in your markdown is slurped into the primary `page` dictionary which is in turn inserted directly into your templates.

There is no plugin system: you extend `embellish` with function hooks. Yes it's a little bit more work, but you get to write function hooks directly in Python, which is ultimately easier than futzing around with plugin rules and DSL's.

## Installation

To install:

    pip install embellish

Python depencencies should be automatically installed. If you want to manually install dependencies:

    pip install markdown pyyaml jinja2 hamlpy jinja2_haml flask rapydcss scss

Now create a `example.mkd` in a temporary directory:

    title: An example file
    category: silly
    ---
    This is an example file.

Save the file, and do:

    embellish .

You should then find `example.html` in your directory. As no templates were specified, a default responsive-web-design is used (`embellish/defaults/default.haml`).



## My choice of formats

There are many formats for webdesign. For markup text, there's .markdown, .textile and .rsT. For CSS, there's .less, .scss and .sass. For Python templates, there's Django, Jinja, Cheetah and Mako. For metadata, there's JSON, YAML, Python pickle.

Well, here's what I recommend:

  - markdown for marking-up your prose 
  - YAML to describe your page metadata
  - HAML/Jinja2 for templating HTML
  - SASS for concise CSS 

It is ironic, I know, but all that significant whitespace technology - YAML, HAML and SASS - is more prevalent in the Ruby world. But when placed in the context of Python, they fit better than a tuxedo on Daniel Craig.

In particular, content is expected as markdown with a YAML header (separated by `---`), call this `example.mkd`:

    template: example.haml
    links:
      - 
        name: apple
        href: http://apple.com
      - 
        name: google
        href: http://google.com 
      - 
        name: yahoo
        href: http://yahoo.com
    ---

    This is some content in the example
              
Throw in some CSS stylings using sass `styles.sass`, which uses the same YAML-inspired format:

    body
      background-color: #FFF
      font-family: Helvetica
      width: 700px
      margin: 0 auto
    .nav
      a 
        display:inline
        padding-right: 1em
      a:link
        text-decoration: none

Finally, using HAML/JINJA2, you mix control structures with YAML inspired indentation for HTML elements, in `example.haml`:

    %head
      %link{rel:'stylesheet',href:'styles.css'}

    %body
      .nav
        - for link in page.links:
          %a{href:'{{ link.href }}'}
            {{ link.name }}
      {{ page.content }}

It' DRY, easy to read, and the control structures look extremely pythonic. 

Having saved these viles into directory (how about `temp`?), then run:

    embellish.py .
    
That's all there is.

## Site configuration file

Obviously for a more complicated website, you might want to separate your content, templates and output. To do this simply create a file `site.yaml`:

    url: http://boscoh.com # if  then use relative urls
    content_dir: content  # look for markdown files
    template_dir: templates  # look for templates
    output_dir: site  # generated files and static files put here
    media_dir: media  # files to be correctly directly into the output file
    ext: .html

To run `embellish` with this configuration file:

    embellish.py site.yaml


## Stasis and Monitor: local web-servers

Most static web-generators come with a little local web-server to solve a common problem where most browsers treat a local file system differently to an actual web-server. In particular, a web-server interprets directory names and index.html differently on local servers than on a remote server. 

Most of the other static website packages provide a little web-server subclassed from the standard SimpleHTTPServer library, which I think is rather awkward. We can do better. 

Here we provide `stasis`, a standalone web-server, written with the gorgeous Flask library. As such `stasis` can directly control the behavior of the local web-server:

 - add trailing / to directories
 - process implied index.html in directories
 - add implied .html to clean urls
 - monitor modfiications in directories 
 - followed-up with a site regeneration hook 
 - attempts to open the /index.html in the local browser

To actually exploit the monitoring and regeneration, you can use `monitor`, which is simply a glue script that hooks `embellish` into `stasis`. `Monitor` looks for `embellish` configuration files or just runs `emblish` against a given directory. `Monitor` allows you to:

 1. simulate the remote server on your local machine to check your links. 
 2. iterate designs on your blog. As you save edits on your content, stylesheets and templates, just refresh the browser for instantaneous updates of the working site.

# Templating guide

`Embellish` is for those of you who want to create your own templates for a bunch of different sites. This means that you want to creatively play with the metadata in each page that is sucked into your templates.

In embellish, there's no need to define 'types' of posts. Simply set the `page.template` field to the template of your choice, and populate the correspoding metadata in your markdown files. As long as the metadata fields and the templates match, you're good to go.

## Metadata

Every page is populated with a set of default metadata. The best way to show this is the default page metadata dictionary from the Python source code:

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

All these fields are accessible in you jinja2 template in the form of:

    {{ page.title }}

In particular, dates are converted to standard Python datetime objects, and can be passed into the jinja templates by calling the datetime string method:

    {{ page.date.strftime("%d %b %Y") }}

If excerpts are not given in the content markdown file, a simple excerpt is generated from the first 50 non-tag words in the content and placed under 'page.excerpt'


## Index Pages

Of course, one of the most important function of blogs is to organise blog posts into archives. A group of metadata is used to generate such pages. These are 'page.index', 'page.template', 'page.category', 'page.sort_key', 'page.sort_reverse', 'page.max_subpages'. 

The controlling variable is the metadata field 'page.index'. If this is set to True, then a group of pages, 'page.subpages', will be generated. Essentially, 'page.subpages' are a list of pages, that are not themselves index pages, with the same 'page.category' as the 'index'. 

If 'page.category' is empty ('') then all non-index pages will be given. 'page.max_subpages' gives the maximum number of subpages that will be generated.

These pages will be sorted by the field given in 'page.sort_key', and this will be either sorted in ascending order, or if 'page.sort_reverse' is True, it is sorted in descending order. The default is to sort by date, from most recent to oldest:

    index: True
    sort_key: date
    sort_reverse: True

You can always populate your own sorting key, with headings, section, chapters, tags etc.

Your template can access the 'page.subpages' field, and thus create your list of archives. As there will always be a 'page' dictionary, use 'subpage' as your looping variable:

    - for subpage in page.subpages:
      .excerpt
        %a{href:"{{ subpage.url }}"} {{ subpage.title }}
          {{ subpage.date.strftime("%d %b %Y ") }}

On pagination: sorry, but I hate pagination on websites, so I haven't implemented it here. My experience is that most blogs are small and don't have that many articles to archive, so why don't you put all the posts in a category on one page? 


## URLs

One of the biggest concerns in building a web-site is putting the files in the right place, so that clean URLs can be generated.

A key design principle of embellish is that it lets you determine the URL and file placement as much as possible. No matter what, 'page.target' will contain the filename of the target HTML file, which is written in the 'site.output_dir' directory. Any child sub-directories will be created on the fly.

Most of the time 'page.url' will match 'page.target', and it will kept as a URL relative to the site's root directory. If no URLs are specified, then it is assumed that the filename of the markdown file with respect to the 'site.content_dir' represents the 'page.target'. In flat-file mode, this means the HTML will appear in the same directory as the markdown file.

An important design principle for `embellish` is that relative URLs should work. That way sites can be placed in any sub-directory on the remote server. 

To use relative URLs in your templates is easy. Let's say in a `page`, you want to refer to `subpage.url`. You then use the `page.rel_site_url` field to take you from `page` to the root directory of the site. Then to take you down to `subpage`, you use `subpage.url`:

    %a{href="{{ page.rel_site_url }}/{{ subpage.url }}"} relative link

If you don't care about relative directories, you can just use `subpage.url` from `/`:

    %a{href="/{{ subpage.url }}"} absolute link

And with the full url in case you are interacting with external javascript libraries:

    %a{href="{{ site.url }}/{{ subpage.url }}"} full url link

Two other fields need to be mentioned. Sometimes legitimate filenames cannot serve as url's, so a conversion is done to turn the basename of the filename into a 'page.slug'. This can be directly overriden if the 'page.slug' field is given.

Finally, the extension of the output files are normally assumed to be '.html' but this can be overriden in 'site.ext' in the configuration file.


# Extension guide

## Architecture

Much of the architecture of `embellish` was inspired by `wok`: yaml metadata, page and site distinctions, url patterns generated from metadata. However, I spent way too much time patching `wok` to get it to work for me. The final straw was trying to get the haml/django extension to work with jinja. 

That's when I realized the plugin system does not work well for static web generators. The reason is that most website generators leverage several different templating systems and text renderers. Each templating engine and text renderer have their own plugin system. So the website generator acts as a frazzled middle-man who tries to build yet another plugin system to harmonize the plugin systems of all the other modules.

So I decided to strip it right down, replacing plugin modules with function hooks. The code is short, as the work-flow of a static website generator is really quite simple, with four major steps:

  1. converting page content into html
  2. parsing page metadata
  3. rendering pages with templates
  4. copying assets

At each step, there is a function hook. To change the behavior, simply replace the hooks with your own, adding your own special logic in Python.

## Caching

From profiling embellish, I found that most of the time was taken in 

  - markdown conversion
  - copying assets from the media file
  - reading from file
  - writing to file

To spend up incremental updating, all the page metadata, and converted text is stored in a single cached Python file `site.cache`. On incremental updates, this one file is read and processed before the site is rescanned. 

As the page metadata includes the content file's modification date, content files are only reread and converted by markdown if changed. 

When the rendered HTML is written, a MD5 checksum is stored. In future renderings, the checksum is compared to the stored checksum, and the final file is only written if the checksum is different. 

Assets are only copied if the original asset's modification time is more recent.





