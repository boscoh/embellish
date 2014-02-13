
# set hrefs to the page
text_href = '.text'
toc_href = '.sidebar'
figlist_href = '.figures'

# responsive web settings
page_margin = 60
two_column_width = 1200
one_columnn_width = 600

# declare module variables
text = null
text_width = null
sidebar = null
figures = null


# resize callback for the window
resize_window = () ->
  window_width = $(window).width()

  if window_width <= one_columnn_width
    sidebar.css('display','none')
    figures.css('display','none')

    supplescroll.set_left(text, 0)
    supplescroll.set_outer_width(text, window_width)

  else if window_width <= two_column_width
    sidebar.css('display','none')
    figures.css('display','block')

    half_window_width = Math.round(window_width/2)
    supplescroll.set_left(text, 0)
    supplescroll.set_outer_width(text, half_window_width)

    figlist_width = window_width - half_window_width
    supplescroll.set_left(figures, half_window_width)
    supplescroll.set_outer_width(figures, figlist_width)

  else # three columns
    sidebar.css('display','block')
    figures.css('display','block')

    supplescroll.set_outer_width(text, text_width)
    supplescroll.set_left(sidebar, page_margin)
    left = supplescroll.get_right(sidebar)
    supplescroll.set_left(text, left)
    figlist_width = window_width - page_margin - page_margin \
        - supplescroll.get_outer_width(sidebar) \
        - supplescroll.get_outer_width(text)
    left = supplescroll.get_right(text)
    supplescroll.set_left(figures, left)
    supplescroll.set_outer_width(figures, figlist_width)


init = () ->
  text = $(text_href)
  sidebar = $(toc_href)
  figures = $(figlist_href)
  text_width = supplescroll.get_outer_width(text)

  supplescroll.init_touchscroll()
  supplescroll.set_figures_and_toc(
      toc_href, text_href, figlist_href)

  $(window).resize(resize_window)
  resize_window()


$(window).ready(init)



