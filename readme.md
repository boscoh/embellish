
# Embellish

_a lightweight static website generator_

`embellish` builds a working static website from a bunch of text files, with optional `HTML` templates and other goodies. It is a lightweight generator, designed to build websites from any directory, allowing you to organically grow your websites.

Docs at <http://boscoh.github.io/embellish>


## Quick & Dirty Websites

Other generators dictate your directories to be structured their way. `embellish` does not. Go to the `embellish` directory and type:

    > embellish -m .

Boom! 

`readme.html` is generated and opened in a browser. Now edit `readme.md`, save, and refresh the browser.


## Installation

To install:

    pip install embellish

Python depencencies should be automatically installed. 

But if you want them manually, they are: `markdown`, `pyyaml`, `python-dateutil`, `jinja2`, `hamlpy`, `jinja2-hamlpy`, `flask` & `sassin`


## Changelog

- 0.9.5
    - added force option
    - fixed help for recursive option


