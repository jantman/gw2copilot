"""
    autoklein

    The sphinx.ext.autodoc-style HTTP API reference builder (from Klein)
    for sphinxcontrib.httpdomain.

    Note this is a custom version for gw2copilot; because of how we use classes
    and ``app`` passing, we can't autodetect Klein apps. So we just directly
    import the ``TwistedServer`` class and call its ``._setup_klein()`` method.

    :copyright: Copyright 2016 by Jason Antman, modified from
      sphinxcontrib.autohttp.flask, Copyright 2011 Hong Minhee
    :license: BSD, see LICENSE for details.

"""

import re
import itertools
import operator

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import ViewList

from sphinx.util import force_decode
from sphinx.util.compat import Directive
from sphinx.util.nodes import nested_parse_with_titles
from sphinx.util.docstrings import prepare_docstring
from sphinx.pycode import ModuleAnalyzer

from sphinxcontrib import httpdomain
from sphinxcontrib.autohttp.common import http_directive

import six
from six.moves import builtins
from six.moves import reduce

from gw2copilot.server import TwistedServer

msg_re = re.compile(
    r'__init__\(\) takes exactly (\d+) arguments \(\d+ given\)'
)


def translate_werkzeug_rule(rule):
    from werkzeug.routing import parse_rule
    buf = six.StringIO()
    for conv, arg, var in parse_rule(rule):
        if conv:
            buf.write('(')
            if conv != 'default':
                buf.write(conv)
                buf.write(':')
            buf.write(var)
            buf.write(')')
        else:
            buf.write(var)
    return buf.getvalue()


def get_routes(app, endpoint=None):
    endpoints = []
    for rule in app.url_map.iter_rules(endpoint):
        if rule.endpoint not in endpoints:
            endpoints.append(rule.endpoint)
    for endpoint in endpoints:
        methodrules = {}
        for rule in app.url_map.iter_rules(endpoint):
            if rule.methods is None:
                # default to GET
                rule.methods = set(['OPTIONS', 'HEAD', 'GET'])
            methods = rule.methods.difference(['OPTIONS', 'HEAD'])
            path = translate_werkzeug_rule(rule.rule)
            for method in methods:
                if method in methodrules:
                    methodrules[method].append(path)
                else:
                    methodrules[method] = [path]
        for method, paths in methodrules.items():
            yield method, paths, endpoint


class AutokleinDirective(Directive):

    has_content = True
    option_spec = {'endpoints': directives.unchanged,
                   'undoc-endpoints': directives.unchanged,
                   'undoc-static': directives.unchanged,
                   'include-empty-docstring': directives.unchanged}

    @property
    def endpoints(self):
        endpoints = self.options.get('endpoints', None)
        if not endpoints:
            return None
        return re.split(r'\s*,\s*', endpoints)

    @property
    def undoc_endpoints(self):
        undoc_endpoints = self.options.get('undoc-endpoints', None)
        if not undoc_endpoints:
            return frozenset()
        return frozenset(re.split(r'\s*,\s*', undoc_endpoints))

    def fix_docstring(self, docstring):
        """
        if <HTTPAPI> is in docstring, only return the docstring from there on
        """
        lines = docstring.split("\n")
        idx = None
        for i, line in enumerate(lines):
           if '<HTTPAPI>' in line:
               idx = i
        if idx is not None:
            del lines[:(idx+1)]
        res = "\n".join(lines)
        return res

    def make_rst(self):
        server = TwistedServer()
        server._setup_klein()
        app = server._app
        if self.endpoints:
            routes = itertools.chain(*[get_routes(app, endpoint)
                    for endpoint in self.endpoints])
        else:
            routes = get_routes(app)
        # sort by path then method
        for method, paths, endpoint in sorted(
                routes, key=operator.itemgetter(1, 0)
        ):
            if endpoint in self.undoc_endpoints:
                continue
            view = app._endpoints[endpoint]
            docstring = view.__doc__ or ''
            if hasattr(view, 'view_class'):
                meth_func = getattr(view.view_class, method.lower(), None)
                if meth_func and meth_func.__doc__:
                    docstring = meth_func.__doc__
            if not isinstance(docstring, six.text_type):
                analyzer = ModuleAnalyzer.for_module(view.__module__)
                docstring = force_decode(docstring, analyzer.encoding)
            if not docstring and 'include-empty-docstring' not in self.options:
                continue
            if '<HTTPAPI>' not in docstring:
                continue
            docstring = self.fix_docstring(docstring)
            docstring = prepare_docstring(docstring)
            for line in http_directive(method, paths, docstring):
                yield line

    def run(self):
        node = nodes.section()
        node.document = self.state.document
        result = ViewList()
        for line in self.make_rst():
            result.append(line, '<autoflask>')
        nested_parse_with_titles(self.state, result, node)
        return node.children


def setup(app):
    if 'http' not in app.domains:
        httpdomain.setup(app)
    app.add_directive('autoklein', AutokleinDirective)
