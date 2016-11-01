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

    def __init__(self, poll_interval=5.0, bind_port=8080):
        """
        Initialize the server.

        :param poll_interval: interval in seconds to poll MumbleLink
        :type poll_interval: float
        :param bind_port: port number to bind to / listen on
        :type bind_port: int
        """
        self.poll_interval = poll_interval
        self.bind_port = bind_port
        self.reactor = reactor
        # saved state:
        self.mumble_link_data = {'foo': 'bar'}
        self.wine_protocol = None
        self.wine_process = None

    def get_active_node(self):
        """
        GET the Consul URL for the 'vault' service health check, parse the JSON
        reply, and return either the active node in (name|ip):port form, or
        None if no active node can be found.

        :return: active node in ``(name|ip):port`` form (str) or None
        """

        """
        url = 'http://%s/v1/health/service/vault' % self.consul_host_port
        # parse the health check results and find the one that's passing
        if self.log_enabled:
            logger.debug('Polling active node from: %s', url)
        r = requests.get(url)
        # return the current leader address
        for node in r.json():
            if 'active' not in node['Service']['Tags']:
                continue
            port = node['Service']['Port']
            n = "%s:%d" % (node['Node']['Node'], port)
            if self.redir_ip:
                n = "%s:%d" % (node['Node']['Address'], port)
            if self.log_enabled:
                logger.info("Got active node as: %s", n)
            return n
        if self.log_enabled:
            logger.critical('NO vault services found with health check passing')
        return None
        """
        pass

    def update_active_node(self):
        """
        Run :py:meth:`~.get_active_node` and update ``self.active_node_ip_port``
        to its value. If it raised an Exception, log the exception and set
        ``self.active_node_ip_port`` to None.
        """

        """
        try:
            newnode = self.get_active_node()
            self.last_poll_time = datetime.now().isoformat()
        except Exception:
            logger.exception('Exception encountered when polling active node')
            # we have a choice here whether to keep serving the old active
            # node, or start serving 503s. Might as well serve the old one, in
            # case the error is with Consul or intermittent. If the node is
            # really down, the client will end up with an error anyway...
            newnode = None
        if self.log_enabled and newnode != self.active_node_ip_port:
            logger.warning("Active vault node changed from %s to %s",
                           self.active_node_ip_port, newnode)
        self.active_node_ip_port = newnode
        """
        pass

    def run_reactor(self):
        """Method to run the Twisted reactor; mock point for testing"""
        self.reactor.run()

    def listentcp(self, site):
        """
        Setup TCP listener for the Site; helper method for testing

        :param site: Site to serve
        :type site: :py:class:`~.VaultRedirectorSite`
        """
        logger.warning('Setting TCP listener on port %d for HTTP requests',
                       self.bind_port)
        self.reactor.listenTCP(self.bind_port, site)

    def add_update_loop(self):
        """
        Setup the LoopingCall to poll Consul every ``self.poll_interval``;
        helper for testing.
        """
        l = LoopingCall(self.wine_protocol.ask_for_output)
        l.clock = self.reactor
        logger.warning('Setting poll interval to %s seconds',
                       self.poll_interval)
        l.start(self.poll_interval)

    def add_mumble_reader(self):
        if platform.system() != 'Linux':
            raise NotImplementedError("ERROR: non-Linux support not "
                                      "impmemented.")
        logger.debug("Creating WineProcessProtocol")
        self.wine_protocol = WineProcessProtocol(self)
        logger.debug(dir(self.wine_protocol))
        logger.debug("Creating spawned process")
        self.wine_process = self.reactor.spawnProcess(
            self.wine_protocol,
            '/home/jantman/GIT/gw2_helper_python/bin/python',
            [
                '/home/jantman/GIT/gw2_helper_python/bin/python',
                '/home/jantman/GIT/gw2_helper_python/gw2_helper_python/output_test.py'
            ],
            {}
        )

    def run(self):
        """setup the site, start listening on port, setup the looping call to
        :py:meth:`~.update_active_node` every ``self.poll_interval`` seconds,
        and start the Twisted reactor"""
        logger.error("TODO: implement initial checks")
        site = Site(GW2HelperSite(self))
        # setup our HTTP(S) listener
        self.listentcp(site)
        # setup the update_active_node poll every POLL_INTERVAL seconds
        self.add_mumble_reader()
        self.add_update_loop()
        logger.warning('Starting Twisted reactor (event loop)')
        self.run_reactor()
