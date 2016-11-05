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
          console.log("Got echo: " + e.data);
       }
    }
};
