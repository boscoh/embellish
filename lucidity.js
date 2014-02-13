(function() {
  var figlist_href, figures, init, one_columnn_width, page_margin, resize_window, sidebar, text, text_href, text_width, toc_href, two_column_width;

  text_href = '.text';

  toc_href = '.sidebar';

  figlist_href = '.figures';

  page_margin = 60;

  two_column_width = 1200;

  one_columnn_width = 600;

  text = null;

  text_width = null;

  sidebar = null;

  figures = null;

  resize_window = function() {
    var figlist_width, half_window_width, left, window_width;
    window_width = $(window).width();
    if (window_width <= one_columnn_width) {
      sidebar.css('display', 'none');
      figures.css('display', 'none');
      supplescroll.set_left(text, 0);
      return supplescroll.set_outer_width(text, window_width);
    } else if (window_width <= two_column_width) {
      sidebar.css('display', 'none');
      figures.css('display', 'block');
      half_window_width = Math.round(window_width / 2);
      supplescroll.set_left(text, 0);
      supplescroll.set_outer_width(text, half_window_width);
      figlist_width = window_width - half_window_width;
      supplescroll.set_left(figures, half_window_width);
      return supplescroll.set_outer_width(figures, figlist_width);
    } else {
      sidebar.css('display', 'block');
      figures.css('display', 'block');
      supplescroll.set_outer_width(text, text_width);
      supplescroll.set_left(sidebar, page_margin);
      left = supplescroll.get_right(sidebar);
      supplescroll.set_left(text, left);
      figlist_width = window_width - page_margin - page_margin - supplescroll.get_outer_width(sidebar) - supplescroll.get_outer_width(text);
      left = supplescroll.get_right(text);
      supplescroll.set_left(figures, left);
      return supplescroll.set_outer_width(figures, figlist_width);
    }
  };

  init = function() {
    text = $(text_href);
    sidebar = $(toc_href);
    figures = $(figlist_href);
    text_width = supplescroll.get_outer_width(text);
    supplescroll.init_touchscroll();
    supplescroll.set_figures_and_toc(toc_href, text_href, figlist_href);
    $(window).resize(resize_window);
    return resize_window();
  };

  $(window).ready(init);

}).call(this);
