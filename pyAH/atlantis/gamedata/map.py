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
    
Main class defined in this module is
:class:`~atlantis.gamedata.map.Map`, the class that holds data from
all map levels and handle all the internals of map viewing logic. Other
classes are :class:`~atlantis.gamedata.map.MapLevel` and
:class:`~atlantis.gamedata.map.MapHex`. All classes implement
:class:`~atlantis.helper.json.JsonSerializable` and
:class:`~atlantis.helper.comparable.RichComparable` interfaces.

"""

from atlantis.gamedata.region import Region

from atlantis.helpers.json import JsonSerializable
from atlantis.helpers.comparable import RichComparable # For testing

HEX_EXITS, HEX_OLD, HEX_CURRENT = range(3)

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
    
    :class:`~atlantis.gamedata.map.MapLevel` has the following public
    attributes:
    
    .. attribute:: name
    
       Name of the level.
    
    .. attribute:: hexes
    
       Dictionary of :class:`~atlantis.gamedata.map.MapHex` objects.
       
    :class:`.MapLevel` defines an iterator on its hexes. So hexes on
    :class:`!MapLevel` instance lvl can be accessed by::
    
        for h in lvl:
            print(h.status)
    
    """
    
    def __init__(self, name):
        """Create an empty :class:`~atlantis.gamedata.map.MapLevel`."""
        self.name = name
        self.hexes = dict()
        
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
        
        lvl = map_hex.region.location[2]
        if not lvl:
            lvl = 'surface'
        if lvl == self.name:
            self.hexes[tuple(map_hex.region.location[:2])] = map_hex
        else:
            raise KeyError('wrong level')
            
    def get_region(self, location):
        """Get a region from the level.
        
        This methods searches the map for the hex at location.
        
        :param location: Two elements tuple with the location of the
            region in the level.
        :return: the :class:`~atlantis.gamedata.map.MapHex` object, or
            *None* if the region is not in not in the map.
        
        """
        
        location = tuple(location)
        if location in self.hexes:
            return self.hexes[location]
        else:
            return None
    
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