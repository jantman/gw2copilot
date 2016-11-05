/* JS loaded at end of HTML body */

$(document).ready(function () {

    /* this sets the active navbar link */
    if ( window.location.pathname != "/" ) {
        $.each($('.navbar-nav').find('li'), function() {
            $(this).toggleClass('active',
                $(this).find('a').attr('href') == window.location.pathname);
        });
    };
});
