"""
gw2copilot/route_helpers.py

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
from functools import update_wrapper

logger = logging.getLogger(__name__)


def classroute(url, *args, **kwargs):
    """
    Route wrapper for decorating class methods as Klein routes. This works
    around the Python (and Klein) ability to decorate class methods as needed.

    So this decorator sets its parameters as the value of a ``_route_params``
    attribute on the wrapped method (so they can be accessed from the class
    instance) and then sets a ``_wrapped_method`` attribute on the wrapper
    pointing back to the original method.

    For the second half of how this works, see
    :py:meth:`~.ClassRouteMixin._add_routes`.

    :param url: A werkzeug URL pattern given to ``werkzeug.routing.Rule``
    :type url: str
    :param branch: A bool indiciated if a branch endpoint should
        be added that allows all child path segments that don't
        match some other route to be consumed.  Default ``False``.
    :type branch: bool
    :param methods: HTTP methods to add this route for, list of strings
    :type methods: list
    :return: decorated handler function
    """
    def real_decorator(meth):
        meth._route_params = (url, args, kwargs)

        def wrapper(self, request):
            return meth(self, request)

        # since we're wrapping a wrapped method, we need to let
        # ``routable_class`` see the innermost method...
        wrapper._wrapped_method = meth
        # we beed this for sphinx autodoc to work
        return update_wrapper(wrapper, meth)
    return real_decorator


class ClassRouteMixin(object):
    """
    Mixin to add ``_add_routes()`` to Klein server classes.
    """

    _route_prefix = ''

    def _add_routes(self):
        """
        Add routes to the Klein app (``self.app``) for our route-handling
        methods. This is a bit of a hack. See :py:func:`~.classroute` for the
        first half of it.

        This method iterates over all attributes of the class instance
        (``self``) and finds ones which themselves have a ``_wrapped_method``
        attribute (as set by :py:func:`~.classroute`). For each of those, it
        checks the value of ``_wrapped_method`` (the inner, wrapped method; the
        actual class method that was wrapped); if that has a ``_route_params``
        attribute, it calls ``self.addroute`` passing it the ``_wrapped_method``
        and the params.

        The end result of this is that we can add a ``@classroute`` decorator to
        class methods and then this function, called from ``__init__``,
        will setup the routes on the Klein app.
        """
        prefix = self._route_prefix
        if prefix[-1] != '/':
            prefix += '/'
        # iterate all attributes of our class
        for name in dir(self):
            method = getattr(self, name)
            # find only the attributes that themselves have a
            # ``_wrapped_method`` attribute
            if not hasattr(method, '_wrapped_method'):
                continue
            wrapped = method._wrapped_method
            # if the inner (wrapped) method has a ``_route_params`` attribute,
            # add a route for it
            if hasattr(wrapped, '_route_params'):
                params = getattr(wrapped, '_route_params')
                url = params[0]
                if url[0] == '/':
                    url = url[1:]
                url = prefix + url
                args = params[1]
                kwargs = params[2]
                logger.debug('Adding route %s served by %s.%s (args=%s '
                             'kwargs=%s)', url,
                             method.im_self.__class__.__name__,
                             wrapped.func_name, args, kwargs)
                self.app.route(url, *args, **kwargs)(wrapped)
                # do something with the method and class
        logger.debug('Done initializing API')
