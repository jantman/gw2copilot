#!/usr/bin/env python
"""
gw2_helper_python/site.py

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
from os import getpid, access, R_OK
from datetime import datetime
from twisted.web import resource
from twisted.web.server import Site
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.web._responses import NOT_FOUND, SERVICE_UNAVAILABLE, OK
from .version import VERSION, PROJECT_URL

logger = logging.getLogger()


class GW2HelperSite(object):
    """
    Unfortunately :py:class:`twisted.web.resource.Resource` is an old-style
    class, so we can't easily subclass it and override its ``__init__``. So,
    we implement the :py:class:`twisted.web.resource.IResource` interface
    ourselves.
    """

    isLeaf = True

    def __init__(self, parent_server):
        """

        :param parent_server: parent TwisterServer instance
        :type parent_server: :py:class:`~.TwistedServer` instance
        """
        self.parent_server = parent_server

    def status_response(self):
        s = json.dumps({
            'healthy': True,
            'application': 'vault-redirector',
            'source': _PROJECT_URL,
            'version': _VERSION,
            'consul_host_port': self.redirector.consul_host_port,
            'active_vault': self.redirector.active_node_ip_port,
            'last_consul_poll': self.redirector.last_poll_time
        })
        return s

    def getChildWithDefault(self, name, request):
        """
        This should never be called; it's simply required to implement the
        :py:class:`twisted.web.resource.IResource` interface. Just returns
        a 404.

        See: :py:meth:`twisted.web.resource.IResource.getChildWithDefault`
        """
        return resource.ErrorPage(NOT_FOUND, "No Such Resource",
                                  "No Such Resource")

    def make_response(self, s):
        """python 3+ needs a binary response; create one"""
        if sys.version_info[0] < 3:
            return s
        return s.encode('utf-8')  # nocoverage - unreachable under py2

    def mumble_status(self, request):
        """
        Return the full MumbleLink data.

        :param request: incoming HTTP request
        :type request: :py:class:`twisted.web.server.Request`
        :return: JSON response data string
        :rtype: str
        """
        statuscode = OK
        msg = self.make_response('OK')
        request.setResponseCode(statuscode, message=msg)
        request.setHeader("Content-Type", 'application/json')
        queued = ''
        if request.queued:
            queued = 'QUEUED '
        logger.info('RESPOND %d for %s%s request for '
                    '/vault-redirector-health from %s:%s',
                    statuscode, queued, str(request.method),
                    request.client.host, request.client.port)
        return self.make_response(
            json.dumps(self.parent_server.mumble_link_data)
        )

    def render(self, request):
        """
        Render the response to the given request. This simply gets the current
        active vault node from ``self.redirector`` (our instance of
        :py:class:`~.VaultRedirector`) and returns a 307 Temporary Redirect
        to the same path as the request, on that active node.

        The ``request`` param is an instance of
        :py:class:`twisted.web.server.Request`, which implements
        :py:class:`twisted.web.iweb.IRequest` and inherits from
        :py:class:`twisted.web.http.Request`

        The return value is meaningless. We simply set a response code and
        headers on the ``request`` parameter.

        If we were unable to retrieve the current active Vault node from the
        Consul API, return a 503 error response. This is the same code that
        Vault uses when it is down for maintenance or sealed.

        :param request: incoming HTTP request
        :type request: :py:class:`twisted.web.server.Request`
        :return: empty string (None)
        :rtype: str
        """
        path = request.uri
        # python3 will get a byte string here
        if not isinstance(path, str):  # nocoverage - py3 only
            path = path.decode('utf-8')
        # find the original Twisted server header
        twisted_server = request.responseHeaders.getRawHeaders(
            'server', 'Twisted'
        )[0]
        request.setHeader('server',
                          'gw2_helper_python/%s/%s' % (VERSION, twisted_server))
        # handle health check request
        if path == '/mumble_status':
            return self.mumble_status(request)
        queued = ''
        if request.queued:
            queued = 'QUEUED '
        logger.info('RESPOND 404 for %s%s request for %s from %s:%s',
                    queued, str(request.method), path,
                    request.client.host, request.client.port)
        return resource.ErrorPage(NOT_FOUND, "No Such Resource",
                                  "No Such Resource")
