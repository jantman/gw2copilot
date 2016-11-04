"""
gw2copilot/api.py

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
import json
from twisted.web._responses import OK
from jinja2 import Environment, PackageLoader

from .utils import _make_response, _set_headers

logger = logging.getLogger()


class GW2CopilotAPI(object):
    """
    Class to add the API routes to our Klein site.
    """

    def __init__(self, site, parent_server):
        """
        Initialize the API. This must only be called from
        :py:meth:`~.GW2CopilotSite.__init__`

        :param site: the parent Site class
        :type site: :py:class:`~.GW2CopilotSite`
        :param parent_server: parent TwisterServer instance
        :type parent_server: :py:class:`~.TwistedServer` instance
        """
        self.parent_server = parent_server
        self.site = site
        # setup routes, since this is ugly with a class
        self.site.app.route('/api/mumble_status')(self.mumble_status)

    def _render_template(self, tmpl_name, **kwargs):
        """
        Simply pass the arguments to ``self.site`` instance's
        :py:meth:`~.GW2CopilotSite._render_template` and return the result.

        :param tmpl_name: name of the template to render
        :type tmpl_name: str
        :param kwargs: kwargs to pass to Jinja2 template render method
        :type kwargs: dict
        :return: rendered template string
        :rtype: str
        """
        return self.site._render_template(tmpl_name, **kwargs)

    # app.route('/api/mumble_status')
    def mumble_status(self, request):
        """
        Return the full MumbleLink data.

        This serves :http:get:`/api/mumble_status` endpoint.

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
        _set_headers(request)
        statuscode = OK
        msg = _make_response('OK')
        request.setResponseCode(statuscode, message=msg)
        request.setHeader("Content-Type", 'application/json')
        logger.info('RESPOND %d for %s%s request for %s from %s:%s',
                    statuscode, ('QUEUED ' if request.queued else ''),
                    str(request.method), request.uri,
                    request.client.host, request.client.port)
        return _make_response(
            json.dumps(self.parent_server.playerinfo.as_dict)
        )
