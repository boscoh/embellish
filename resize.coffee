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

