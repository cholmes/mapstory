// Make MovingBoxes Slideshow
$(window).load(function(){
    var slideShowDelay = 4000, // 4000 millisecond = 4 seconds
        timer,
        mb = $('#slider').data('movingBoxes'),
        loop = function(){
            // if wrap is true, check for last slide, then stop slideshow
            if (mb.options.wrap !== true && mb.curPanel >= mb.totalPanels){
                // click the button to pause
                $('button.slideshow').trigger('click');
                return;
            }
            // next slide, use mb.goBack(); to reverse direction
            mb.goForward();
            // run loop again
            timer = setTimeout(function(){
                loop();
            }, slideShowDelay);
        };
        loop();
});

$(function(){
  $('#slider').movingBoxes({
    startPanel   : 3,      // start with this panel
    reducedSize  : 0.8,    // non-current panel size: 80% of panel size
    wrap         : true   // if true, the panel will "wrap" (it really rewinds/fast forwards) at the ends
  });
});