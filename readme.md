
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
    category: example-of-a-category
    ---
    This is an example file.

Save the file, and do:

    embellish -m .

Because of the '-m' option, embellish will attempt to open up the site in a web-browser using a local web-server. 

You should then find `example.html` in your directory. As no templates were specified, a default responsive-web-design is used (`embellish/defaults/default.haml`).


## My choice of formats

There are many formats for webdesign. For markup text, there's .markdown, .textile and .rsT. For CSS, there's .less, .scss and .sass. For Python templates, there's Django, Jinja, Cheetah and Mako. For metadata, there's JSON, YAML, Python pickle.

Well, here's what I recommend:

  - markdown for marking-up your prose 
  - YAML to describe your page metadata
  - HAML/Jinja2 for templating HTML
  - SASS for concise CSS 

It's ironic, I know, but all that significant whitespace technology - YAML, HAML and SASS - is more prevalent in the Ruby world. When placed in the context of Python, they fit better than a tuxedo on Daniel Craig.

The structure the markdown content page has 3 sections, separated by `---`:

    title: Header section
    new-field: anything that works with YAML
    ---
    Excerpt of text
    ---
    Main body of the text in markdown

The excerpt and header are both optional. The text is in the human-readable format [markdown](http://daringfireball.net/projects/markdown/basics).

In the header, apart from the standard metadata fields, which you can override, you can add pretty much any field that PyYAML can parse ([quick guide to YAML](https://github.com/Animosity/CraftIRC/wiki/Complete-idiot's-introduction-to-yaml)). Here's an example that will work with a HAML/Jinja2 template to be described below:

    template: example.haml
    links:
      - 
        name: apple
        href: http://apple.com
      - 
        name: google
        href: http://google.com 
    ---
    This is some content in the example
              
Notice the template field. You'd better have a template with that name in either:

  - the same directory as the content
  - in the `template_dir` of the site configuration
  - in the system's `defaults` directory. 

`Embellish` understands `.haml` files as HAML/Jinja2 templates (strictly speaking, it's actually a [HAML/Django template](https://github.com/jessemiller/HamlPy/blob/master/reference.md) piped into Jinja2), anything else will be treated as Jinja2 templates. I chose Jinja2 as it's compatible with Django templates, and has a sufficiently regular syntax that allows a HAML/Jinja2 subset to be defined.

So here's what `example.haml` might look like:

    %head
      %link{rel:'stylesheet',href:'styles.css'}

    %body
      .nav
        - for link in page.links:
          %a{href:'{{ link.href }}'}
            {{ link.name }}
      {{ page.content }}

I think it's extremely easy to read. It's DRY (Don't-Repeat-Yourself) and the control structure look extremely pythonic. Never will you have to go searching for that missing closing tag.

Notice though that `example.haml` links a style-sheet `styles.css`. Now you can provide this directly, or you can create a [SASS](http://sass-lang.com/docs/yardoc/file.INDENTED_SYNTAX.html) stylesheet instead `styles.sass`:

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

`Embellish` will convert any `.sass` file into the equivalent `.css` file. As you can see, the SASS format with indented spaces provides a consistent mix with YAML, HAML and Python.

Having saved all these files into your directory, go run:

    embellish .
    
Hopefully, you'll find an `example.html` that opens in your browser.

That's all there is.

## Larger Web-site Projects

Obviously for a more complicated website, you might want to separate your content, templates, assets (movies/stylesheets/images) and output. To do this simply create the site configuration file `site.yaml`:

    url: http://boscoh.com # if  then use relative urls
    content_dir: content  # look for markdown files
    template_dir: templates  # look for templates
    output_dir: site  # generated files and static files put here
    media_dir: media  # files to be correctly directly into the output file
    ext: .html

The benefits of this is that all the templates can be placed in the one directory `template_dir`. As well, production files are then copied into the `output_dir` as a clean directory with no source files mixed in.

Currently, in the copying of the assets `media_dir` into the `output_dir`, the `.sass` files are converted into `.css` files. As well, `.haml` files that are straight HAML and not HAML/Jinja2 are converted into `.html` files. This is for the case of special webpages that don't parse well into markdown-HAML/Jinja2 templates, such as pages that provide hooks into other web-services like login pages. You might then simply want to bash out straight HAML for these pages.

To run `embellish` against this configuration file:

    embellish site.yaml


## Testing on a Local Webserver

There is a common problem in building static websites in that most browsers treat a local file system differently from an actual web-server, making it difficult to debug the site properly. In particular, a web-server reads local directories directly and ignores index.html files. To overcome this, most static website generators provide a local server, typically written by subclassing from the crusty python module SimpleHTTPServer, that generates a local website from a local directory. 

Here, a local web-server `embellish.server` is provided. The code is written against the gorgeous [Flask](http://flask.pocoo.org/) library, resulting in much cleaner code. In particular, `embellish.server` can redirect clean URLs to the corresponding `.html` file. Specifically, this server can:

 - add trailing / to directories
 - process implied index.html in directories
 - add implied .html to clean urls
 - monitor modfiications in directories 
 - followed-up with a site regeneration hook 
 - attempts to open the /index.html in the local browser

To run the webserver, simply run `embellish` with the `--monitor` or `-m` flag:

    embellish -m site.yaml

The server will attempt to open the local files as a website on 127.0.0.1:5000 in the local browser. Browsing the static website through the local webserver will allow you to: 

 1. simulate the remote server on your local machine to check your links. 
 2. iterate designs quickly on your blog. Everytime you refresh a page, if changes have been detected on your source file (i.e. you saved the file in a text-editor), the site will be incrementally regenerated, and the updated page will be served.

# Templating guide

`Embellish` is designed to help you play around with templates. In `embellish`, there's no need to define different types of posts. Simply set the `page.template` field to the template of your choice, and populate the correspoding metadata in your markdown files. `Embellish` is quite flexible in looking for template files. And as long as the metadata and the templates match, you're good to go.

## Metadata

In order to make awesome templates, you have to understand the metadata that are piped into them. During rendering, two dictionaries are passed into every template:

  - `page`: contains all the information of a given page. For instance, the content is found in `page.content`
  - `site`: contains all the settings for the entire site. This includes all the source directories, site url, and is essentially, the information in the `site.yaml` configuration file.

Every `page` dictionary comes equiped with a set of default metadata. The best way to show this is from the Python source code:

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

This relevant fields in the `page` dictionary is then overriden by the YAML header of the corresponding source file. 

In a HAML/Jinja2 template, these fields are accessible in the form of:

    {{ page.title }}

In particular, dates are converted to standard Python datetime objects, and can be passed into the jinja templates by calling the datetime string method:

    {{ page.date.strftime("%d %b %Y") }}

If excerpts are not given, `page.excerpt` is set to the first 50 non-tag words in the main text.


## Index Pages

One of the most important function of static web generators is to organise blog posts into archives. The  metadata used to generate such pages are: `page.index`, `page.template`, `page.category`, `page.sort_key`, `page.sort_reverse`, `page.max_subpages`. 

The controlling variable is the `page.index`. If this is set to True, then a group of pages, `page.subpages`, will be generated. Essentially, `page.subpages` are a list of pages, that are not themselves index pages. 

Furthermore, only pages with the same `page.category` as the index page are collected with the number of pages capped to `page.max_subpages` if this is given. If `page.category` is empty ('') then pretty much the entire site will be put into `page.subpages` except of course for other index pages.

These pages will be sorted by the field given in `page.sort_key`, and this will be either sorted in ascending order, or if `page.sort_reverse` is True, it is sorted in descending order. The default is to sort by date, from most recent to oldest:

    index: True
    sort_key: date
    sort_reverse: True

You can always populate your own sorting key, with headings, section, chapters, tags etc.

In your HAML/Jinja2 template, to make a list of items such as in an archive of posts, you simply loop through the `page.subpages` field. As there already exists  a `page` dictionary, don't use that variable name! Use `subpage` instead as your looping variable:

    - for subpage in page.subpages:
      .excerpt
        %a{href:"{{ subpage.url }}"} {{ subpage.title }}
          {{ subpage.date.strftime("%d %b %Y ") }}

On pagination: sorry, but I hate pagination so I haven't implemented it here. My experience is that most blogs are not that big and don't have that many articles to archive. It would be so much easier to browse if all the posts were put in one page.


## URLs

Two design principles of `embellish` is that it lets you determine the URL and file placement as much as possible, and that relative URLs should work. No matter what, `page.target` will contain the filename of the target HTML file, which is written in the `site.output_dir` directory. If `page.url` or `page.target` are specified, these will be used.

Most of the time `page.url` will match `page.target`. If `page.url` is not specified, then it is assumed that the path of the markdown file with respect to the `site.content_dir` represents the `page.url` and the `page.target`. In flat-file mode, this means the `.html` file will appear in the same directory as the markdown file. 

A common exception to this are index.html files in subdirectories. Because browsers default to `dir/` for `dir/index.html`, a useful motif in the header for `index.html` files is:

    url: archive/
    target: archive/index.html



To use relative URLs in your templates is easy. Let's say in a `page`, you want to refer to the url of another page `subpage.url`. You then use the `page.rel_site_url` field to take you from `page` to the root directory of the site. Then to take you down to `subpage`, you use `subpage.url`:

    %a{href="{{ page.rel_site_url }}/{{ subpage.url }}"} relative link

If you don't care about relative directories, you can just use `subpage.url` from `/`:

    %a{href="/{{ subpage.url }}"} absolute link

And with the full url in case you are interacting with external javascript libraries:

    %a{href="{{ site.url }}/{{ subpage.url }}"} full url link

Two other fields need to be mentioned. Sometimes legitimate filenames cannot serve as URLs, so a conversion is done to turn the basename of the filename into a `page.slug`. This can be directly overriden if the `page.slug` field is given.

Finally, the extension of the output files are normally assumed to be `.html` but this can be overriden in `site.ext` in the configuration file.


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





