# Notes on Embellish website

  - docs
    - introduction
    - design
    - methods to upload 

# Transferring files

An important parameter is the `media` directory. These are files that are to be transferred to the website directory. Now most of the files here will be directly copied, but `embellish` is aware of limited number of files that will be processed in some ways. 

These are:

  - .sass indented-syntax files => CSS
  - .scss SCSS files => CSS
  - .haml files => HTML
  - .coffee coffeescript files => JS 

It might be a little confusing to see .haml files, but .haml expresses plain HTML files that do not necessarily have to be Jinja2 templates. They could describe static HTML files that have complicated layouts and thus not suitable for the .markdown treatment.

# Local web-server

I've found that a key to efficient webdesign is the ability to iterate changes quickly. And one of the key to this is having an effective local web-server.

Why do you need this? The main reason is that relative web-addresses on a server work differently to relative file-names so you need to serve your local website in a web-server to really test the links.

But the more important thing is that a local webserver can watch your source files and automatically recompile your site whenever it detects a change. 

Thus your workflow will be one where your programing text-editor is open in one side of your page, and your browser will be open on the other side. 

You make a change to your source file, and you save it. Then you click on the browser to refresh. The new page gets compiled.
      - markdown
      - hamlpy site
      - coffeescript 

# Examples
      - readme doc
      - simple website
      - blog/index
      - xml/rss
      - table of contents
    - extension examples
      - api 
      - textile instead of markdown
      - table of contents