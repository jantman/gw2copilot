#!/usr/bin/env python
"""
gw2_helper_python/server.py

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

import sys
import logging
import signal
import json
import platform
from os import getpid, access, R_OK
from datetime import datetime
from twisted.web import resource
from twisted.web.server import Site
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.web._responses import NOT_FOUND, SERVICE_UNAVAILABLE, OK

from .version import VERSION, PROJECT_URL
from .site import GW2HelperSite
from .wine_reader import WineProcessProtocol

logger = logging.getLogger()


class TwistedServer(object):
    """
    TwistedServer is the heart of the application, which handles all IO and
    bridges the MumbleLink to the web frontend and other logic.
    """

    def __init__(self, poll_interval=5.0, bind_port=8080):
        """
        Initialize the Twisted Server, the heart of the application...

        :param poll_interval: interval in seconds to poll MumbleLink
        :type poll_interval: float
        :param bind_port: port number to bind to / listen on
        :type bind_port: int
        """
        self.poll_interval = poll_interval
        self.bind_port = bind_port
        self.reactor = reactor
        # @TODO perform the initial cache gets
        # saved state:
        self._mumble_link_data = {'foo': 'bar'}
        self._wine_protocol = None
        self._wine_process = None

    def run_reactor(self):
        """Method to run the Twisted reactor; mock point for testing"""
        self.reactor.run()

    def listentcp(self, site):
        """
        Setup TCP listener for the Site; helper method for testing

        :param site: Site to serve
        :type site: :py:class:`~.GW2HelperSite`
        """
        logger.warning('Setting TCP listener on port %d for HTTP requests',
                       self.bind_port)
        self.reactor.listenTCP(self.bind_port, site)

    def add_update_loop(self):
        """
        Setup the LoopingCall to poll MumbleLink every ``self.poll_interval``;
        helper for testing.
        """
        l = LoopingCall(self.wine_protocol.ask_for_output)
        l.clock = self.reactor
        logger.warning('Setting poll interval to %s seconds',
                       self.poll_interval)
        l.start(self.poll_interval)

    def add_mumble_reader(self):
        # @TODO fix this; 2 classes one for Native and one for Wine;
        # have them do everything in here.
        if platform.system() != 'Linux':
            raise NotImplementedError("ERROR: non-Linux support not "
                                      "impmemented.")
        logger.debug("Creating WineProcessProtocol")
        self._wine_protocol = WineProcessProtocol(self)
        logger.debug(dir(self.wine_protocol))
        logger.debug("Creating spawned process")
        self._wine_process = self.reactor.spawnProcess(
            self._wine_protocol,
            '/home/jantman/GIT/gw2_helper_python/bin/python',
            [
                '/home/jantman/GIT/gw2_helper_python/bin/python',
                '/home/jantman/GIT/gw2_helper_python/gw2_helper_python/output_test.py'
            ],
            {}  # @TODO need to use the wine process' environment
        )
        # update on a regular basis
        self.add_update_loop()

    def run(self):
        """setup the web Site, start listening on port, setup the MumbleLink
        reader, and start the Twisted reactor"""
        # setup the web Site and HTTP listener
        site = Site(GW2HelperSite(self))
        self.listentcp(site)
        # setup the MumbleLink reader
        self.add_mumble_reader()
        # run the main reactor event loop
        logger.warning('Starting Twisted reactor (event loop)')
        self.run_reactor()
