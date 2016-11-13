/* JS loaded at end of HTML body */

/*
gw2copilot/js/main.js

The latest version of this package is available at:
<https://github.com/jantman/gw2copilot>

################################################################################
Copyright 2016 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

    This file is part of gw2copilot.

    gw2copilot is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    gw2copilot is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with gw2copilot.  If not, see <http://www.gnu.org/licenses/>.

The Copyright and Authors attributions contained herein may not be removed or
otherwise altered, except to add the Author attribution of a contributor to
this work. (Additional Terms pursuant to Section 7b of the AGPL v3)
################################################################################
While not legally required, I sincerely request that anyone who finds
bugs please submit them at <https://github.com/jantman/gw2copilot> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me via email.
################################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
################################################################################
*/

$(document).ready(function () {

    /* this sets the active navbar link */
    if ( window.location.pathname != "/" ) {
        $.each($('.navbar-nav').find('li'), function() {
            $(this).toggleClass('active',
                $(this).find('a').attr('href') == window.location.pathname);
        });
    };
});



/**
 * Given an Object, return an array of its properties as [key, value] arrays,
 * sorted by value.
 *
 * from https://gist.github.com/umidjons/9614157
 *
 * @param {Object} obj - input object
 * @returns {Array} array of [key, value] object property arrays, sorted by val
 */
function sortProperties(obj)
{
  // convert object into array
    var sortable=[];
    for(var key in obj)
        if(obj.hasOwnProperty(key))
            sortable.push([key, obj[key]]); // each item is an array in format [key, value]

    // sort items by value
    sortable.sort(function(a, b)
    {
        var x=a[1].toLowerCase(),
            y=b[1].toLowerCase();
        return x<y ? -1 : x>y ? 1 : 0;
    });
    return sortable; // array in format [ [ key1, val1 ], [ key2, val2 ], ... ]
}

/**
 * Given an object, return an array of the values of all of its properties.
 *
 * @param {Object} obj - input object
 * @returns {Array} array of obj's property values
 */
function objectValues(obj) {
    props = [];
    for(key in obj){
        if(obj.hasOwnProperty(key)) {
            props.push(obj[key]);
        }
    }
    return props;
}