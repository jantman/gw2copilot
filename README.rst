gw2copilot
=================

.. image:: https://img.shields.io/github/forks/jantman/gw2copilot.svg
   :alt: GitHub Forks
   :target: https://github.com/jantman/gw2copilot/network

.. image:: https://img.shields.io/github/issues/jantman/gw2copilot.svg
   :alt: GitHub Open Issues
   :target: https://github.com/jantman/gw2copilot/issues

.. image:: https://secure.travis-ci.org/jantman/gw2copilot.png?branch=master
   :target: http://travis-ci.org/jantman/gw2copilot
   :alt: travis-ci for master branch

.. image:: https://codecov.io/github/jantman/gw2copilot/coverage.svg?branch=master
   :target: https://codecov.io/github/jantman/gw2copilot?branch=master
   :alt: coverage report for master branch

.. image:: https://readthedocs.org/projects/gw2copilot/badge/?version=latest
   :target: https://readthedocs.org/projects/gw2copilot/?badge=latest
   :alt: sphinx documentation for latest release

.. image:: http://www.repostatus.org/badges/latest/wip.svg
   :alt: Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.
   :target: http://www.repostatus.org/#wip

A Python-based GuildWars2 helper tool.

Overview
--------

gw2copilot is a browser-based "helper" for Guild Wars 2, to automate manual
tasks that players currently perform out of the game.

It is developed for either native Windows or Wine/PlayOnLinux and interfaces with both the official ArenaNet GuildWars ReST API (for both general information and account-specific data) and also makes use of the `MumbleLink <https://wiki.guildwars2.com/wiki/API:MumbleLink>`_ memory-mapped file to retrieve realtime character location from the game.

This aims to automate manual tasks that players currently perform, including looking up zone maps online, tracking ToDo's, etc.

This project is *not* a game overlay; its runs as a standalone webserver, intended to display data in a browser on a second monitor. It also does not, and will not, incorporate anything that violates the User Agreement or Rules of Conduct; aside from the documented `ReST APIs <https://wiki.guildwars2.com/wiki/API:Main>`_ which it uses to communicate with ArenaNet servers, the only way this software interacts with the game is by reading information from the documented `MumbleLink <https://wiki.guildwars2.com/wiki/API:MumbleLink>`_ memory-mapped file to determine current character and location.

Planned features
++++++++++++++++

- Store a list of ToDo items/reminders per-zone, and display them when you're in that zone
- Track zone completion percentages.
- Displaying an interactive map of the current zone, including your location as well as waypoints, POIs, etc (with links to the relevant wiki articles).
- Using manual input (i.e. clicking on hearts/waypoints/etc. that you've already gotten), track what you haven't completed in each zone.
- Possibly showing gathering node locations on the interactive map.
- Tracking a list of crafting recipes that you want to make, and what materials you have vs still need.

Status
------

This is *very alpha* software. I wrote it for myself and a small number of friends. If it's useful to you, great, but I don't intend on doing a whole lot of development on it. The codebase is pretty rough, and I'm probably not even going to write tests for it, let alone the rest of what goes along with real released software; sorry, but I have too many personal projects, and I just want the end result of this.

Note that running natively under Windows is *not currently functional*, as I can't get GW2 to
login under VirtualBox.

Requirements
------------

* Python 2.7 (for Windows users, get it `here <https://www.python.org/downloads/windows/>`_) with `pip <https://pip.pypa.io/en/stable/>`_
* `Guild Wars 2 <https://www.guildwars2.com/en/>`_
* Windows, or Linux and GW2 running via `wine <https://www.winehq.org/>`_ or `PlayOnLinux <https://www.playonlinux.com/en/>`_

Installation
------------

It's recommended that you install into a virtual environment (virtualenv /
venv). See the `virtualenv usage documentation <http://www.virtualenv.org/en/latest/>`_
for information on how to create a venv.

.. code-block:: bash

    pip install git+https://github.com/jantman/gw2copilot.git@master#egg=gw2copilot

If you're running under Linux (wine/PlayOnLinux), you'll also need to install Python2.7 in the same WINEPREFIX as GW2.

1. Download the Windows Python 2.7 installer linked above; GW2 is usually run in a 32-bit WINEPREFIX, so be sure to use the correct installer.
2. Under plain ``wine``, just run the installer with wine. Under PlayOnLinux, click the game in the main PoL dialog and then click "Configure". On the Miscellaneous tab, click "Run a .exe file in this virtual drive" and browse to the Python ``.msi`` installer.
3. Complete the installation with defaults.

Usage
-----

You'll need an `API Key <https://wiki.guildwars2.com/wiki/API:API_key>`_ for the GuildWars2 API;
log in to your account and generate one, and then either export it as the ``GW2_API_KEY`` environment
variable, or pass it via the ``-k`` / ``--api-key`` command line option. The key you generate
must have at least the ``account``, ``characters`` and ``inventories`` permissions. It is recommended
for security that each application you use have its own API key.

@TODO this.

Internals
---------

Dependencies and Thanks
+++++++++++++++++++++++

gw2copilot is built on the shoulders of giants; it makes use of the following Free or Open Source tools:

* `bootstrap <http://getbootstrap.com/>`_ and `html5boilerplate <https://html5boilerplate.com/>`_ for the UI, downloaded via `initizlizr <http://www.initializr.com/>`_, which themselves include `jquery <https://jquery.com/>`_ and `modernizr <https://modernizr.com/>`_.
* The `twisted <https://twistedmatrix.com/>`_ event-based asynchronous framework at the heart of the app (reading the MumbleLink file, serving HTTP and websockets, and timer-based actions).
* The `Klein <https://klein.readthedocs.io/en/latest/>`_ microframework for serving HTTP, with user-oriented pages templated using `Jinja2 <http://jinja.pocoo.org/>`_.
* The python `psutil <https://pythonhosted.org/psutil/>`_ package, which greatly simplifies finding the running GW2 wine environment.
* Crossbar's `autobahn Python <http://crossbar.io/autobahn/>`_ websocket server.
* `leaflet <http://leafletjs.com/>`_ for rendering the interactive maps, greatly helped by the `example on the GW wiki <https://wiki.guildwars2.com/wiki/API:Maps>`_ and `an example from Cliff Spradlin <http://jsfiddle.net/cliff/CRRGC/>`_.

Reading the MumbleLink File
+++++++++++++++++++++++++++

If you're running natively under Windows, it simply reads the memory-mapped MumbleLink file.

If you're running under Linux (wine/PoL), it's a bit more complicated and involves some "magic", as the memory-mapped file can only be read by other programs running within the same wine server.

1. Look at the running process list, and attempt to find the ``Gw2.exe`` process.
2. Find the correct WINEPREFIX from ``Gw2.exe``'s environment via the ``/proc`` filesystem.
3. Look for Python2.7 at the default install location of ``WINEPREFIX/drive_c/Python27/python.exe``.
4. Find the correct ``wine`` binary by searching for it using the ``PATH`` of the ``Gw2.exe`` process.
5. Execute a small helper "shim" script, with GW2's ``wine`` binary and environment, that reads the memory-mapped file and writes all changes to it as JSON to STDOUT.
6. The main script reads that process' STDOUT to retrieve the information.

Bugs and Feature Requests
-------------------------

Bug reports and feature requests are happily accepted via the `GitHub Issue Tracker <https://github.com/jantman/gw2copilot/issues>`_. Pull requests are
welcome. Issues that don't have an accompanying pull request will be worked on
as my time and priority allows.

Development
===========

To install for development:

1. Fork the `gw2copilot <https://github.com/jantman/gw2copilot>`_ repository on GitHub
2. Create a new branch off of master in your fork.

.. code-block:: bash

    $ virtualenv gw2copilot
    $ cd gw2copilot && source bin/activate
    $ pip install -e git+git@github.com:YOURNAME/gw2copilot.git@BRANCHNAME#egg=gw2copilot
    $ cd src/gw2copilot

The git clone you're now in will probably be checked out to a specific commit,
so you may want to ``git checkout BRANCHNAME``.

Guidelines
----------

* pep8 compliant with some exceptions (see pytest.ini)
* 100% test coverage with pytest (with valid tests)

Testing
-------

Testing is done via `pytest <http://pytest.org/latest/>`_, driven by `tox <http://tox.testrun.org/>`_.

* testing is as simple as:

  * ``pip install tox``
  * ``tox``

* If you want to pass additional arguments to pytest, add them to the tox command line after "--". i.e., for verbose pytext output on py27 tests: ``tox -e py27 -- -v``

Release Checklist
-----------------

1. Open an issue for the release; cut a branch off master for that issue.
2. Confirm that there are CHANGES.rst entries for all major changes.
3. Ensure that Travis tests passing in all environments.
4. Ensure that test coverage is no less than the last release (ideally, 100%).
5. Increment the version number in gw2copilot/version.py and add version and release date to CHANGES.rst, then push to GitHub.
6. Confirm that README.rst renders correctly on GitHub.
7. Upload package to testpypi:

   * Make sure your ~/.pypirc file is correct (a repo called ``test`` for https://testpypi.python.org/pypi)
   * ``rm -Rf dist``
   * ``python setup.py register -r https://testpypi.python.org/pypi``
   * ``python setup.py sdist bdist_wheel``
   * ``twine upload -r test dist/*``
   * Check that the README renders at https://testpypi.python.org/pypi/gw2copilot

8. Create a pull request for the release to be merged into master. Upon successful Travis build, merge it.
9. Tag the release in Git, push tag to GitHub:

   * tag the release. for now the message is quite simple: ``git tag -a X.Y.Z -m 'X.Y.Z released YYYY-MM-DD'``
   * push the tag to GitHub: ``git push origin X.Y.Z``

11. Upload package to live pypi:

    * ``twine upload dist/*``

10. make sure any GH issues fixed in the release were closed.

License and Disclaimer
----------------------

This software is licensed under version 3 of the `GNU Affero GPL <https://www.gnu.org/licenses/agpl-3.0.en.html>`_. The gist is this means you can't build a publicly-accessible service using this code unless you release your complete source code to all of your users under the same license.

This software does not, and will not, violate the Guild Wars 2 `User Agreement <https://www.guildwars2.com/en/legal/guild-wars-2-user-agreement/>`_, `Rules of Conduct <https://www.guildwars2.com/en/legal/guild-wars-2-rules-of-conduct/>`_ or `Terms of Use <https://www.guildwars2.com/en-gb/legal/guild-wars-2-content-terms-of-use/>`_.
