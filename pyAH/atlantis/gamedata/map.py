"""This module implements an Atlantis game map.

An Atlantis map is made of several map levels. It's convenient having
several 2D levels than having a 3D map as actually 2D maps will be
shown to the user and the world is not a real 3D workd, but several
2D levels connected by shafts.

Data from the map hexes can come from various sources, and depending
on the source the hex is in different states. Data can come from:

- Visited hexagons
    Map will have complete information about their inhabitants,
    markets, production, etc.
- Passed through hexagons
    Depending on the game can have the same information than visited
    hexes, but units information. Hexes are classified depending on
    its information, so *passed* hexes doesn't exist.
- Exits report hexagons
    Hexes adjacents to visited hexes are shown in their *exits* report.
    These reports has information about the region name, type, and
    towns in the hex.
- Battle report hexagons
    When a battle takes place a small report of the hex with his type
    is given. This report won't be used because before having a battle
    in an hex a *visited* hexagon report will have been received.
    
In addition map data is hold from turn to turn, so old data can be
shown from previous turns. Preference when showing hex information
will be:

#. Battle report
    This won't actually be used.

#. Exits report
    Information in exits report is immutable, so there's no need to
    make any difference between old and current information. Old
    information is just passed from turn to turn.

#. Old visited reports
    Information in old reports is used if no current information
    exists. Some information can be changed due to hex development,
    pillage, structures built and so on.

#. Visited hex reports
    This is the preferred view of an hex. If complete reports are
    received from passed through hexes then a report of units existing
    last time the hex was visited can be optionally given.
    
Because of that :mod:`atlantis.gamedata.map` declares the following
constant values:

.. attribute:: HEX_EXITS

   For data coming from an exits report.

.. attribute:: HEX_OLD

   For data coming from an old region report.

.. attribute:: HEX_CURRENT

   For data coming from a current report.

.. attribute:: SEEN_CURRENT

   Used for ``when`` attributes when info is current.
   
.. attribute:: LEVEL_NEXUS

   Level type for ``nexus`` levels. Only one ``nexus`` level exist.

.. attribute:: LEVEL_SURFACE

   Level type for ``surface`` levels. Only one ``surface`` level exists.

.. attribute:: LEVEL_UNDERWORLD

   Level type for ``underworld`` levels.

.. attribute:: LEVEL_UNDERDEEP

   Level type for ``underdeep`` levels.

.. attribute:: LEVEL_ABYSS

   Level type for ``abyss` levels. Only one ``abyss`` level exists.
    
Main class defined in this module is
:class:`~atlantis.gamedata.map.Map`, the class that holds data from
all map levels and handle all the internals of map viewing logic. Other
classes are :class:`~atlantis.gamedata.map.MapLevel` and
:class:`~atlantis.gamedata.map.MapHex`. All classes implement
:class:`~atlantis.helper.json.JsonSerializable` and
:class:`~atlantis.helper.comparable.RichComparable` interfaces.

"""

from atlantis.gamedata.region import Region
from atlantis.gamedata.rules import DIR_NORTH, DIR_NORTHEAST, DIR_SOUTHEAST, \
    DIR_SOUTH, DIR_SOUTHWEST, DIR_NORTHWEST

from atlantis.helpers.json import JsonSerializable
from atlantis.helpers.comparable import RichComparable # For testing

import re

HEX_EXITS, HEX_OLD, HEX_CURRENT = range(3)

LEVEL_NEXUS, LEVEL_SURFACE, LEVEL_UNDERWORLD, LEVEL_UNDERDEEP, LEVEL_ABYSS = \
    range(5)

SEEN_CURRENT = (0, 0)

#from atlantis.gamedata.region import Region

class MapHex(JsonSerializable, RichComparable):
    """Holds the information of an hex in Atlantis PBEM map.
    
    :class:`~atlantis.gamedata.map.MapHex` differs from
    :class:`atlantis.gamedata.region.Region` in which
    :class:`!Region` hold information read current turn from report,
    while :class:`!MapHex` holds some more information about the actual
    status of the information: is it old information? which turn was
    the information reported? etc. 
    
    :class:`~atlantis.gamedata.map.MapHex` has the following public
    attributes:
    
    .. attribute:: region
    
       A :class:`atlantis.gamedata.region.Region` object with region
       information.
    
    .. attribute:: status
    
       Status of the information.
    
    .. attribute:: last_seen
    
       Turn in which current map hex information is received. It is a
       tuple with year and month. First turn is ``(1, 1)``. There is a
       special value ``SEEN_CURRENT``. 
    
    """
    def __init__(self, region, status, last_seen=SEEN_CURRENT):
        """Create a :class:`MapHex` object.
        
        :param region: :class:`atlantis.gamedata.region.Region` object.
        :param status: status of the information. Can be ``HEX_EXITS``,
            ``HEX_OLD`` or ``HEX_CURRENT``.
        :param last_seen: turn in which the information was received as
            a (*year*, *month*) tuple. Special value ``SEEN_CURRENT`` is   
            also allowed.
        
        """
            
        self.region = region
        self.status = status
        self.last_seen = tuple(last_seen)
    
    def get_region_info(self):
        """Return the :class:`atlantis.gamedata.region.Region` object.
        
        :return: :class:`atlantis.gamedata.region.Region` stored in the
            :class:`~atlantis.gamedasta.map.MapHex`.
        
        """
        return self.region
    
    def get_last_seen(self):
        """Return when the region was last seen.
        
        :return: last turn when the region was seen as a tuple with
            *year* and *month* of that turn, or the special value
            ``SEEN_CURRENT`` if it has been seen current turn.
        
        """
        
        return self.last_seen
    
    def is_complete(self):
        """Check if stored information is complete.
        
        :return: *True* if information is complete (the hex has been
            visited), *False* if it's incomplete (from exits info from
            another hex).
            
        """
        
        if self.status in (HEX_CURRENT, HEX_OLD):
            return True
        else:
            return False
    
    def is_current(self):
        """Check if stored information if current or old.
        
        :return: *True* if information is fresh (from current turn),
            and *False* if it's from a previous turn.
        
        """
        
        if self.status == HEX_CURRENT:
            return True
        else:
            return False
    
    # JsonSerializable methods
    def json_serialize(self):
        """Return a serializable version of :class:`MapHex`.
        
        :return: a *dict* representing the :class:`MapHex` object.
        
        .. seealso::
           :meth:`JsonSerializable.json_serialize`
        
        """
        return {'status': self.status, 'last_seen': self.last_seen,
                'region': self.region.json_serialize()}
    
    @staticmethod
    def json_deserialize(json_object):
        """Load :class:`MapHex` from a deserialized json object.

        :param json_object: object returned by :func:`json.load`.
        
        :return: the :class:`MapHex` object from json data.
        
        .. seealso::
           :meth:`JsonSerializable.json_deserialize`
        
        """
        mh = MapHex(Region.json_deserialize(json_object['region']),
                    json_object['status'], json_object['last_seen'])
        return mh

class MapLevel(JsonSerializable, RichComparable):
    """Holds the information of a level in Atlantis PBEM map.
    
    Each level is made of a list of regions (hexes) and the name of
    the level. Level names as follow (from higher to deeper):
    
    #. nexus
    
    #. surface
    
    #. underworld
        if several underworld levels exist then they are named
        ``underworld``, ``deep underworld``, ``very deep underworld``,
        ``very very deep underworld`` and so on.
    
    #. underdeep
        if several underdeep levels exist then they are named
        ``underdeep``, ``deep underdeep``, ``very deep underdeep``,
        ``very very deep underdeep`` and so on.
    
    #. abyss
        abyss is a special level below underdeep.
    
    :class:`~atlantis.gamedata.map.MapLevel` has the following public
    attributes:
    
    .. attribute:: name
    
       Name of the level.
    
    .. attribute:: hexes
    
       Dictionary of :class:`~atlantis.gamedata.map.MapHex` objects.
    
    .. attribute:: level_type
    
       Tuple with two values, level type (from ``nexus`` to ``abyss``)
       and level depth.
       
    :class:`.MapLevel` defines an iterator on its hexes. So hexes on
    :class:`!MapLevel` instance lvl can be accessed by::
    
        for h in lvl:
            print(h.status)
    
    """
    
    def __init__(self, name):
        """Create an empty :class:`~atlantis.gamedata.map.MapLevel`.
        
        :param name: name of the level.
        
        :raise: :class:`KeyError` if *name* is not a valid level name.
        
        """
        if not re.match(
                r'(very )*(deep )?(underworld|underdeep)|nexus|surface|abyss',
                name):
            raise KeyError('{}: invalid level name'.format(name))
            
        self.name = name
        self.hexes = dict()
        
        if name == 'nexus':
            level_type = LEVEL_NEXUS
            level_deep = 0
        elif name == 'surface':
            level_type = LEVEL_SURFACE
            level_deep = 0
        elif name.endswith('underworld'):
            level_type = LEVEL_UNDERWORLD
            dummy = name.split(' ')
            level_deep = len(dummy) - 1
        elif name.endswith('underdeep'):
            level_type = LEVEL_UNDERDEEP
            dummy = name.split(' ')
            level_deep = len(dummy) - 1
        else:
            level_type = LEVEL_ABYSS
            level_deep = 0
        
        self.level_type = (level_type, level_deep)
        self._hex_rect = None
        
    def __iter__(self):
        """Iterate level hexes."""
        for h in self.hexes.values():
            yield h
    
    def set_region(self, map_hex):
        """Set a region in the level.
        
        This method adds new region information to the level.
        
        :param region: :class:`~atlantis.gamedata.map.MapHex` data
            to be added to the level.
            
        :raise: :class:`KeyError` if region does not belong to this
            level. 
            
        """
        
        x, y, lvl = map_hex.region.location
        if not lvl:
            lvl = 'surface'
        if lvl == self.name:
            self.hexes[(x, y)] = map_hex
        else:
            raise KeyError('region level {} does not match level name {}'.
                           format(lvl, self.name))
            
    def get_region(self, location):
        """Get a region from the level.
        
        This methods searches the map for the hex at location.
        
        :param location: two elements tuple with the location of the
            region in the level.
        :return: the :class:`~atlantis.gamedata.map.MapHex` object, or
            *None* if the region is not in not in the map.
        
        """
        
        location = tuple(location)
        if location in self.hexes:
            return self.hexes[location]
        else:
            return None
    
    def get_type(self):
        """Get level type.
        
        Return the level type.
        
        :return: level type. It will be one of ``LEVEL_NEXUS``,
            ``LEVEL_SURFACE``, ``LEVEL_UNDERWORLD``, ``LEVEL_UNDERDEEP``
            and ``LEVEL_ABYSS``.
            
        """
        return self.level_type[0]

    def get_depth(self):
        """Get level depth.
        
        Return level depth, relative to its type. So first underworld
        level will return a depth of 0, not 2.
        
        :return: depth of the level relative to its type.
        
        """
        return self.level_type[1]
    
    def get_rect(self):
        """Get map level rect.
        
        Return a four elements tuple determining the rectangle which
        encloses all known regions in the level. First two elements are
        the upper left corner (x, y), and the last two elements the
        lower right corner (x, y).
        
        The enclosing rectangle is computed following Atlantis PBEM.
        Particularly, it takes in account that surface sizes are always
        multiple of eight, underworld multiple of four, underdeep and
        nexus multiple of two, and abyss is always four hexes width and
        height.
        
        :return: the four elements tuple which determines level rect.
        
        """
        x = [k[0] for k in self.hexes.keys()]
        x0, x1 = min(x), max(x)
        y = [k[1] for k in self.hexes.keys()]
        y0, y1 = min(y), max(y)
        
        if self.level_type[0] == LEVEL_NEXUS:
            if x1 == 0 and y1 == 0:
                return (0, 0, 0, 0)
            else:
                scale = 2
        elif self.level_type[0] == LEVEL_ABYSS:
            return (0, 0, 3, 3)
        else:
            scale = 2 ** (4 - self.level_type[0])
        
        x0 -= x0 % scale 
        y0 -= y0 % scale
        
        x1 += scale - x1 % scale - 1
        y1 += scale - y1 % scale - 1
        
        return (x0, y0, x1, y1)
    
    def wraps_horizontally(self):
        """Check if the level wraps horizontally.
        
        :return: *True* if the level wraps horizontally, *False*
            otherwise.
        
        """
        x0, y0, x1, y1 = self.get_rect()
        if x0 == 0:
            left_border = [h.region for k, h in self.hexes.items() if h.status in (HEX_CURRENT, HEX_OLD) and k[0] == x0]
            for r in left_border:
                for direction in (DIR_NORTHWEST, DIR_SOUTHWEST):
                    if direction in r.exits and r.exits[direction][0] == x1:
                        return True
        right_border = [h.region for k, h in self.hexes.items() if h.status in (HEX_CURRENT, HEX_OLD) and k[0] == x1]
        for r in right_border:
            for direction in (DIR_NORTHEAST, DIR_SOUTHEAST):
                if direction in r.exits and r.exits[direction][0] == x0:
                    return True
        return False
            
    
    def wraps_vertically(self):
        """Check if the level wraps vertically.
        
        :return: *True* if the level wraps vertically, *False*
            otherwise.
        
        """
        return False
        
    
    # JsonSerializable methods
    def json_serialize(self):
        """Return a serializable version of :class:`MapLevel`.
        
        :return: a *dict* representing the :class:`MapLevel` object.
        
        .. seealso::
           :meth:`JsonSerializable.json_serialize`
        
        """
        return {'name': self.name,
                'hexes': [ob.json_serialize() \
                          for ob in self.hexes.values()]}
    
    @staticmethod
    def json_deserialize(json_object):
        """Load :class:`MapLevel` from a deserialized json object.

        :param json_object: object returned by :func:`json.load`.
        
        :return: the :class:`MapLevel` object from json data.
        
        .. seealso::
           :meth:`JsonSerializable.json_deserialize`
        
        """
        ml = MapLevel(json_object['name'])
        ml.hexes = dict([(tuple(mh.region.location[:2]), mh) \
                         for mh in \
                            [MapHex.json_deserialize(ob) \
                             for ob in json_object['hexes']]])
        return ml

class Map(JsonSerializable, RichComparable):
    """Holds all data of Atlantis PBEM map.
    
    This class holds all data of an Atlantis PBEM map. Hexes (regions)
    are organized in levels, and :class:`!Map` stores a dictionary of
    levels.
    
    This class also holds all the logic related to Atlantis map
    handling. It is in charge of keeping information about from turn
    to turn, handling priority between different sources of information
    and so on.
    
    :class:`~atlantis.gamedata.map.Map` has the following public
    attributes:
    
    .. attribute:: levels
    
       Dictionary with all levels in the map.
    
    """
    
    def __init__(self):
        """Create an empty map."""
        self.levels = dict()
    
    def add_region_info(self, region, source=HEX_CURRENT):
        """Add a region to the map.
        
        This method adds new region information to the map. Actually
        it doesn't add always the region, but looks for it in its
        regions dictionary and updates its data if needed.
        
        :param region: :class:`~atlantis.gamedata.region.Region` data
            to be added to the map.
        :param source: source of the information. Valid values are
            ``HEX_CURRENT`` and ``HEX_EXITS``.
        
        """

        if source == HEX_CURRENT or not self.get_region(region.location):
            self.set_region(MapHex(region, source))
            
    def set_region(self, map_hex):
        """Set a region in the map.
        
        This method add new region information to the map.
        
        :param region: :class:`~atlantis.gamedata.map.MapHex` data
            to be added to the map.
        
        """
        
        lvl = self.get_level(map_hex.region.location[2])
        lvl.set_region(map_hex)
            
    def get_region(self, location):
        """Get a region from the map.
        
        This methods searches the map for the hex at location.
        
        :param location: Three elements tuple with the location of the
            region.
        :return: the :class:`~atlantis.gamedata.map.MapHex` object, or
            *None* if the region is not in not in the map.
        
        """
        
        lvl = self.get_level(location[2], False)
        if lvl:
            return lvl.get_region(location[:2])
        else:
            return None
    
    def get_level(self, level_name, create=True):
        """Get a level from the map.
        
        This method search for a map level and returns it. The create
        parameter can be set to *True* if we want the level to be
        created if it doesn't exist.
        
        :param level_name: name of the *level*. If it's *None* then
            surface is assumed.
        :param create: if *True* the level will be created if it
            doesn't exist.
        :return: the :class:`~atlantis.gamedata.map.MapLevel` object.
        
        """
        
        if not level_name:
            level_name = 'surface'
            
        if level_name not in self.levels.keys():
            self.levels[level_name] = MapLevel(level_name)
            
        return self.levels[level_name]
    
    # JsonSerializable methods
    def json_serialize(self):
        """Return a serializable version of :class:`Map`.
        
        :return: a *dict* representing the :class:`Map` object.
        
        .. seealso::
           :meth:`JsonSerializable.json_serialize`
        
        """
        return {'levels': dict([(k, level.json_serialize()) \
                                for k, level in self.levels.items()])}
    
    @staticmethod
    def json_deserialize(json_object):
        """Load :class:`Map` from a deserialized json object.

        :param json_object: object returned by :func:`json.load`.
        
        :return: the :class:`Map` object from json data.
        
        .. seealso::
           :meth:`JsonSerializable.json_deserialize`
        
        """
        m = Map()
        m.levels = dict([(k, MapLevel.json_deserialize(ob)) \
                         for (k, ob) in json_object['levels'].items()])
        return m