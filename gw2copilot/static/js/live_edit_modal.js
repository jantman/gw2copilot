/*
gw2copilot/js/live_edit_modal.js

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

// @TODO pull this from API, via https://github.com/jantman/gw2copilot/issues/16
var zone_id_to_name = {
    15: "Queensdale",
    17: "Harathi Hinterlands",
    18: "Divinity's Reach",
    19: "Plains of Ashford",
    20: "Blazeridge Steppes",
    21: "Fields of Ruin",
    22: "Fireheart Rise",
    23: "Kessex Hills",
    24: "Gendarran Fields",
    25: "Iron Marches",
    26: "Dredgehaunt Cliffs",
    27: "Lornar's Pass",
    28: "Wayfarer Foothills",
    29: "Timberline Falls",
    30: "Frostgorge Sound",
    31: "Snowden Drifts",
    32: "Diessa Plateau",
    34: "Caledon Forest",
    35: "Metrica Province",
    39: "Mount Maelstrom",
    50: "Lion's Arch",
    51: "Straits of Devastation",
    53: "Sparkfly Fen",
    54: "Brisban Wildlands",
    62: "Cursed Shore",
    65: "Malchor's Leap",
    73: "Bloodtide Coast",
    91: "The Grove",
    139: "Rata Sum",
    218: "Black Citadel",
    326: "Hoelbrak",
    873: "Southsun Cove",
    988: "Dry Top",
    1015: "The Silverwastes",
    1041: "Dragon's Stand",
    1043: "Auric Basin",
    1045: "Tangled Depths",
    1052: "Verdant Brink",
    1165: "Bloodstone Fen",
    1175: "Ember Bay"
};

// BEGIN building drop-down choices array

// array to hold the choices for the zone selection dropdowns on edit modal
zone_options = [ { value: 0, label: '{Select a Zone}' } ];

// main.js provides sortProperties()
sortProperties(zone_id_to_name).map( function(item) {
    // item is an array of [key (map_id), value (map_name)]
    zone_options.push({ value: item[0], label: item[1]});
});
// END building drop-down choices array

// appendGrid for Edit Zone Reminders modal
$(function () {
    $('#zoneRemindersTable').appendGrid({
        initRows: 1,
        columns: [
            { name: 'map_id', display: 'Zone', type: 'select', ctrlOptions: zone_options, ctrlCss: { width: '100%' } },
            { name: 'text', display: 'Reminder Text', type: 'text', ctrlCss: { width: '100%' } },
            { name: 'id', type: 'hidden', value: 0 }
        ],
        hideButtons: {
            removeLast: true,
            moveUp: true,
            moveDown: true,
            insert: true
        },
        customGridButtons: {
            append: function() { return $('<button/>').attr({ type: 'button' }).append('<span class="ui-button-icon-primary ui-icon ui-icon-plusthick"></span>', '<span class="ui-button-text"></span>'); },
            remove: function() { return $('<button/>').attr({ type: 'button' }).append('<span class="ui-button-icon-primary ui-icon ui-icon-trash"></span>', '<span class="ui-button-text"></span>'); }
        }
    });
});