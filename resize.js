(function() {
  var get_bottom, get_content_height, get_content_width, get_left, get_outer_height, get_outer_width, get_right, get_spacing_width, get_top, resize_img_dom, set_left, set_outer_height, set_outer_width, set_top;

  set_outer_height = function(div, height) {
    var margin;
    margin = div.outerHeight(true) - div.innerHeight();
    margin += parseInt(div.css('padding-top'));
    margin += parseInt(div.css('padding-bottom'));
    return div.height(height - margin);
  };

  set_outer_width = function(div, width) {
    var margin;
    margin = div.outerWidth(true) - div.innerWidth();
    margin += parseInt(div.css('padding-left'));
    margin += parseInt(div.css('padding-right'));
    return div.width(width - margin);
  };

  get_outer_width = function(div) {
    return div.outerWidth(true);
  };

  get_spacing_width = function(div) {
    return get_outer_width(div) - get_content_width(div);
  };

  get_outer_height = function(div) {
    return div.outerHeight(true);
  };

  get_content_width = function(div) {
    var width;
    width = div.innerWidth();
    width -= parseInt(div.css('padding-left'));
    width -= parseInt(div.css('padding-right'));
    return width;
  };

  get_content_height = function(div) {
    var height;
    height = div.innerHeight();
    height -= parseInt(div.css('padding-top'));
    height -= parseInt(div.css('padding-bottom'));
    return height;
  };

  get_bottom = function(div) {
    return div.position().top + div.outerHeight(true);
  };

  get_right = function(div) {
    return div.position().left + div.outerWidth(true);
  };

  get_top = function(div) {
    return div.position().top;
  };

  get_left = function(div) {
    return div.position().left;
  };

  set_top = function(div, top) {
    return div.css('top', top);
  };

  set_left = function(div, left) {
    return div.css('left', left);
  };

  resize_img_dom = function(img_dom, width) {
    var img_elem;
    img_elem = $(img_dom);
    if (img_dom.naturalWidth < width) {
      return img_elem.css({
        'width': ''
      });
    } else {
      return img_elem.css({
        'width': '100%'
      });
    }
  };

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
  };

}).call(this);
