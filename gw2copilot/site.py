"""
gw2copilot/site.py

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
import json
from datetime import datetime, timedelta
from twisted.web._responses import OK
from twisted.web.static import File
from jinja2 import Environment, PackageLoader
from klein import Klein
import os

from .utils import make_response, set_headers, log_request
from .route_helpers import classroute, ClassRouteMixin
from .version import VERSION, PROJECT_URL

logger = logging.getLogger(__name__)


class GW2CopilotSite(ClassRouteMixin):
    """
    Class to add the UI routes to our Klein app.
    """

    #: ``klein.app.Klein()`` instance for all web serving
    app = Klein()

    #: route prefix to prepend to all @classroutes
    _route_prefix = '/'

    def __init__(self, parent_server):
        """
        Initialize the UI site. This must only be called from
        :py:meth:`~.TwistedSite._setup_klein`.

        :param app: the parent Site class
        :type app: :py:class:`~.GW2CopilotSite`
        :param parent_server: parent TwisterServer instance
        :type parent_server: :py:class:`~.TwistedServer` instance
        """
        logger.debug('Initializing API')
        self.parent_server = parent_server
        self._resource = None
        self._tmpl_env = Environment(
            loader=PackageLoader('gw2copilot', 'templates'),
            extensions=['jinja2.ext.loopcontrols']
        )
        self._add_routes()

    @property
    def resource(self):
        """
        Return the Twisted resource for the Klein app.

        :return: Twisted site resource for Klein app.
        :rtype: klein.resource.KleinResource
        """
        if self._resource is None:
            self._resource = self.app.resource()
        return self._resource

    def _render_template(self, tmpl_name, request, **kwargs):
        """
        Render a Jinja2 template of the given name (passed as argument to
        :py:meth:`jinja2.Environment.get_template`) with the
        specified kwargs (passed as kwargs to :py:meth:`jinja2.Template.render`)

        :param tmpl_name: name of the template to render
        :type tmpl_name: str
        :param request: incoming HTTP request
        :type request: :py:class:`twisted.web.server.Request`
        :param kwargs: kwargs to pass to Jinja2 template render method
        :type kwargs: dict
        :return: rendered template string
        :rtype: str
        """
        tmpl = self._tmpl_env.get_template(tmpl_name)
        kwargs['VERSION'] = VERSION
        kwargs['PROJECT_URL'] = PROJECT_URL
        kwargs['ws_port'] = self.parent_server.ws_port
        rendered = tmpl.render(**kwargs)
        return rendered

    @classroute('static/', branch=True)
    def static_files(self, request):
        """
        Meta-endpoint for serving static files from the ``static/`` directory.

        This serves the ``/static/`` endpoint via
        :py:class:twisted.web.static.File`

        :param request: incoming HTTP request
        :type request: :py:class:`twisted.web.server.Request`
        :return: Twisted File resource
        :rtype: twisted.web.static.File
        """
        log_request(request)
        path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'static'
        )
        set_headers(request)
        return File(path)

    @classroute('status')
    def status(self, request):
        """
        Generate the end-user Status page.

        This serves the ``/status`` UI page.

        :param request: incoming HTTP request
        :type request: :py:class:`twisted.web.server.Request`
        :return: HTML output
        :rtype: str
        """
        log_request(request)
        set_headers(request)
        statuscode = OK
        msg = make_response('OK')
        request.setResponseCode(statuscode, message=msg)
        mumble_dt = self.parent_server.mumble_update_datetime
        mumble_td = (datetime.now() - mumble_dt)
        if mumble_td < timedelta(seconds=4):
            mumble_td = 'less than 4 seconds'
        return make_response(
            self._render_template(
                'status.html',
                request,
                playerinfo=json.dumps(
                    self.parent_server.playerinfo.as_dict,
                    sort_keys=True, indent=4, separators=(',', ': ')
                ),
                mumble_data=json.dumps(
                    self.parent_server.raw_mumble_link_data,
                    sort_keys=True, indent=4, separators=(',', ': ')
                ),
                mumble_time=mumble_dt,
                mumble_td=mumble_td
            )
        )

    @classroute('/')
    def homepage(self, request):
        """
        Generate the end-user landing ("Home") page.

        This serves the ``/`` UI page.

        :param request: incoming HTTP request
        :type request: :py:class:`twisted.web.server.Request`
        :return: HTML output
        :rtype: str
        """
        log_request(request)
        set_headers(request)
        statuscode = OK
        msg = make_response('OK')
        request.setResponseCode(statuscode, message=msg)
        return make_response(
            self._render_template(
                'index.html',
                request
            )
        )

    @classroute('live')
    def livedata(self, request):
        """
        Generate the end-user "Live" page.

        This serves the ``/live`` UI page.

        :param request: incoming HTTP request
        :type request: :py:class:`twisted.web.server.Request`
        :return: HTML output
        :rtype: str
        """
        log_request(request)
        set_headers(request)
        statuscode = OK
        msg = make_response('OK')
        request.setResponseCode(statuscode, message=msg)
        return make_response(
            self._render_template(
                'live.html',
                request,
                playerinfo=self.parent_server.playerinfo.as_dict
            )
        )

    @classroute('crafting')
    def crafting(self, request):
        """
        Generate the end-user "Crafting" page.

        This serves the ``/crafting`` UI page.

        :param request: incoming HTTP request
        :type request: :py:class:`twisted.web.server.Request`
        :return: HTML output
        :rtype: str
        """
        log_request(request)
        set_headers(request)
        statuscode = OK
        msg = make_response('OK')
        request.setResponseCode(statuscode, message=msg)
        return make_response(
            self._render_template(
                'crafting.html',
                request
            )
        )

    @classroute('help')
    def help_page(self, request):
        """
        Generate the end-user "Help" page.

        This serves the ``/help`` UI page.

        :param request: incoming HTTP request
        :type request: :py:class:`twisted.web.server.Request`
        :return: HTML output
        :rtype: str
        """
        log_request(request)
        set_headers(request)
        statuscode = OK
        msg = make_response('OK')
        request.setResponseCode(statuscode, message=msg)
        return make_response(
            self._render_template(
                'help.html',
                request
            )
        )