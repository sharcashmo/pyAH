"""Hex map canvas.

Most important part of an Atlantis PBEM client is the map. Actually you
could develop a Atlantis PBEM helper that does only show a map, while
any other action can be done using a text editor.

This module defines an :class:`HexMapWindow` class that implements a
`wxPython <http://www.wxpython.org>`_ :class:`ScrolledCanvas` that
shows an hexagonal map.

:class:`HexMapWindow` won't hold map data on his own, but will define
instead an interface that must to be implemented by map controllers.

"""

import wx
import wx.lib.newevent
import math

HexSelected, EVT_HEX_SELECTED = wx.lib.newevent.NewCommandEvent()

class HexMapData():
    """Holds data for an hex."""
    def __init__(self, location, terrain_type, hex_symbols, hex_borders):
        """:class:HexMapData constructor.
        
        Creates an object with all data :class:`HexMapWindow` needs
        to draw an hexagon.
        
        :param location: a tuple with (x,y) hexagon coordinates.
        :param terrain_type: this parameter controls hexagon
            background.
        :param hex_symbols: a list of tuples. Each tuple has the form
            of (type, name) of the symbol.
            This parameter controls which symbols have to be drawn on
            the hex.
        :param hex_borders: a list of tuples. Each tuple has the form
            of (border, type) of the border.
            This parameter controls which borders have to be drawn on
            the hex.
            
        """
        self.location = location
        self.terrain_type = terrain_type
        self.hex_symbols = hex_symbols
        self.hex_borders = hex_borders

class HexMapWindow(wx.ScrolledCanvas):
    """Hex map canvas.
    
    Implements a :class:`wx.ScrolledCanvas` that shows an hex-based
    map.
    
    Defined constants:
    - Zoom values:
        + ZOOM_25: zooms the map at 25% size.
        + ZOOM_50: zooms the map at 50% size.
        + ZOOM_75: zooms the map at 75% size.
        + ZOOM_100: zooms the map at 100% (normal) size.
        + ZOOM_150: zooms the map at 150% size.
        + ZOOM_200: zooms the map at 200% size.
        + ZOOM_OUT: equivalent to ZOOM_25.
        + ZOOM_IN: equivalent to ZOOM_200.
    
    """

    # Zoom constant values
    ZOOM_VALUES = 6
    ZOOM_25, ZOOM_50, ZOOM_75, ZOOM_100, ZOOM_150, ZOOM_200 = range(ZOOM_VALUES)
    ZOOM_OUT = ZOOM_25
    ZOOM_IN = ZOOM_200
    
    _min_size = 6
    """Hex side size for zoomed out map."""
    
    _hex_sizes = [r * 6 for r in [1, 2, 3, 4, 6, 8]]
    """Hex side sizes for each zoom value."""
    
    _x_size = 128
    _y_size = 128
    
    _padding = _min_size
    """Map padding in pixels."""
    
    _ratio = math.sin(math.radians(60))
    """Half the height of a side 1 hexagon."""
    
    _normalized_hexagon = ((-.5, -1), (.5, -1), (1, 0),
                           (.5, 1), (-.5, 1), (-1, 0))
    """Skeleton of an hexagon polygon.
    
    x values have to be multiplied by hexside size, and y values by
    its half height value (sin(60) + hexside).
    
    """
    
    # Data used to configure how each element has to be drawn
    _terrain_brushes = None
    
    # Map data
    _map_data = None
    
    # These values have to be set
    _zoom = None
    """Current zoom value"""
    
    _hex_long_side = None
    """Side size of the hexagon."""
    
    _hex_short_side = None
    """Half height of the hexagon."""
    
    _map_width = None
    """Map width in pixels, padding included."""
     
    _map_height = None
    """Map height in pixels, padding included."""
    
    _current_hex = None
    """Current selected hex."""
    
    _buffer = None
    """Image buffer for double buffering."""

    def __init__(self, *args, **kwargs):
        kwargs['style'] = kwargs.setdefault('style',
                                            wx.NO_FULL_REPAINT_ON_RESIZE) | \
                          wx.FULL_REPAINT_ON_RESIZE
        wx.ScrolledCanvas.__init__(self, *args, **kwargs)
        
        self._select_pen = wx.Pen(wx.RED, 3, wx.PENSTYLE_SOLID)
        self._thin_pen = wx.GREY_PEN

        self.Bind(wx.EVT_PAINT, self._OnPaint)
        self.Bind(wx.EVT_SIZE, self._OnSize)
        self.Bind(wx.EVT_SCROLLWIN, self._OnScroll)
#        self.Bind(wx.EVT_MOTION, self._OnMouseMove)
        self.Bind(wx.EVT_LEFT_UP, self._OnMouseClick)
        
        # Initialize map data
        self.clear_terrain_types()
        
        self.set_zoom(self.ZOOM_200)
    
    ## Definitions controlling how the map has to be shown
    
    # Terrain types definitions
    def add_terrain_type(self, terrain_type, brush):
        """Adds a new terrain type to the map.
        
        Each hexagon of the given terrain_type will be drawn with the
        give background for this type. Whether terrain_type existed
        its information is overwritten.
        
        :param terrain_type: terrain type added to the map.
        :param brush: :class:`wx.Brush` used to draw the hex.
        
        """
        self._terrain_brushes[terrain_type] = brush
        
    def delete_terrain_type(self, terrain_type):
        """Delete a terrain type from the map.
        
        Drop this terrain type information from :class:`HexMapWindow`.
        
        :param terrain_type: terrain type to be deleted.
        
        :raise KeyError: if terrain type does not exist.
        
        """
        del self._terrain_brushes[terrain_type]
    
    def clear_terrain_types(self):
        """Deletes terrain types information."""
        self._terrain_brushes = dict()
        
    ## Map data
    
    # Map data
    def set_map_data(self, map_data):
        """Set map data to be shown in by :class:`HexMapWindow`.
        
        This map data has to be a list of hexes, where each hex
        is an :class:`HexMapData`.
        
        After setting map_data :class:`HexMapWindow` is forced to
        redraw with the new data.
        
        :param map_data: list of :class:`HexMapData`.
        
        """
        self._map_data = map_data
        self._redraw()
    
    # Zoom    
    def set_zoom(self, zoom):
        """Set map zoom.
        
        """
        if zoom in range(self.ZOOM_VALUES):
            if zoom != self._zoom:
                self._zoom = zoom
                
                self._hex_long_side = self._hex_sizes[zoom]
                self._hex_short_side = round(self._hex_long_side * self._ratio)
                
                self._hexagon = [(x * self._hex_long_side,
                                  y * self._hex_short_side) \
                                 for (x, y) in self._normalized_hexagon]
                
                self._map_width = (self._x_size * 1.5 + .5) * \
                                  self._hex_long_side
                self._map_height = (self._y_size + 1) * self._hex_short_side
                
                self.SetVirtualSize(self._map_width + 2 * self._padding,
                                    self._map_height + 2 * self._padding)
                self.SetScrollRate(self._hex_long_side, self._hex_long_side)
                
                self._redraw()
        else:
            raise IndexError('Zoom out of range')

    # Event handlers
    def _OnPaint(self, event):
        dc = wx.BufferedPaintDC(self, self._buffer, wx.BUFFER_CLIENT_AREA)
        del dc

    def _OnSize(self, event):
        self._redraw()

    def _OnScroll(self, event):
        wx.CallAfter(self._redraw)
    
    def _OnMouseClick(self, event):
        """Handle mouse clicks.
        
        """
        target_hex = self._event_position_to_hex(event)
        if not self._current_hex or target_hex != self._current_hex:
            self._current_hex = target_hex
            self._redraw()
            event = HexSelected(self.GetId())
            event.hexagon = target_hex
            wx.QueueEvent(self, event)
        
    def _OnMouseMove(self, event):
        target_hex = self._event_position_to_hex(event)
        if not self._current_hex or target_hex != self._current_hex:
            self._current_hex = target_hex
            self._redraw()
            
    # Miscellaneus methods with hex math
    def _hex_position(self, hexagon):
        """Compute hex position on canvas.
        
        This method return position of hex center as an (x, y) tuple.
        Canvas padding is taken into account, while scrolling is not.
        Position is virtual position in the Scrolled canvas.
        
        Parameter:
            hexagon
                Hexagon coordinates as an (x, y) tuple.
        
        Returns:
            Hexagon position.
        
        """
        print(hexagon)
        x, y = hexagon
        xoffset = (1.5 * x + 1) * self._hex_long_side + self._padding
        yoffset = self._hex_short_side * (y + 1) + self._padding
        return (xoffset, yoffset)
    
    def _is_in_hex(self, point, hexagon):
        """Check if point is inside the hex.
        
        This method returns *True* if point is inside the hex, and
        *False* otherwise.
        
        Parameters:
            point
                Point to check, as an (x, y) tuple.
            hexagon
                Hexagon against the check is done, as (x, y)
                coordinates.
        
        """
        xhex, yhex = self._hex_position(hexagon)
        xpoint, ypoint = point
        q2x = abs(xpoint - xhex)
        q2y = abs(ypoint - yhex)
        # Check against bounding rect
        if q2x > self._hex_long_side or q2y > self._hex_short_side:
            return False
        # Check against the hexagon
        if (self._hex_long_side * self._hex_short_side) < \
           (self._hex_short_side * q2x + .5 * self._hex_long_side * q2y):
            return False
        else:
            return True
    
    def _event_position_to_hex(self, event):
        """Return hex coordinates of the event.
        
        This method returns the hexagon coordinates where the event
        has been fired.
        
        Parameter:
            event
                Event fired from which hex coordinates are needed.
        
        Returns:
            Hexagon coordinates as an (x, y) tuple, or *None* if the
            event is fired on no valid hexagon.
            
        """
        dc = wx.ClientDC(self)
        self.DoPrepareDC(dc)
        xe, ye = event.GetLogicalPosition(dc)
        x = xe - self._padding - self._hex_long_side
        y = ye - self._padding - self._hex_short_side
        x = round(x / 1.5 / self._hex_long_side)
        if x % 2:
            y = round(y / self._hex_short_side / 2 - .5) * 2 + 1
        else:
            y = round(y / self._hex_short_side / 2) * 2
        # Check if it's valid hex and, finally, if point is inside
        for xr in (x-1, x, x+1):
            for yr in (y-1, y, y+1):
                if xr in range(self._x_size) and \
                   yr in range(self._y_size) and \
                   (xr + yr) % 2 == 0 and \
                   self._is_in_hex((xe, ye), (xr, yr)):
                    return (xr, yr)
        else:
            return None
    
    # Drawing methods. These do all the hard work.
    def _redraw(self):
        """Redraw current window.
        
        This method is called when visible window contents change. This
        can be caused by:
        
        - The user has resized the window.
        - The window has been scrolled.
        - Selected hex has changed.
        - Zoom level has changed.
        
        """
        w, h = self.GetClientSize()
        self._buffer = wx.Bitmap.FromRGBA(w, h, 0xff, 0xff, 0xff, 0)
        self._draw_map()
        self.Update()

    def _draw_map(self):
        dc = wx.BufferedDC(wx.ClientDC(self), self._buffer,
                           wx.BUFFER_CLIENT_AREA)
        self.DoPrepareDC(dc)
        
        if self._map_data:
            for h in self._map_data:
                self._draw_hex(dc, h)
        
        self._draw_selected_hex(dc)
        del dc
    
    def _draw_hex(self, dc, hexagon):
        xoffset, yoffset = self._hex_position(hexagon.location)
        dc.SetPen(self._thin_pen)
        dc.SetBrush(self._terrain_brushes[hexagon.terrain_type])
        dc.DrawPolygon(self._hexagon, xoffset=xoffset, yoffset=yoffset)
    
    def _draw_selected_hex(self, dc):
        if not self._current_hex:
            return
        xoffset, yoffset = self._hex_position(self._current_hex)
        dc.SetPen(self._select_pen)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawPolygon(self._hexagon, xoffset=xoffset, yoffset=yoffset)

if __name__ == '__main__':
    class TestFrame(wx.Frame):
        def __init__(self, parent=None):
            wx.Frame.__init__(self, parent, size=(500, 500),
                              title='Test frame', style=wx.DEFAULT_FRAME_STYLE)
            self.mapwindow = HexMapWindow(self)
            
            self.Bind(EVT_HEX_SELECTED, self.OnSelectHex, source=self.mapwindow)
        
        def OnSelectHex(self, event):
            print(event.hexagon)

    app = wx.App()
    frame = TestFrame(None)
    
    frame.mapwindow.add_terrain_type('ocean', wx.BLUE_BRUSH)
    frame.mapwindow.add_terrain_type('forest', wx.GREEN_BRUSH)
    frame.mapwindow.add_terrain_type('mountain', wx.RED_BRUSH)
    frame.mapwindow.add_terrain_type('plain', wx.YELLOW_BRUSH)
    
    import random
    map_data = []
    for i in range(8):
        for j in range(i % 2, 8, 2):
            hmd = HexMapData((i, j),
                             random.choice(('ocean', 'forest',
                                            'mountain', 'plain')),
                             None, None)
            print((i,j), hmd.terrain_type)
            map_data.append(hmd)
    
    frame.mapwindow.set_map_data(map_data)

    frame.Show()
    app.MainLoop()