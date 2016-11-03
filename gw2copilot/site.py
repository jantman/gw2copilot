#!/usr/bin/env python
"""
gw2copilot/site.py

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

import sys
import logging
import json
from .version import VERSION
from klein import Klein
from twisted.web._responses import OK
from jinja2 import Environment, PackageLoader

logger = logging.getLogger()

app = Klein()


class GW2CopilotSite(object):
    """
    Wrapper around ``klein.app.Klein`` to handle the site.
    """

    def __init__(self, parent_server):
        """
        Initialize the Site.
        :param parent_server: parent TwisterServer instance
        :type parent_server: :py:class:`~.TwistedServer` instance
        """
        self.parent_server = parent_server
        self.app = app
        self._tmpl_env = Environment(
            loader=PackageLoader('gw2copilot', 'templates'),
            extensions=['jinja2.ext.loopcontrols']
        )
        # setup routes, since this is ugly with a class
        self.app.route('/mumble_status')(self.mumble_status)
        self.app.route('/')(self.homepage)

    def site_resource(self):
        """
        Return the Klein app's ``resource``, for Twisted to use as its endpoint.

        This replaces Klein's ``app.run()``.

        :return: Klein app root resource
        :rtype: twisted.web.resource
        """
        return self.app.resource()

    def _make_response(self, s):
        """
        If running under python 3+, utf-8 encode the response.

        :param s: response string
        :type s: str
        :return: response string, possibly encoded
        :rtype: str
        """
        if sys.version_info[0] < 3:
            return s
        return s.encode('utf-8')  # nocoverage - unreachable under py2

    def _set_headers(self, request):
        """
        Set headers that all responses should have.

        :param request: incoming HTTP request
        :type request: :py:class:`twisted.web.server.Request`
        """
        # find the original Twisted server header
        twisted_server = request.responseHeaders.getRawHeaders(
            'server', 'Twisted'
        )[0]
        request.setHeader('server',
                          'gw2copilot/%s/%s' % (VERSION, twisted_server))

    def _render_template(self, tmpl_name, **kwargs):
        """
        Render a Jinja2 template of the given name (passed as argument to
        :py:meth:`Jinja2.Environment.get_template`) with the specified kwargs
        (passed as kwargs to :py:method:`jinja2.Template.render`).

        :param tmpl_name: name of the template to render
        :type tmpl_name: str
        :param kwargs: kwargs to pass to Jinja2 template render method
        :type kwargs: dict
        :return: rendered template string
        :rtype: str
        """
        tmpl = self._tmpl_env.get_template(tmpl_name)
        rendered = tmpl.render(**kwargs)
        return rendered

    # app.route('/mumble_status')
    def mumble_status(self, request):
        """
        Return the full MumbleLink data.

        This serves :http:get:`/mumble_status` endpoint.

        :param request: incoming HTTP request
        :type request: :py:class:`twisted.web.server.Request`
        :return: JSON response data string
        :rtype: str


        <HTTPAPI>
        Return the current MumbleLink data as JSON.

        Served by :py:meth:`.mumble_status`.

        **Example request**:

        .. sourcecode:: http

          GET /mumble_status HTTP/1.1
          Host: example.com

        **Example Response**:

        .. sourcecode:: http

          HTTP/1.1 200 OK
          Content-Type: application/json

          {"something": "goes here"}

        :>json facing_direction: *(float)* direction the character is facing
        :>json elevation: *(float)* character's elevation in inches
        :>json map_id: *(int)* current map ID
        :>json name: *(string)* character name
        :>json profession_id: *(int)* character profession ID
        :>json profession_name: *(string)* character profession name
        :>json race_id: *(int)* character race ID
        :>json race_name: *(string)* character race name
        :>json continent_id: *(int)* current continent ID
        :>json continent_name: *(string)* current continent name
        :>json region_id: *(int)* current region ID
        :>json region_name: *(string)* current region name
        :>json map_name: *(string)* current map name
        :>json map_level_range: *(string)* current map level range
        :>json position: *(2-tuple of floats)* current position in inches
        :statuscode 200: successfully returned result
        """
        self._set_headers(request)
        statuscode = OK
        msg = self._make_response('OK')
        request.setResponseCode(statuscode, message=msg)
        request.setHeader("Content-Type", 'application/json')
        logger.info('RESPOND %d for %s%s request for %s from %s:%s',
                    statuscode, ('QUEUED ' if request.queued else ''),
                    str(request.method), request.uri,
                    request.client.host, request.client.port)
        return self._make_response(
            json.dumps(self.parent_server.playerinfo.as_dict)
        )

    # app.route('/')
    def homepage(self, request):
        """
        Generate the end-user landing ("Home") page.

        This serves :http:get:`/` endpoint.

        :param request: incoming HTTP request
        :type request: :py:class:`twisted.web.server.Request`
        :return: HTML output
        :rtype: str


        <HTTPAPI>
        Return the HTML for the / end-user "home" page.

        Served by :py:meth:`.homepage`.

        **Example request**:

        .. sourcecode:: http

          GET / HTTP/1.1
          Host: example.com

        **Example Response**:

        .. sourcecode:: http

          HTTP/1.1 200 OK
          Content-Type: text/html

          HTML OUTPUT HERE.

        """
        self._set_headers(request)
        statuscode = OK
        msg = self._make_response('OK')
        request.setResponseCode(statuscode, message=msg)
        logger.info('RESPOND %d for %s%s request for %s from %s:%s',
                    statuscode, ('QUEUED ' if request.queued else ''),
                    str(request.method), request.uri,
                    request.client.host, request.client.port)
        return self._make_response(
            self._render_template(
                'index.html'
            )
        )
