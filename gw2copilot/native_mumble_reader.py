"""
gw2copilot/native_mumble_reader.py

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
from twisted.internet.task import LoopingCall
from .read_mumble_link import GW2MumbleLinkReader

logger = logging.getLogger(__name__)


class NativeMumbleLinkReader(object):
    """
    Class to handle reading MumbleLink natively (direct mmap).
    """

    def __init__(self, parent_server, poll_interval):
        """
        Initialize the class. Create the :py:class:`~.GW2MumbleLinkReader`
        instance.

        :param parent_server: the TwistedServer instance that started this
        :type parent_server: :py:class:`~.TwistedServer`
        :param poll_interval: interval in seconds to poll MumbleLink
        :type poll_interval: float
        """
        logger.debug("Instantiating NativeMumbleLinkReader")
        self.server = parent_server
        self._poll_interval = poll_interval
        self._looping_deferred = None
        self._reader = GW2MumbleLinkReader()
        self._add_update_loop()

    def _add_update_loop(self):
        """
        Setup the LoopingCall to poll MumbleLink every ``self.poll_interval``;
        helper for testing. The LoopingCall will simply call :py:meth:`~._read`.
        """
        logger.debug("Creating LoopingCall")
        l = LoopingCall(self._read)
        l.clock = self.server.reactor
        logger.info('Setting poll interval to %s seconds',
                    self._poll_interval)
        self._looping_deferred = l.start(self._poll_interval)
        self._looping_deferred.addErrback(logger.error)

    def _read(self):
        """
        Read from the mmap via ``self._reader`` (
        :py:meth:`~.GW2MumbleLinkReader.read`) and pass data back to
        ``self.parent_server`` via :py:meth:`~.TwistedServer.update_mumble_data`
        """
        logger.debug("Reading MumbleLink mmap")
        d = self._reader.read()
        self.server.update_mumble_data(d)
