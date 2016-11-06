/*
gw2copilot/js/map.js

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

var map;
var popup = L.popup();
var m = {
    WORLD_ZOOM: 2,
    WORLD_COORDS: [-152, 126],
    playerMarker: null,
    playerLatLng: null,
    followPlayer: false
};

/* initialize map */
$(document).ready(function () {
    "use strict";

    map = L.map("map", {
        minZoom: 1,
        maxZoom: 7,
        crs: L.CRS.Simple
    }).setView(m.WORLD_COORDS, m.WORLD_ZOOM);

    L.tileLayer("/api/tiles?continent=1&floor=1&zoom={z}&x={x}&y={y}", {
        attribution: "Map Data and Imagery &copy; " +
            "<a href=\"https://wiki.guildwars2.com/wiki/API:Main\">GuildWars2/ArenaNet</a>" +
            "; <a href=\"https://github.com/jantman/gw2copilot\">gw2copilot is AGPL Free Software</a>",
        continuousWorld: true
    }).addTo(map);

    addLayers();

    map.on("click", onMapClick);
});

/******************************************************
 Binding functions for map-related buttons and clicks
 ******************************************************/
function onMapClick(e) {
    popup
        .setLatLng(e.latlng)
        .setContent("You clicked the map at " + map.project(e.latlng) +
    "; zoom=" + map.getZoom() + "; unprojected=" + e.latlng +
    "; center=" + map.getCenter() + "; bounds=[" + map.getBounds().getSouthWest()
    + ", " + map.getBounds().getNorthEast() + "]")
        .openOn(map);
}

//
// Layer toggling
//

$("#btn_toggle_all").click(function() {
    alert("TODO: btn_toggle_all not implemented");
});

$("#btn_toggle_waypoints").click(function() {
    alert("TODO: btn_toggle_waypoints not implemented");
});

$("#btn_toggle_hearts").click(function() {
    alert("TODO: btn_toggle_hearts not implemented");
});

$("#btn_toggle_heropoints").click(function() {
    alert("TODO: btn_toggle_herpoints not implemented");
});

$("#btn_toggle_POIs").click(function() {
    alert("TODO: btn_toggle_POIs not implemented");
});

$("#btn_toggle_vistas").click(function() {
    alert("TODO: btn_toggle_vistas not implemented");
});

$("#btn_toggle_events").click(function() {
    alert("TODO: btn_toggle_events not implemented");
});

//
// Map movement and zooming
//

// center the map on the player
$("#btn_center_player").click(function() { map.panTo(m.playerLatLng); });

// follow the player - keep the map centered on them
$("#btn_follow_player").click(function() {
    if ( m.followPlayer === true ) {
        // toggle off / false
        $("#btn_follow_player").switchClass('btn-success', 'btn-danger');
        m.followPlayer = false;
    } else {
        // toggle on / true
        $("#btn_follow_player").switchClass('btn-danger', 'btn-success');
        m.followPlayer = true;
    }
});

// zoom the map to the player's current zone
$("#btn_zoom_zone").click(function() {
    alert("TODO: btn_zoom_zone not implemented");
});

// zoom the map to the player, full zoom
$("#btn_zoom_player").click(function() {
    map.setZoom(map.getMaxZoom());
    map.panTo(m.playerLatLng);
});

// zoom the map out to the whole world
$("#btn_zoom_world").click(function() { map.setView(m.WORLD_COORDS, m.WORLD_ZOOM); });

/******************************************************
 Map utility functions
 ******************************************************/

function unproject(coord) {
    return map.unproject(coord, map.getMaxZoom());
}

function addPlayerMarker(latlng) {
    m.playerMarker = L.marker(latlng)
        .bindPopup("Player position.")
        .addTo(map);
}

function addLayers() {
    console.log("adding layers");
}