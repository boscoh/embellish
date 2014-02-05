is_onscreen = (parent_div, div) ->
  x1 = parent_div.scrollTop()
  x2 = x1 + parent_div.height()
  y1 = div.position().top
  y2 = y1 + div.outerHeight(true)
  if x1 <= y1 and y1 <= x2
    return true
  if x1 <= y2 and y2 <= x2
    return true
  if y1 <= x1 and x1 <= y2
    return true
  if y1 <= x2 and x2 <= y2
    return true
  return false


class FigureList
  # text_href must be 'position:relative'
  constructor: (@toc_href, @text_href, @figlist_href) ->
    # initialize properties
    @selected_figlink = null
    @selected_header = null
    @selected_headerlink = null
    @is_autodetect_figlink = true
    @headers = []
    @figlinks = []
    
    $(@text_href).append(
        $('<div>').addClass('page-filler'))

    if @figlist_href != ''
      @transfer_figs()
      @make_figlinks()
      $(@figlist_href).append(
          $('<div>').addClass('page-filler'))

    if @toc_href != ''
      @make_toc()
      $(@toc_href).append(
          $('<div>').addClass('page-filler'))

    $(@text_href).scroll(() => @text_scroll_fn())

    # handle initial hash code
    hash = window.location.hash
    if hash.slice(0, 5) == '#header'
      @select_header($(hash))
    else if hash.slice(0, 4) == '#fig'
      for figlink in @figlinks
        if figlink.attr('href') == hash
          fig = $(hash)
          # wait till all assets have been loaded!
          fig.ready(@select_figlink_and_scroll_to_fig_fn(figlink))
    else
      @text_scroll_fn()

  select_figlink: (figlink) ->
    if @selected_figlink != null
      @selected_figlink.removeClass('active')
      selected_fig_href = @selected_figlink.attr('href')
      $(selected_fig_href).removeClass('active')
    @selected_figlink = figlink
    @selected_figlink.addClass('active')
    selected_fig_href = @selected_figlink.attr('href')
    $(selected_fig_href).addClass('active')

  select_figlink_and_scroll_to_fig: (figlink, callback) ->
    @select_figlink(figlink)
    fig_href = @selected_figlink.attr('href')
    figlist = $(@figlist_href)
    if figlist.css('display') == 'none'
      console.log('haha', fig_href, @text_href)
      $(@text_href).scrollTo(fig_href, 500, callback)
    else
      figlist.scrollTo(fig_href, 500, callback)

  select_figlink_and_scroll_to_fig_fn: (figlink) ->
    (e) => 
      change_hash = () -> 
        window.location.hash = figlink.attr('href')
      @select_figlink_and_scroll_to_fig(figlink, change_hash)
      false

  select_header: (header) ->
    @selected_header = header
    header_id = header.attr('id')

    # deselect old header in toc
    if @selected_headerlink != null
      @selected_headerlink.removeClass('active')

    # make header active
    @selected_headerlink = @headerlinks[header_id]
    @selected_headerlink.addClass('active')

    window.location.hash = '#' + header_id

  scroll_to_href_in_text: (href, is_autodetect_figlink, callback) ->
    @is_autodetect_figlink = is_autodetect_figlink
    finish = () => 
      @is_autodetect_figlink=true
      if callback?
        callback()
    $(@text_href).scrollTo(
        href, 
        500, 
        { 
          onAfter:()->setTimeout(finish, 250),
          offset: { top:-15 }
        })

  scroll_to_href_in_text_fn: (href, is_autodetect_figlink) ->
    (e) =>
      e.preventDefault()
      @scroll_to_href_in_text(href, is_autodetect_figlink, ()=>@text_scroll_fn())
      false

  transfer_figs: () ->
    figlist = $(@figlist_href)
    # in @text_href, move all <div id='fig*'> into @figlist_href
    num_fig = 1
    for div_dom in $(@text_href).find('div')
      div_id = $(div_dom).attr('id')
      if div_id? and div_id[0..2] == 'fig'
        div = $(div_dom)
        div.prepend('(Figure ' + num_fig + '). ') 
        new_div = div.clone()
        div.addClass('fig-in-text')
        new_div.addClass('fig-in-figlist')
        figlist.append(new_div)
        num_fig += 1

  make_figlinks: () ->
    # in @figlist_href, for <div id='fig*'>, assign label 'Figure.#'
    @i_fig_dict = {}
    @fig_hrefs = []
    @fig_href_from_orig = {}
    @fig_label_dict = {}

    # find all figures in the figlist, and set their id's
    n_fig = 1
    for fig_div_dom in $(@figlist_href).find('div')
      fig = $(fig_div_dom)
      fig_id = fig.attr('id')
      if fig_id? and fig_id[0..2] == 'fig'
        orig_fig_href = '#' + fig_id
        new_fig_href = '#figure' + n_fig
        @fig_href_from_orig[orig_fig_href] = new_fig_href
        @i_fig_dict[new_fig_href] = n_fig
        @fig_hrefs.push(new_fig_href)
        @fig_label_dict[new_fig_href] = $('<span>')
        fig.attr('id', 'figure' + n_fig)
        n_fig += 1

    # find all figlinks, and set their href's and id's
    n_figlink = 1
    @figlinks = []
    for figlink_dom in $(@text_href).find('a[href*="fig"]')
      figlink = $(figlink_dom)
      figlink_id = 'figlink'+n_figlink
      figlink.attr('id', figlink_id)
      figlink.addClass('figlink')
      figlink.click(@select_figlink_and_scroll_to_fig_fn(figlink))

      orig_fig_href = figlink.attr('href')
      fig_href = @fig_href_from_orig[orig_fig_href]
      i_fig =  @i_fig_dict[fig_href]
      figlink_label = '(Figure ' + i_fig + ')&rArr;'
      figlink.html(figlink_label)
      figlink.attr('href', fig_href)

      @figlinks.push(figlink)
      n_figlink += 1

      figlink_href = '#'+figlink_id
      reverse_link = $('<a>').append('&lArr;').attr('href', figlink_href)
      reverse_link.click(@scroll_to_href_in_text_fn(figlink_href, false))
      @fig_label_dict[fig_href].append(reverse_link)

    if @figlinks[0]
      @select_figlink(@figlinks[0])
    
    for fig_href, i in @fig_hrefs
      num_fig = i + 1
      fig_label = @fig_label_dict[fig_href]
      $(fig_href).prepend(fig_label)

  make_toc: ->
    toc = $(@toc_href)
    div = $('<div>').addClass('toc')
    toc.append(div)

    n_header = 1
    @headers = []
    @headerlinks = {}
    for header_dom in $(@text_href).find('h1, h2, h3, h4')
      # give the header an id to link against
      header = $(header_dom)
      header_id = 'header' + n_header
      n_header += 1
      header.attr('id', header_id)
      @headers.push(header)

      # create a link in the toc
      header_href = '#' + header_id
      headerlink = $('<a>').attr('href', header_href)
      headerlink.append(header.clone().attr('id', ''))
      @headerlinks[header_id] = headerlink
      headerlink.click(@scroll_to_href_in_text_fn(header_href, false))
      div.append(headerlink)

  text_scroll_fn: () ->
    # $(@text_href) must be position:relative to work
    text = $(@text_href)

    # check for onscreen header, and update toc
    onscreen_header = null
    for header in @headers
      if is_onscreen(text, header)
        onscreen_header = header
        break
    if onscreen_header? 
      if onscreen_header != @selected_header
        @select_header(onscreen_header)

    if @is_autodetect_figlink
      # check if @selected_figlink is onsceen
      if @selected_figlink?
        if is_onscreen(text, @selected_figlink)
          return
      # check if @selected_figlink is onsceen
      onscreen_figlink = null
      for figlink in @figlinks
        if is_onscreen(text, figlink)
          onscreen_figlink = figlink
          break
      if onscreen_figlink? and onscreen_figlink != @selected_figlink
        @select_figlink_and_scroll_to_fig(onscreen_figlink)



set_outer_height = (div, height) ->
  margin = div.outerHeight(true) - div.innerHeight()
  margin += parseInt(div.css('padding-top'))
  margin += parseInt(div.css('padding-bottom'))
  div.height(height - margin)

set_outer_width = (div, width) ->
  margin = div.outerWidth(true) - div.innerWidth()
  margin += parseInt(div.css('padding-left'))
  margin += parseInt(div.css('padding-right'))
  div.width(width - margin)

get_outer_width = (div) -> div.outerWidth(true)

get_spacing_width = (div) -> 
  get_outer_width(div) - get_content_width(div)

get_outer_height = (div) -> div.outerHeight(true)

get_content_width = (div) ->
  width = div.innerWidth()
  width -= parseInt(div.css('padding-left'))
  width -= parseInt(div.css('padding-right'))
  width

get_content_height = (div) ->
  height = div.innerHeight()
  height -= parseInt(div.css('padding-top'))
  height -= parseInt(div.css('padding-bottom'))
  height

get_bottom = (div) -> div.position().top + div.outerHeight(true)

get_right = (div) -> div.position().left + div.outerWidth(true)

get_top = (div) -> div.position().top

get_left = (div) -> div.position().left

set_top = (div, top) -> div.css('top', top)

set_left = (div, left) -> div.css('left', left)

resize_img_dom = (img_dom, width) ->
  img_elem = $(img_dom)
  if img_dom.naturalWidth < width
    img_elem.css('width': '')
  else
    img_elem.css('width': '100%')


# Link to outside world

window.articulator = {
  set_figures_and_toc: (toc_href, text_href, figlist_href) ->
    window.figure_list = new FigureList(toc_href, text_href, figlist_href)
}


window.resize = {
  set_outer_height: set_outer_height, 
  set_outer_width: set_outer_width,
  get_outer_width: get_outer_width,
  get_spacing_width: get_spacing_width,
  get_outer_height: get_outer_height,
  get_content_width: get_content_width, 
  get_content_height: get_content_height,
  get_bottom: get_bottom,
  get_right: get_right,
  get_left: get_left,
  get_top: get_top,
  set_top: set_top, 
  set_left: set_left, 
  resize_img_dom: resize_img_dom 
}



window.touchscroll = {
  init: () ->
    # block whole document from bouncing
    $(document).on('touchmove', (e)->e.preventDefault())

    # allow elements with .touchscroll to bounce
    $('body').on(
        'touchmove', '.touchscroll', 
        (e)->e.stopPropagation())

    # useful hack: shift a little from edge to avoid parent
    # from bouncing, which normally can't be disabled
    shift_from_edge = (e) ->
      target = e.currentTarget
      bottom = target.scrollTop + target.offsetHeight
      if target.scrollTop == 0
        target.scrollTop = 1
      else if target.scrollHeight == bottom
        target.scrollTop -= 1
 
    $('body').on(
        'touchstart', '.touchscroll', 
        (e)-> shift_from_edge(e))
}
