"""
setup.py

The latest version of this package is available at:
<https://github.com/jantman/gw2_helper_python>

################################################################################
Copyright 2016 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

    This file is part of gw2_helper_python.

    gw2_helper_python is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    gw2_helper_python is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with gw2_helper_python.  If not, see <http://www.gnu.org/licenses/>.

The Copyright and Authors attributions contained herein may not be removed or
otherwise altered, except to add the Author attribution of a contributor to
this work. (Additional Terms pursuant to Section 7b of the AGPL v3)
################################################################################
While not legally required, I sincerely request that anyone who finds
bugs please submit them at <https://github.com/jantman/gw2_helper_python> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me via email.
################################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
################################################################################
"""

from setuptools import setup, find_packages
from gw2_helper_python.version import VERSION, PROJECT_URL

with open('README.rst') as file:
    long_description = file.read()

"""
requires = [
    'something'
]
"""

classifiers = [
    'Development Status :: 2 - Pre-Alpha',
    'Environment :: Console',
    'Environment :: Web Environment',
    'Framework :: Twisted',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
    'Natural Language :: English',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 2 :: Only',
    # Programming Language :: Python :: 3
    # Programming Language :: Python :: 3.0
    # Programming Language :: Python :: 3.1
    # Programming Language :: Python :: 3.2
    # Programming Language :: Python :: 3.3
    # Programming Language :: Python :: 3.4
    # Programming Language :: Python :: 3.5
    # Programming Language :: Python :: 3.6
    # Programming Language :: Python :: 3 :: Only
    'Programming Language :: Python :: Implementation :: CPython',
    'Topic :: Games/Entertainment'
]

setup(
    name='gw2_helper_python',
    version=VERSION,
    author='Jason Antman',
    author_email='jason@jasonantman.com',
    packages=find_packages(),
    url=PROJECT_URL,
    description='gw2_helper_python is a browser-based "helper" for Guild Wars '
                '2, to automate manual tasks that players currently perform '
                'out of the game.',
    long_description=long_description,
    # install_requires=requires,
    keywords="gw2 guildwars arenanet mumble mumblelink",
    classifiers=classifiers
)