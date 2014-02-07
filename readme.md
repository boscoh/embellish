
# Embellish

A LOW-FRICTION WEBSITE GENERATOR


## Making Quick & Dirty Websites

Most Python website generators are highly opinionated.

This one is not.

Other generators dictate your directories to be structured their way.

embellish can make a website out of any directory.

Go to a directory (e.g. the embellish directory) with a markdown file (e.g. readme.txt):

> embellish -m .
Boom!

readme.html is generated and opened in a browser.

Now edit readme.txt, save, and refresh the browser.


## Installation

To install:

    pip install embellish

Python depencencies should be automatically installed. If you want to manually install dependencies:

    pip install markdown pyyaml python-dateutil jinja2 hamlpy flask sassin pyScss

Now create a `example.mkd` in a temporary directory:

    title: An example file
    category: example-of-a-category
    ---
    This is an example file.

Save the file, and do:

    embellish -m .

Because of the '-m' option, embellish will attempt to open up the site in a web-browser using a local web-server. 

You should then find `example.html` in your directory. As no templates were specified, a default responsive-web-design is used (`embellish/defaults/default.haml`).


## Documentation

Further documentation is found at <http://boscoh.github.io/embellish>

