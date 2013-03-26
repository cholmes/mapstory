    $(document).ready(function() {
        // override default options (also overrides global overrides)
        $('div.expandable p').expander({
            slicePoint:       80,  // default is 100
            expandPrefix:     ' ', // default is '... '
            expandText:       '[...]', // default is 'read more'
            collapseTimer:    5000, // re-collapses after 5 seconds; default is 0, so no re-collapsing
            userCollapseText: '[^]'  // default is 'read less'
        });
    });
