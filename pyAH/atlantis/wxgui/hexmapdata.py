"""This module implements
:class:`atlantis.wxgui.hexmap.HexMapDataHex` and
:class:`atlantis.wxgui.hexmap.HexMapData` interfaces.

The goal is keeping :mod:`atlantis.wxgui.hexmap` module as generic as
possible and with no references to any data structure outside the
:obj:`atlantis.wxgui` package. Any relationship with structures in
:obj:`atlantis.gamedata` package modules is moved to these
implementations.

Classes defined here are :class:`MapDataHex`, which implements
:class:`atlantis.wxgui.hexmap.HexMapDataHex` interface, and
:class:`MapData`, which implements
:class:`atlantis.wxgui.hexmap.HexMapData` interface.

"""

from atlantis.gamedata.map import HEX_EXITS

from atlantis.wxgui.hexmap import HexMapDataHex, HexMapData

# from atlantis.wxgui.hexmap import ZOOM_VALUES, ZOOM_25, ZOOM_50,
#     ZOOM_75, ZOOM_100, ZOOM_150, ZOOM_200, ZOOM_OUT, ZOOM_IN


import wx
import os.path

class MapDataHex(HexMapDataHex):
    """Implements :class:`atlantis.wxgui.hexmap.HexMapDataHex`."""
    
    def __init__(self, mh, parent):
        """Create an instance of :class:`MapDataHex`.
        
        :param mh: :class:`atlantis.gamedata.map.MapHex` object with
            data about the region.
        :param parent: :class:`MapData` parent object.
        
        """
        self._map_hex = mh
        self._parent = parent
    
    def get_brushes(self):
        """Return the brushes the hexagon has to be painted with.
        
        :return: a list of :class:`wx.Brush` objects.
        
        """
        return self._parent.get_brushes(self._map_hex.region.terrain,
                                        self._map_hex.status)

    def get_bitmaps(self):
        """Return the bitmaps to be drawn on the hexagon.
        
        :return: a list of :class:`wx.Bitmap` objects.
        
        """
        
        bitmaps = []
        if self._map_hex.region.town:
            bitmap = \
                self._parent.get_town_bitmap( self._map_hex.region.town['type'])
            if bitmap:
                bitmaps.append(bitmap)
        
        return bitmaps
            
        
    def get_location(self):
        """Return hexagon location.
        
        :return: A two elements tuple with hexagon location within its
            level.
            
        """
        return tuple(self._map_hex.region.location[:2])
        

class MapData(HexMapData):
    """Implements :class:`atlantis.wxgui.hexmap.HexMapData`.
    
    Implements :class:`~atlantis.wxgui.hexmap.HexMapData` interface. It
    also uses data from :class:`~atlantis.gamedata.theme.Theme`
    for hexagon colors, brushes and icons, and data from
    :mod:`atlantins.gamedata.map` classes to populate its attributes.
    
    :class:`MapData` implements an iterator on the class that returns
    all hexes in current level.
    
    """
    def __init__(self):
        """Empty constructor"""
        self._zoom = None
        self._theme = None
        self._map_data = None
        self._current_level = None
    
    def __iter__(self):
        """Return an iterator on :class:`HexMapData` instance.
        
        This method implements :meth:`!__iter__` in 
        :class:`atlantis.wxgui.hexmap.HexMapData` interface. The
        iterator returned by the method iterates over all
        :class:`HexMapDataHex` objects in the map.
        
        :return: an iterator on :class:`HexMapDataHex` in the map.
        
        """
        
        if self._map_data and self._current_level and self._theme:
            lvl = self._map_data.get_level(self._current_level)
            for mh in lvl:
                yield MapDataHex(mh, self)
    
    def set_zoom(self, zoom):
        """Set map zoom.
        
        This method implements :meth:`!set_zoom` in
        :class:`atlantis.wxgui.hexmap.HexMapData` interface.
        Map zoom is used by :class:`HexMapDataHex` themed class to
        choose with elements have to be shown (in case some of them
        are only shown in inner zoom values) and to resize bitmaps if
        needed.
        
        :param zoom: zoom value, must be between ``ZOOM_OUT`` and
            ``ZOOM_IN``.
        
        """
        self._zoom = zoom
        print('Aqui')
        self._town_bitmaps = dict()
        for town, image in self._town_images.items():
            print('creando bitmap', town)
            im = image.Scale(32, 32, wx.IMAGE_QUALITY_HIGH)
            self._town_bitmaps[town] = im.ConvertToBitmap()
    
    def use_theme(self, theme):
        """Set the theme used for this map.
        
        Theme are passed in a
        :class:`atlantis.gamedata.theme.Theme` object. This theme is
        used to set corresponding background to hexes based on their
        terrain type, for example.
        
        :param theme: the
            :class:`~atlantis.gamedata.theme.Theme` object with the GUI
            configuration.
        
        """
        self._theme = theme
        self._colours = dict(
                [(terrain, wx.Colour(*colour)) \
                 for (terrain, colour) \
                 in theme._data['terrain_types'].items()])
        self._visited_brushes = dict(
                [(terrain, wx.Brush(colour, wx.BRUSHSTYLE_SOLID)) \
                 for (terrain, colour) in self._colours.items()])
        self._unvisited_brushes = dict(
                [(terrain, wx.Brush([c/2 for c in colour],
                                    wx.BRUSHSTYLE_CROSSDIAG_HATCH)) \
                 for (terrain, colour) in self._colours.items()])
        
        self._town_images = dict(
                [(town, wx.Image(os.path.join(theme.get_art_folder(), bname))) \
                 for (town, bname) in theme._data['towns'].items()])
        self._town_bitmaps = None
        
    
    def use_map(self, map_data):
        """Set map data used for this map
        
        Map data is passed in a :class:`atlantis.gamedata.map.Map`
        instance to populate hexes in the :class:`MapData` object.
        
        Take in account that :class:`~atlantis.gamedata.map.Map` and
        :class:`atlantis.wxgui.hexmapdata.MapData` are very different
        classes and are used for different things. The former
        :class:`!Map` class stores all data about a region (hex) parsed
        from a game report; it stores game data. The latter
        :class:`!MapData` stores data needed to draw an hexagonal map.
        
        So there will be some game data not in :class:`!MapData` as
        it's not needed for the drawn map, and there will be some
        additional data in :class:`!MapData` that it's not actually
        game data but data about how the map is rendered, as brushes or
        bitmaps used.
        
        :param map_data: the :class:`~atlantis.gamedata.map.Map` object
            with the world data.
        
        """
        self._map_data = map_data
        if not self._current_level:
            levels = list(map_data.levels.keys())
            if 'surface' in levels:
                self._current_level = 'surface'
            elif levels:
                self._current_level = levels[0]
            else:
                self._current_level = None
    
    def current_level(self, level_name=None):
        """Set current level to be shown, or return current level.
        
        This method can be used in two forms. The first::
        
            mapdata.current_level('underworld')
        
        sets current level to 'underworld'.
        
        An alternative use is::
        
            mapdata.current_level()
        
        which returns current level set for :class:`MapData` object.
        
        :param level_name: name of the level that has to be set as the
            current one.
            
        :return: if called with no arguments name of current map level.
        
        """
        if level_name:
            levels = list(self._map_data.levels.keys())
            if level_name in levels:
                self._current_level = level_name
            else:
                raise KeyError('level {} does not exist'.format(level_name))
        else:
            return self._current_level
    
    def get_brushes(self, terrain, status):
        """Return the brushes used for a terrain and a status.
        
        Return the list of brushes needed to paint a region of a given
        terrain and status. First brush will be a solid one made from
        the colour defined at
        :class:`~atlantis.gamedata.theme.Theme` object.
        Optionally a CROSSDIAG_HATCH brush will be added for unvisited
        ones.
        
        :param terrain: terrain type.
        :param status: status of the information. Can be ``HEX_EXITS``,
            ``HEX_OLD`` or ``HEX_CURRENT``.
            
        :return: a list of :class:`wx.Brush` objects.
        
        """
        brushes = [self._visited_brushes[terrain]]
        if status == HEX_EXITS:
            brushes.append(self._unvisited_brushes[terrain])
        return brushes
    
    def get_town_bitmap(self, town):
        """Return the bitmap used to show a town.
        
        :meth:`get_town_bitmap` can return *None* if there's no icon
        for the town type, or current zoom level causes towns to not be
        shown.
        
        :param town: town type. Valid values are ``village``, ``town``
            and ``city``.
        
        :return: a :class:`wx.Bitmap` object, or **None** if no bitmap
            has to be shown.
        
        """
        try:
            return self._town_bitmaps[town]
        except (KeyError, TypeError):
            return None
        
    @staticmethod
    def from_map_and_theme(map_data, theme):
        """Create a :class:`MapData` from map data and a theme.
        
        Return a :class:`MapData` object from a
        :class:`atlantis.gamedata.map.Map` object with the data and a
        :class:`atlantis.gamedata.theme.Theme` object the theme to be
        used.
        
        :param map_data: the :class:`~atlantis.gamedata.map.Map` object
            with the world data.
        :param theme: the :class:`~atlantis.gamedata.theme.Theme`
            object.
            
        :return: a :class:`MapData` object.
        
        """
        
        md = MapData()
        md.use_theme(theme)
        md.use_map(map_data)
        
        return md