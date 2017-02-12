
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

- uses `commonmark` to translate your markdown.
- `yaml` front-matter to store meta-data
- `pug` templates to generate HTML files.

## Installation

To install:

    npm install embellish

## Todo
- modified file check for media transfers
- keep track of templates and modifications
- add a watcher for processing
- static webserver

## Changelog

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
