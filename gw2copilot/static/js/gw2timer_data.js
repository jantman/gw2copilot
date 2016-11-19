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
    //ResourceLayers: ["Metal", "RichMetal", "PermanentMetal", "Plant", "RichPlant", "PermanentPlant", "Wood", "RichWood", "PermanentWood"]
    for(var i =0; i < m.ResourceLayers.length; i++) {
        m.resourceGroups[m.ResourceLayers[i]] = L.layerGroup()
    }

    for (res_name in GW2T_RESOURCE_DATA) {
        if (GW2T_RESOURCE_DATA.hasOwnProperty(res_name)) {
            resource = GW2T_RESOURCE_DATA[res_name];
            name = resource.name_en;
            res_type = resource.type;
            if (resource.hasOwnProperty("Rich") && resource["Rich"].length > 0) {
                title = "Rich " + name + " node (" + resource.item + ")";
                gw2timer_add_markers_for_resource("Rich" + res_type, resource["Rich"], title, ICONS[res_type]);
            }
            if (resource.hasOwnProperty("Permanent") && resource["Permanent"].length > 0) {
                title = "Permanent " + name + " node (" + resource.item + ")";
                gw2timer_add_markers_for_resource("Permanent" + res_type, resource["Permanent"], title, ICONS[res_type]);
            }
            if (resource.hasOwnProperty("Hotspot") && resource["Hotspot"].length > 0) {
                title = name + " node (" + resource.item + ")";
                gw2timer_add_markers_for_resource(res_type, resource["Hotspot"], title, ICONS[res_type]);
            }
            if (resource.hasOwnProperty("Regular") && resource["Regular"].length > 0) {
                title = name + " node (" + resource.item + ")";
                gw2timer_add_markers_for_resource(res_type, resource["Regular"], title, ICONS[res_type]);
            }
        }
    }

    console.log("DEBUG ONLY"); // while testing, always show them
    for(var i =0; i < m.ResourceLayers.length; i++) {
        map.addLayer(m.resourceGroups[m.ResourceLayers[i]]);
    }
}

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