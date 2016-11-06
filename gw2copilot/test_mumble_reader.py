"""
gw2copilot/test_mumble_reader.py

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

logger = logging.getLogger(__name__)


class TestMumbleLinkReader(object):
    """
    Test class to spit back a static dict that looks like Mumble Link data.
    """

    mumble_data = {
        'uiVersion': 2,
        'fAvatarTop': [0.0, 0.0, 0.0],
        'description': '',
        'fCameraTop': [0.0, 0.0, 0.0],
        'uiTick': 2,
        'fAvatarPosition': [
            -174.71437072753906,
            20.880884170532227,
            192.11866760253906
        ],
        'context_len': 48,
        'context': {
            'buildId': 68778,
            'mapId': 50,
            'shardId': 268435480,
            'instance': 0,
            'mapType': 5,
            'serverAddress': {
                'sin_port': 27999,
                'sin_addr': '97.105.110.95',
                'sin_family': 24380
            }
        },
        'fAvatarFront': [
            0.1378183364868164,
            0.0,
            -0.9904575347900391
        ],
        'fCameraFront': [
            0.13758768141269684,
            -0.22495095431804657,
            -0.9646070003509521
        ],
        'fCameraPosition': [
            -176.2913818359375,
            26.569297790527344,
            203.17486572265625
        ],
        'identity': {
            'fov': 0.873,
            'map_id': 50,
            'name': 'Jantman',
            'profession': 4,
            'team_color_id': 0,
            'commander': False,
            'race': 3,
            'world_id': 268435480
        },
        'name': u'Guild Wars 2'
    }

    def __init__(self, parent_server, poll_interval, test_type):
        """
        Initialize the class.

        :param parent_server: the TwistedServer instance that started this
        :type parent_server: :py:class:`~.TwistedServer`
        :param poll_interval: interval in seconds to poll MumbleLink
        :type poll_interval: float
        :param test_type: the type of test to run
        :type test_type: str
        """
        logger.warning("Instantiating TestMumbleLinkReader")
        self.server = parent_server
        self._poll_interval = poll_interval
        self.uiTick = 2
        self._looping_deferred = None
        self._loop_movement = False
        if test_type == 'staticdata':
            self._add_update_loop()
        elif test_type == 'once':
            logger.debug('Test type "once" - not adding update loop')
            self._read()
        elif test_type in ['runfast', 'lightspeed']:
            logger.debug('Test type: %s', test_type)
            self._looping_test(test_type)
        else:
            raise Exception("Invalid test type: %s" % test_type)

    def _looping_test(self, test_type):
        """
        Setup a looping test that moves the player position along a defined path

        :param test_type: type of test to run
        :type test_type: str
        """
        self._loop_movement = True
        # @TODO - implement looping movement

    def _add_update_loop(self):
        """
        Setup the LoopingCall to return data every ``self.poll_interval``;
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
        Update the server with a static dict of data that looks like what
        :py:meth:`~.GW2MumbleLinkReader.read` would return.
        """
        logger.warning("STATIC TEST DATA ONLY - not actually from game!")
        self.uiTick += 1
        self.mumble_data['uiTick'] = self.uiTick
        if self._loop_movement:
            # @TODO implement looping movement
            pass
        self.server.update_mumble_data(self.mumble_data)
