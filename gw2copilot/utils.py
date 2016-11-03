"""
gw2copilot/utils.py

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
from .version import VERSION


def _make_response(s):
    """
    Return the value for a Twisted/Klein response; if running under python 3+
    utf-8 encode the response, otherwise return ``s``.

    :param s: response string
    :type s: str
    :return: response string, possibly encoded
    :rtype: str
    """
    if sys.version_info[0] < 3:
        return s
    return s.encode('utf-8')  # nocoverage - unreachable under py2


def _set_headers(request):
    """
    Set headers that all HTTP responses should have.

    :param request: incoming HTTP request
    :type request: :py:class:`twisted.web.server.Request`
    """
    # find the original Twisted server header
    twisted_server = request.responseHeaders.getRawHeaders(
        'server', 'Twisted'
    )[0]
    request.setHeader('server',
                      'gw2copilot/%s/%s' % (VERSION, twisted_server))
