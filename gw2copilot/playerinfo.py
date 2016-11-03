"""
gw2copilot/playerinfo.py

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
import requests
import math

logger = logging.getLogger()


class PlayerInfo(object):
    """
    Class to store MumbleLink- and API-derived data about the current player.
    """

    def __init__(self, cache):
        """
        Initialize the object.

        :param cache: the CachingAPIClient instance to use to get/set cache
        :type cache: :py:class:`~.CachingAPIClient`
        """
        self._cache = cache
        self._mumble_link_data = {}
        self._current_map = -1
        self._current_map_data = {}
        # calculated values
        self._facing_direction = 0
        self._elevation = 0
        self._continent_id = 0
        self._continent_name = ''
        self._region_id = 0
        self._region_name = ''
        self._map_name = ''
        self._position = [0, 0]

    @property
    def as_dict(self):
        """
        Return a dictionary representation of relevant information about the
        current player.

        :return: player information
        :rtype: dict
        """
        return {
            'facing_direction': self._facing_direction,
            'elevation': self._elevation,
            'map_id': self._current_map,
            'name': self._mumble_link_data['identity']['name'],
            'profession_id': self._mumble_link_data['identity']['profession'],
            'race_id': self._mumble_link_data['identity']['race'],
            'continent_id': self._continent_id,
            'continent_name': self._continent_name,
            'region_id': self._region_id,
            'region_name': self._region_name,
            'map_name': self._map_name,
            'map_level_range': '%d-%d' % (
                self._current_map_data['min_level'],
                self._current_map_data['max_level']
            ),
            'position': self._position
        }

    def update_mumble_link(self, mumble_link_data):
        """
        Update any values that have changed from mumble link data.

        :param mumble_link_data: raw mumble link data
        :type mumble_link_data: dict
        """
        logger.debug("Updating mumble link data")
        self._mumble_link_data = mumble_link_data
        if self._current_map != mumble_link_data['context']['mapId']:
            logger.debug("Changed maps from %d to %d", self._current_map,
                         mumble_link_data['context']['mapId'])
            self._handle_map_change(mumble_link_data['context']['mapId'])
        self._facing_direction = -(
            math.atan2(mumble_link_data['fAvatarFront'][2],
                       mumble_link_data['fAvatarFront'][0]
                       )*180/math.pi
        ) % 360
        self._elevation = m2i(mumble_link_data['fAvatarPosition'][1])
        self._update_position()

    def _update_position(self):
        """
        Update player position with current mumble and map data.
        """
        map_rect = self._current_map_data['map_rect']
        con_rect = self._current_map_data['continent_rect']
        x = m2i(self._mumble_link_data['fAvatarPosition'][0])
        y = m2i(self._mumble_link_data['fAvatarPosition'][2])
        self._position = self._continent_coords(con_rect, map_rect, x, y)

    def _continent_coords(self, con_rect, map_rect, x, y):
        """
        Given a continent rectangle and map rectangle from map data, plus the
        MumbleLink-provided player x and y corrdinates, determine the continent
        coordinates.

        :param con_rect: continent rectangle from map data
        :type con_rect: list
        :param map_rect: map rectangle from map data
        :type map_rect: list
        :param x: player x position from MumbleLink (inches)
        :type x: float
        :param y: player y position from MumbleLink (inches)
        :type y: float
        :return: continent coordinate (x, y) 2-tuple
        :rtype: tuple
        """
        con_x = (x - map_rect[0][0]) / (map_rect[1][0] - map_rect[0][0]) * \
                (con_rect[1][0] - con_rect[0][0]) + con_rect[0][0]
        con_y = ((-1 * y) - map_rect[0][1]) / \
                (map_rect[1][1] - map_rect[0][1]) * \
                (con_rect[1][1] - con_rect[0][1]) + con_rect[0][1]
        return con_x, con_y

    def _handle_map_change(self, new_map_id):
        """
        Handle when a player changes maps.

        :param new_map_id: new map ID
        :type new_map_id: int
        """
        self._current_map = new_map_id
        mapdata = self._cache.map_data(new_map_id)
        self._continent_id = mapdata['continent_id']
        self._continent_name = mapdata['continent_name']
        self._region_id = mapdata['region_id']
        self._region_name = mapdata['region_name']
        self._map_name = mapdata['map_name']
        self._current_map_data = mapdata


def m2i(m):
    """
    Convert meters to inches.

    :param m: value in meters
    :type m: float
    :return: value in inches
    :rtype: float
    """
    return m * 39.3701