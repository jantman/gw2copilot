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
    resourceGroups: {},
    layerGroups: {}, // populated by addLayers()
    ZOOM_THRESH: 4, // cutoff between showing detailed data or not; >= this is detailed
    lastShownZone: null,
    hidden: {
        waypoints: false,
        POIs: false,
        vistas: false,
        heropoints: false,
        hearts: false,
        all: false,
        travel: false
        // the resource layer keys here are created by gw2timer_data:gw2timer_add_resource_markers()
    },
    travelLayer: null, // populated by gw2timer_add_travel(), called from addLayers()
    heartAreas: {},
    shownHeartAreas: [],
    POIlayers: ["waypoints", "POIs", "vistas", "heropoints", "hearts"],
    ResourceLayers: ["Metal", "RichMetal", "Plant", "RichPlant", "Wood", "RichWood"]
};

var ICONS = {
    player: L.icon({
        iconUrl: '/static/img/blue_dot_32x32.png',
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
    }),
    Metal: L.icon({
        iconUrl: '/cache/assets/map_node_mining_32x32.png',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, 0]
    }),
    Plant: L.icon({
        iconUrl: '/cache/assets/map_node_harvesting_32x32.png',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, 0]
    }),
    Wood: L.icon({
        iconUrl: '/cache/assets/map_node_logging_32x32.png',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, 0]
    }),
    asura_gate: L.icon({
        iconUrl: '/static/img/asura_gate.png',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, 0]
    }),
    interborder: L.icon({
        iconUrl: '/static/img/interborder.png',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, 0]
    }),
    skritt_tunnel: L.icon({
        iconUrl: '/static/img/skritt_tunnel_32x32.png',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, 0]
    }),
    launchpad: L.icon({
        iconUrl: '/static/img/launchpad.png',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, 0]
    }),
    launchpad_target: L.icon({
        iconUrl: '/static/img/launchpad_target.png',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, 0]
    }),
    asura_gate_highlighted: L.icon({
        iconUrl: '/static/img/asura_gate_highlighted.png',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, 0]
    }),
    interborder_highlighted: L.icon({
        iconUrl: '/static/img/interborder_highligted.png',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, 0]
    }),
    skritt_tunnel_highlighted: L.icon({
        iconUrl: '/static/img/skritt_tunnel_highlighted_32x32.png',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, 0]
    }),
    launchpad_highlighted: L.icon({
        iconUrl: '/static/img/launchpad_highlighted.png',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, 0]
    }),
    launchpad_target_highlighted: L.icon({
        iconUrl: '/static/img/launchpad_target_highlighted.png',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, 0]
    }),
};

/* initialize map */
$(document).ready(function () {
    "use strict";

    map = L.map("map", {
        minZoom: 1,
        maxZoom: 7,
        crs: L.CRS.Simple,
        contextmenu: true,
        contextmenuItems: []
    }).setView(m.WORLD_COORDS, m.WORLD_ZOOM);

    L.tileLayer("/api/tiles?continent=1&floor=1&zoom={z}&x={x}&y={y}", {
        attribution: "Map Data and Imagery &copy; " +
            "<a href=\"https://wiki.guildwars2.com/wiki/API:Main\">GuildWars2/ArenaNet</a>; " +
            "some data from <a href=\"http://gw2timer.com/\">gw2timer.com</a>" +
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
    showHideLayers();
}

//
// Layer toggling
//

// handler for "ALL" POI layers
$("#btn_toggle_all").click(function() {
    m.hidden.all = ! m.hidden.all;
    showHideLayers();
});

$("#btn_toggle_travel").click(function() {
    m.hidden.travel = ! m.hidden.travel;
    showHideLayers();
});

// add handlers for POI layer-hiding button clicks
for(var i =0; i < m.POIlayers.length; i++) {
    layername = m.POIlayers[i];
    $("#btn_toggle_" + layername).click({layername: layername}, function(event) {
        m.hidden[event.data.layername] = ! m.hidden[event.data.layername];
        showHideLayers();
    });
}

// add handlers for resource layer-hiding button clicks
for(var i =0; i < m.ResourceLayers.length; i++) {
    layername = m.ResourceLayers[i];
    $("#btn_toggle_" + layername).click({layername: layername}, function(event) {
        m.hidden[event.data.layername] = ! m.hidden[event.data.layername];
        showHideLayers();
    });
}

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
    zoomToZone(P.map_id);
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
    for(var i =0; i < m.POIlayers.length; i++) {
        m.layerGroups[m.POIlayers[i]] = L.layerGroup()
    }

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
                borders: L.rectangle(
                    layer_bounds,
                    {
                        contextmenu: true,
                        contextmenuItems: [
                            {
                                text: data.map_name + " (map " + map_id + ")",
                                index: 0
                            },
                            {
                                separator: true,
                                index: 1
                            },
                            {
                                text: "Zoom to Zone",
                                index: 2,
                                callback: function(e) { zoomToZone(this.map_id); },
                                context: { map_id: map_id }
                            }
                        ]
                    }
                ).setStyle(initial_layer_style),
                waypoints: L.layerGroup(),
                hearts: L.layerGroup(),
                heropoints: L.layerGroup(),
                POIs: L.layerGroup(),
                vistas: L.layerGroup()
            }
        };

        // add markers to the layer groups
        addZoneMarkersToLayers(map_id);

        // add layer groups to the global lists for toggling
        for(var i =0; i < m.POIlayers.length; i++) {
            m.layerGroups[m.POIlayers[i]].addLayer(m.zones[map_id].layers[m.POIlayers[i]]);
        }

        // add the borders layer and set mouse handlers on it
        m.zones[map_id].layers.borders.on('mouseover', handleZoneMouseIn, { map_id: map_id });
        m.zones[map_id].layers.borders.on('mouseout', handleZoneMouseOut, { map_id: map_id });
        m.zones[map_id].layers.borders.addTo(map);
    }
    gw2timer_add_resource_markers();
    gw2timer_add_travel();
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
                    icon: ICONS.waypoint,
                    contextmenu: true,
                    contextmenuItems: [
                        {
                            text: poi.name + " (POI " + poi.poi_id + ")",
                            index: 0
                        },
                        {
                            index: 1,
                            text: poi.chat_link + ' (copy to clipboard)',
                            callback: function(e) { copyTextToClipboard(this.chat_link); },
                            context: { chat_link: poi.chat_link }
                        },
                        {
                            text: '<a href="#">wiki.guildwars2.com</a>',
                            index: 2,
                            context: { link: "http://wiki.guildwars2.com/index.php?title=Special%3ASearch&search=" + encodeURIComponent(poi.chat_link) + "&go=Go" },
                            callback: function(e) { window.open(this.link); }
                        },
                        {
                            text: '<a href="#">gw2.mmorpg-life.com</a>',
                            index: 3,
                            context: { link : "http://gw2.mmorpg-life.com/mojsearch.php?s=" + encodeURIComponent(poi.name) + "&submit=Search" },
                            callback: function(e) { window.open(this.link); }
                        }
                    ]
                }
            )
        );
    }

    // POIs / "landmarks"
    for (idx in MAP_INFO[map_id]["points_of_interest"]["landmark"]) {
        poi = MAP_INFO[map_id]["points_of_interest"]["landmark"][idx];
        layers.POIs.addLayer(
            L.marker(
                gw2latlon(poi["coord"]),
                {
                    title: poi.name + " (" + poi.poi_id + ")",
                    alt: poi.name + " (" + poi.poi_id + ")",
                    riseOnHover: true,
                    icon: ICONS.poi,
                    contextmenu: true,
                    contextmenuItems: [
                        {
                            text: poi.name + " (POI " + poi.poi_id + ")",
                            index: 0
                        },
                        {
                            index: 1,
                            text: poi.chat_link + ' (copy to clipboard)',
                            callback: function(e) { copyTextToClipboard(this.chat_link); },
                            context: { chat_link: poi.chat_link }
                        }
                    ]
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
                    icon: ICONS.vista,
                    contextmenu: true,
                    contextmenuItems: [
                        {
                            text: poi.name + " (POI " + poi.poi_id + ")",
                            index: 0
                        },
                        {
                            index: 1,
                            text: poi.chat_link + ' (copy to clipboard)',
                            callback: function(e) { copyTextToClipboard(this.chat_link); },
                            context: { chat_link: poi.chat_link }
                        }
                    ]
                }
            )
        );
    }

    // heropoints / "skill_challenges"
    for (idx in MAP_INFO[map_id]["skill_challenges"]) {
        poi = MAP_INFO[map_id]["skill_challenges"][idx];
        layers.heropoints.addLayer(
            L.marker(
                gw2latlon(poi["coord"]),
                {
                    title: poi.idx,
                    alt: poi.idx,
                    riseOnHover: true,
                    icon: ICONS.heropoint
                }
            )
        );
    }

    // hearts
    for (idx in MAP_INFO[map_id]["tasks"]) {
        poi = MAP_INFO[map_id]["tasks"][idx];
        layers.hearts.addLayer(
            L.marker(
                gw2latlon(poi["coord"]),
                {
                    title: poi.objective + " (task_id " + poi.task_id + ")",
                    alt: poi.objective + " (task_id " + poi.task_id + ")",
                    riseOnHover: true,
                    icon: ICONS.heart
                }
            ).on('click', handleHeartClick, {task_id: poi.task_id})
            .on('mouseover', handleHeartMouseOver, {task_id: poi.task_id})
            .on('mouseout', handleHeartMouseOut, {task_id: poi.task_id})
        );
        // heartAreas
        bounds = poi.bounds.slice(0, poi.bounds.length - 1);
        m.heartAreas[poi.task_id] = L.polygon(
            bounds.map(function(e) { return gw2latlon(e); })
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

/**
 * Zoom the map to show as much of the specified zone (map_id) as possible.
 *
 * @param {int} map_id - the map_id to zoom to
 */
function zoomToZone(map_id) {
    sw_latlng = gw2latlon(MAP_INFO[map_id]['continent_rect'][0]);
    ne_latlng = gw2latlon(MAP_INFO[map_id]['continent_rect'][1]);
    map.fitBounds([sw_latlng, ne_latlng]);
}

/**
 * Given the current ``m.hidden`` settings and the current map zoom level,
 * show and hide marker layers as appropriate.
 */
function showHideLayers() {
    if ( map.getZoom() >= m.ZOOM_THRESH ) {
        // zoomed in enough, show all POIs based on our settings
        if( m.hidden.all === true ){
            // POI layers; "all" doesn't touch resource layers
            for(var i =0; i < m.POIlayers.length; i++) {
                if(map.hasLayer(m.layerGroups[m.POIlayers[i]])) {
                    map.removeLayer(m.layerGroups[m.POIlayers[i]]);
                }
            }
            // travel layer
            if(map.hasLayer(m.travelLayer)) {
                map.removeLayer(m.travelLayer);
            }
            $("#btn_toggle_all").switchClass('btn-success', 'btn-danger');
        } else {
            $("#btn_toggle_all").switchClass('btn-danger', 'btn-success');
            // POI layers
            for(var i =0; i < m.POIlayers.length; i++) {
                if ( m.hidden[m.POIlayers[i]] === true ) {
                    if(map.hasLayer(m.layerGroups[m.POIlayers[i]])) {
                        map.removeLayer(m.layerGroups[m.POIlayers[i]]);
                    }
                    $("#btn_toggle_" + m.POIlayers[i]).switchClass('btn-success', 'btn-danger');
                } else {
                    map.addLayer(m.layerGroups[m.POIlayers[i]]);
                    $("#btn_toggle_" + m.POIlayers[i]).switchClass('btn-danger', 'btn-success');
                }
            }
            // handle travel layer
            if( m.hidden["travel"] === true ) {
                if(map.hasLayer(m.travelLayer)) {
                    map.removeLayer(m.travelLayer);
                }
                $("#btn_toggle_travel").switchClass('btn-success', 'btn-danger');
            } else {
                map.addLayer(m.travelLayer);
                $("#btn_toggle_travel").switchClass('btn-danger', 'btn-success');
            }
        }
        // resource layers
        for(var i =0; i < m.ResourceLayers.length; i++) {
            if ( m.hidden[m.ResourceLayers[i]] === true ) {
                if(map.hasLayer(m.resourceGroups[m.ResourceLayers[i]])) {
                    map.removeLayer(m.resourceGroups[m.ResourceLayers[i]]);
                }
                $("#btn_toggle_" + m.ResourceLayers[i]).switchClass('btn-success', 'btn-danger');
            } else {
                map.addLayer(m.resourceGroups[m.ResourceLayers[i]]);
                $("#btn_toggle_" + m.ResourceLayers[i]).switchClass('btn-danger', 'btn-success');
            }
        }
    } else {
        // hide all POIs; let the mouseover handle them
        for(var i =0; i < m.POIlayers.length; i++) {
            if(map.hasLayer(m.layerGroups[m.POIlayers[i]])) {
                map.removeLayer(m.layerGroups[m.POIlayers[i]]);
            }
        }
        // hide all resource layers
        for(var i =0; i < m.ResourceLayers.length; i++) {
            if(map.hasLayer(m.resourceGroups[m.ResourceLayers[i]])) {
                map.removeLayer(m.resourceGroups[m.ResourceLayers[i]]);
            }
        }
        // hide travel layer
        if(map.hasLayer(m.travelLayer)) {
            map.removeLayer(m.travelLayer);
        }
    }
}

/**
 * Handle a click on a heart.
 *
 * The handler's context (``this``) will be an object with one property,
 * ``task_id``.
 *
 * @param {MouseEvent} e - Leaflet
 *   [MouseEvent](http://leafletjs.com/reference.html#mouse-event).
 */
function handleHeartClick(e) {
    if ( m.shownHeartAreas.indexOf(this.task_id) > -1 ) {
        map.removeLayer(m.heartAreas[this.task_id]);
        m.shownHeartAreas.splice(m.shownHeartAreas.indexOf(this.task_id), 1);
    } else {
        map.addLayer(m.heartAreas[this.task_id]);
        m.shownHeartAreas.push(this.task_id);
    }
}

/**
 * Handle mouse entering a heart.
 *
 * The handler's context (``this``) will be an object with one property,
 * ``task_id``.
 *
 * @param {MouseEvent} e - Leaflet
 *   [MouseEvent](http://leafletjs.com/reference.html#mouse-event).
 */
function handleHeartMouseOver(e) {
    if ( ! map.hasLayer(m.heartAreas[this.task_id]) ) {
        map.addLayer(m.heartAreas[this.task_id]);
    }
}

/**
 * Handle mouse exiting a heart.
 *
 * The handler's context (``this``) will be an object with one property,
 * ``task_id``.
 *
 * @param {MouseEvent} e - Leaflet
 *   [MouseEvent](http://leafletjs.com/reference.html#mouse-event).
 */
function handleHeartMouseOut(e) {
    if ( m.shownHeartAreas.indexOf(this.task_id) < 0 ) {
        map.removeLayer(m.heartAreas[this.task_id]);
    }
}
