#!/usr/bin/env python
"""
gw2copilot/runner.py

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
import os
import argparse
import logging

from .version import VERSION, PROJECT_URL
from .server import TwistedServer

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger()

# suppress requests internal logging below WARNING level
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)
requests_log.propagate = True


class Runner(object):
    """command-line entry point for the main TwistedServer"""

    def parse_args(self, argv):
        """
        parse arguments/options

        :param argv: argument list to parse, usually ``sys.argv[1:]``
        :type argv: list
        :returns: parsed arguments
        :rtype: :py:class:`argparse.Namespace`
        """
        desc = 'Python-based GW2 helper app'
        p = argparse.ArgumentParser(description=desc)
        p.add_argument('-v', '--verbose', dest='verbose', action='count',
                       default=0,
                       help='verbose output. specify twice for debug-level '
                       'output.')
        ver_str = 'gw2copilot {v} (see <{s}> for source code)'.format(
            s=PROJECT_URL,
            v=VERSION
        )
        p.add_argument('-V', '--version', action='version', version=ver_str)
        p.add_argument('-p', '--poll-interval', dest='poll_interval',
                       default=2.0, action='store', type=float,
                       help='MumbleLink polling interval in seconds '
                       '(default: 2.0)')
        p.add_argument('-P', '--port', dest='bind_port', action='store',
                       type=int, default=8080,
                       help='Port number to listen on (default 8080)')
        cd = os.path.abspath(os.path.expanduser('~/.gw2copilot/cache'))
        p.add_argument('-c', '--cache-dir', dest='cache_dir', action='store',
                       default=cd, type=str,
                       help='cache directory path (default: %s)' % cd)
        test_types = {
            'staticdata': 'always send the same fake data, except timestamp',
            'once': 'send fake data, but only once'
        }
        p.add_argument('-t', '--test', dest='test_mumble', action='store',
                       type=str, default=None, choices=test_types.keys(),
                       help='do not actually connect to game via MumbleLink; '
                            'use static example/test data; possible values: ' +
                            ', '.join(
                           ['"%s" - %s' % (
                               k, test_types[k]) for k in test_types.keys()]
                       ))
        args = p.parse_args(argv)
        return args

    def console_entry_point(self):
        """parse arguments, handle them, run the TwistedServer"""
        args = self.parse_args(sys.argv[1:])
        if args.verbose == 1:
            set_log_info()
        elif args.verbose > 1:
            set_log_debug()

        s = TwistedServer(
            poll_interval=args.poll_interval,
            bind_port=args.bind_port,
            test=args.test_mumble,
            cache_dir=args.cache_dir
        )
        s.run()


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


def console_entry_point():
    """
    console entry point - create a :py:class:`~.Runner` and call its
    :py:meth:`~.Runner.console_entry_point` method.
    """
    r = Runner()
    r.console_entry_point()


if __name__ == "__main__":
    console_entry_point()
