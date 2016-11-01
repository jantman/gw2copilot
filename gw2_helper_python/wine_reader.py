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
    """
    An implementation of :py:class:`twisted.internet.protocol.ProcessProtocol`
    to communicate with :py:mod:`~.read_mumble_link` when it is executed
    as a command-line script under wine. This handles reading data from the
    process and requesting more.
    """

    def __init__(self, parent_server):
        """
        Initialize; save an instance variable pointing to our
        :py:class:`~.TwistedServer`

        :param parent_server: the TwistedServer instance that started this
        :type parent_server: :py:class:`~.TwistedServer`
        """
        logger.debug("Initializing")
        self.parent_server = parent_server

    def connectionMade(self):
        """Triggered when the process starts; just logs a debug message"""
        logger.debug("Connection made")

    def ask_for_output(self):
        """
        Write a newline to the process' STDIN, prompting it to re-read the map
        and write the results to STDOUT, which will be received by
        :py:meth:`~.outReceived`.
        """
        logger.debug("asking for output")
        self.transport.write("\n")

    def outReceived(self, data):
        """
        Called when output is received from the process; attempts to deserialize
        JSON and on success passes it back to
        ``self.parent_server.update_mumble_data``
        (:py:meth:`~.TwistedServer.update_mumble_data`).

        :param data: JSON data read from MumbleLink
        :type data: str
        """
        logger.debug("Data received: %s", data)
        try:
            d = json.loads(data.strip())
            self.parent_server.update_mumble_data(d)
        except Exception:
            logger.exception("Could not deserialize data")

    def processExited(self, status):
        """called when the process exits; just logs a debug message"""
        logger.debug("Process exited %s", status)

    def processEnded(self, status):
        """called when the process ends and is cleaned up;
        just logs a debug message"""
        logger.debug("Process exited %s", status)

    def inConnectionLost(self):
        """called when STDIN connection is lost; just logs a debug message"""
        logger.debug("STDIN connection lost")

    def outConnectionLost(self):
        """called when STDOUT connection is lost; just logs a debug message"""
        logger.debug("STDOUT connection lost")

    def errConnectionLost(self):
        """called when STDERR connection is lost; just logs a debug message"""
        logger.debug("STDERR connection lost")
