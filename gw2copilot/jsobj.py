"""
############################
Vendored in; retrieved 2016-11-20 from
https://github.com/darkf/py-js-object-parser/blob/master/jsobj.py
as of f73c2e711ab45d5e051611b2eb270cf1c8b90dd7

with minor formatting/pep8/pyflakes changes
############################
Simple JavaScript/ECMAScript object literal reader

Only supports object literals wrapped in `var x = ...;` statements, so you
  might want to do read_js_object('var x = %s;' % literal) if it's in another format.

If you pass in the keyword argument use_unicode it will decode
utf8 as well as unicode code points into python unicode
strings

Requires the slimit <https://github.com/rspivak/slimit> library for parsing.

Basic constand folding on strings and numbers is done, e.g. "hi " + "there!" reduces to "hi there!",
and 1+1 reduces to 2.

Copyright (c) 2013 darkf
Licensed under the terms of the WTFPL:

    DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
                    Version 2, December 2004

    Everyone is permitted to copy and distribute verbatim or modified
    copies of this license document, and changing it is allowed as long
    as the name is changed.

               DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
      TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

      0. You just DO WHAT THE FUCK YOU WANT TO.

"""

from slimit.parser import Parser
import slimit.ast as ast
import re

unicodepoint = re.compile('\\\\u([0-9a-fA-F]{4})')


def unicode_replace(match):
    return unichr(int(match.group(1),16))


def read_js_object(code, use_unicode=False):
    """Takes in code and returns a dictionary of assignments to object literals, e.g.
        `var x = {y: 1, z: 2};`
        returns {'x': {'y': 1, 'z': 2}}."""
    def visit(node):
        if isinstance(node, ast.Program):
            d = {}
            for child in node:
                if not isinstance(child, ast.VarStatement):
                    raise ValueError("All statements should be var statements")
                key, val = visit(child)
                d[key] = val
            return d
        elif isinstance(node, ast.VarStatement):
            return visit(node.children()[0])
        elif isinstance(node, ast.VarDecl):
            return visit(node.identifier), visit(node.initializer)
        elif isinstance(node, ast.Object):
            d = {}
            for prop in node:
                key = visit(prop.left)
                value = visit(prop.right)
                d[key] = value
            return d
        elif isinstance(node, ast.BinOp):
            # simple constant folding
            if node.op == '+':
                if (isinstance(node.left, ast.String) and
                        isinstance(node.right, ast.String)):
                    return visit(node.left) + visit(node.right)
                elif (isinstance(node.left, ast.Number) and
                        isinstance(node.right, ast.Number)):
                    return visit(node.left) + visit(node.right)
                else:
                    raise ValueError(
                        'Cannot + on anything other than two literals')
            else:
                raise ValueError("Cannot do operator '%s'" % node.op)
        elif isinstance(node, ast.String):
            s = node.value.strip('"').strip("'")
            if use_unicode:
                us = s.decode('utf8')
                return unicodepoint.sub(unicode_replace, us)
            else:
                return s
        elif isinstance(node, ast.Array):
            return [visit(x) for x in node]
        elif isinstance(node, ast.Number):
            try:
                i = int(node.value)
                if node.value == '%d' % i:
                    return i
            except Exception:
                pass
            return float(node.value)
        elif isinstance(node, ast.Boolean):
            # properly handle boolean
            if node.value.lower().startswith('t'):
                return True
            return False
        elif isinstance(node, ast.Null):
            # properly handle null -> None
            return None
        elif isinstance(node, ast.Identifier):
            return node.value
        else:
            raise Exception("Unhandled node: %r" % node)
    return visit(Parser().parse(code))
