---
title: embellish - a lightweight static website generator
banner: embellish - a lightweight static website generator
---


# Embellish

> _a lightweight static website generator_

There are many static website generators out there, but most of them are quite opionated: they demand your posts be put in this directory and your posts ordered in that way, and they often include some tricky custom-defined formats.

Static websites are really quite simple. They're just a bunch of HTML files in a directory. A static website generator simply transforms text files into HTML files, and includes a few goodies like stylesheets and javascript modules.

`embellish` is a lightweight generator, that can build a website from any directory, transforming any text files it finds into HTML, allowing you to organically grow your website. It's also very small, and quite easy to modify. 

As `embellish` is designed around the Python ecosystem, it carefully uses standard Python-like indented-text formats, that have been well-tested, namely:

  - markdown for text
  - YAML front-matter 
  - pug templates

## Example Websites Built with Embellish

- [Bosco Ho's Emporium of Words](http://boscoh.com) - my personal website
- [supplescroll](http://boscoh.github.io/supplescroll) - a document decorator used to build this page
- [the human gene parade](http://boscoh.com/geneparade/human/) - an interactive genome browser

## Quick & Dirty Websites

Other generators dictate your website to be structured their way. `embellish` does not. 

Go to a directory with a `markdown` file (e.g. the `embellish` directory):

	> embellish .

Boom! 

`readme.html` is generated and opened in a browser.

Now edit `readme.txt`, save, and refresh the browser.





## Installation

The project is hosted at [github](https://github.com/boscoh/embellish).

Have `node` installed? Then:

	  > npm install -g embellishjs

Or install manually using the [zip file](https://github.com/boscoh/embellish/archive/master.zip):

    > npm link

All the following examples can be found in the `examples` directory of the zip file.


## Blog with Categories

Any litmus test for a static website generator is to make a blog. Here's a quick guide using `embellish` where `markdown` is used for the text, `YAML` for metadata, and `haml` to write the HTML.


`embellish` will recognize files with extensions `.txt`, `.md`, `.mkd` and `.markdown` as post/article pages.

### Article page

`embellish` expects a text page with an optional YAML front-matter defined  by `---`  such as in `post.mkd` [](#fig-post).


<div id="fig-post">
  <code>post.mkd</code> - example of a Markdown Post

```
---
title: The Title of this Post
template: post.pug
---
# Great Post in Markdown

## Markdown Sub-headers!

This is the _body_ of the text 
written in markdown
```

</div>


The front-matter is optional. `embellish` reads the header as [YAML](https://github.com/Animosity/CraftIRC/wiki/Complete-idiot's-introduction-to-yaml) metadata. There are a few fields used by `embellish` but you can add anything you want. This metadata will be made available to you in the template as a dictionary called `page`.

To generate an HTML page from this article post, a template is required. In this case, the template referred to in the header is `post.pug`. If no template is given, a default one is used that is located in the embllish directory under `defaults/default.pug`.


### Templates and Style Sheets

Templates are used to generate HTML files from text files and their attendant header information.

`embellish` uses [pug](https://pugjs.org/api/getting-started.html) templates. A simple example is `post.pug` [](#fig-template), which was referred in `post.txt` above.

<div id="fig-template"> 
  <code>post.pug</code> - example of a simple HAML template to generate an article HTML

```
head
  link(href='styles.css' rel='stylesheet')
body
  .title
    | #{ page.title }
  .nav
    | category: 
    | #{ page.category } &#183;
    | published: 
    | #{ page.date }#
  hr
  | !{ page.content }
```

</div>

For details on how templates work in `embellish`, see the Template Guide below.

Notice that there is a link to a style sheet `styles.css` [](#fig-template). Now, you could simply creat your own `styles.css` and put it in the directory, but I strongly recommend you to write [SASS](https://github.com/boscoh/sassin) style sheets such as `styles.sass` [](#fig-sass), and use [`sass`](http://sass-lang.com/) to compile into `styles.css`. **note** in previous versions, this was done for you but it was rather fragile and difficult to debug. Now, you should just compile to css yourself.

<div id="fig-sass"> 
  <code>style.sass</code> - a SASS file to generate <code>style.css</code>

```
body
  background-color: #FFF
  font-family: Helvetica
  width: 450px
  margin: 40px auto
.title
  text-transform: uppercase
  font-weight: 900
  font-size: 18px
  letter-spacing: 0.1em
.nav
  font-style: italic
  font-size: 12px
```

</div>

With the post, the template, and the style sheet done, we are now ready to make the blog:

    > embellish .

Open `post.html` in your browser.


### Index Pages

To really get the blog going, though, we will need to build an index page to list a bunch of posts. First, we create a text file that will generate an index of posts `index.mkd` [](#fig-index-mkd).

<div id="fig-index-mkd"> <code>index.mkd</code> - example of a markdown file that generates a blog index file

```
---
template: index.pug
index: True
sortKey: date
sortReverse: True
maxSubpages: 5
title: Blog Posts
---
Some words to describe the following list of 
posts that are arranged in reverse chronological 
order.
```

</div>

In the header of the post, the key flag is:

    index: True

which tells `embellish` to send a list of posts into the template during compilation of the HTML file. Since in this case, no `category` was given, all the posts found by `embellish` will be used.

The posts will be sorted by date as indicated by:
    
    sortKey: date

Any other field could have been used, but let's start with date. We'd also like to do it in reverse order as fits blogging convention:

    sortReverse: True

And we don't want too many posts, so
 
    maxSubpages: 5



### Templating Index Pages

Okay now the text file is done, let's make the template for an index file `index.pug` [](#fig-index-haml).

<div id="fig-index-haml"> <code>index.pug</code> - example of a HAML template that generates the HTML code for an index markdown file

```
head
  link(href='styles.css' rel='stylesheet')
body
  .title
    | #{ page.title }
  | !{ page.content }
  ul  
    each subpage in page.subpages
      li
        b
          a(href= `${subpage.relSiteUrl}/${subpage.url}`)= subpage.title
        br
        i= subpage.excerpt
        br
        .nav
          if subpage.category
            | category: #{ subpage.category }
            br
          | date: #{subpage.date}
        br
        br

```

</div>

How it works is that during compilation, `embellish` will package all the information for the page into a dictionary `page` and send it into the template. As well another dictionary `site` will also be sent that includes the site configuration information. These will be described in detail below in the Templating Guide.

The header of the template is pretty similar to `post.pug` [](#fig-template) above, with the big difference in that `index.pug` [](#fig-index-haml) can handle a special field called `page.subpages`. 

`page.subpages` holds a list of all the pages found by `embellish` that belong to this index page. If a `category` was given, then only pages with the same `category` will be kept in the list. Here, since no `category` was given, all pages are given.

To handle the display of all the `page.subpages`, there is a pug control loop:

    each subpage in page.subpages
        | #{ subpage.title }
        | #{ subpage.excerpt }

**Note**: it's important you use `subpage` as the looping variable, as `page` would otherwise clash with the main `page` dictionary.

You might have noticed that there is no pagination. I hate pagination, so I did not implement it. Just put all posts in one page. 



### Referring to URLs 

It's important to get the URL's right to show up in the template.

First we need the site URL, and there are two ways to get it:

1. The site's absolute URL, which is `#{ site.url }`
2. The site's relative URL which depends on the location of the page in question `#{page.relSiteUrl}`

The URL of a page thus combines the site's URL with the page's URL. 

If you want the absolute URL, you can construct the url using this interpolated string (notice the use of back-ticks):

    `${site.url}/${page.url}` 

For the relative URL of a page, which is more flexible, but more prone to breaking during deployment :

    `${site.relSiteUrl}/${page.url}` 

In `index.pug` [](#fig-index-haml), relative links are used for the `subpage` in the looping through the collected posts, so the link is:

    `${subpage.relSiteUrl}/${supbage.url}`


### Archiving With Categories

Now with blog posts, you might want to archive posts under different categories. 

Let's say you have a post about vampires `vampire.mkd` [](#fig-vampire-post). You give it a category in the header by:

    category: vampire

<div id="fig-vampire-post"> <code>vampire.mkd</code> - a post with a category of vampire.

```
---
title: The Vampire Post
template: post.pug
category: vampire
---
# This is Vampire Post

## There's Vampire as Category!

This is also in __markdown__.
```

</div>

<div id="fig-archive-index"> <code>archive.mkd</code> - a post with a category of vampire.

```
---
template: index.pug
index: True
sortKey: date
category: vampire
sortReverse: True
title: Archive of Posts about Vampires
---
```

</div>

Then, to collect all your vampire posts in an archive, you can create an index file `archive.mkd` [](#fig-archive-index), where the only difference from `index.mkd` [](#fig-index-mkd), is that a category is given:

    category: vampire

And then you run:

    > embellish .

Which will generate an index post of all pages in `index.html` and an archive page for vampire posts `archive.html`.






## Larger Websites

### Configuration Files

Obviously for a more complicated website, you want to separate your content, templates, assets, and output into different directories.

To tell `embellish` where the directories are, you create a configuration file in the YAML format, such as `site.yaml` [](#fig-config):

<div id="fig-config"> <code>site.yaml</code> a YAML configuration file for a larger website
<pre class="codehilite">
url: http://boscoh.com # if  then use relative urls
contentDir: content  # look for markdown files
templateDir: templates  # look for templates
cachedPages: site.cache
outputDir: site  # generated files and static files put here
recursive: True # recursively searches through directories
mediaDir: media  # files to be copied directly into the output directory
writeExt: .html
</pre>
</div>

To whit:

- `url`: the hard-coded URL of your website. If given, this is available in any templates you make as `site.url`.
- `contentDir`: the directory where you put all your posts and index files.
- `templateDir`: for holding templates
- `mediaDir`: your supporting files - javascript, css style sheets, images, movies, etc. These will be copied directly into the `outputDir`
- `outputDir`: the directory where all compiled contents and contents of `mediaDir` are put
- `writeExt`: the extension for the html files, typically `.html` or `.htm`

To run `embellish` against this configuration file:

    embellish site.yaml

And the result will be in the `outputDir`.

Note: when using `embellish` with a directory as the argument, such as:

     > embellish .

Internally, `embellish` sets these fields in `site` - `contentDir`, `templateDir`, `mediaDir`, `outputDir` - to the current directory. `embellish` will skip the copying of files, and thus the website is made in place!



### Recursive Directory Processing

Since `embellish` is meant to be a quick-and-dirty website generator, the default is to search only in the directory specified for content files. 

This avoids accidentally telling `embellish` to search through a very large forest of subdirectories.

But you can tell `embellish` to exhaustively process all subdirectories with the `-r` option:

    > embellish -r .


## Templating guide

To write custom templates in `jinja2-haml`, you'll have to understand the data model `embellish` uses to compile templates.


During compilation, two dictionaries are passed into every template:

1. `site`: contains all the settings for the entire site. This includes all the source directories, site url, and is essentially, the information in the `site.yaml` [](#fig-config) configuration file.

2. `page`: contains all the information of a given page, including `subpages` when the `page` is an index.


### Page Metadata

Every `page` dictionary comes equiped with a set of default metadata. The best way to show this is from the Python source code [](#fig-page-dictionary):

<div id="fig-page-dictionary"> <code>page</code> - the python dictionary that is piped into every template

```
let defaultPage = {
  template: 'default.pug',  // name of template file
  filename: null,  // name of markdown file
  checksum: '', // checksum used to check final output to avoid redundant writes
  excerpt: '', // text to put in excerpt, no tags please!
  content: '',  // main text of article
  title: '',  // title for indexing and for large display
  category: '',  // category of article for indexing
  relSiteUrl: '',  // the top site directory relative to this page
  dateFormatString: null, // dateFormat formatting string
  date: null,  // published date
  slug: null,  // url-safe name of article used to make url and files
  url: '',   // relative url used for links in index files
  target: '',    // target filename, maybe different to url due to redirection
  index: false,   // indicates if this is an indexing page
  sortKey: null,  // the field on which to sort under in indexing
  sortReverse: true,  // ascending or descing order for sorting
  subpages: [],   // in indexing, pages belonging to the index placed here
  maxSubpages: null,  // a maximum limit of files to put in subpages
};
```

</div>

This relevant fields in the `page` dictionary is then overriden by the YAML header of the corresponding source file. 

In a `pug` template, these fields are accessible in the form of:

    #{ page.title }

In particular, dates are converted to standard Python datetime objects, and can be passed into the jinja templates by calling the datetime string method:

    #{ page.date }

If excerpts are not given, `page.excerpt` is set to the first 50 non-tag words in the main text.



### Filenames and Directory Structure 

Two design principles of `embellish` is that it lets you determine the URL and file placement as much as possible, and that relative URLs should work. No matter what, `page.target` will contain the filename of the target HTML file, which is written in the `site.outputDir` directory. If `page.url` or `page.target` are specified, these will be used.

Most of the time `page.url` will match `page.target`. If `page.url` is not specified, then it is assumed that the path of the markdown file with respect to the `site.contentDir` represents the `page.url` and the `page.target`. In flat-file mode, this means the `.html` file will appear in the same directory as the markdown file. 

A common exception to this are index.html files in subdirectories. Because browsers default to `dir/` for `dir/index.html`, a useful motif in the header for `index.html` files is:

    url: archive/
    target: archive/index.html

Two other fields need to be mentioned. Sometimes legitimate filenames cannot serve as URLs, so a conversion is done to turn the basename of the filename into a `page.slug`. This can be directly overriden if the `page.slug` field is given.

Finally, the extension of the output files are normally assumed to be `.html` but this can be overriden in `site.ext` in the configuration file.

### Absolute & Relative URLs

To reiterate, the site's URL is given in:

1. an absolute form `#{site.url}`
2. a relative form, relative to the page `#{page.relSiteurl}`

Where for instance if `embellish` was run in the current directory, and so is the file, then:

    page.relSiteurl = ''

The page's URL is thus a combination of the site URL and the page's relative URL:

1. absolute: `` `${site.url }/${ page.url}` ``
2. relative `` `${page.relSiteurl}/${ page.url}` ``



