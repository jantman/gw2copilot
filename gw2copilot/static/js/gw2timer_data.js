/**
 * We're using resource data from gw2timer.com; see
 * https://github.com/jantman/gw2copilot/issues/4 and
 * https://github.com/jantman/gw2copilot/issues/19 and
 * gw2copilot.caching_api_client.CachingAPIClient._get_gw2timer_data()
 *
 * That data is a JavaScript source file. This serves to manipulate the data
 * for our purposes.
 */

/**
 * Add markers for resource locations from gw2timer resource.js
 */
function gw2timer_add_resource_markers() {
    console.log("adding gw2timer resource layers");
    //ResourceLayers: ["Metal", "RichMetal", "Plant", "RichPlant", "Wood", "RichWood"]
    for(var i =0; i < m.ResourceLayers.length; i++) {
        m.resourceGroups[m.ResourceLayers[i]] = L.layerGroup()
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
                gw2timer_add_markers_for_resource(res_type, resource["Hotspot"], title, ICONS[res_type]);
            }
            if (resource.hasOwnProperty("Regular") && resource["Regular"].length > 0) {
                gw2timer_add_markers_for_resource(res_type, resource["Regular"], title, ICONS[res_type]);
            }
        }
    }

    console.log("DEBUG ONLY"); // while testing, always show them
    for(var i =0; i < m.ResourceLayers.length; i++) {
        map.addLayer(m.resourceGroups[m.ResourceLayers[i]]);
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