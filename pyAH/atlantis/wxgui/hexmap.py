"""Handle tan hex map scrolled canvas.

Most important part of an Atlantis PBEM client is the map. Actually you
could develop a Atlantis PBEM helper that does only show a map, while
any other action can be done using a text editor.

This module defines an :class:`~atlantis.wxgui.hexmap.HexMapWindow`
class that implements a `wxPython <http://www.wxpython.org>`_
:class:`wx.ScrolledCanvas` that shows an hexagonal map.

In addition a set of interfaces are defined to handle data to be shown
by :class:`HexMapWindow`. These classes are
:class:`~atlantis.wxgui.hexmap.HexMapDataHex` and
:class:`~atlantis.wxgui.hexmap.HexMapData` that hold hexagon and map
data respectively.
    
:mod:`atlantis.wxgui.hexmap` defines the following constant attributes:

Zoom values:

.. attribute:: ZOOM_25
   
   zooms the map at 25% size.

.. attribute:: ZOOM_50
   
   zooms the map at 50% size.
   
.. attribute:: ZOOM_75

   zooms the map at 75% size.
   
.. attribute:: ZOOM_100

   zooms the map at 100% (normal) size.
   
.. attribute:: ZOOM_150
  
   zooms the map at 150% size.
   
.. attribute:: ZOOM_200
   
   zooms the map at 200% size.
   
.. attribute:: ZOOM_OUT

   equivalent to ``ZOOM_25``.
   
.. attribute:: ZOOM_IN

   equivalent to ``ZOOM_200``.

.. attribute:: ZOOM_VALUES

   total number of zoom values

"""

import wx
import wx.lib.newevent
import math

from atlantis.wxgui import resources

HexSelected, EVT_HEX_SELECTED = wx.lib.newevent.NewCommandEvent()

ZOOM_VALUES = 6
ZOOM_25, ZOOM_50, ZOOM_75, ZOOM_100, ZOOM_150, ZOOM_200 = range(ZOOM_VALUES)
ZOOM_OUT = ZOOM_25
ZOOM_IN = ZOOM_200

class HexMapDataHex():
    """Interface to hold data for an HexMapWindow hex.
    
    This interface should be implemented by data willing to be shown
    by :class:`~atlantis.wxgui.hexmap.HexMapWindow`.
    
    """
    
    def get_brushes(self):
        """Return the brushes the hexagon has to be painted with.
        
        :return: a list of :class:`wx.Brush` objects.
        
        """
        raise NotImplementedError('method must be defined')
    

    def get_bitmaps(self):
        """Return the bitmaps to be drawn on the hexagon.
        
        :return: a list of :class:`wx.Bitmap` objects.
        
        """
        raise NotImplementedError('method must be defined')

    def get_location(self):
        """Return hexagon location.
        
        :return: A two elements tuple with hexagon location within its
            level.
            
        """
        raise NotImplementedError('method must be defined')

class HexMapData():
    """Interface to hold data for an HexMapWindow map.
    
    This interface should be implemented by data willing to be shown
    by :class:`HexMapWindow`.
    
    """
        
    def __iter__(self):
        """Return an iterator on :class:`HexMapData` instance.
        
        This iterator returns all
        :class:`HexMapDataHex` objects in the map.
        
        :return: an iterator on :class:`HexMapDataHex` in the map.
        
        """ 
        raise NotImplementedError('method must be defined')

    def set_zoom(self, zoom):
        """Set map zoom.
        
        Map zoom is used by :class:`HexMapDataHex` themed class to
        choose with elements have to be shown (in case some of them
        are only shown in inner zoom values) and to resize bitmaps if
        needed.
        
        :param zoom: zoom value, must be between ``ZOOM_OUT`` and
            ``ZOOM_IN``.
        
        """
        raise NotImplementedError('method must be defined')
    

class HexMapWindow(wx.ScrolledCanvas):
    """Hex map canvas.
    
    Implements a :class:`wx.ScrolledCanvas` that shows an hex-based
    map.
    
    """
    
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
        self._start_position = None
        self._dragging = False

        self.Bind(wx.EVT_PAINT, self._OnPaint)
        self.Bind(wx.EVT_SIZE, self._OnSize)
        self.Bind(wx.EVT_SCROLLWIN, self._OnScroll)
        self.Bind(wx.EVT_MOTION, self._OnMouseMove)
        self.Bind(wx.EVT_LEFT_DOWN, self._OnMouseStartDrag)
        self.Bind(wx.EVT_LEFT_UP, self._OnMouseClick)
        self.Bind(wx.EVT_MOUSEWHEEL, self._OnMouseWheel)
        
        self.set_zoom(ZOOM_200)
        
    ## Map data
    
    # Map data
    def set_map_data(self, map_data):
        """Set map data to be drawn.
        
        This map data has to be an instance of
        :class:`~atlantis.wxgui.hexmap.HexMapData`.
        
        After setting map data
        :class:`~atlantis.wxgui.hexmap.HexMapWindow` is forced to
        redraw with the new data.
        
        :param map_data: a :class:`~atlantis.wxgui.hexmap.HexMapData`
            instance.
        
        """
        self._map_data = map_data
        self._map_data.set_zoom(self._zoom)
        self._redraw()
    
    # Zoom    
    def set_zoom(self, zoom, centered_pos=None, centered_hex=None):
        """Set map zoom.
        
        :param zoom: zoom value. It must be one value from ``ZOOM_OUT``
            to ``ZOOM_IN``.
        
        """
        if zoom in range(ZOOM_VALUES):
            if zoom != self._zoom:
                self._zoom = zoom
                
                if self._map_data:
                    self._map_data.set_zoom(zoom)
                
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
                
                if centered_pos and centered_hex:
                    self._center_at(centered_pos, centered_hex)
                
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
        """Handle scroll events."""
        wx.CallAfter(self._redraw)
    
    def _OnMouseClick(self, event):
        """Handle mouse clicks."""
        print('click')
        if self._dragging:
            self._dragging = False
            self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        else:
            target_hex = self._event_position_to_hex(event)
            if not self._current_hex or target_hex != self._current_hex:
                self._current_hex = target_hex
                self._redraw()
                event = HexSelected(self.GetId())
                event.hexagon = target_hex
                wx.QueueEvent(self, event)
    
    def _OnMouseStartDrag(self, event):
        """Start dragging the mouse.
        
        Drag will only start once the mouse is moved while button is
        not released.
        
        """
        print('start drag')
        self._start_position = event.GetPosition()
        self._start_view = self.GetViewStart()
        
    def _OnMouseMove(self, event):
        if event.Dragging():
            if not self._dragging:
                self.SetCursor(resources.get_drag_cursor())
                self._dragging = True
            x0, y0 = self._start_position
            x1, y1 = event.GetPosition()
            dx = x1 - x0
            dy = y1 - y0
            sx, sy = self._start_view
            print('start', sx, sy)
            print('end', sx-dx, sy-dy)
            print('end?', sx+dx, sy+dy)
            self.Scroll(sx - dx/self._hex_long_side, sy - dy/self._hex_long_side)
            self._redraw()
            
    def _OnMouseWheel(self, event):
        rotation = event.GetWheelRotation()
        centered_hex = self._event_position_to_hex(event)
        centered_pos = event.GetPosition()
        
        if rotation > 0:
            if self._zoom < ZOOM_IN:
                self.set_zoom(self._zoom + 1, centered_pos, centered_hex)
        else:
            if self._zoom > ZOOM_OUT:
                self.set_zoom(self._zoom - 1, centered_pos, centered_hex)
        
            
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
    def _center_at(self, pos, hexagon):
        """Scroll and center view to ``hexagon``.
        
        :param pos: position in the view where the hexagon must be at.
        :param hexagon: hexagon position as an (x, y) tuple.
        
        """
        x, y = self._hex_position(hexagon)
        sx, sy = pos
        
        self.Scroll((x - sx) / self._hex_long_side,
                    (y - sy) / self._hex_long_side)
        
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
        xoffset, yoffset = self._hex_position(hexagon.get_location())
        dc.SetPen(self._thin_pen)
        for br in hexagon.get_brushes():
            dc.SetBrush(br)
            dc.DrawPolygon(self._hexagon, xoffset=xoffset, yoffset=yoffset)
        for bm in hexagon.get_bitmaps():
            dc.DrawBitmap(bm, xoffset - bm.GetWidth() / 2,
                          yoffset - bm.GetHeight() / 2)
    
    def _draw_selected_hex(self, dc):
        if not self._current_hex:
            return
        xoffset, yoffset = self._hex_position(self._current_hex)
        dc.SetPen(self._select_pen)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawPolygon(self._hexagon, xoffset=xoffset, yoffset=yoffset)

