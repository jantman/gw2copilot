/*
gw2copilot/js/gw2timer_data.js

#####
We're using resource data from gw2timer.com; see
https://github.com/jantman/gw2copilot/issues/4 and
https://github.com/jantman/gw2copilot/issues/19 and
gw2copilot.caching_api_client.CachingAPIClient._get_gw2timer_data()

That data is a JavaScript source file. This serves to manipulate the data
for our purposes.
#####

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

/**
 * Add markers for travel points from travel.js
 */
function gw2timer_add_travel() {
    console.log("adding gw2timer travel layer");
    m.travelLayer = L.layerGroup();

    // interborders - zone portals
    for(var i =0; i < GW2T_TRAVEL_PATHS["interborders"].length; i++) {
        data = GW2T_TRAVEL_PATHS["interborders"][i];
        markerA = L.marker(
            gw2latlon(data["end_a"]["coord"]),
            {
                title: data["end_a"]["title"],
                alt: data["end_a"]["title"],
                riseOnHover: true,
                icon: ICONS[data["end_a"]["icon"]],
                opacity: 0.75
            }
        );
        markerB = L.marker(
            gw2latlon(data["end_b"]["coord"]),
            {
                title: data["end_b"]["title"],
                alt: data["end_b"]["title"],
                riseOnHover: true,
                icon: ICONS[data["end_b"]["icon"]],
                opacity: 0.75
            }
        );
        markerA.on('mouseover', function(e) { console.log("markerA mouseover"); this.otherMarker.setOpacity(1.0); }, { otherMarker: markerB } );
        markerA.on('mouseout', function(e) { console.log("markerA mouseout"); this.otherMarker.setOpacity(0.75); }, { otherMarker: markerB } );
        m.travelLayer.addLayer(markerA);
        m.travelLayer.addLayer(markerB);
    }

    // FINALLY, in map.js, hide/show layer (and add a button for it in live-sidebar.html)
    // @TODO: DEBUG
    map.addLayer(m.travelLayer);
    // @TODO: END DEBUG
}

/**
 * Add markers for resource locations from gw2timer resource.js
 */
function gw2timer_add_resource_markers() {
    console.log("adding gw2timer resource layers");
    //ResourceLayers: ["Metal", "RichMetal", "Plant", "RichPlant", "Wood", "RichWood"]
    for(var i =0; i < m.ResourceLayers.length; i++) {
        m.resourceGroups[m.ResourceLayers[i]] = L.layerGroup();
        m.hidden[m.ResourceLayers[i]] = true;
    }

    for (res_name in GW2T_RESOURCE_DATA) {
        if (GW2T_RESOURCE_DATA.hasOwnProperty(res_name)) {
            resource = GW2T_RESOURCE_DATA[res_name];
            name = resource.name_en;
            res_type = resource.type;
            // formulate most of the tooltip title, except Rich/Perm. prefix
            if ( res_type == 'Wood' ) {
                // 'Green Wood' sounds right...
                title = name + " " + res_type + " node (" + resource.item + ")";
            } else {
                // 'Mithril Metal' doesn't...
                title = name + " node (" + resource.item + ")";
            }
            // ok, add all of the nodes
            if (resource.hasOwnProperty("Rich") && resource["Rich"].length > 0) {
                gw2timer_add_markers_for_resource("Rich" + res_type, resource["Rich"], ("Rich " + title), ICONS[res_type]);
            }
            if (resource.hasOwnProperty("Permanent") && resource["Permanent"].length > 0) {
                gw2timer_add_markers_for_resource("Rich" + res_type, resource["Permanent"], ("Permanent " + title), ICONS[res_type]);
            }
            if (resource.hasOwnProperty("Hotspot") && resource["Hotspot"].length > 0) {
                gw2timer_add_markers_for_resource(res_type, resource["Hotspot"], ("probable " + title), ICONS[res_type]);
            }
            if (resource.hasOwnProperty("Regular") && resource["Regular"].length > 0) {
                gw2timer_add_markers_for_resource(res_type, resource["Regular"], ("possible " + title), ICONS[res_type]);
            }
        }
    }
}

/**
 * Add the markers for a single type of resource, and a single
 * rarity/availability (i.e. Regulat/Hotspot/Rich/Permanent).
 *
 * This should only be called from gw2timer_add_resource_markers()
 *
 * @param {String} group_name - layerGroup name in ``m.resourceGroups`` to add
 *   the marker to; this is usually /(Rich|)(Metal|Wood|Plant)/
 * @param {Array} res_list - the list of resource dicts from gw2timer_data.js
 *   for this type of resource.
 * @param {String} title - the title and alt text of the popup for this marker
 * @param {Icon} icon - the Icon to use for this marker
 */
function gw2timer_add_markers_for_resource(group_name, res_list, title, icon) {
    for(idx in res_list) {
        if (res_list[idx].hasOwnProperty("c")) {
            m.resourceGroups[group_name].addLayer(
                L.marker(
                    gw2latlon(res_list[idx]["c"]),
                    {
                        title: title,
                        alt: title,
                        riseOnHover: true,
                        icon: icon
                    }
                )
            );
        }
    }
}