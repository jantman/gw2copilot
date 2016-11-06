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

from .utils import make_response, set_headers, log_request
from .route_helpers import classroute, ClassRouteMixin

logger = logging.getLogger(__name__)


class GW2CopilotAPI(ClassRouteMixin):
    """
    Class to add the API routes to our Klein site.
    """

    #: route prefix to prepend to all @classroutes
    _route_prefix = '/api'

    def __init__(self, app, parent_server):
        """
        Initialize the API. This must only be called from
        :py:meth:`~.TwistedSite._setup_klein`.

        :param app: the parent Site class
        :type app: :py:class:`~.GW2CopilotSite`
        :param parent_server: parent TwisterServer instance
        :type parent_server: :py:class:`~.TwistedServer` instance
        """
        logger.debug('Initializing API')
        self.parent_server = parent_server
        self.app = app
        self._add_routes()

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

    @classroute('player_info')
    def player_info(self, request):
        """
        Return the full PlayerInfo data. This returns the exact return value
        of :py:attr:`~.PlayerInfo.as_dict`.

        This serves :http:get:`/api/player_info` endpoint.

        :param request: incoming HTTP request
        :type request: :py:class:`twisted.web.server.Request`
        :return: JSON response data string
        :rtype: str


        <HTTPAPI>
        Return the current MumbleLink data as JSON. This returns the exact
        return value of :py:attr:`~.PlayerInfo.as_dict`.

        Served by :py:meth:`.player_info`.

        **Example request**:

        .. sourcecode:: http

          GET /player_info HTTP/1.1
          Host: example.com

        **Example Response**:

        .. sourcecode:: http

          HTTP/1.1 200 OK
          Content-Type: application/json

          {
              "facing_direction": 82.0783777035753,
              "profession_id": 4,
              "elevation": 822.0824978822708,
              "region_id": 4,
              "race_name": "Human",
              "map_name": "Lion's Arch",
              "map_id": 50,
              "region_name": "Kryta",
              "profession_name": "Ranger",
              "map_level_range": "0-80",
              "name": "Jantman",
              "level": 80,
              "continent_id": 1,
              "race_id": 3,
              "continent_name": "Tyria",
              "position": [16097.394906375821, 14788.844535192553]
          }

        :>json facing_direction: *(float)* direction the character is facing
        :>json elevation: *(float)* character's elevation in inches
        :>json map_id: *(int)* current map ID
        :>json name: *(string)* character name
        :>json level: *(int)* character level
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
        log_request(request)
        set_headers(request)
        statuscode = OK
        msg = make_response('OK')
        request.setResponseCode(statuscode, message=msg)
        request.setHeader("Content-Type", 'application/json')
        return make_response(
            json.dumps(self.parent_server.playerinfo.as_dict)
        )

    @classroute('position')
    def position(self, request):
        """
        Return the player's current position. This returns the exact return
        value of :py:attr:`~.PlayerInfo.position`.

        This serves :http:get:`/api/position` endpoint.

        :param request: incoming HTTP request
        :type request: :py:class:`twisted.web.server.Request`
        :return: JSON response data string
        :rtype: str

        <HTTPAPI>
        Return the player's current position as JSON.

        Served by :py:meth:`.position`.

        **Example request**:

        .. sourcecode:: http

          GET /position HTTP/1.1
          Host: example.com

        **Example Response**:

        .. sourcecode:: http

          HTTP/1.1 200 OK
          Content-Type: application/json

          [1.234, 5.678]

        :>jsonarr x: *(float)* player's X coordinate
        :>jsonarr y: *(float)* player's Y coordinate
        :statuscode 200: successfully returned result
        """
        log_request(request)
        set_headers(request)
        statuscode = OK
        msg = make_response('OK')
        request.setResponseCode(statuscode, message=msg)
        request.setHeader("Content-Type", 'application/json')
        return make_response(
            json.dumps(self.parent_server.playerinfo.position)
        )

    @classroute('player_dict')
    def player_dict(self, request):
        """
        Return a dict of information about the player/character; This returns
        the exact return value of :py:attr:`~.PlayerInfo.player_dict`.

        This serves :http:get:`/api/player_dict` endpoint.

        :param request: incoming HTTP request
        :type request: :py:class:`twisted.web.server.Request`
        :return: JSON response data string
        :rtype: str

        <HTTPAPI>
        Return a dict of information about the player/character as JSON.

        Served by :py:meth:`.player_dict`.

        **Example request**:

        .. sourcecode:: http

          GET /player_dict HTTP/1.1
          Host: example.com

        **Example Response**:

        .. sourcecode:: http

          HTTP/1.1 200 OK
          Content-Type: application/json

          {
              "name": "Character Name",
              "profession": "Profession",
              "race": "Race",
              "level": 80,
          }

        :>json name: *(string)* character name
        :>json profession: *(string)* character's profession
        :>json race: *(string)* character's race
        :>json level: *(int)* character's level
        :statuscode 200: successfully returned result
        """
        log_request(request)
        set_headers(request)
        statuscode = OK
        msg = make_response('OK')
        request.setResponseCode(statuscode, message=msg)
        request.setHeader("Content-Type", 'application/json')
        return make_response(
            json.dumps(self.parent_server.playerinfo.player_dict)
        )

    @classroute('map_info')
    def map_info(self, request):
        """
        Return a dict of information about the player's current map and
        location; This returns the exact return value of
        :py:attr:`~.PlayerInfo.map_info`.

        This serves :http:get:`/api/map_info` endpoint.

        :param request: incoming HTTP request
        :type request: :py:class:`twisted.web.server.Request`
        :return: JSON response data string
        :rtype: str

        <HTTPAPI>
        Return a dict of information about the player's current map as JSON.

        Served by :py:meth:`.map_info`.

        **Example request**:

        .. sourcecode:: http

          GET /map_info HTTP/1.1
          Host: example.com

        **Example Response**:

        .. sourcecode:: http

          HTTP/1.1 200 OK
          Content-Type: application/json

          {
              "map_name": "Lion's Arch",
              "map_id": 50,
              "map_level_range": "0-80",
              "continent_name": "Tyria",
              "continent_id": 1,
              "region_name": "Kryta",
              "region_id": 4
          }

        :>json map_name: *(string)* current map name
        :>json map_id: *(int)* current map ID
        :>json map_level_range: *(string)* current map level range
        :>json continent_name: *(string)* current continent name
        :>json continent_id: *(int)* current continent ID
        :>json region_name: *(string)* current region name
        :>json region_id: *(int)* current region ID
        :statuscode 200: successfully returned result
        """
        log_request(request)
        set_headers(request)
        statuscode = OK
        msg = make_response('OK')
        request.setResponseCode(statuscode, message=msg)
        request.setHeader("Content-Type", 'application/json')
        return make_response(
            json.dumps(self.parent_server.playerinfo.map_info)
        )

    @classroute('map_floors')
    def map_floors(self, request):
        """
        Provides local filesystem caching of GW2 map floor information. If the
        requested data is not already in the cache, it will be requested from
        the  GW2 Tiles API.

        This serves :http:get:`/api/map_floors` endpoint.

        :param request: incoming HTTP request
        :type request: :py:class:`twisted.web.server.Request`
        :return: JSON response data string
        :rtype: str

        <HTTPAPI>
        Return the specified GW2 map floor information, from cache on disk.

        Served by :py:meth:`.map_floors`.

        **Example request**:

        .. sourcecode:: http

          GET /map_floors?continent=1&floor=1 HTTP/1.1
          Host: example.com

        **Example Response**:

        .. sourcecode:: http

          HTTP/1.1 200 OK
          Content-Type: application/json

          <JSON here>

        :query int continent: continent ID
        :query int floor: floor number
        :statuscode 200: successfully returned result
        """
        log_request(request)
        set_headers(request)
        required = ['continent', 'floor']
        if sorted(request.args.keys()) != required:
            request.setResponseCode(500, message='MISSING PARAMETERS')
            return ''
        data = self.parent_server.cache.map_floor(
            int(request.args['continent'][0]),
            int(request.args['floor'][0]))
        if data is None:
            request.setResponseCode(500, message='CACHE ERROR')
            return ''
        statuscode = OK
        msg = make_response('OK')
        request.setResponseCode(statuscode, message=msg)
        return make_response(json.dumps(data))

    @classroute('tiles')
    def tiles(self, request):
        """
        Provides local filesystem caching of GW2 map tiles. If the requested tile
        is not already in the cache, it will be requested from the  GW2 Tiles API.

        This serves :http:get:`/api/tiles` endpoint.

        :param request: incoming HTTP request
        :type request: :py:class:`twisted.web.server.Request`
        :return: JSON response data string
        :rtype: str

        <HTTPAPI>
        Return the specified GW2 map tile, from cache on disk.

        Served by :py:meth:`.tiles`.

        **Example request**:

        .. sourcecode:: http

          GET /tiles?continent=1&floor=1&zoom=1&x=x&y=y HTTP/1.1
          Host: example.com

        **Example Response**:

        .. sourcecode:: http

          HTTP/1.1 200 OK
          Content-Type: image/png

          <binary data>

        :query int continent: continent ID
        :query int floor: floor number
        :query int zoom: zoom level
        :query int x: x coordinate
        :query int y: y coordinate
        :statuscode 200: successfully returned result
        :statuscode 500: invalid parameters
        :statuscode 403: tile not available
        """
        log_request(request)
        set_headers(request)
        required = ['continent', 'floor', 'x', 'y', 'zoom']
        if sorted(request.args.keys()) != required:
            request.setResponseCode(500, message='MISSING PARAMETERS')
            return ''
        data = self.parent_server.cache.tile(
            int(request.args['continent'][0]),
            int(request.args['floor'][0]),
            int(request.args['zoom'][0]),
            int(request.args['x'][0]),
            int(request.args['y'][0])
        )
        if data is None:
            request.setResponseCode(403, message='CACHE ERROR')
            return ''
        statuscode = OK
        msg = make_response('OK')
        request.setResponseCode(statuscode, message=msg)
        request.setHeader("Content-Type", 'image/jpeg')
        return data
