
# embellish

_a lightweight static website generator_

`embellish` builds a working static website from a bunch of text files, with optional `HTML` templates and other goodies. It is a lightweight generator, designed to build websites from any directory, allowing you to organically grow your websites.

Docs at <http://boscoh.github.io/embellish>

## Quick & Dirty Websites

Other generators dictate your directories to be structured their way. `embellish` does not. Go to the `embellish` directory and type:

    > embellish -r .

Boom! 

`readme.html` is generated and opened in a browser. Now edit `readme.md`, save, and refresh the browser.

## Modules

- `commonmark` to translate markdown - allows markdown in html tags!
- `yaml` front-matter to store meta-data
- `pug` templates to generate HTML files and RSS feeds

## Installation

To install:

    npm install embellishjs

## Todo
- modified file check for media transfers
- keep track of templates and modifications

## Changelog

- 27/8/2018
    - fixed bug with double-rendering of md -> html
    - static syntax highlight.js with markdown-it
    - always compile index pages (otherwise doesn't pick up changes)
- 2.0.0-beta 16/2/2017
    - added watch
    - added static server
- 2.0.0-alpha 5/2/2017
    - translated to javascript ES2015
    - pug templates - much better templating system than pyhaml, different templating language
    - commonmark - allows markdown in <div> tags
    - simplified architecture 
    - standard yaml front-matter - different template semantics
    - removed lots of pre-processing from the python version
    - use file comparison for efficent caching
- 0.9.7
    - added single file mode 
    - docstring cleanup
    - docopt in binary
- 0.9.6
    - added force option
    - fixed help for recursive option
