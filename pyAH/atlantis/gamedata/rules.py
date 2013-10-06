"""Handles Atlantis PBEM world rules.

Most of these rules can be guessed from Atlantis game manual. Main goal
of this module, however, is having a set of standard rules written from
Atlantis PBEM source code, written in json files, and allowing players
to edit this data to accommodate it to actual rules.

"""

from atlantis.helpers.json import json_load_list
from atlantis.helpers.json import json_load_dict
from atlantis.helpers.json import JsonSerializable
from atlantis.helpers.comparable import RichComparable # For testing

import os.path
    
class TerrainType(JsonSerializable, RichComparable):
    """Handles different terrain types (swamps, woods, etc).
    
    """
    name = None
    """Terrain type name."""
    
    riding_mounts = False
    """Flag if riding mounts get combat bonus."""
    
    flying_mounts = False
    """Flag if flying mounts get combat bonus."""
    
    products = None
    """List of products available, as a dictionary with *chance*,
    *amount* and *product* (item abbreviature)."""
    
    normal_races = None
    """List of races that can be found in this terrain as item abbr."""
    
    coastal_races = None
    """List of races that can be found in this terrain when it's
    coastal, as item abbr."""
    
    def __init__(self,
                  name=None, riding_mounts=False,
                  flying_mounts=False, products=None,
                  normal_races=None, coastal_races=None):
        """Default constructor.
        
        This is the default constructor used when we want to
        instantiate :class:`TerrainType` from its former data.
        
        :param name: terrain type name.
        :param riding_mounts: flag if riding mounts give combat bonus.
        :param flying_mounts: flag if flying mounts give combat bonus.
        :param products: list of products available, as a dictionary
            with *chance*, *amount* and *product* (item abbreviature).
        :param normal_races: list of races that can be found in this
            terrain type as item abbreviatures.
        :param coastal_races: list of races that can be found in this
            terrain type when it's coastal, as item abbreviatures.
        
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
           :meth:`JsonSerializable.json_serialize`
        
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
           :meth:`JsonSerializable.json_deserialize`
        
        """
        return TerrainType(**json_object)


class AtlantisRules(JsonSerializable, RichComparable):
    """Handles Atlantis PBEM basic rules.
    
    Atlantis PBEM rules are those static elements in the game that
    usually can be guessed from *rules* web page.
    
    Some of this information can be completed by turn reports. Mainly
    discovered skills, items and objects reports will complete
    rules information. Other information can be terrain types stats
    (movement cost, available products, etc).
    
    """
    
    terrain_types = None
    """List of :class:`TerrainType` definitions."""
    
    def __init__(self, json_data=None):
        """:class:`AtlantisRules` constructor.
        
        The constructor can be used as an empty constructor, or may
        receive data from :meth:`~AtlantisRules.json_deserialize`.
        
        :param json_data: dictionary with object data from json file.
        
        """
        if json_data:
            if 'terrain_types' in json_data.keys():
                self.terrain_types = dict(
                        [(ob['name'], TerrainType.json_deserialize(ob)) \
                         for ob in json_data['terrain_types']])
    
    def json_serialize(self):
        """Return a serializable version of :class:`AtlantisRules`.
        
        :return: a *dict* representing the :class:`AtlantisRules`
            object.
        
        .. seealso::
           :meth:`JsonSerializable.json_serialize`
        
        """
        json_object = dict()
        if self.terrain_types:
            json_object['terrain_types'] = \
                    [t.json_serialize() for t in self.terrain_types.values()]
        return json_object
    
    @staticmethod
    def json_deserialize(json_object):
        """Load :class:`AtlantisRules` from a deserialized json object.

        :param json_object: object returned by :func:`json.load`.
        
        :return: the :class:`AtlantisRules` object from json data.
        
        .. seealso::
           :meth:`JsonSerializable.json_deserialize`
        
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
        
        with open(os.path.join(folder_name, 'strings.json')) as f:
            ar.strings = json_load_dict(f)
        
        with open(os.path.join(folder_name, 'gui_colors.json')) as f:
            ar.gui_colors = json_load_dict(f)
        
        return ar
        
if __name__ == '__main__':
    import json
    
    ar = AtlantisRules.read_folder('../../rulesets/havilah_1.0.0')
    for t in ar.terrain_types:
        print(t.name, t.products, t.normal_races)
    print(ar.strings)
    
    with open('../../rulesets/havilah_1.0.0.json') as f:
        ar = AtlantisRules.json_deserialize(json.load(f))
        print(len(ar.terrain_types))
        for t in ar.terrain_types.values():
            print(t.name, t.products, t.normal_races)