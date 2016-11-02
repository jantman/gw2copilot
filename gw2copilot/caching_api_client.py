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

logger = logging.getLogger()


class CachingAPIClient(object):
    """
    Caching GW2 API client - performs API requests and returns data, caching
    locally on disk.
    """

    def __init__(self, parent_server, cache_dir):
        """
        Initialize the cache class.

        :param parent_server: the TwistedServer instance that started this
        :type parent_server: :py:class:`~.TwistedServer`
        :param cache_dir: cache directory on filesystem
        :type cache_dir: str
        """
        self._cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            logger.debug('Creating cache directory at: %s', cache_dir)
            os.makedirs(cache_dir, 0700)
        logger.debug('Initialized with cache directory at: %s', cache_dir)

    def _cache_path(self, cache_type, cache_key):
        """
        Return the path on disk to the cache file of the given type and key.

        :param cache_type: the cache type name (directory)
        :type cache_type: str
        :param cache_key: the cache key (filename without extension)
        :type cache_key: str
        :returns: absolute path to cache file
        :rtype: str
        """
        return os.path.join(self._cache_dir, cache_type, '%s.json' % cache_key)

    def _cache_get(self, cache_type, cache_key):
        """
        Read the cache file from disk for the given cache type and cache key;
        return None if it does not exist. If it does exist, return the decoded
        JSON file content.

        :param cache_type: the cache type name (directory)
        :type cache_type: str
        :param cache_key: the cache key (filename without extension)
        :type cache_key: str
        :returns: cache data or None
        :rtype: dict
        """
        p = self._cache_path(cache_type, cache_key)
        if not os.path.exists(p):
            logger.debug('cache MISS for type=%s key=%s (path: %s)',
                         cache_type, cache_key, p)
            return None
        logger.debug('cache HIT for type=%s key=%s (path: %s)',
                     cache_type, cache_key, p)
        with open(p, 'r') as fh:
            raw = fh.read()
        j = json.loads(raw)
        return j

    def _cache_set(self, cache_type, cache_key, data):
        """
        Cache the given data.

        :param cache_type: the cache type name (directory)
        :type cache_type: str
        :param cache_key: the cache key (filename without extension)
        :type cache_key: str
        :param data: the data to cache (value)
        :type data: dict
        """
        p = self._cache_path(cache_type, cache_key)
        logger.debug('cache SET type=%s key=%s (path: %s)',
                     cache_type, cache_key, p)
        cd = os.path.join(self._cache_dir, cache_type)
        if not os.path.exists(cd):
            logger.debug('Creating cache directory: %s', cd)
            os.mkdir(cd, 0700)
        raw = json.dumps(data)
        with open(p, 'w') as fh:
            fh.write(raw)

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
        url = 'https://api.guildwars2.com/v1/maps.json?map_id=%d' % map_id
        logger.debug('GETting map data from: %s', url)
        r = requests.get(url)
        logger.debug('Got map data (HTTP status %d) response length %d',
                     r.status_code, len(r.text))
        result = r.json()['maps'][str(map_id)]
        self._cache_set('mapdata', map_id, result)
        return result
