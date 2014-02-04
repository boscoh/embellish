(function() {

  window.touchscroll = {
    init: function() {
      var shift_from_edge;
      $(document).on('touchmove', function(e) {
        return e.preventDefault();
      });
      $('body').on('touchmove', '.touchscroll', function(e) {
        return e.stopPropagation();
      });
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
      return $('body').on('touchstart', '.touchscroll', function(e) {
        return shift_from_edge(e);
      });
    }
  };

}).call(this);
