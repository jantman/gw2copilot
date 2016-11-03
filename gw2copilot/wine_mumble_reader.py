"""
gw2copilot/wine_mumble_reader.py

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
import os
import json
import psutil
import pkg_resources
from twisted.internet import protocol
from twisted.internet.task import LoopingCall

logger = logging.getLogger()


class WineMumbleLinkReader(object):
    """
    Class to handle reading MumbleLink via wine.
    """

    def __init__(self, parent_server, poll_interval):
        """
        Initialize the class.
        :param parent_server: the TwistedServer instance that started this
        :type parent_server: :py:class:`~.TwistedServer`
        :param poll_interval: interval in seconds to poll MumbleLink
        :type poll_interval: float
        """
        logger.debug("Instantiating WineMumbleLinkReader")
        self.server = parent_server
        self._poll_interval = poll_interval
        self._wine_protocol = None
        self._wine_process = None
        self._looping_deferred = None
        self._setup_process()
        self._add_update_loop()

    def _add_update_loop(self):
        """
        Setup the LoopingCall to poll MumbleLink every ``self.poll_interval``;
        helper for testing.
        """
        logger.debug("Creating LoopingCall")
        l = LoopingCall(self._wine_protocol.ask_for_output)
        l.clock = self.server.reactor
        logger.info('Setting poll interval to %s seconds',
                    self._poll_interval)
        self._looping_deferred = l.start(self._poll_interval)
        self._looping_deferred.addErrback(logger.error)

    def _setup_process(self):
        """
        Setup and spawn the process to read MumbleLink.
        """
        logger.debug("Creating WineProcessProtocol")
        self._wine_protocol = WineProcessProtocol(self.server)
        logger.debug("Finding process executable, args and environ")
        executable, args, env = self._gw2_wine_spawn_info
        logger.debug(
            "Creating spawned process; executable=%s args=%s len(env)=%d",
            executable, args, len(env)
        )
        self._wine_process = self.server.reactor.spawnProcess(
            self._wine_protocol, executable, args, env)

    @property
    def _gw2_wine_spawn_info(self):
        """
        Return the information required to spawn :py:mod:`~.read_mumble_link`
        as a Python script running under GW2's wine install.

        :return: return a 3-tuple of wine executable path (str), args to pass
          to wine (list, wine python binary path and ``read_mumble_link.py``
          module path), wine process environment (dict)
        :rtype: tuple
        """
        gw2_ps = self._gw2_process
        env = gw2_ps.environ()
        wine_path = os.path.join(os.path.dirname(gw2_ps.exe()), 'wine')
        logger.debug("Gw2.exe executable: %s; inferred wine binary as: %s",
                     gw2_ps.exe(), wine_path)
        wine_args = [
            wine_path,
            self._wine_python_path(env['WINEPREFIX']),
            self._read_mumble_path,
            '-i'
        ]
        return wine_path, wine_args, env

    @property
    def _read_mumble_path(self):
        """
        Return the absolute path to :py:mod:`~.read_mumble_link` on disk.

        :return: absolute path to :py:mod:`~.read_mumble_link`
        :rtype: str
        """
        p = pkg_resources.resource_filename('gw2copilot', 'read_mumble_link.py')
        p = os.path.abspath(os.path.realpath(p))
        logger.debug('Found path to read_mumble_link as: %s', p)
        return p

    def _wine_python_path(self, wineprefix):
        """
        Given a specified ``WINEPREFIX``, return the path to the Python binary
        in it.

        :param wineprefix: ``WINEPREFIX`` env var
        :type wineprefix: str
        :return: absolute path to wine's Python binary
        :rtype: str
        """
        p = os.path.join(wineprefix, 'drive_c', 'Python27', 'python.exe')
        if not os.path.exists(p):
            raise Exception("Unable to find wine Python at: %s", p)
        logger.debug('Found wine Python binary at: %s', p)
        return p

    @property
    def _gw2_process(self):
        """
        Find the Gw2.exe process; return the Process object.

        :return: Gw2.exe process
        :rtype: psutil.Process
        """
        gw2_p = None
        for p in psutil.process_iter():
            if p.name() != 'Gw2.exe':
                continue
            if gw2_p is not None:
                raise Exception("Error: more than one Gw2.exe process found")
            gw2_p = p
        if gw2_p is None:
            raise Exception("Error: could not find a running Gw2.exe process")
        logger.debug("Found Gw2.exe process, PID %d", gw2_p.pid)
        return gw2_p


class WineProcessProtocol(protocol.ProcessProtocol):
    """
    An implementation of :py:class:`twisted.internet.protocol.ProcessProtocol`
    to communicate with :py:mod:`~.read_mumble_link` when it is executed
    as a command-line script under wine. This handles reading data from the
    process and requesting more.
    """

    def __init__(self, parent_server):
        """
        Initialize; save an instance variable pointing to our
        :py:class:`~.TwistedServer`

        :param parent_server: the TwistedServer instance that started this
        :type parent_server: :py:class:`~.TwistedServer`
        """
        logger.debug("Initializing WineProcessProtocol")
        self.parent_server = parent_server
        self.have_data = False

    def connectionMade(self):
        """Triggered when the process starts; just logs a debug message"""
        logger.debug("Connection made")

    def ask_for_output(self):
        """
        Write a newline to the process' STDIN, prompting it to re-read the map
        and write the results to STDOUT, which will be received by
        :py:meth:`~.outReceived`.
        """
        logger.debug("asking for output")
        self.transport.write("\n")

    def outReceived(self, data):
        """
        Called when output is received from the process; attempts to deserialize
        JSON and on success passes it back to ``self.parent_server`` via
        :py:meth:`~.TwistedServer.update_mumble_data`.

        :param data: JSON data read from MumbleLink
        :type data: str
        """
        logger.debug("Data received: %s", data)
        try:
            d = json.loads(data.strip())
            self.have_data = True
            self.parent_server.update_mumble_data(d)
        except Exception:
            logger.exception("Could not deserialize data")

    def errReceived(self, data):
        """
        Called when STDERR from the process has output; if we have not yet
        successfully deserialized a JSON message, logs STDERR at debug-level;
        otherwise discards it.

        :param data: STDERR from the process
        :type data: str
        """
        if not self.have_data:
            logger.debug('Process STDERR: %s', data)

    def processExited(self, status):
        """called when the process exits; just logs a debug message"""
        logger.debug("Process exited %s", status)

    def processEnded(self, status):
        """called when the process ends and is cleaned up;
        just logs a debug message"""
        logger.debug("Process ended %s", status)

    def inConnectionLost(self):
        """called when STDIN connection is lost; just logs a debug message"""
        logger.debug("STDIN connection lost")

    def outConnectionLost(self):
        """called when STDOUT connection is lost; just logs a debug message"""
        logger.debug("STDOUT connection lost")
        raise Exception('read_mumble_link.py (wine process) '
                        'STDOUT connection lost')

    def errConnectionLost(self):
        """called when STDERR connection is lost; just logs a debug message"""
        logger.debug("STDERR connection lost")
