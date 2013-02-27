// old way??
//var uvOptions = {};
//(function() {
//  var uv = document.createElement('script'); uv.type = 'text/javascript'; uv.async = true;
//  uv.src = ('https:' == document.location.protocol ? 'https://' : 'http://') + 'widget.uservoice.com/DhyHXis6WVw0y7RC7hHUNw.js';
//  var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(uv, s);
//})();

// new way??
(function(){var uv=document.createElement('script');uv.type='text/javascript';uv.async=true;uv.src='//widget.uservoice.com/gu0AM9xKZuBLDfJArcA.js';var s=document.getElementsByTagName('script')[0];s.parentNode.insertBefore(uv,s)})()

UserVoice = window.UserVoice || [];
UserVoice.push(['showTab', 'classic_widget', {
  mode: 'full',
  primary_color: '#cc6d00',
  link_color: '#007dbf',
  default_mode: 'support',
  forum_id: 189612,
  tab_label: 'Feedback & Support',
  tab_color: '#cc6d00',
  tab_position: 'middle-right',
  tab_inverted: false
}]);