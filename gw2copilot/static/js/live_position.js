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
var playerinfo_dict = null;
var playerinfo_map_info = null;
var playerinfo_position = null;

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
    console.log("done getting initial data.");
}

/**
 * Handle an update to the player_dict data
 *
 * @param {object} data - player_dict data
 */
function handleUpdatePlayerDict(data) {
    console.log("handleUpdatePlayerData(" + JSON.stringify(data) + ")");
    if ( playerinfo_dict != data ) {
        $("#player_info_header").text(
            data["name"] + " (" + data["level"] + " " + data["race"] + " " +
            data["profession"] + ")"
        );
        playerinfo_dict = data;
    }
}

/**
 * Handle an update to the map_info data
 *
 * @param {object} data - map_info data
 */
function handleUpdateMapInfo(data) {
    console.log("handleUpdateMapInfo(" + JSON.stringify(data) + ")");
    if ( playerinfo_map_info != data ) {
        $("#map_info_header").text(
            data["map_name"] + " (" + data["map_level_range"] + "), " +
            data["region_name"] + ", " + data["continent_name"]
        );
        playerinfo_map_info = data;
    }
}

/**
 * Handle an update to the position data
 *
 * @param {array} data - position data
 */
function handleUpdatePosition(data) {
    console.log("handleUpdatePosition(" + JSON.stringify(data) + ")");
    m.playerLatLng = unproject(data);
    if ( m.playerMarker === null ) {
        addPlayerMarker(m.playerLatLng);
    } else {
        m.playerMarker.setLatLng(m.playerLatLng);
    }
    if ( m.followPlayer === true ) {
        map.panTo(m.playerLatLng);
    }
}
