/*
gw2copilot/js/live_position.js

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

var sock = null;

/* player info */
var P = {
    /* player dict; updated by handleUpdatePlayerDict() */
    dict: null,
    /* map information; updated by handleUpdateMapInfo() */
    map_info: null,
    /* position information; updated by handleUpdatePosition() */
    position: null,
    /* object with keys of map_id, values list of string zone reminders */
    /* updated by live_edit_modal.js makeZoneRemindersCache() */
    zone_reminders: {}
};

/**
 * Setup websocket server and hook in message handler.
 */
window.onload = function() {
    var wsuri;

    if (window.location.protocol === "file:") {
       wsuri = "ws://localhost:" + ws_port;
    } else {
       wsuri = "ws://" + window.location.hostname + ":" + ws_port;
    }

    if ("WebSocket" in window) {
       sock = new WebSocket(wsuri);
    } else if ("MozWebSocket" in window) {
       sock = new MozWebSocket(wsuri);
    } else {
       log("Browser does not support WebSocket!");
    }

    if (sock) {
       sock.onopen = function() {
          console.log("Connected to " + wsuri);
       }

       sock.onclose = function(e) {
          console.log("Connection closed (wasClean = " + e.wasClean + ", code = " + e.code + ", reason = '" + e.reason + "')");
          sock = null;
       }

       sock.onmessage = function(e) {
          console.log("Got websocket message: " + e.data);
          j = JSON.parse(e.data);
          if ( j["type"] == "tick" ) {
              console.log("ignoring websocket tick");
          }
          handleWebSocketMessage(j);
       }
    }

    getInitialData();
};

/**
 * Handle an incoming websocket message; dispatch it to the correct
 * handle_* function.
 *
 * @param {object} data - the JSON-decoded message content
 */
function handleWebSocketMessage(data) {
    console.log("handleWebSocketMessage(" + JSON.stringify(data) + ")");
    if ( data.type == "position") {
        handleUpdatePosition(data.data);
    } else if ( data.type == "map_info" ) {
        handleUpdateMapInfo(data.data);
    } else if ( data.type == "player_dict" ) {
        handleUpdatePlayerDict(data.data);
    } else {
        console.log("handleWebSocketMessage got message of unknown type: "
            + JSON.stringify(data) + ")"
        );
    }
}

/**
 * Perform the initial data request to initialize the UI. This requests all of
 * the information that we receive via websockets, in case the app started
 * and websocket broadcasts were sent before the page loaded.
 */
function getInitialData() {
    console.log("Getting initial data.");
    $.ajax({
        url: "/api/player_dict"
    }).done(function( data ){
        handleUpdatePlayerDict(data);
    });
    $.ajax({
        url: "/api/map_info"
    }).done(function( data ){
        handleUpdateMapInfo(data);
    });
    $.ajax({
        url: "/api/position"
    }).done(function( data ){
        handleUpdatePosition(data);
    });
    // fill the zone/map reminders cache
    getZoneRemindersFromAPI();
    console.log("done getting initial data.");
}

/**
 * Handle an update to the player_dict data
 *
 * @param {object} data - player_dict data
 */
function handleUpdatePlayerDict(data) {
    console.log("handleUpdatePlayerData(" + JSON.stringify(data) + ")");
    if ( P.dict != data ) {
        $("#player_info_header").text(
            data["name"] + " (" + data["level"] + " " + data["race"] + " " +
            data["profession"] + ")"
        );
        P.dict = data;
    }
}

/**
 * Handle an update to the map_info data
 *
 * @param {object} data - map_info data
 */
function handleUpdateMapInfo(data) {
    console.log("handleUpdateMapInfo(" + JSON.stringify(data) + ")");
    if ( P.map_info != data ) {
        $("#map_info_header").text(
            data["map_name"] + " (" + data["map_level_range"] + "), " +
            data["region_name"] + ", " + data["continent_name"]
        );
        P.map_info = data;
        doZoneReminder(data["map_id"]);
    }
}

/**
 * Handle an update to the position data
 *
 * @param {array} data - position data
 */
function handleUpdatePosition(data) {
    console.log("handleUpdatePosition(" + JSON.stringify(data) + ")");
    P.position = data;
    m.playerLatLng = gw2latlon(data);
    if ( m.playerMarker === null ) {
        addPlayerMarker(m.playerLatLng);
    } else {
        m.playerMarker.setLatLng(m.playerLatLng);
    }
    if ( m.followPlayer === true ) {
        map.panTo(m.playerLatLng);
    }
}

/**
 * When we change maps, update the Zone Reminders as necessary
 *
 * @param {integer} map_id - the new map ID
 */
function doZoneReminder(map_id) {
    // first, hide and empty the current span
    $('#zone_reminder_span').hide();
    $('#zone_reminder_span').text('');
    // now, if we have new reminder(s), show them
    if ( P.zone_reminders.hasOwnProperty(map_id) && P.zone_reminders[map_id].length > 0 ) {
        reminders = P.zone_reminders[map_id];
        html = '';
        if ( reminders.length < 2 ) {
            html = reminders[0] + '<br />';
        } else {
            reminders.map( function(item) {
                html = html + item + '<br /><br />';
            });
        }
        $('#zone_reminder_span').html(html);
        $('#zone_reminder_span').show();
        // flash the containing box red...
        // slowly turn it red...
        $('#zoneRemindersListItem').animate(
            {backgroundColor:'#f00'}, 1000, "swing", function() {
                // ...and then when that's complete, back to white
                $('#zoneRemindersListItem').animate(
                    {backgroundColor:'#fff'}, 1000
                );
            }
        );
    }
}