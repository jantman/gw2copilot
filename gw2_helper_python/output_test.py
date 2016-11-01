#!/usr/bin/env python
"""
gw2_helper_python/output_test.py

If we're running natively under Windows, methods in this module will be run
 directly from the main app. If, however, we're running under Linux/Wine,
 we'll need to execute this as a Python script from inside wine, and read the
 output.

This is all jammed in one module so we can run it under wine's Python without
worrying about packages, PYTHONPATH, etc.

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
from datetime import datetime

FORMAT = "[%(asctime)s %(levelname)s] %(message)s"
logging.basicConfig(level=logging.WARNING, format=FORMAT)
logger = logging.getLogger()


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


set_log_debug()
res = {'baz': 'blam'}
while True:
    sys.stdout.write(json.dumps({'baz': 'blam', 'dt': str(datetime.now())}) + "\n")
    sys.stdout.flush()
    logger.debug("Pausing until newline on STDIN...")
    sys.stdin.readline()
