gw2_helper_python
=================

A Python-based GuildWars2 helper tool.

Overview
--------

gw2_helper_python is a browser-based "helper" for Guild Wars 2, developed for either native Windows or Wine/PlayOnLinux. It interfaces with both the official ArenaNet GuildWars ReST API (for both general information and account-specific data) and also makes use of the [MumbleLink](https://wiki.guildwars2.com/wiki/API:MumbleLink) memory-mapped file to retrieve realtime character location from the game.

This aims to automate manual tasks that players currently perform, including looking up zone maps online, tracking ToDo's, etc.

This project is _not_ a game overlay; its runs as a standalone webserver, intended to display data in a browser on a second monitor. It also does not, and will not, incorporate anything that violates the User Agreement or Rules of Conduct; aside from the documented [ReST APIs](https://wiki.guildwars2.com/wiki/API:Main) which it uses to communicate with ArenaNet servers, the only way this software interacts with the game is by reading information from the documented [MumbleLink](https://wiki.guildwars2.com/wiki/API:MumbleLink) memory-mapped file to determine current character and location.

Planned features include:

- Allowing you to store a list of ToDo items/reminders per-zone, and displaying them when you're in that zone.
- Displaying an interactive map of the current zone, including your location.
- Tracking a list of crafting recipes that you want to make, and what materials you have vs still need.

Status
------

This is _very alpha_ software. I wrote it for myself and a small number of friends. If it's useful to you, great, but I don't intend on doing a whole lot of development on it. The codebase is pretty rough, and I'm probably not even going to write tests for it, let alone the rest of what goes along with real released software; sorry, but I have too many personal projects, and I just want the end result of this.

Requirements
------------

* Python 2.7 (for Windows users, get it [here](https://www.python.org/downloads/windows/)) with [pip](https://pip.pypa.io/en/stable/)
* [Guild Wars 2](https://www.guildwars2.com/en/)
* Windows, or Linux and GW2 running via [wine](https://www.winehq.org/) or [PlayOnLinux](https://www.playonlinux.com/en/)
* 

Installation
------------

@TODO this.

If you're running under Linux (wine/PlayOnLinux), you'll also need to install Python2.7 in the same WINEPREFIX as GW2.

1. Download the Windows Python 2.7 installer linked above; GW2 is usually run in a 32-bit WINEPREFIX, so be sure to use the correct installer.
2. Under plain ``wine``, just run the installer with wine. Under PlayOnLinux, click the game in the main PoL dialog and then click "Configure". On the Miscellaneous tab, click "Run a .exe file in this virtual drive" and browse to the Python ``.msi`` installer.
3. Complete the installation with defaults.

Usage
-----

@TODO this.

Internals
---------

Reading the MumbleLink File
---------------------------

If you're running natively under Windows, it simply reads the memory-mapped MumbleLink file.

If you're running under Linux (wine/PoL), it's a bit more complicated and involves some "magic", as the memory-mapped file can only be read by other programs running within the same wine server.

1. Look at the running process list, and attempt to find the ``Gw2.exe`` process.
2. Find the correct WINEPREFIX from ``Gw2.exe``'s environment via the ``/proc`` filesystem.
3. Look for Python2.7 at the default install location of ``WINEPREFIX/drive_c/Python27/python.exe``.
4. Find the correct ``wine`` binary by searching for it using the ``PATH`` of the ``Gw2.exe`` process.
5. Execute a small helper "shim" script, with GW2's ``wine`` binary and environment, that reads the memory-mapped file and writes all changes to it as JSON to STDOUT.
6. The main script reads that process' STDOUT to retrieve the information.

Notes/References/Links
----------------------

* Searching for [MumbleLink in Python code on GitHub](https://github.com/search?l=Python&q=MumbleLink&type=Code&utf8=%E2%9C%93) yields a number of other projects that read the memory-mapped MumbleLink file, including quite a few for GW2.

License and Disclaimer
----------------------

This software is licensed under version 3 of the [GNU Affero GPL](https://www.gnu.org/licenses/agpl-3.0.en.html). The gist is this means you can't build a publicly-accessible service using this code unless you release your complete source code to all of your users under the same license.

This software does not, and will not, violate the Guild Wars 2 [User Agreement](https://www.guildwars2.com/en/legal/guild-wars-2-user-agreement/), [Rules of Conduct](https://www.guildwars2.com/en/legal/guild-wars-2-rules-of-conduct/) or [Terms of Use](https://www.guildwars2.com/en-gb/legal/guild-wars-2-content-terms-of-use/).
