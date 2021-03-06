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
import logging
import inspect
import json
import time
import os
import re

logger = logging.getLogger(__name__)


def make_response(s):
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


def set_headers(request):
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


def log_request(request):
    """
    Log request information and handling function, via Python logging.

    :param request: incoming HTTP request
    :type request: :py:class:`twisted.web.server.Request`
    """
    # find caller information
    curframe = inspect.currentframe()
    callingframe = inspect.getouterframes(curframe, 2)
    caller_name = callingframe[1][3]
    caller_class = callingframe[1][0].f_locals.get('self', None)
    if caller_class is None:
        class_name = ''
    else:
        class_name = caller_class.__class__.__name__ + '.'
    caller = class_name + caller_name
    logger.info('REQUEST %s%s for %s from %s:%s handled by %s()',
                ('QUEUED ' if request.queued else ''),
                str(request.method), request.uri,
                request.client.host, request.client.port, caller
                )


def dict2js(varname, data):
    """
    Convert dict ``data`` to javascript source code for a javascript variable
    named ``varname``.

    :param varname: name of the JS source variable
    :type varname: str
    :param data: dict to represent as an object
    :type data: dict
    :return: javascript source snippet
    :rtype: str
    """
    return "var %s = %s;\n" % (
        varname, json.dumps(data, sort_keys=True, indent=4)
    )


def file_age(p):
    """
    Return the age of a file in seconds.

    :param p: path to the file
    :type p: str
    :return: file age in seconds
    :rtype: float
    """
    return time.time() - os.stat(p).st_mtime


def extract_js_var(s, varname):
    """
    Given a string of javascript source code, extract the source of the given
    variable name. Makes rather naive assumptions about correct formatting.

    :param s: original JS source string
    :type s: str
    :param varname: the variable name to get
    :type v: str
    :return: source of specified variable
    :rtype: str
    """
    vname_re = re.compile('^var %s\s+=\s+{.*$' % varname)
    src = ''
    in_var = False
    for line in s.split("\n"):
        if not in_var and vname_re.match(line):
            in_var = True
            src += line + "\n"
        elif in_var:
            src += line + "\n"
            if '};' in line:
                return src
    raise Exception("Could not parse JS variable %s from source" % varname)
