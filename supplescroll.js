(function() {
  var FigureList, build_page, get_bottom, get_content_height, get_content_width, get_left, get_outer_height, get_outer_width, get_right, get_spacing_width, get_top, init_touchscroll, is_onscreen, resize_img_dom, set_left, set_outer_height, set_outer_width, set_top, shift_from_edge;

  is_onscreen = function(parent_div, div) {
    var x1, x2, y1, y2;
    x1 = parent_div.scrollTop();
    x2 = x1 + parent_div.height();
    y1 = div.position().top;
    y2 = y1 + div.outerHeight(true);
    if (x1 <= y1 && y1 <= x2) {
      return true;
    }
    if (x1 <= y2 && y2 <= x2) {
      return true;
    }
    if (y1 <= x1 && x1 <= y2) {
      return true;
    }
    if (y1 <= x2 && x2 <= y2) {
      return true;
    }
    return false;
  };

  FigureList = (function() {

    function FigureList(toc_href, text_href, figlist_href) {
      var fig, figlink, hash, _i, _len, _ref,
        _this = this;
      this.toc_href = toc_href;
      this.text_href = text_href;
      this.figlist_href = figlist_href;
      this.selected_figlink = null;
      this.selected_header = null;
      this.selected_headerlink = null;
      this.is_autodetect_figlink = true;
      this.is_autodetect_header = true;
      this.is_scrolling = false;
      this.headers = [];
      this.figlinks = [];
      $(this.text_href).append($('<div>').addClass('page-filler'));
      if (this.figlist_href !== '') {
        this.transfer_figs();
        this.make_figlinks();
        $(this.figlist_href).append($('<div>').addClass('page-filler'));
      }
      if (this.toc_href !== '') {
        this.make_toc();
        $(this.toc_href).append($('<div>').addClass('page-filler'));
      }
      $(this.text_href).scroll(function() {
        return _this.scroll_in_text();
      });
      hash = window.location.hash;
      if (hash.slice(0, 7) === '#header') {
        this.select_header($(hash));
      } else if (hash.slice(0, 4) === '#fig') {
        _ref = this.figlinks;
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          figlink = _ref[_i];
          if (figlink.attr('href') === hash) {
            fig = $(hash);
            fig.ready(this.select_figlink_fn(figlink));
          }
        }
      } else {
        this.scroll_in_text();
      }
    }

    FigureList.prototype.make_toc = function() {
      var div, finish, header, header_dom, header_href, header_id, headerlink, n_header, toc, _i, _len, _ref, _results,
        _this = this;
      toc = $(this.toc_href);
      div = $('<div>').addClass('toc');
      toc.append(div);
      n_header = 1;
      this.headers = [];
      this.headerlinks = {};
      _ref = $(this.text_href).find('h1, h2, h3, h4');
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        header_dom = _ref[_i];
        header = $(header_dom);
        header_id = 'header' + n_header;
        n_header += 1;
        header.attr('id', header_id);
        this.headers.push(header);
        header_href = '#' + header_id;
        headerlink = $('<a>').attr('href', header_href);
        headerlink.append(header.clone().attr('id', ''));
        this.headerlinks[header_id] = headerlink;
        finish = function() {
          return _this.select_onscreen_figlink_and_figure();
        };
        headerlink.click(this.scroll_to_href_in_text_fn(header_href, false, finish));
        _results.push(div.append(headerlink));
      }
      return _results;
    };

    FigureList.prototype.transfer_figs = function() {
      var div, div_dom, div_id, figlist, new_div, num_fig, _i, _len, _ref, _results;
      figlist = $(this.figlist_href);
      num_fig = 1;
      _ref = $(this.text_href).find('div');
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        div_dom = _ref[_i];
        div_id = $(div_dom).attr('id');
        if ((div_id != null) && div_id.slice(0, 3) === 'fig') {
          div = $(div_dom);
          div.prepend('(Figure ' + num_fig + '). ');
          new_div = div.clone();
          div.addClass('fig-in-text');
          new_div.addClass('fig-in-figlist');
          figlist.append(new_div);
          _results.push(num_fig += 1);
        } else {
          _results.push(void 0);
        }
      }
      return _results;
    };

    FigureList.prototype.make_figlinks = function() {
      var click_fn, fig, fig_div_dom, fig_href, fig_id, fig_label, figlink, figlink_dom, figlink_href, figlink_id, figlink_label, i, i_fig, n_fig, n_figlink, new_fig_href, num_fig, orig_fig_href, reverse_link, select_fig_fn, _i, _j, _k, _len, _len1, _len2, _ref, _ref1, _ref2, _results;
      this.i_fig_dict = {};
      this.fig_hrefs = [];
      this.fig_href_from_orig = {};
      this.fig_label_dict = {};
      n_fig = 1;
      _ref = $(this.figlist_href).find('div');
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        fig_div_dom = _ref[_i];
        fig = $(fig_div_dom);
        fig_id = fig.attr('id');
        if ((fig_id != null) && fig_id.slice(0, 3) === 'fig') {
          orig_fig_href = '#' + fig_id;
          new_fig_href = '#figure' + n_fig;
          this.fig_href_from_orig[orig_fig_href] = new_fig_href;
          this.i_fig_dict[new_fig_href] = n_fig;
          this.fig_hrefs.push(new_fig_href);
          this.fig_label_dict[new_fig_href] = $('<span>');
          fig.attr('id', 'figure' + n_fig);
          n_fig += 1;
        }
      }
      n_figlink = 1;
      this.figlinks = [];
      _ref1 = $(this.text_href).find('a[href*="fig"]');
      for (_j = 0, _len1 = _ref1.length; _j < _len1; _j++) {
        figlink_dom = _ref1[_j];
        figlink = $(figlink_dom);
        figlink_id = 'figlink' + n_figlink;
        figlink.attr('id', figlink_id);
        figlink.addClass('figlink');
        figlink.click(this.select_figlink_fn(figlink));
        orig_fig_href = figlink.attr('href');
        if (orig_fig_href in this.fig_href_from_orig) {
          fig_href = this.fig_href_from_orig[orig_fig_href];
          i_fig = this.i_fig_dict[fig_href];
          figlink_label = '(Figure ' + i_fig + ')&rArr;';
          figlink.html(figlink_label);
          figlink.attr('href', fig_href);
          figlink_href = '#' + figlink_id;
          reverse_link = $('<a>').append('&lArr;').attr('href', figlink_href);
          select_fig_fn = this.select_figlink_fn(figlink);
          click_fn = this.scroll_to_href_in_text_fn(figlink_href, false, select_fig_fn);
          reverse_link.click(click_fn);
          this.figlinks.push(figlink);
          this.fig_label_dict[fig_href].append(reverse_link);
          n_figlink += 1;
        }
      }
      if (this.figlinks[0]) {
        this.select_figlink(this.figlinks[0]);
      }
      _ref2 = this.fig_hrefs;
      _results = [];
      for (i = _k = 0, _len2 = _ref2.length; _k < _len2; i = ++_k) {
        fig_href = _ref2[i];
        num_fig = i + 1;
        fig_label = this.fig_label_dict[fig_href];
        _results.push($(fig_href).prepend(fig_label));
      }
      return _results;
    };

    FigureList.prototype.select_figlink = function(figlink) {
      var selected_fig_href;
      if (this.selected_figlink === figlink) {
        return;
      }
      if (this.selected_figlink !== null) {
        this.selected_figlink.removeClass('active');
        selected_fig_href = this.selected_figlink.attr('href');
        $(selected_fig_href).removeClass('active');
      }
      this.selected_figlink = figlink;
      this.selected_figlink.addClass('active');
      selected_fig_href = this.selected_figlink.attr('href');
      return $(selected_fig_href).addClass('active');
    };

    FigureList.prototype.select_figlink_and_scroll_to_fig = function(figlink) {
      var callback, fig_href, figlist;
      if (this.selected_figlink === figlink) {
        return;
      }
      this.select_figlink(figlink);
      fig_href = this.selected_figlink.attr('href');
      figlist = $(this.figlist_href);
      callback = function() {
        return window.location.hash = figlink.attr('href');
      };
      if (figlist.css('display') === 'none') {
        return $(this.text_href).scrollTo(fig_href, 500, callback);
      } else {
        return figlist.scrollTo(fig_href, 500, callback);
      }
    };

    FigureList.prototype.select_figlink_fn = function(figlink) {
      var _this = this;
      return function(e) {
        if ((e != null) && e.hasOwnProperty('preventDefault')) {
          e.preventDefault();
        }
        return _this.select_figlink_and_scroll_to_fig(figlink);
      };
    };

    FigureList.prototype.select_header = function(header) {
      var hash, header_id;
      if (this.selected_header === header) {
        return;
      }
      this.selected_header = header;
      header_id = header.attr('id');
      if (this.selected_headerlink !== null) {
        this.selected_headerlink.removeClass('active');
      }
      this.selected_headerlink = this.headerlinks[header_id];
      this.selected_headerlink.addClass('active');
      hash = '#' + header_id;
      if (history.pushState) {
        return history.pushState(null, null, hash);
      } else {
        return window.location.hash = hash;
      }
    };

    FigureList.prototype.scroll_to_href_in_text = function(href, is_autodetect_figlink, callback) {
      var finish, settings,
        _this = this;
      if (this.is_scrolling) {
        return;
      }
      this.is_scrolling = true;
      this.is_autodetect_figlink = is_autodetect_figlink;
      finish = function() {
        _this.is_autodetect_figlink = true;
        _this.is_scrolling = false;
        if (callback != null) {
          return callback();
        }
      };
      settings = {
        onAfter: function() {
          return setTimeout(finish, 250);
        },
        offset: {
          top: -15
        }
      };
      return $(this.text_href).scrollTo(href, 500, settings);
    };

    FigureList.prototype.scroll_to_href_in_text_fn = function(href, is_autodetect_figlink, callback) {
      var _this = this;
      return function(e) {
        e.preventDefault();
        _this.scroll_to_href_in_text(href, is_autodetect_figlink, callback);
        return false;
      };
    };

    FigureList.prototype.select_onscreen_figlink_and_figure = function() {
      var figlink, onscreen_figlink, text, _i, _len, _ref;
      text = $(this.text_href);
      if (this.selected_figlink != null) {
        if (is_onscreen(text, this.selected_figlink)) {
          return;
        }
      }
      onscreen_figlink = null;
      _ref = this.figlinks;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        figlink = _ref[_i];
        if (is_onscreen(text, figlink)) {
          onscreen_figlink = figlink;
          break;
        }
      }
      if (onscreen_figlink != null) {
        return this.select_figlink_and_scroll_to_fig(onscreen_figlink);
      }
    };

    FigureList.prototype.select_onscreen_header = function() {
      var header, onscreen_header, text, _i, _len, _ref;
      text = $(this.text_href);
      onscreen_header = null;
      _ref = this.headers;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        header = _ref[_i];
        if (is_onscreen(text, header)) {
          onscreen_header = header;
          break;
        }
      }
      if (onscreen_header != null) {
        return this.select_header(onscreen_header);
      }
    };

    FigureList.prototype.scroll_in_text = function() {
      this.select_onscreen_header();
      if (this.is_autodetect_figlink) {
        return this.select_onscreen_figlink_and_figure();
      }
    };

    return FigureList;

  })();

  build_page = function(toc_href, text_href, figlist_href) {
    return window.figure_list = new FigureList(toc_href, text_href, figlist_href);
  };

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

  shift_from_edge = function(e) {
    var bottom, target;
    target = e.currentTarget;
    bottom = target.scrollTop + target.offsetHeight;
    if (target.scrollTop === 0) {
      return target.scrollTop = 1;
    } else if (target.scrollHeight === bottom) {
      return target.scrollTop -= 1;
    }
  };

  init_touchscroll = function() {
    $(document).on('touchmove', function(e) {
      return e.preventDefault();
    });
    $('body').on('touchmove', '.touchscroll', function(e) {
      return e.stopPropagation();
    });
    return $('body').on('touchstart', '.touchscroll', function(e) {
      return shift_from_edge(e);
    });
  };

  window.supplescroll = {
    build_page: build_page,
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
    resize_img_dom: resize_img_dom,
    init_touchscroll: init_touchscroll
  };

}).call(this);