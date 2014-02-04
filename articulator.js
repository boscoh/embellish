(function() {
  var FigureList, is_onscreen;

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
        return _this.text_scroll_fn();
      });
      hash = window.location.hash;
      if (hash.slice(0, 5) === '#header') {
        this.select_header($(hash));
      } else if (hash.slice(0, 4) === '#fig') {
        _ref = this.figlinks;
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          figlink = _ref[_i];
          if (figlink.attr('href') === hash) {
            fig = $(hash);
            fig.ready(this.select_figlink_and_scroll_to_fig_fn(figlink));
          }
        }
      } else {
        this.text_scroll_fn();
      }
    }

    FigureList.prototype.select_figlink = function(figlink) {
      var selected_fig_href;
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

    FigureList.prototype.select_figlink_and_scroll_to_fig = function(figlink, callback) {
      var fig_href, figlist;
      this.select_figlink(figlink);
      fig_href = this.selected_figlink.attr('href');
      figlist = $(this.figlist_href);
      if (figlist.css('display') === 'none') {
        console.log('haha', fig_href, this.text_href);
        return $(this.text_href).scrollTo(fig_href, 500, callback);
      } else {
        return figlist.scrollTo(fig_href, 500, callback);
      }
    };

    FigureList.prototype.select_figlink_and_scroll_to_fig_fn = function(figlink) {
      var _this = this;
      return function(e) {
        var change_hash;
        change_hash = function() {
          return window.location.hash = figlink.attr('href');
        };
        _this.select_figlink_and_scroll_to_fig(figlink, change_hash);
        return false;
      };
    };

    FigureList.prototype.select_header = function(header) {
      var header_id;
      this.selected_header = header;
      header_id = header.attr('id');
      if (this.selected_headerlink !== null) {
        this.selected_headerlink.removeClass('active');
      }
      this.selected_headerlink = this.headerlinks[header_id];
      this.selected_headerlink.addClass('active');
      return window.location.hash = '#' + header_id;
    };

    FigureList.prototype.scroll_to_href_in_text = function(href, is_autodetect_figlink, callback) {
      var finish,
        _this = this;
      this.is_autodetect_figlink = is_autodetect_figlink;
      finish = function() {
        _this.is_autodetect_figlink = true;
        if (callback != null) {
          return callback();
        }
      };
      return $(this.text_href).scrollTo(href, 500, {
        onAfter: function() {
          return setTimeout(finish, 250);
        },
        offset: {
          top: -15
        }
      });
    };

    FigureList.prototype.scroll_to_href_in_text_fn = function(href, is_autodetect_figlink) {
      var _this = this;
      return function(e) {
        e.preventDefault();
        _this.scroll_to_href_in_text(href, is_autodetect_figlink, function() {
          return _this.text_scroll_fn();
        });
        return false;
      };
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
      var fig, fig_div_dom, fig_href, fig_id, fig_label, figlink, figlink_dom, figlink_href, figlink_id, figlink_label, i, i_fig, n_fig, n_figlink, new_fig_href, num_fig, orig_fig_href, reverse_link, _i, _j, _k, _len, _len1, _len2, _ref, _ref1, _ref2, _results;
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
        figlink.click(this.select_figlink_and_scroll_to_fig_fn(figlink));
        orig_fig_href = figlink.attr('href');
        fig_href = this.fig_href_from_orig[orig_fig_href];
        i_fig = this.i_fig_dict[fig_href];
        figlink_label = '(Figure ' + i_fig + ')&rArr;';
        figlink.html(figlink_label);
        figlink.attr('href', fig_href);
        this.figlinks.push(figlink);
        n_figlink += 1;
        figlink_href = '#' + figlink_id;
        reverse_link = $('<a>').append('&lArr;').attr('href', figlink_href);
        reverse_link.click(this.scroll_to_href_in_text_fn(figlink_href, false));
        this.fig_label_dict[fig_href].append(reverse_link);
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

    FigureList.prototype.make_toc = function() {
      var div, header, header_dom, header_href, header_id, headerlink, n_header, toc, _i, _len, _ref, _results;
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
        headerlink.click(this.scroll_to_href_in_text_fn(header_href, false));
        _results.push(div.append(headerlink));
      }
      return _results;
    };

    FigureList.prototype.text_scroll_fn = function() {
      var figlink, header, onscreen_figlink, onscreen_header, text, _i, _j, _len, _len1, _ref, _ref1;
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
        if (onscreen_header !== this.selected_header) {
          this.select_header(onscreen_header);
        }
      }
      if (this.is_autodetect_figlink) {
        if (this.selected_figlink != null) {
          if (is_onscreen(text, this.selected_figlink)) {
            return;
          }
        }
        onscreen_figlink = null;
        _ref1 = this.figlinks;
        for (_j = 0, _len1 = _ref1.length; _j < _len1; _j++) {
          figlink = _ref1[_j];
          if (is_onscreen(text, figlink)) {
            onscreen_figlink = figlink;
            break;
          }
        }
        if ((onscreen_figlink != null) && onscreen_figlink !== this.selected_figlink) {
          return this.select_figlink_and_scroll_to_fig(onscreen_figlink);
        }
      }
    };

    return FigureList;

  })();

  window.articulator = {
    set_figures_and_toc: function(toc_href, text_href, figlist_href) {
      return window.figure_list = new FigureList(toc_href, text_href, figlist_href);
    }
  };

}).call(this);
