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

function unproject(coord) {
    return map.unproject(coord, map.getMaxZoom());
}

function onMapClick(e) {
    console.log("You clicked the map at " + map.project(e.latlng));
}

$(document).ready(function () {
    "use strict";

    var southWest, northEast;

    map = L.map("mapcontainer", {
        minZoom: 0,
        maxZoom: 7,
        crs: L.CRS.Simple
    }).setView([0, 0], 0);

    southWest = unproject([0, 32768]);
    northEast = unproject([32768, 0]);

    map.setMaxBounds(new L.LatLngBounds(southWest, northEast));

    L.tileLayer("/api/tiles?continent=1&floor=1&zoom={z}&x={x}&y={y}", {
        minZoom: 0,
        maxZoom: 7,
        continuousWorld: true
    }).addTo(map);

    map.on("click", onMapClick);

    $.getJSON("/api/map_floors?continent=1&floor=1", function (data) {
        var region, gameMap, i, il, poi;

        for (region in data.regions) {
            region = data.regions[region];

            for (gameMap in region.maps) {
                gameMap = region.maps[gameMap];

                for (i = 0, il = gameMap.points_of_interest.length; i < il; i++) {
                    poi = gameMap.points_of_interest[i];

                    if (poi.type != "waypoint") {
                        continue;
                    }

                    L.marker(unproject(poi.coord), {
                        title: poi.name
                    }).addTo(map);
                }
            }
        }
    });
});