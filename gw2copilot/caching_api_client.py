"""
gw2copilot/caching_api_client.py

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
import os
import json
import urllib

logger = logging.getLogger()


class CachingAPIClient(object):
    """
    Caching GW2 API client - performs API requests and returns data, caching
    locally on disk.
    """

    def __init__(self, parent_server, cache_dir, api_key=None):
        """
        Initialize the cache class.

        :param parent_server: the TwistedServer instance that started this
        :type parent_server: :py:class:`~.TwistedServer`
        :param cache_dir: cache directory on filesystem
        :type cache_dir: str
        :param api_key: GW2 API Key
        :type api_key: str
        """
        self._cache_dir = cache_dir
        self._api_key = api_key
        self._characters = {}  # these don't get cached to disk
        if not os.path.exists(cache_dir):
            logger.debug('Creating cache directory at: %s', cache_dir)
            os.makedirs(cache_dir, 0700)
        logger.debug('Initialized with cache directory at: %s', cache_dir)

    def _cache_path(self, cache_type, cache_key, extn):
        """
        Return the path on disk to the cache file of the given type and key.

        :param cache_type: the cache type name (directory)
        :type cache_type: str
        :param cache_key: the cache key (filename without extension)
        :type cache_key: str
        :param extn: file extension
        :type extn: str
        :returns: absolute path to cache file
        :rtype: str
        """
        return os.path.join(
            self._cache_dir, cache_type, '%s.%s' % (cache_key, extn)
        )

    def _cache_get(self, cache_type, cache_key, binary=False, extension='json'):
        """
        Read the cache file from disk for the given cache type and cache key;
        return None if it does not exist. If it does exist, return the decoded
        JSON file content.

        :param cache_type: the cache type name (directory)
        :type cache_type: str
        :param cache_key: the cache key (filename without extension)
        :type cache_key: str
        :param binary: whether to read as binary data
        :type binary: bool
        :param extension: file extension to save in cache with
        :type extension: str
        :returns: cache data or None
        :rtype: dict
        """
        p = self._cache_path(cache_type, cache_key, extn=extension)
        if not os.path.exists(p):
            logger.debug('cache MISS for type=%s key=%s (path: %s)',
                         cache_type, cache_key, p)
            return None
        logger.debug('cache HIT for type=%s key=%s (path: %s)',
                     cache_type, cache_key, p)
        if binary:
            with open(p, 'rb') as fh:
                r = fh.read()
            return r
        with open(p, 'r') as fh:
            raw = fh.read()
        j = json.loads(raw)
        return j

    def _cache_set(self, cache_type, cache_key, data, binary=False,
                   extension='json'):
        """
        Cache the given data.

        :param cache_type: the cache type name (directory)
        :type cache_type: str
        :param cache_key: the cache key (filename without extension)
        :type cache_key: str
        :param data: the data to cache (value)
        :type data: dict
        :param binary: if True, write as binary data
        :type binary: bool
        :param extension: file extension to save in cache with
        :type extension: str
        """
        p = self._cache_path(cache_type, cache_key, extn=extension)
        logger.debug('cache SET type=%s key=%s (path: %s)',
                     cache_type, cache_key, p)
        cd = os.path.join(self._cache_dir, cache_type)
        if not os.path.exists(cd):
            logger.debug('Creating cache directory: %s', cd)
            os.mkdir(cd, 0700)
        if binary:
            with open(p, 'wb') as fh:
                fh.write(data)
            return
        raw = json.dumps(data)
        with open(p, 'w') as fh:
            fh.write(raw)

    def _get(self, path, auth=False):
        """
        Perform a GET against the GW2 API. Return the response object.

        :param path: path to request, beginning with version (e.g. ``/v1/foo``)
        :type path: str
        :param auth: whether or not to provide authentication
        :type auth: bool
        :return: response object
        :rtype: requests.Response
        """
        url = 'https://api.guildwars2.com' + path

        if auth:
            # yeah, quick and dirty...
            if '?' in url:
                url += '&access_token=%s' % self._api_key
            else:
                url += '?access_token=%s' % self._api_key
        logger.debug('GET %s (auth=%s)', url, auth)
        r = requests.get(url)
        logger.debug('GET %s returned status %d', url, r.status_code)
        return r

    def map_data(self, map_id):
        """
        Return dict of map data for the given map ID.

        :param map_id: requested map ID
        :type map_id: int
        :return: map data
        :rtype: dict
        """
        cached = self._cache_get('mapdata', map_id)
        if cached is not None:
            return cached
        r = self._get('/v1/maps.json?map_id=%d' % map_id)
        logger.debug('Got map data (HTTP status %d) response length %d',
                     r.status_code, len(r.text))
        result = r.json()['maps'][str(map_id)]
        self._cache_set('mapdata', map_id, result)
        return result

    def map_floor(self, continent_id, floor):
        """
        Return dict of map floor information for the given continent ID and
        floor.

        :param continent_id: requested continent ID
        :type continent_id: int
        :param floor: floor number
        :type floor: int
        :return: map data
        :rtype: dict
        """
        key = '%d_%d' % (continent_id, floor)
        cached = self._cache_get('map_floors', key)
        if cached is not None:
            return cached
        r = self._get('/v1/map_floor.json?continent_id=%d&floor=%d' % (
            continent_id, floor
        ))
        logger.debug('Got map floor data (HTTP status %d) response length %d',
                     r.status_code, len(r.text))
        if r.status_code != 200:
            logger.debug("Response: %s", r.text)
            return None
        result = r.json()
        self._cache_set('map_floors', key, result)
        return result

    def character_info(self, name):
        """
        Return character information for the named character. This is NOT cached
        to disk; it is cached in-memory only.

        :param name: character name
        :type name: str
        :return: GW2 API character information
        :rtype: dict
        """
        if name in self._characters:
            logger.debug('Using cached character info for: %s', name)
            return self._characters[name]
        path = '/v2/characters/%s' % urllib.quote(name)
        r = self._get(path, auth=True)
        j = r.json()
        logger.debug('Got character information for %s: %s', name, j)
        self._characters[name] = j
        return j

    def tile(self, continent, floor, zoom, x, y):
        """
        Get a tile from local cache, or if not cached, from the GW2 Tile Service

        :param continent: continent ID
        :type continent: int
        :param floor: floor number
        :type floor: int
        :param zoom: zoom level
        :type zoom: int
        :param x: x coordinate
        :type x: int
        :param y: y coordinate
        :type y: int
        :return: binary tile JPG content
        """
        cache_key = '%d_%d_%d_%d_%d' % (continent, floor, zoom, x, y)
        cached = self._cache_get('tiles', cache_key, binary=True,
                                 extension='jpg')
        if cached:
            return cached
        url = 'https://tiles.guildwars2.com/{continent_id}/{floor}/' \
              '{zoom}/{x}/{y}.jpg'.format(
            continent_id=continent,
            floor=floor,
            zoom=zoom,
            x=x,
            y=y
        )
        logger.debug('GET %s', url)
        r = requests.get(url)
        logger.debug('GET %s returned status %d, %d bytes', url,
                     r.status_code, len(r.content))
        if r.status_code != 200:
            logger.debug("Response: %s", r.text)
            return None
        self._cache_set('tiles', cache_key, r.content, binary=True,
                        extension='jpg')
        return r.content
