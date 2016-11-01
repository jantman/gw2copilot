#!/usr/bin/env python
"""
gw2copilot/read_mumble_link.py

If we're running natively under Windows, methods in this module will be run
 directly from the main app. If, however, we're running under Linux/Wine,
 we'll need to execute this as a Python script from inside wine, and read the
 output.

This is all jammed in one module so we can run it under wine's Python without
worrying about packages, PYTHONPATH, etc.

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

See: https://wiki.guildwars2.com/wiki/API:MumbleLink
"""

import sys
import binascii
import time
import json
from socket import inet_ntoa
import ctypes
import mmap
import argparse
import logging
from traceback import format_exc

logger = logging.getLogger(__name__)


class GW2MumbleLinkReader(object):
    """
    Class to read GuildWars2 data from the MumbleLink memory-mapped file.

    This reads and returns the raw data exactly as it's presented in the
    MumbleLink file.
    """

    def __init__(self):
        """open the memory-mapped file and prepare for reading"""
        self.fname = "MumbleLink"
        self.map_size = ctypes.sizeof(Link)
        logger.debug("Initializing mmap(0, %d, %s)", self.map_size, self.fname)
        self.memfile = mmap.mmap(0, self.map_size, self.fname)
        logger.debug("memfile initialized")
        self.first = True
        self.previous_tick = 0

    def read(self):
        """
        Read memfile once. Return a dict of its contents if the game has written
        to it (uiTick has changed) since the last read; otherwise return None.

        This should return something like (note the units are not yet converted
        to GW2's coordinate system):

            {
                "description": "",
                "fAvatarPosition": [
                    -33.63362503051758,
                    25.565895080566406,
                    316.7268981933594
                ],
                "context_len": 48,
                 "fCameraPosition": [
                     -33.867549896240234,
                     27.54537582397461,
                     318.3669128417969
                 ],
                 "identity": {
                     "name": "Jantman",
                     "profession": 4,
                     "race": 3,
                     "map_id": 50,
                     "world_id": 268435465,
                     "team_color_id": 0,
                     "commander": false,
                     "fov": 0.873
                 },
                 "uiVersion": 2,
                 "fAvatarTop": [0.0, 0.0, 0.0],
                 "name": "Guild Wars 2",
                 "fCameraTop": [0.0, 0.0, 0.0],
                 "uiTick": 124,
                 "context": {
                     "buildId": 68550,
                     "mapId": 50,
                     "shardId": 268435465,
                     "instance": 0,
                     "mapType": 5,
                     "serverAddress": {
                         "sin_port": 27999,
                         "sin_addr": "97.105.110.95",
                         "sin_family": 24380
                     }
                 },
                 "fCameraFront": [
                     0.13758735358715057,
                     -0.22495177388191223,
                     -0.9646068811416626
                 ],
                 "fAvatarFront": [
                     0.1378183364868164,
                     0.0,
                     -0.9904575347900391
                 ]
            }

        :return: dict of map contents, or None if no changes
        :rtype: dict
        """
        self.memfile.seek(0)
        logger.debug("Reading memfile; previous_tick=%s first=%s",
                     self.previous_tick, self.first)
        data = self.memfile.read(self.map_size)
        logger.debug("Read data: 0x%s", binascii.b2a_hex(data))
        result = Unpack(Link, data)
        if result.uiVersion == 0 and result.uiTick == 0:
            logger.info("MumbleLink contains no data, setting up and waiting")
            try:
                init = Link(2, name="Guild Wars 2")
                self.memfile.seek(0)
                self.memfile.write(init)
                logger.debug("Init struct written")
            except Exception:
                logger.exception("Error writing init data")
        if result.uiTick != self.previous_tick:
            if self.first:
                logger.info("MumbleLink seems to be active, hope for the best")
                first = False
            self.previous_tick = result.uiTick
            logger.debug("Returning dict; new tick=%s", self.previous_tick)
            return result.as_dict()
        # else
        logger.debug("No data change")
        return None


def console_entry_point(argv):
    """
    Console entry point called when this is exec'ed as a standalone Python
    script from inside wine.

    :param argv: command line arguments, ``sys.argv[1:]``
    :type argv: list
    """
    args = parse_args(argv)
    if args.verbose > 1:
        set_log_debug()
    elif args.verbose > 0:
        set_log_info()
    try:
        m = GW2MumbleLinkReader()
    except Exception as ex:
        print(json.dumps({
            'error': True,
            'exception': str(ex),
            'traceback': str(format_exc())
        }))
        raise SystemExit(1)
    while True:
        try:
            res = m.read()
            if res is not None:
                print(json.dumps(res))
        except Exception as ex:
            print(json.dumps({
                'error': True,
                'exception': str(ex),
                'traceback': str(format_exc())
            }))
        if args.pause_in:
            logger.debug("Pausing until newline on STDIN...")
            sys.stdin.readline()
        else:
            time.sleep(args.sleep_sec)


def parse_args(argv):
    """
    Console entry point called when this is exec'ed as a standalone Python
    script from inside wine.

    :param argv: list of arguments to parse (``sys.argv[1:]``)
    :type argv: list
    :return: parsed arguments
    :rtype: :py:class:`argparse.Namespace`
    """
    p = argparse.ArgumentParser(
        description='read MumbleLink memory-mapped file from GuildWars2, print '
                    'all substabtial changes to STDOUT as JSON')
    p.add_argument('-v', '--verbose', dest='verbose', action='count',
                   default=0,
                   help='verbose output. specify twice for debug-level output.')
    p.add_argument('-s', '--sleep', dest='sleep_sec', type=float,
                   action='store', default=2.0, help='number of seconds to '
                                                     'sleep between reads')
    p.add_argument('-i', '--input', dest='pause_in', action='store_true',
                   default=False,
                   help='instead of sleeping for a specified time between '
                        'reads, sleep until a newline is received on STDIN')
    args = p.parse_args(argv)
    return args

##############################
# BEGIN command line helpers #
##############################


def set_log_info():
    """set logger level to INFO"""
    set_log_level_format(logging.INFO,
                         '%(asctime)s %(levelname)s:%(name)s:%(message)s')


def set_log_debug():
    """set logger level to DEBUG, and debug-level output format"""
    set_log_level_format(
        logging.DEBUG,
        "%(asctime)s [%(levelname)s %(filename)s:%(lineno)s - "
        "%(name)s.%(funcName)s() ] %(message)s"
    )


def set_log_level_format(level, format):
    """
    Set logger level and format.

    :param level: logging level; see the :py:mod:`logging` constants.
    :type level: int
    :param format: logging formatter format string
    :type format: str
    """
    formatter = logging.Formatter(fmt=format)
    logger.handlers[0].setFormatter(formatter)
    logger.setLevel(level)

###################################
# BEGIN Struct definition classes #
###################################


def carray_to_array(a, alen):
    """
    Convert a ``ctypes.array`` to a native Python list.

    :param a: ctypes array
    :param alen: length of ctypes array
    :type alen: int
    :return: native Python list
    :rtype: list
    """
    floatPtr = ctypes.cast(a, ctypes.POINTER(ctypes.c_float))
    return [floatPtr[i] for i in range(alen)]


def Unpack(ctype, buf):
    """
    Given binary string from :py:meth:`mmap.mmap.read`, unpack it as the given
    ctype Structure, and return an instance of the Structure.

    :param ctype: ctype Structure to unpack as
    :type ctype: ctypes.Structure
    :param buf: binary data read from :py:meth:`mmap.mmap.read`
    :type buf: str
    :return: unpacked Structure object (instance of ``ctype``)
    :rtype: ctypes.Structure
    """
    cstring = ctypes.create_string_buffer(buf)
    ctype_instance = ctypes.cast(ctypes.pointer(cstring), ctypes.POINTER(ctype)).contents
    return ctype_instance


class in_addr(ctypes.Structure):
    """
    ctypes Structure for in_addr

    struct in_addr {
        unsigned long s_addr;  // load with inet_aton()
    };
    """
    _fields_ = [
        ('s_addr', ctypes.c_byte * 4),
    ]

    def value(self):
        return inet_ntoa(self.s_addr)


class sockaddr_in(ctypes.Structure):
    """
    ctypes Structure for sockaddr_in

    struct sockaddr_in {
        short            sin_family;   // e.g. AF_INET
        unsigned short   sin_port;     // e.g. htons(3490)
        struct in_addr   sin_addr;     // see struct in_addr, below
        char             sin_zero[8];  // zero this if you want to
    }
    """
    _fields_ = [
        ('sin_family', ctypes.c_short),
        ('sin_port',   ctypes.c_ushort),
        ('sin_addr',   in_addr),
    ]

    def as_dict(self):
        d = {
            'sin_family': int(self.sin_family),
            'sin_port': int(self.sin_port),
            'sin_addr': self.sin_addr.value()
        }
        return d


class GW2context(ctypes.Structure):
    """
    ctypes Structure for GW2-specific context element in Link.

    see: https://wiki.guildwars2.com/wiki/API:MumbleLink

    struct MumbleContext {
        byte serverAddress[28]; // contains sockaddr_in or sockaddr_in6
        unsigned mapId;
        unsigned mapType;
        unsigned shardId;
        unsigned instance;
        unsigned buildId;
    };
    """
    _fields_ = [
        ("serverAddress",  ctypes.c_byte * 28),
        ("mapId",          ctypes.c_uint),
        ("mapType",        ctypes.c_uint),
        ("shardId",        ctypes.c_uint),
        ("instance",       ctypes.c_uint),
        ("buildId",        ctypes.c_uint),
    ]

    def as_dict(self):
        d = {
            'mapId': int(self.mapId),
            'mapType': int(self.mapType),
            'shardId': int(self.shardId),
            'instance': int(self.instance),
            'buildId': int(self.buildId),
            'serverAddress': Unpack(
                sockaddr_in, str(self.serverAddress)).as_dict()
        }
        return d


class Link(ctypes.Structure):
    """ctypes Structure for MumbleLink memory map"""
    # see: https://wiki.guildwars2.com/wiki/API:MumbleLink

    _fields_ = [
        ("uiVersion",       ctypes.c_uint32),
        ("uiTick",          ctypes.c_ulong),
        ("fAvatarPosition", ctypes.c_float * 3),
        ("fAvatarFront",    ctypes.c_float * 3),
        ("fAvatarTop",      ctypes.c_float * 3),
        ("name",            ctypes.c_wchar * 256),
        ("fCameraPosition", ctypes.c_float * 3),
        ("fCameraFront",    ctypes.c_float * 3),
        ("fCameraTop",      ctypes.c_float * 3),
        ("identity",        ctypes.c_wchar * 256),
        ("context_len",     ctypes.c_uint32),
        ("context",         GW2context),
        ("description",     ctypes.c_wchar * 2048)
    ]

    def as_dict(self):
        """
        Return a JSON-encoded string representation of the struct.
        """
        d = {
            'uiVersion': int(self.uiVersion),
            'uiTick': int(self.uiTick),
            'fAvatarPosition': carray_to_array(self.fAvatarPosition, 3),
            'fAvatarFront': carray_to_array(self.fAvatarFront, 3),
            'fAvatarTop': carray_to_array(self.fAvatarTop, 3),
            'name': self.name,
            'fCameraPosition': carray_to_array(self.fCameraPosition, 3),
            'fCameraFront': carray_to_array(self.fCameraFront, 3),
            'fCameraTop': carray_to_array(self.fCameraTop, 3),
            'context_len': int(self.context_len),
            'context': self.context.as_dict(),
            'description': self.description
        }
        try:
            d['identity'] = json.loads(self.identity)
        except:
            d['identity'] = self.identity
        return d

if __name__ == "__main__":
    # setup the logger for command-line (non-library) use
    FORMAT = "[%(asctime)s %(levelname)s] %(message)s"
    logging.basicConfig(level=logging.WARNING, format=FORMAT)
    logger = logging.getLogger()
    console_entry_point(sys.argv[1:])
