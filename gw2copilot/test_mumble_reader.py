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
        # vars for loop movement tests
        self._loop_movement = False
        self.x_step = 0  # how far to move every _read()
        self.y_step = 0  # how far to move every _read()
        # these values are world coordinates and need to be run through
        # self.parent_server.playerinfo._map_coords_from_position()
        # and then divided by 39.3701 before being returned as MumbleLink data
        self.min_x = 1100.8
        self.max_x = 30976
        self.min_y = 14976
        self.max_y = 14976
        self.curr_x = self.min_x
        self.curr_y = self.min_y
        self.x_direction = 1
        self.y_direction = 1
        if test_type == 'once':
            logger.debug('Test type "once" - not adding update loop')
            self._read()
        elif test_type in ['runfast', 'lightspeed', 'staticdata']:
            logger.debug('Test type: %s', test_type)
            if test_type == 'runfast':
                self._loop_movement = True
                self.x_step = (self.max_x - self.min_x) * .01
                self.y_step = (self.max_y - self.min_y) * .01
            elif test_type == 'lightspeed':
                self._loop_movement = True
                self.x_step = (self.max_x - self.min_x) * .1
                self.y_step = (self.max_y - self.min_y) * .1
            self._add_update_loop()
        else:
            raise Exception("Invalid test type: %s" % test_type)

    def _looping_test(self):
        """
        Setup a looping test that moves the player position along a defined path

        :param test_type: type of test to run
        :type test_type: str
        """
        logger.debug('curr_x=%s curr_y=%s', self.curr_x, self.curr_y)
        self.curr_x = self._step('x')
        self.curr_y = self._step('y')
        try:
            map_id, map_x, map_y = \
                self.server.playerinfo._map_coords_from_position(
                    (self.curr_x, self.curr_y))
            # meters to inches
            map_x /= 39.3701
            map_y /= 39.3701
            logger.debug('new_x=%s new_y=%s map_id=%d map_x=%s map_y=%s',
                         self.curr_x, self.curr_y, map_id, map_x, map_y)
            self.mumble_data['fAvatarPosition'][0] = map_x
            self.mumble_data['fAvatarPosition'][2] = map_y
            self.mumble_data['context']['mapId'] = map_id
        except Exception:
            self._looping_test()

    def _step(self, axis):
        """
        Step a value by the step amount; if we run over max or under min,
        reverse direction.

        :param axis: the axis to step, "x" or "y"
        :type axis: str
        :return: new value
        :rtype: float
        """
        curr = getattr(self, 'curr_%s' % axis)
        min_v = getattr(self, 'min_%s' % axis)
        max_v = getattr(self, 'max_%s' % axis)
        step_amt = getattr(self, '%s_step' % axis)
        direction = getattr(self, '%s_direction' % axis)
        step = step_amt * direction
        if (curr + step) > max_v:
            logger.debug('reversing direction - going backwards')
            setattr(self, '%s_direction' % axis, -1)
            step = step_amt * -1
        elif (curr + step) < min_v:
            logger.debug('reversing direction - going forwards')
            setattr(self, '%s_direction' % axis, 1)
            step = step_amt
        curr += step
        return curr

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
            self._looping_test()
        self.server.update_mumble_data(self.mumble_data)
