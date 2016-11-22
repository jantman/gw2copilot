"""
gw2copilot/static_data.py

This file maintains bits of data that need to be manually-curated.

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

#: Dict mapping map_id to map_name for "normal" world zones that appear on the
#: standard world map.
world_zones = {
    15: "Queensdale",
    17: "Harathi Hinterlands",
    18: "Divinity's Reach",
    19: "Plains of Ashford",
    20: "Blazeridge Steppes",
    21: "Fields of Ruin",
    22: "Fireheart Rise",
    23: "Kessex Hills",
    24: "Gendarran Fields",
    25: "Iron Marches",
    26: "Dredgehaunt Cliffs",
    27: "Lornar's Pass",
    28: "Wayfarer Foothills",
    29: "Timberline Falls",
    30: "Frostgorge Sound",
    31: "Snowden Drifts",
    32: "Diessa Plateau",
    34: "Caledon Forest",
    35: "Metrica Province",
    39: "Mount Maelstrom",
    50: "Lion's Arch",
    51: "Straits of Devastation",
    53: "Sparkfly Fen",
    54: "Brisban Wildlands",
    62: "Cursed Shore",
    65: "Malchor's Leap",
    73: "Bloodtide Coast",
    91: "The Grove",
    139: "Rata Sum",
    218: "Black Citadel",
    326: "Hoelbrak",
    873: "Southsun Cove",
    988: "Dry Top",
    1015: "The Silverwastes",
    1041: "Dragon's Stand",
    1043: "Auric Basin",
    1045: "Tangled Depths",
    1052: "Verdant Brink",
    1165: "Bloodstone Fen",
    1175: "Ember Bay"
}

#: List of Black Lion Trading Posts; each key is an identifier and each value
#: is a coordinate [x, y] list
#: see https://wiki.guildwars2.com/wiki/Trading_Post
trading_posts = {
    'Black Citadel - Memorial Quadrant': [],
    'Divinity\'s Reach - Dwayna High Road': [],
    'Hoelbrak - Trade Commons': [],
    'Lion\'s Arch - Trader\'s Forum': [16103.117606165886,14784.75094229819],
    'Rata Sum - Interdisciplinary Accessium': [],
    'The Grove - Reckoner\'s Terrace': [10432.584755667544,20937.22088452924],
    'Ascalon': [],
    'Diessa Plateau - Town of Nolan': [],
    'Fields of Ruin - Stronghold of Ebonhawke': [],
    'Kryta': [],
    'Queensdale - Altar Brook Trading Post - Jaklan': [],
    'Kessex Hills - Delanian Foothills': [],
    'Gendarran Fields - Traveler\'s Dale - Grietje': [],
    'Harathi Hinterlands - Cloven Hoof Pass - Seraph Sergeant': [],
    'Harathi Hinterlands - Arca Lake - Jadus Phinn': [],
    'Harathi Hinterlands - Nightguard Beach - Debbie Lantys': [],
    'Bloodtide Coast - Portage Hills': [],
    'Maguuma Jungle': [],
    'Mount Maelstrom - Sootberme': [],
    'Ruins of Orr': [],
    'Malchor\'s Leap - Pagga\'s Post': [],
    'Cursed Shore - Pursuit Pass - Elana': [],
    'Shiverpeak Mountains': [],
    'Snowden Drifts - Hunter\'s Pitfalls - Trader Jan and Trader Jed': [],
    'Lornar\'s Pass - Durmand Priory': [],
    'Timberline Falls - Kyesjard': [],
    'Frostgorge Sound - Yakkington\'s Toil': []
}

#: List of Bankers; each key is an identifier and each value
#: is a coordinate [x, y] list
#: see https://wiki.guildwars2.com/wiki/Banker
bankers = {
    '"Wheezy" Teicheria': [],  # Fort Marriner (Lion's Arch)
    'Argeid': [10460.23631961077,21112.515109055323],  # Reckoner's Terrace (The Grove)
    'Banker': [16328.441601395718,14586.077972198487],  # Trader's Forum (Lion's Arch)
    'Banker2': [16342.52235058628,14590.250712594605],  # Trader's Forum (Lion's Arch)
    'Banker Blossri': [],  # Sootberme (Mount Maelstrom)
    'Consortium Banker': [],  # Southsun Shoals (Southsun Cove)
    'Cratus': [],  # Canton Factorium (Black Citadel)
    'Cuina': [],  # Canal Ward (Lion's Arch)
    'Drifa': [],  # Canal Ward (Lion's Arch)
    'Froda': [],  # Hall of Memories (Heart of the Mists)
    'Ikka': [],  # Interdisciplinary Accessium (Rata Sum)
    'Kallin': [],  # Trade Commons (Hoelbrak)
    'Lizette': [],  # Canal Ward (Lion's Arch)
    'Mona': [10471.991963881128,21114.38070884897],  # Reckoner's Terrace (The Grove)
    'Orres': [],  # Canton Factorium (Black Citadel)
    'Randver': [],  # Trade Commons (Hoelbrak)
    'Salanda': [],  # Dwayna High Road (Divinity's Reach)
    'Tekk': [],  # Interdisciplinary Accessium (Rata Sum)
    'Thurmain': [],  # Dwayna High Road (Divinity's Reach)
    'Ubbi Skarsgard': [],  # Stronghold of Ebonhawke (Fields of Ruin)
    'Vaness': [],  # Dwayna High Road (Divinity's Reach)
}
