#!/usr/bin/env python
"""
https://github.com/zeeZ/gw2-location/blob/75f446535ed448e569bc458ccdabc71413a5f2ed/client/location_sender.py



See also:
https://github.com/hackedd/gw2api/blob/6e785b257180473b9e8ce0653f101c54d59c7144/gw2api/mumble.py
https://github.com/TheTerrasque/gw2lib/blob/2fd7a5efea1e3036a84cfda172a3571399a1e3de/gw2lib/mumble.py
https://github.com/teomat/gw2-wurm-blocking-helper/blob/1e4380073ebf98407351d8f066681779a6def4d9/wurm%20overlay.py
https://github.com/nandokun/gw2_event_map/blob/cb9b2cb94daeb200684407b325b4b09fd9b46b36/server/web_server.py

https://wiki.guildwars2.com/wiki/API:MumbleLink
"""

import mmap
import struct
import binascii
import time
import json
from socket import inet_ntoa

fname = "MumbleLink"
#fmt = 'IL3f3f3f512s3f'
fmt = 'IL3f256s3f256sL256s2048s'
mapsize = struct.calcsize(fmt)
    
import ctypes
import mmap

class in_addr(ctypes.Structure):
    """
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
    struct sockaddr_in {
        short            sin_family;   // e.g. AF_INET
        unsigned short   sin_port;     // e.g. htons(3490)
        struct in_addr   sin_addr;     // see struct in_addr, below
        char             sin_zero[8];  // zero this if you want to
    };
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
        }
        d['sin_addr'] = self.sin_addr.value()
        return d

class GW2context(ctypes.Structure):
    """
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
            #'serverAddress': self.serverAddress,
            'mapId': int(self.mapId),
            'mapType': int(self.mapType),
            'shardId': int(self.shardId),
            'instance': int(self.instance),
            'buildId': int(self.buildId)
        }
        d['serverAddress'] = Unpack(sockaddr_in, str(self.serverAddress)).as_dict()
        return d

class Link(ctypes.Structure):
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
        #("context",         ctypes.c_uint32 * 64), # is actually 256 bytes of whatever
        ("context",         GW2context),
        ("description",     ctypes.c_wchar * 2048)
    ]

    def as_dict(self):
        """
        Return a JSON-encoded string representation of the struct.
        """
        d = {
            'uiVersion': int(self.uiVersion),
            'uiTick': int(result.uiTick),
            'fAvatarPosition': carray_to_array(result.fAvatarPosition, 3),
            'fAvatarFront': carray_to_array(result.fAvatarFront, 3),
            'fAvatarTop': carray_to_array(result.fAvatarTop, 3),
            'name': result.name,
            'fCameraPosition': carray_to_array(result.fCameraPosition, 3),
            'fCameraFront': carray_to_array(result.fCameraFront, 3),
            'fCameraTop': carray_to_array(result.fCameraTop, 3),
            'identity': result.identity,
            'context_len': int(result.context_len),
            #'context': carray_to_array(result.context, 64),
            'context': result.context.as_dict(),
            'description': result.description
        }
        if d['name'] == 'Guild Wars 2':
            # use GW2-specific context struct
            #ctx = Unpack(GW2context, result.context).as_json()
            pass
        return d

def carray_to_array(a, alen):
    floatPtr = ctypes.cast(a, ctypes.POINTER(ctypes.c_float))
    return [floatPtr[i] for i in range(alen)]

def Unpack(ctype, buf):
    cstring = ctypes.create_string_buffer(buf)
    ctype_instance = ctypes.cast(ctypes.pointer(cstring), ctypes.POINTER(ctype)).contents
    return ctype_instance


def continent_coords(continent_rect, map_rect, point):
    return (
        ( point[0]-map_rect[0][0])/(map_rect[1][0]-map_rect[0][0])*(continent_rect[1][0]-continent_rect[0][0])+continent_rect[0][0],
        (-point[1]-map_rect[0][1])/(map_rect[1][1]-map_rect[0][1])*(continent_rect[1][1]-continent_rect[0][1])+continent_rect[0][1]
    )


current_map = 0
current_map_data = None
previous_tick = 0
first = True
memfile = mmap.mmap(0, ctypes.sizeof(Link), "MumbleLink")
while True:
    memfile.seek(0)
    data = memfile.read(ctypes.sizeof(Link))
    result = Unpack(Link, data)
    if result.uiVersion == 0 and result.uiTick == 0:
        print("MumbleLink contains no data, setting up and waiting")
        try:
            init = Link(2,name="Guild Wars 2")
            memfile.seek(0)
            memfile.write(init)
        except Exception, e:
            logging.exception("Error writing init data",e)
    if result.uiTick != previous_tick:
        if first:
            print("MumbleLink seems to be active, hope for the best")
            first = False
        r = result.as_dict()
        print(r)
    previous_tick = result.uiTick
    time.sleep(2)
