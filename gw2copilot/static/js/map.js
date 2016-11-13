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
    followPlayer: false,
    zones: {},
    layerGroups: {
        waypoints: []
    }
};

var ICONS = {
    player: L.icon({
        iconUrl: '/static/img/crosshair_32x32.png',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, 0]
    })
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
        .setContent("You clicked the map at " + e.latlng + " (GW2 coords: " +
        latlon2gw(e.latlng).toString() + ")")
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
    sw_latlng = gw2latlon(MAP_INFO[P.map_id]['continent_rect'][0]);
    ne_latlng = gw2latlon(MAP_INFO[P.map_id]['continent_rect'][1]);
    map.fitBounds([sw_latlng, ne_latlng]);
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

/**
 * Convert gw2 coordinates to map lat/long.
 * wrapper around ``map.unproject()``.
 *
 * @param {Point} coord - gw2 (x, y) coordinate
 * @returns {LatLng} map lat/long coordinate
 */
function gw2latlon(coord) {
    return map.unproject(coord, map.getMaxZoom());
}

/**
 * Convert Leaflet map lat/long to gw2 (x, y) coordinates.
 * Wrapper around ``map.project()``.
 *
 * @param {array} coord - (x, y) lat/long map coordinate
 * @returns {Point} gw2 (x, y) coordinate
 */
function latlon2gw(latlon) {
    return map.project(latlon, map.getMaxZoom());
}

/**
 * Add the player marker at the current position.
 *
 * @param {array} latlng - (x, y) map Lat/Long position
 */
function addPlayerMarker(latlng) {
    m.playerMarker = L.marker(latlng, {icon: ICONS.player})
        .bindPopup("Player position.")
        .addTo(map);
}

var initial_layer_style = {
    weight: 0,
    fill: false
};

/**
 * Add the per-zone layers to the map.
 */
function addLayers() {
    console.log("adding layers");
    for (map_id in WORLD_ZONES_IDtoNAME) {
        data = MAP_INFO[map_id];
        layer_bounds = [
            gw2latlon(data.continent_rect[0]),
            gw2latlon(data.continent_rect[1])
        ]
        // build the data object, and the layers
        m.zones[map_id] = {
            data: data,
            layers: {
                borders: L.rectangle(layer_bounds).setStyle(initial_layer_style),
                waypoints: L.layerGroup()
            }
        };

        // add markers to the layer groups
        addZoneMarkersToLayers(map_id);

        // add layer groups to the global lists for toggling
        m.layerGroups.waypoints.push(m.zones[map_id].layers.waypoints);

        // create the featureGroup
        m.zones[map_id].feature_group = L.featureGroup(
            objectValues(m.zones[map_id].layers)
        );
        m.zones[map_id].feature_group.on('mouseover', function(e) {
            handleZoneMouseIn(e, map_id);
        });
        m.zones[map_id].feature_group.on('mouseout', function(e) {
            handleZoneMouseOut(e, map_id);
        });
        m.zones[map_id].feature_group.on('contextmenu', function(e) {
            handleZoneContextMenu(e, map_id);
        });
        m.zones[map_id].feature_group.addTo(map);
    }
    console.log("done adding layers.");
}

/**
 * Add the various markers for the zone to their layers.
 *
 * Updates ``m.zones[map_id]``
 */
function addZoneMarkersToLayers(map_id) {
    layers = m.zones[map_id].layers;

    // waypoints
    for (idx in MAP_INFO[map_id]["points_of_interest"]["waypoint"]) {
        poi = MAP_INFO[map_id]["points_of_interest"]["waypoint"][idx];
        console.log(poi);
        layers.waypoints.addLayer(
            L.marker(
                gw2latlon(poi["coord"]),
                {
                    title: poi.name + " (" + poi.poi_id + ")",
                    alt: poi.name + " (" + poi.poi_id + ")",
                    riseOnHover: true
                }
            )
        );
    }
}

/**
 * Handler for when the user's mouse/cursor enters a zone layer.
 *
 * @param {MouseEvent} e - Leaflet
 *   [MouseEvent](http://leafletjs.com/reference.html#mouse-event).
 * @param {int} map_id - map_id that layer corresponds to
 */
function handleZoneMouseIn(e, map_id) {
    console.log("Mouse entered " + map_id);
    console.log(e);
    e.target.setStyle({
        weight: 5,
        color: '#03f',
        dashArray: '',
        fillOpacity: 0.7,
        fill: true
    });
    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
        e.target.bringToFront();
    }
}

/**
 * Handler for when the user's mouse/cursor exits a zone layer.
 *
 * @param {MouseEvent} e - Leaflet
 *   [MouseEvent](http://leafletjs.com/reference.html#mouse-event).
 * @param {int} map_id - map_id that layer corresponds to
 */
function handleZoneMouseOut(e, map_id) {
    console.log("Mouse exited " + map_id);
    console.log(e);
    e.target.setStyle(initial_layer_style);
}

/**
 * Handler for when the user right-clicks on a zone layer.
 *
 * @param {MouseEvent} e - Leaflet
 *   [MouseEvent](http://leafletjs.com/reference.html#mouse-event).
 * @param {int} map_id - map_id that layer corresponds to
 */
function handleZoneContextMenu(e, map_id) {
    console.log("Right-click on zone layer " + map_id);
    console.log(e);
}
