"""Handles Graphics User Interface theming.

The goal of this package is handle information about how
game data is to be shown by the Graphics User Interface.

"""

from atlantis.helpers.json import json_load_dict
from atlantis.helpers.json import JsonSerializable
from atlantis.helpers.comparable import RichComparable # For testing

import os.path

class Theme(JsonSerializable, RichComparable):
    """Handles GUI theme.
    
    This class holds data about how game data is to be shown by the
    User Interface.
    
    Note that this :class:`Theme` class does nothing about wx (or any
    other graphics library used) objects, but just read and store
    theming parameters as colors and bitmap names.
    
    """
    
    def __init__(self, data_dict=None):
        """:class:`Theme` constructor.
        
        Creates an instance of
        :class:`Theme` using the data provided, if any. Typically
        instances of this class will be created via its static methods
        :meth:`json_deserialize` and :meth:`read_folder`.
        
        :param data_dict: dictionary with configuration data. Typically
            this parameter is used by :meth:`json_deserialize` to
            create the object.
        
        """
        self._base_folder = None
        self._data = data_dict
    
    def get_art_folder(self):
        """Return art folder.
        
        Art folder is the place where bitmaps for the theme are stored.
        It's always an **art** folder within the theme folder.
        
        :return: a string with the complete art folder.
        
        """
        return self._base_folder
    
    def json_serialize(self):
        """Return a serializable version of :class:`Theme`.
        
        :return: a *dict* representing the :class:`Theme` object.
        
        .. seealso::
           :class:`atlantis.helpers.json.JsonSerializable`
        
        """
        return self._data 
    
    @staticmethod
    def json_deserialize(json_object):
        """Load :class:`Theme` from a deserialized json object.

        :param json_object: object returned by
            :func:`atlantis.helpers.json.load`.
        
        :return: the :class:`Theme` object from json data.
        
        .. seealso::
           :class:`atlantis.helpers.json.JsonSerializable`
        
        """
        gc = Theme()
        gc._data = json_object
        return gc
    
    @staticmethod
    def read_folder(folder_name):
        """Load :class:`Theme` from a folder.
        
        This method loads data from a rules folder with the following
        files:
            
        - theme.json
            Colors and bitmaps used by the GUI to show data.

        :param folder_name: folder where the files are read from.
        
        :return: a :class:`Theme` object.
        
        """
        gd = Theme()
        
        with open(os.path.join(folder_name, 'theme.json')) as f:
            gd._data = json_load_dict(f)
            gd._base_folder = folder_name
        
        return gd
        
if __name__ == '__main__':
    pass