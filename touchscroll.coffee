

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
