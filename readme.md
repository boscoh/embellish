
# Embellij

_a lightweight static website generator_

`embellish` builds a working static website from a bunch of text files, with optional `HTML` templates and other goodies. It is a lightweight generator, designed to build websites from any directory, allowing you to organically grow your websites.

Docs at <http://boscoh.github.io/embellish>


## Quick & Dirty Websites

Other generators dictate your directories to be structured their way. `embellish` does not. Go to the `embellish` directory and type:

    > embellij -r .

Boom! 

`readme.html` is generated and opened in a browser. Now edit `readme.md`, save, and refresh the browser.


## Modules

- uses `commonmark` to translate your markdown.
- `yaml` front-matter to store meta-data
- `pug` templates to generate HTML files.

## Installation

To install:

    npm install embellij

## Todo
- modified files check to save files
- modified file check for media transfers
- keep track of templates and modifications
- add a watcher for processing

## Changelog

- 1.0 5/2/2017
    + translated from python embellish
