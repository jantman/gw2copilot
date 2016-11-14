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
    layerGroups: {}, // populated by addLayers()
    ZOOM_THRESH: 4, // cutoff between showing detailed data or not; >= this is detailed
    lastShownZone: null
};

var ICONS = {
    player: L.icon({
        iconUrl: '/static/img/crosshair_32x32.png',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, 0]
    }),
    waypoint: L.icon({
        iconUrl: '/cache/assets/map_waypoint_32x32.png',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, 0]
    }),
    poi: L.icon({
        iconUrl: '/cache/assets/map_poi_32x32.png',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, 0]
    }),
    vista: L.icon({
        iconUrl: '/cache/assets/map_vista_32x32.png',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, 0]
    }),
    heart: L.icon({
        iconUrl: '/cache/assets/map_heart_empty_32x32.png',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, 0]
    }),
    heropoint: L.icon({
        iconUrl: '/cache/assets/map_heropoint_32x32.png',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, 0]
    }),
    event: L.icon({
        iconUrl: '/cache/assets/map_special_event_32x32.png',
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
    map.on("zoomend", onZoomChange);
});

/******************************************************
 Binding functions for map-related buttons and clicks
 ******************************************************/

/**
 * Handle clicks on the map.
 *
 * @param {MouseEvent} e - Leaflet
 *   [MouseEvent](http://leafletjs.com/reference.html#mouse-event).
 */
function onMapClick(e) {
    popup
        .setLatLng(e.latlng)
        .setContent("You clicked the map at " + e.latlng + " (GW2 coords: " +
        latlon2gw(e.latlng).toString() + ")")
        .openOn(map);
}

/**
 * Handle when the map zoom changes
 *
 * @param {Event} e - Leaflet event
 */
function onZoomChange(e) {
    z = map.getZoom();
    if (z >= m.ZOOM_THRESH) {
        // waypoints
        map.addLayer(m.layerGroups.waypoints);
        map.addLayer(m.layerGroups.POIs);
        map.addLayer(m.layerGroups.vistas);
    } else {
        // hide all POIs; let the mouseover handle them
        map.removeLayer(m.layerGroups.waypoints);
        map.removeLayer(m.layerGroups.POIs);
        map.removeLayer(m.layerGroups.vistas);
    }
}

//
// Layer toggling
//

$("#btn_toggle_all").click(function() {
    alert("TODO: btn_toggle_all not implemented");
});

$("#btn_toggle_waypoints").click(function() {
    if( map.hasLayer() ) {
    } else {
    }
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
    m.layerGroups.waypoints = L.layerGroup();
    m.layerGroups.hearts = L.layerGroup();
    m.layerGroups.heropoints = L.layerGroup();
    m.layerGroups.POIs = L.layerGroup();
    m.layerGroups.vistas = L.layerGroup();
    m.layerGroups.events = L.layerGroup();

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
                waypoints: L.layerGroup(),
                hearts: L.layerGroup(),
                heropoints: L.layerGroup(),
                POIs: L.layerGroup(),
                vistas: L.layerGroup(),
                events: L.layerGroup()
            }
        };

        // add markers to the layer groups
        addZoneMarkersToLayers(map_id);

        // add layer groups to the global lists for toggling
        m.layerGroups.waypoints.addLayer(m.zones[map_id].layers.waypoints);
        m.layerGroups.hearts.addLayer(m.zones[map_id].layers.hearts);
        m.layerGroups.heropoints.addLayer(m.zones[map_id].layers.heropoints);
        m.layerGroups.POIs.addLayer(m.zones[map_id].layers.POIs);
        m.layerGroups.vistas.addLayer(m.zones[map_id].layers.vistas);
        m.layerGroups.events.addLayer(m.zones[map_id].layers.events);

        // add the borders layer and set mouse handlers on it
        m.zones[map_id].layers.borders.on('mouseover', handleZoneMouseIn, { map_id: map_id });
        m.zones[map_id].layers.borders.on('mouseout', handleZoneMouseOut, { map_id: map_id });
        m.zones[map_id].layers.borders.on('contextmenu', handleZoneContextMenu, { map_id: map_id });
        m.zones[map_id].layers.borders.addTo(map);
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
        layers.waypoints.addLayer(
            L.marker(
                gw2latlon(poi["coord"]),
                {
                    title: poi.name + " (" + poi.poi_id + ")",
                    alt: poi.name + " (" + poi.poi_id + ")",
                    riseOnHover: true,
                    icon: ICONS.waypoint
                }
            )
        );
    }

    // POIs
    for (idx in MAP_INFO[map_id]["points_of_interest"]["landmark"]) {
        poi = MAP_INFO[map_id]["points_of_interest"]["landmark"][idx];
        layers.POIs.addLayer(
            L.marker(
                gw2latlon(poi["coord"]),
                {
                    title: poi.name + " (" + poi.poi_id + ")",
                    alt: poi.name + " (" + poi.poi_id + ")",
                    riseOnHover: true,
                    icon: ICONS.poi
                }
            )
        );
    }

    // vistas
    for (idx in MAP_INFO[map_id]["points_of_interest"]["vista"]) {
        poi = MAP_INFO[map_id]["points_of_interest"]["vista"][idx];
        layers.vistas.addLayer(
            L.marker(
                gw2latlon(poi["coord"]),
                {
                    title: poi.name + " (" + poi.poi_id + ")",
                    alt: poi.name + " (" + poi.poi_id + ")",
                    riseOnHover: true,
                    icon: ICONS.vista
                }
            )
        );
    }
}

/**
 * Handler for when the user's mouse/cursor enters a zone layer.
 *
 * The handler's context (``this``) will be an object with one property,
 * ``map_id``.
 *
 * @param {MouseEvent} e - Leaflet
 *   [MouseEvent](http://leafletjs.com/reference.html#mouse-event).
 */
function handleZoneMouseIn(e) {
    //console.log("Mouse entered " + this.map_id);
    // only toggle markers on mouse if zoomed out past m.ZOOM_THRESH
    if (map.getZoom() < m.ZOOM_THRESH) {
        if (m.lastShownZone !== null && m.lastShownZone != this.map_id) {
            map.removeLayer(m.zones[m.lastShownZone].layers.waypoints);
        }
        map.addLayer(m.zones[this.map_id].layers.waypoints);
        m.zones[map_id].layers.borders.bringToFront();
        m.lastShownZone = this.map_id;
    }
}

/**
 * Handler for when the user's mouse/cursor exits a zone layer.
 *
 * The handler's context (``this``) will be an object with one property,
 * ``map_id``.
 *
 * @param {MouseEvent} e - Leaflet
 *   [MouseEvent](http://leafletjs.com/reference.html#mouse-event).
 */
function handleZoneMouseOut(e) {
    if (! e.target.getBounds().contains(e.latlng)) {
        //console.log("Mouse exited " + this.map_id);
        // only toggle markers on mouse if zoomed out past m.ZOOM_THRESH
        if (map.getZoom() < m.ZOOM_THRESH) {
            console.log("remove waypoints for map_id " + this.map_id);
            map.removeLayer(m.zones[this.map_id].layers.waypoints);
        }
    }
}

/**
 * Handler for when the user right-clicks on a zone layer.
 *
 * The handler's context (``this``) will be an object with one property,
 * ``map_id``.
 *
 * @param {MouseEvent} e - Leaflet
 *   [MouseEvent](http://leafletjs.com/reference.html#mouse-event).
 */
function handleZoneContextMenu(e) {
    console.log("Right-click on zone layer " + map_id);
    console.log(e);
}
