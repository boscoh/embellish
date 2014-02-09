
# Embellish

low friction website generator


## What is Embellish

Embellish builds a working static website from a bunch of text files, with optional HTML templates.

It is designed to work with static websites in many forms, even in an existing directory. 


## Quick & Dirty Websites

Other generators dictate your directories to be structured their way.

Embellish does not.

Go to a directory (the embellish directory) with a markdown file (readme.md),  and:

    > embellish -m .

Boom! readme.html is generated and opened in a browser.

Now edit readme.txt, save, and refresh the browser.


## Docs

Go to <http://boscoh.github.io/embellish>



## Installation

To install:

    pip install embellish

Python depencencies should be automatically installed. 

But if you want them manually, they are: markdown, pyyaml, python-dateutil, jinja2, hamlpy, jinja2_hamlpy, flask, sassin

