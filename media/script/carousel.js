function runCarousel() {
    var tiles = Ext.select('#carousel .tile'),
        carousel = Ext.get('carousel'),
        twidth = 256,
        margin = (carousel.getWidth() - (3 * twidth)) / 4,
        positions = [margin, (2 * margin) + twidth, (3 * margin) + (2 * twidth)],
        idx = 0, timeout = 5000;
    tiles.setVisibilityMode(Ext.Element.DISPLAY);
    if (tiles.getCount() == 0) return;
    // reselect after stripping any bad images
    tiles = Ext.select('#carousel .tile');
    function tile(off) {
        var tidx = idx + off;
        if (off < 0) tidx += tiles.getCount();
        return tidx % tiles.getCount();
    }
    function align(right) {
        tiles.setLeft( right ? carousel.getWidth() : -twidth);
        for (var i = 0; i < 3; i++ ) {
            tiles.item( tile(i) ).setLeft(positions[i]);
        }
    }
    align(true);
    function go(left) {
        var lidx = left ? idx : tile(2);
        tiles.item(lidx).shift({x: left ? -twidth: carousel.getWidth() + twidth, callback: function() {
            tiles.item(lidx).setLeft(left ? carousel.getRight() : -twidth);
        }});
        idx = tile( left ? 1: -1);
        for (var i = 0; i < 3; i++) {
            var p = positions[i] + carousel.getLeft();
            tiles.item( tile(i) ).shift({x: p});
        }
    }

    var handle = window.setInterval(function() {go(true)}, timeout);
    var arrows = carousel.select('.arrow');
    arrows.item(0).on('click',function() {
       window.clearInterval(handle);
       align(true);
       go(true);
    });
    arrows.item(1).on('click',function() {
       window.clearInterval(handle);
       align(false);
       go(false);
    });
    window.tile= tile;
}

Ext.onReady(function(){
    runCarousel();
});