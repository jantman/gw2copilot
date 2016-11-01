"""
gw2_helper_python/wine_reader.py

The latest version of this package is available at:
<https://github.com/jantman/gw2_helper_python>

################################################################################
Copyright 2016 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

    This file is part of gw2_helper_python.

    gw2_helper_python is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    gw2_helper_python is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with gw2_helper_python.  If not, see <http://www.gnu.org/licenses/>.

The Copyright and Authors attributions contained herein may not be removed or
otherwise altered, except to add the Author attribution of a contributor to
this work. (Additional Terms pursuant to Section 7b of the AGPL v3)
################################################################################
While not legally required, I sincerely request that anyone who finds
bugs please submit them at <https://github.com/jantman/gw2_helper_python> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me via email.
################################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
################################################################################
"""

import logging
import json
from twisted.internet import protocol

logger = logging.getLogger()


class WineProcessProtocol(protocol.ProcessProtocol):

    def __init__(self, parent_server):
        logger.debug("Initializing")
        self.parent_server = parent_server

    def connectionMade(self):
        logger.debug("Connection made")

    def ask_for_output(self):
        logger.debug("asking for output")
        self.transport.write("\n")

    def outReceived(self, data):
        logger.debug("Data received: %s", data)
        try:
            d = json.loads(data.strip())
            self.parent_server.mumble_link_data = d
        except:
            logger.exception("Could not deserialize data")

    def errReceived(self, data):
        """just discard STDERR"""
        pass

    def processExited(self, status):
        logger.debug("Process exited %s", status)

    def processEnded(self, status):
        logger.debug("Process exited %s", status)

    def inConnectionLost(self):
        logger.debug("STDIN connection lost")

    def outConnectionLost(self):
        logger.debug("STDOUT connection lost")

    def errConnectionLost(self):
        logger.debug("STDERR connection lost")