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
from base64 import b64encode
from PIL import Image
from StringIO import StringIO

from .utils import dict2js, file_age
from .static_data import world_zones

logger = logging.getLogger(__name__)

#: Cache TTL - 1 day, in seconds
TTL_1DAY = 86400

#: Cache TTL - 1 hour, in seconds
TTL_1HOUR = 3600


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
        self._server = parent_server
        self._characters = {}  # these don't get cached to disk
        self._all_maps = None  # cache in memory as well
        self._zone_reminders = None  # cache in memory as well
        self._map_floors = {}  # cached in memory as well
        if not os.path.exists(cache_dir):
            logger.debug('Creating cache directory at: %s', cache_dir)
            os.makedirs(cache_dir, 0700)
        logger.debug('Initialized with cache directory at: %s', cache_dir)

    def fill_persistent_cache(self):
        """
        Ensure we have cached data for things we *know* we will need...
        """
        # ensure we have all map data cached
        _ = self.all_maps
        self._make_map_data_js()
        self._get_gw2_api_files()

    @property
    def cache_dir(self):
        """
        Return the current cache directory on disk.

        :return: cache directory path
        :rtype: str
        """
        return self._cache_dir

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

    def _cache_get(self, cache_type, cache_key, binary=False, extension='json',
                   ttl=None):
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
        :param ttl: cache TTL in seconds; if not None, and the file exists on
          disk, it will only be returned (non-None result) if newer than this
          number of seconds
        :type ttl: int
        :returns: cache data or None
        :rtype: dict
        """
        p = self._cache_path(cache_type, cache_key, extn=extension)
        if not os.path.exists(p):
            logger.debug('cache MISS for type=%s key=%s (path: %s)',
                         cache_type, cache_key, p)
            return None
        age = file_age(p)
        if ttl is not None and age >= ttl:
            logger.debug('cache expired for type=%s key=%s (age=%s)',
                         cache_type, cache_key, age)
            return None
        if binary:
            with open(p, 'rb') as fh:
                r = fh.read()
            return r
        with open(p, 'r') as fh:
            raw = fh.read()
        j = json.loads(raw)
        return j

    def _cache_set(self, cache_type, cache_key, data, binary=False, raw=False,
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
        :param raw: if True, write exact string provided
        :type raw: bool
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
        if raw:
            with open(p, 'w') as fh:
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

    @property
    def all_maps(self):
        """
        Return a dict of map data for ALL maps, keys are map IDs and values are
        map data, as would be returned by :py:meth:`~.map_data`.

        :return: dict of all map data, keys are map ID and values are map data
        :rtype: dict
        """
        if self._all_maps is not None:
            logger.debug('Already have all maps in cache')
            return self._all_maps
        ids = self._cache_get('mapdata', 'ids', ttl=TTL_1DAY)
        if ids is None:
            r = self._get('/v2/maps')
            ids = r.json()
            self._cache_set('mapdata', 'ids', ids)
        logger.debug('Got list of all %d map IDs', len(ids))
        maps = {}
        logger.info("Starting to fill map data cache...")
        for _id in ids:
            maps[_id] = self.map_data(_id)
        logger.info('Cached all map data')
        self._all_maps = maps
        self._cache_set('mapdata', 'all_maps', maps)
        return self._all_maps

    def _make_map_data_js(self):
        """
        Write a javascript source file to
        ``{self._cache_dir}/mapdata/mapdata.js`` that contains javascript source
        for ``all_maps`` as well as the standard world zones, as id to name and
        name to id.
        """
        s = "// generated at server start by gw2copilot.caching_api_client." \
            "CachingAPIClient._make_map_data_js()\n"
        s += dict2js('MAP_INFO', self._all_maps)
        s += dict2js('WORLD_ZONES_IDtoNAME', world_zones)
        zones_name_to_id = {}
        for id, name in world_zones.iteritems():
            zones_name_to_id[name] = id
        s += dict2js('WORLD_ZONES_NAMEtoID', zones_name_to_id)
        self._cache_set('mapdata', 'mapdata', s, extension='js', raw=True)

    def map_data(self, map_id):
        """
        Return dict of map data for the given map ID. This combines the data
        container in the GW2 API's ``/v1/maps.json?map_id=ID`` endpoint with
        the POI information from the ``/v1/map_floor.json`` endpoint.

        :param map_id: requested map ID
        :type map_id: int
        :return: map data
        :rtype: dict
        """
        if self._all_maps is not None and map_id in self._all_maps:
            return self._all_maps[map_id]
        cached = self._cache_get('mapdata', map_id)
        if cached is not None:
            return cached
        r = self._get('/v1/maps.json?map_id=%d' % map_id)
        logger.debug('Got map data (HTTP status %d) response length %d',
                     r.status_code, len(r.text))
        result = r.json()['maps'][str(map_id)]
        # get the floor
        floor = self.map_floor(result['continent_id'], result['default_floor'])
        try:
            f_info = floor['regions'][
                str(result['region_id'])]['maps'][str(map_id)]
            result['points_of_interest'] = {}
            for poi in f_info['points_of_interest']:
                if poi['type'] not in result['points_of_interest']:
                    result['points_of_interest'][poi['type']] = []
                result['points_of_interest'][poi['type']].append(
                    self._add_chat_link_to_poi_dict(poi)
                )
            result['skill_challenges'] = f_info.get('skill_challenges', [])
            result['tasks'] = f_info.get('tasks', [])
        except (TypeError, KeyError):
            logger.error("Could not find floor info for map_id %d "
                         "(contient_id=%d default_floor=%d region_id=%d)",
                         map_id, result['continent_id'],
                         result['default_floor'], result['region_id'])
        self._cache_set('mapdata', map_id, result)
        return result

    def _add_chat_link_to_poi_dict(self, poi):
        """
        Given a POI dictionary such as the one returned by the floor_info API
        (i.e. a dict containing a ``type`` key (string value) and a ``poi_id``
        key (int value)), add a ``chat_link`` key to the dict containing the
        appropriate 0x04 chat link for the POI.

        The links are base64-encoded values enclosed in single square brackets
        with a leading ampersand, i.e. ``[&BASE64]``.

        POI/Waypoint links have a first byte of 0x04, followed by the ID as a
        2-byte little endian integer, two null bytes.

        :param poi: POI information
        :type poi: dict
        :return: dict with added ``chat_link`` key
        :rtype: dict
        """
        b = b'\x04' + chr(poi['poi_id'] % 256) + chr(
            int(poi['poi_id'] / 256)) + b'\x00\x00'
        poi['chat_link'] = '[&' + b64encode(b).decode(encoding="UTF-8") + ']'
        return poi

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
        if key in self._map_floors:
            return self._map_floors[key]
        cached = self._cache_get('map_floors', key)
        if cached is not None:
            self._map_floors[key] = cached
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
        self._map_floors[key] = cached
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
            if cached == '':
                logger.debug('Returning cached 403 for tile')
                return None
            return cached
        url = 'https://tiles.guildwars2.com/{continent_id}/{floor}/' \
              '{zoom}/{x}/{y}.jpg'.format(continent_id=continent, floor=floor,
                                          zoom=zoom, x=x, y=y)
        logger.debug('GET %s', url)
        r = requests.get(url)
        logger.debug('GET %s returned status %d, %d bytes', url,
                     r.status_code, len(r.content))
        if r.status_code != 200 and r.status_code != 403:
            logger.debug("Response: %s", r.text)
            return None
        if r.status_code == 403:
            logger.debug('403 - Tile does not exist')
            self._cache_set('tiles', cache_key, r.content, binary=True,
                            extension='jpg')
            return None
        self._cache_set('tiles', cache_key, r.content, binary=True,
                        extension='jpg')
        return r.content

    def _get_gw2_api_files(self):
        """
        Get assets that we need from the GW2
        `files API <https://wiki.guildwars2.com/wiki/API:1/files>`_ and add them
        to cache; this is mainly map icons.
        """
        files_to_get = [
            'map_adventure',
            'map_adventure_complete',
            'map_adventure_locked',
            'map_bank',
            'map_complete',
            'map_heart_empty',
            'map_heart_full',
            'map_heropoint',
            'map_node_harvesting',
            'map_node_logging',
            'map_node_mining',
            'map_poi',
            'map_repair',
            'map_special_event',
            'map_story',
            'map_trading_post',
            'map_vendor',
            'map_vista',
            'map_waypoint',
            'map_waypoint_contested',
            'map_waypoint_hover',
        ]
        logger.debug('Getting assets from GW2 files API')
        files = self._cache_get('api', 'files', ttl=TTL_1DAY)
        if files is None:
            r = self._get('/v1/files.json?ids=all', auth=True)
            files = r.json()
            self._cache_set('api', 'files', files)
        for name in files_to_get:
            if os.path.exists(self._cache_path('assets', name, 'png')):
                logger.debug('Already have asset: %s', name)
                continue
            if name not in files:
                logger.error("Error: /v1/files no longer contains: %s", name)
                continue
            f = files[name]
            url = '{base}/file/{signature}/{file_id}.{format}'.format(
                base='https://render.guildwars2.com',
                signature=f['signature'],
                file_id=f['file_id'],
                format='png'
            )
            r = requests.get(url)
            if r.status_code != 200:
                logger.debug("HTTP %d response for %s: %s", r.status_code, url,
                             r.text)
                continue
            self._cache_set('assets', name, r.content, binary=True,
                            extension='png')
            self._resize_asset(name, r.content)
        logger.debug('Done getting assets')

    def _resize_asset(self, name, bin_content):
        """
        Given the filename and binary content of a PNG image asset, resize it
        to 32x32 and write it to cache with a "_32x32" suffix on the filename.

        :param name: asset/file name
        :type name: str
        :param bin_content: image binary content
        :type bin_content: str
        """
        name += '_32x32'
        img = Image.open(StringIO(bin_content))
        img.thumbnail((32, 32))
        sio = StringIO()
        img.save(sio, format='png')
        self._cache_set('assets', name, sio.getvalue(), binary=True,
                        extension='png')

    @property
    def zone_reminders(self):
        """
        Return list of zone reminders. Each list element is a dict with keys
        "map_id" (int map ID) and "text" (string).

        :return: zone reminders (list of dicts)
        :rtype: list
        """
        if self._zone_reminders is not None:
            return self._zone_reminders
        r = self._cache_get('user_settings', 'zone_reminders')
        if r is None:
            r = []
        self._zone_reminders = r
        return r

    def set_zone_reminders(self, reminders):
        """
        Set the zone_reminders in cache and in memory. Parameter is a list of
        zone reminders. Each list element is a dict with keys "map_id"
        (int map ID) and "text" (string).

        :param reminders: list of reminder dicts
        :type reminders: list
        """
        self._zone_reminders = reminders
        self._cache_set('user_settings', 'zone_reminders', reminders)
