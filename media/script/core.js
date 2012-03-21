$(function() {
  // open external links in a new tab
  $(document).delegate('a', 'click', function() {
      var root = location.href.replace(location.pathname + location.search + location.hash, '');

      if ( !this.href ) return;

      if ( 0 != this.href.indexOf(root) ) {
          window.open(this.href);
          return false;
      }
  });
});