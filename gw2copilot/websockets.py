"""
gw2copilot/websockets.py

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
"""

import logging
from autobahn.twisted.websocket import (
    WebSocketServerFactory, WebSocketServerProtocol
)

logger = logging.getLogger(__name__)


class BroadcastServerProtocol(WebSocketServerProtocol):
    """
    WebSocket Server Protocol for tracking connected clients and broadcasting
    messages to them.
    """

    def onOpen(self):
        self.factory.register(self)

    def onMessage(self, payload, isBinary):
        if not isBinary:
            msg = "{} from {}".format(payload.decode('utf8'), self.peer)
            self.factory.broadcast(msg)

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)


class BroadcastServerFactory(WebSocketServerFactory):

    """
    Simple broadcast server broadcasting any message it receives to all
    currently connected clients.
    """

    def __init__(self, url, reactor, enable_tick=True):
        WebSocketServerFactory.__init__(self, url)
        self.clients = []
        self.tickcount = 0
        self.reactor = reactor
        if enable_tick:
            self.tick()

    def tick(self):
        self.tickcount += 1
        self.broadcast(
            '{"type": "tick", "message": "tick %d from server"}' % \
            self.tickcount
        )
        self.reactor.callLater(1, self.tick)

    def register(self, client):
        if client not in self.clients:
            logger.info("registered client {}".format(client.peer))
            self.clients.append(client)

    def unregister(self, client):
        if client in self.clients:
            logger.info("unregistered client {}".format(client.peer))
            self.clients.remove(client)

    def broadcast(self, msg):
        logger.info("broadcasting prepared message '{}' ..".format(msg))
        prepared_msg = self.prepareMessage(msg)
        for c in self.clients:
            c.sendPreparedMessage(prepared_msg)
            logger.debug("prepared message sent to {}".format(c.peer))
