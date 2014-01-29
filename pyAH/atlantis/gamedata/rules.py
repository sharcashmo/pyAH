"""Handles Atlantis PBEM world rules.

Main class in this module is :class:`AtlantisRules`. This class includes
all those immutable data that controls how Atlantis PBEM world behaves
and is shown. :class:`AtlantisRules` doesn't include *real* objects,
even if immutable (as the :class:`~atlantis.gamedata.map.Map`) but it
will hold information about the different :class:`TerrainType`,
:class:`ItemType`, :class:`RaceType` and so on.

Most of this data can be guessed from Atlantis game manual, as the
:class:`RaceType` in the game and which :class:`SkillType` can
specialize each one. Some of this data is hidden, however: advanced
:class:`ItemType` or magic :class:`SkillType` are discovered as the
game advances.

The goal of this module is having a set of standard rules written for
each ruleset stored in json files. Players will be able to easily edit
these json files to incorporate any change introduced by their
gamemaster. The :class:`~atlantis.parsers.reportparser.ReportParser` is
also able to automatically get this information from turn reports,
either to fix any wrong data from ruleset files or incorporate advanced
:class:`ItemType`, :class:`StructureType` or :class:`SkillType` as
they are discovered.

:class:`StructureType` holds data about a type of
:class:`~atlantis.gamedata.structure.Structure`.
While there can be multiple ``mine`` :class:`Structure` objects in the
game, they all have in common the same :class:`StructureType`, ``mine``.

This module also defines the following public attributes:

Directions:

.. attribute:: DIR_NORTH

   north direction.

.. attribute:: DIR_NORTHEAST

   northeast direction.

.. attribute:: DIR_SOUTHEAST

   southeast direction.

.. attribute:: DIR_SOUTH

   south direction.

.. attribute:: DIR_SOUTHWEST

   southwest direction.

.. attribute:: DIR_NORTHWEST

   northwest direction.

Structure types:

.. attribute:: STRUCTURE_BUILDING

   Constant for :class:`StructureType` that are buildings.
   
.. attribute:: STRUCTURE_SHIP

   Constant for :class:`StructureType` that are ships.
   
.. attribute:: STRUCTURE_FLEET

   Constant for :class:`StructureType` that are fleets of ships.
   
"""

from atlantis.helpers.json import json_load_list
from atlantis.helpers.json import json_load_dict
from atlantis.helpers.json import JsonSerializable
from atlantis.helpers.comparable import RichComparable # For testing

import os.path

DIR_NORTH, DIR_NORTHEAST, DIR_SOUTHEAST, \
    DIR_SOUTH, DIR_SOUTHWEST, DIR_NORTHWEST = range(6)

STRUCTURE_BUILDING = 'building'
STRUCTURE_SHIP = 'ship'
STRUCTURE_FLEET = 'group of ships'
    
class TerrainType(JsonSerializable, RichComparable):
    """Handles different terrain types (swamps, woods, etc).
    
    :class:`TerrainType` has the following public attributes:
    
    .. attribute:: name
    
       :class:`TerrainType` name.
    
    .. attribute:: riding_mounts
    
       Flags if riding mounts get combat bonus in :class:`TerrainType`.
    
    .. attribute:: flying_mounts
    
       Flags if flying mounts get combat bonus in :class:`TerrainType`.
    
    .. attribute:: products
    
       List of products available in :class:`TerrainType`, as a
       dictionary with *chance*, *amount* and *product* (item
       abbreviature).
    
    .. attribute:: normal_races
    
       List of races that can be found at :class:`TerrainType` as item
       abbr.
    
    .. attribute:: coastal_races
    
       List of additional races that can be found at coastal
       :class:`TerrainType` as item abbr.
    
    """
    
    def __init__(self,  name=None, riding_mounts=False, flying_mounts=False,
                 products=None, normal_races=None, coastal_races=None):
        """Default constructor.
        
        :param name: :class:`TerrainType` name.
        :param riding_mounts: flag if riding mounts give combat bonus.
        :param flying_mounts: flag if flying mounts give combat bonus.
        :param products: list of products available, as a dictionary
            with *chance*, *amount* and *product* (item abbreviature).
        :param normal_races: list of races that can be found in this
            :class:`TerrainType` as item abbreviatures.
        :param coastal_races: list of races that can be found in this
            :class:`TerrainType` when it's coastal, as item
            abbreviatures.
        
        """
        self.name = name
        self.riding_mounts = riding_mounts
        self.flying_mounts = flying_mounts
        self.products = products
        self.normal_races = normal_races
        self.coastal_races = coastal_races
    
    def json_serialize(self):
        """Return a serializable version of :class:`TerrainType`.
        
        :return: a *dict* representing the :class:`TerrainType` object.
        
        .. seealso::
           :class:`atlantis.helpers.json.JsonSerializable`
        
        """
        return {'name': self.name,
                'riding_mounts': self.riding_mounts,
                'flying_mounts': self.flying_mounts,
                'products': self.products,
                'normal_races': self.normal_races,
                'coastal_races': self.coastal_races}
    
    @staticmethod
    def json_deserialize(json_object):
        """Load :class:`TerrainType` from a deserialized json object.

        :param json_object: object returned by :func:`json.load`.
        
        :return: the :class:`TerrainType` object from json data.
        
        .. seealso::
           :class:`atlantis.helpers.json.JsonSerializable`
        
        """
        return TerrainType(**json_object)
    

class StructureType(JsonSerializable, RichComparable):
    """Hold definition of a structure type.
    
    :class:`StructureType` has the following public attributes:
    
    .. attribute:: name
       
       Name of the :class:`StructureType`. This name is used to identify
       the :class:`StructureType`.
    
    .. attribute:: structuretype
    
       Generic type of the structure. Structure can be a
       ``STRUCTURE_BUILDING``, a ``STRUCTURE_SHIP`` or a
       ``STRUCTURE_FLEET``.
    
    .. attribute:: monster
    
       *True* if it's a monster lair.
    
    .. attribute:: nomonstergrowth
    
       *True* if monsters in this structure won't regenerate.
    
    .. attribute:: protect
    
       number of soldiers the structure can protect.
    
    .. attribute:: defense
    
       defense bonus granted to the soldiers protected by the structure.
       It's a dictionary where keys are the attack types and values the
       bonus granted.
       
    .. attribute:: maxMages
    
       number of mages that can study inside the structure magic skills
       beyond 2nd level.
    
    .. attribute:: specials
    
       list of special effects affected by the structure. Each element
       in the list is a dictionary with two keys:
       
           *specialname*
               name of the special effect affected of the structure.
           *affected*
               if *True*, units inside this structure are affected by
               the special. If *False*, units inside the structure are
               not affected by it.
    .. attribute:: sailors
    
       number of sailors needed to sail the ship. Only for ship
       structures.
    
    .. attribute:: productionAided
    
       *names* string of the item the structure aids to produce.
       *entertainment* is an allowed special value.
    
    .. attribute:: neverdecay
       
       *True* if the structure never decay.
    
    .. attribute:: maxMaintenance
    
       maximum points of damage taken by the structure before it begins
       to decay.
    
    .. attribute:: maxMonthlyDecay

       maximum damage the structure will take per month as decay.
    
    .. attribute:: maintFactor
    
       damage repaired per unit of material used.
    
    .. attribute:: maintItem
    
       *name* string of the item used to repair the structure.
       *wood or stone* is a valid special value.
    
    """
    
    def __init__(self, name, structuretype, monster=False,
                 nomonstergrowth=False, canenter=False, nobuildable=False,
                 protect=None, defense=None, maxMages=None, specials=None,
                 sailors=None, productionAided=None, neverdecay=False,
                 maxMaintenance=None, maxMonthlyDecay=None, maintFactor=None,
                 maintItem=None):
        """Class constructor."""
        
        self.name = name
        self.structuretype = structuretype
        self.monster = monster
        self.nomonstergrowth = nomonstergrowth
        self.canenter = canenter
        self.nobuildable = nobuildable
        self.protect = protect
        self.defense = defense
        self.maxMages = maxMages
        self.specials = specials
        self.sailors = sailors
        self.productionAided = productionAided
        self.neverdecay = neverdecay
        self.maxMaintenance = maxMaintenance
        self.maxMonthlyDecay = maxMonthlyDecay
        self.maintFactor = maintFactor
        self.maintItem = maintItem
    
    # JsonSerializable methods
    def json_serialize(self):
        """Return a serializable version of :class:`StructureType`.
        
        :return: a *dict* representing the :class:`StructureType`
            object.
        
        .. seealso::
           :class:`atlantis.helpers.json.JsonSerializable`
        
        """
        
        json_object = {'name': self.name,
                       'structuretype': self.structuretype,
                       'monster': self.monster,
                       'nomonstergrowth': self.nomonstergrowth,
                       'canenter': self.canenter,
                       'nobuildable': self.nobuildable,
                       'protect': self.protect,
                       'defense': self.defense,
                       'maxMages': self.maxMages,
                       'specials': self.specials,
                       'sailors': self.sailors,
                       'productionAided': self.productionAided,
                       'neverdecay': self.neverdecay,
                       'maxMaintenance': self.maxMaintenance,
                       'maxMonthlyDecay': self.maxMonthlyDecay,
                       'maintFactor': self.maintFactor,
                       'maintItem': self.maintItem}
                
        return json_object
    
    @staticmethod
    def json_deserialize(json_object):
        """Load :class:`StructureType` from a deserialized json object.

        :param json_object: object returned by :func:`json.load`.
        
        :return: the :class:`StructureType` object from json data.
        
        .. seealso::
           :class:`atlantis.helpers.json.JsonSerializable`
        
        """
        
        s = StructureType(**json_object)
        
        return s


class AtlantisRules(JsonSerializable, RichComparable):
    """Handles Atlantis PBEM basic rules.
    
    Atlantis PBEM rules are those static elements in the game that
    usually can be guessed from *rules* web page.
    
    Some of this information can be completed by turn reports. Mainly
    discovered :class:`SkillType`, :class:`ItemType` and
    :class:`StructureType` reports will complete rules information.
    Other information can be :class:`TerrainType` stats (movement cost,
    available products, etc).
    
    :class:`AtlantisRules` has the following public attributes:
    
    .. attribute:: terrain_types
    
       A dictionary TBC.
    
    .. attribute:: strings
    
       A dictionary TBC.
    
    """
    
    def __init__(self, json_data=None):
        """Default constructor.
        
        The constructor can be used as an empty constructor, or may
        receive data from :meth:`~AtlantisRules.json_deserialize`.
        
        :param json_data: dictionary with object data from json file.
        
        """
        
        self.terrain_types = dict()
        self.structures = dict()
        self.strings = dict()
        
        if json_data:
            if 'terrain_types' in json_data.keys():
                self.terrain_types = dict(
                        [(ob['name'], TerrainType.json_deserialize(ob)) \
                         for ob in json_data['terrain_types']])
            if 'structures' in json_data.keys():
                self.structures = dict(
                        [(ob['name'], StructureType.json_deserialize(ob)) \
                         for ob in json_data['structures']])
            if 'strings' in json_data.keys():
                self.strings = json_data['strings']
    
    def get_direction(self, dir_str):
        """Return the direction represented by a string.
        
        Converts a string to the direction it represents.
        
        :param dir_str: direction string.
        
        :return: direction value. It will be a value from ``DIR_NORTH``
            to ``DIR_NORTHWEST``.
        
        :raise: :class:`KeyError` if the string is not a valid
            direction.
        
        """
        for i in range(6):
            if dir_str.lower() in self.strings['directions'][i]:
                return i
        else:
            raise KeyError('{}: bad direction'.format(dir_str))
    
    def json_serialize(self):
        """Return a serializable version of :class:`AtlantisRules`.
        
        :return: a *dict* representing the :class:`AtlantisRules`
            object.
        
        .. seealso::
           :class:`atlantis.helpers.json.JsonSerializable`
        
        """
        json_object = dict()
        
        if self.terrain_types:
            json_object['terrain_types'] = \
                    [t.json_serialize() for t in self.terrain_types.values()]
        
        if self.structures:
            json_object['structures'] = \
                    [s.json_serialize() for s in self.structures.values()]
                    
        if self.strings:
            json_object['strings'] = self.strings
            
        return json_object 
    
    @staticmethod
    def json_deserialize(json_object):
        """Load :class:`AtlantisRules` from a deserialized json object.

        :param json_object: object returned by :func:`json.load`.
        
        :return: the :class:`AtlantisRules` object from json data.
        
        .. seealso::
           :class:`atlantis.helpers.json.JsonSerializable`
        
        """
        return AtlantisRules(json_data=json_object)
    
    @staticmethod
    def read_folder(folder_name):
        """Load :class:`AtlantisRules` from a folder.
        
        This method loads data from a rules folder with the following
        files:
        
        - strings.json
            Basic strings in the game (months, directions, etc).
            
        - terrain_types.json
            Terrain types in the game, with their stats.

        :param folder_name: folder where the files are readed from.
        
        """
        ar = AtlantisRules()
        
        with open(os.path.join(folder_name, 'terrain_types.json')) as f:
            ar.terrain_types = json_load_list(f, TerrainType)
        
        with open(os.path.join(folder_name, 'structures.json')) as f:
            ar.structures = json_load_list(f, StructureType)
        
        with open(os.path.join(folder_name, 'strings.json')) as f:
            ar.strings = json_load_dict(f)
        
        return ar
        
if __name__ == '__main__':
    pass