"""Handle an hex map scrolled canvas.

Most important part of an Atlantis PBEM client is the map. Actually you
could develop a Atlantis PBEM helper that does only show a map, while
any other action can be done using a text editor.

This module defines an :class:`HexMapWindow`
class that implements a `wxPython <http://www.wxpython.org>`_
:class:`wx.Window` that shows an hexagonal map.

:class:`HexMapWindow` supports drag scrolling and selecting hex, and
dispatches events to its listeners.

In addition a set of interfaces are defined to handle data to be shown
by :class:`HexMapWindow`. These classes are
:class:`HexMapDataHex` and :class:`HexMapData` that hold hexagon and map
data respectively. Classes implementing these interfaces will cover the
gap between pure gui classes in this module and pure Atlantis data in
:ref:`atlantis.gamedata` package.

:mod:`atlantis.wxgui.hexmap` defines the following events.

.. attribute:: HexSelected

   An hexagon has been selected. Its event binder is
   ``EVT_HEX_SELECTED``.

"""

import wx
import wx.lib.newevent

from atlantis.wxgui import resources
from atlantis.helpers.hex_math import HexMath

from atlantis.helpers.hex_math import ZOOM_OUT, ZOOM_IN

HexSelected, EVT_HEX_SELECTED = wx.lib.newevent.NewCommandEvent()


class HexMapDataLabel():
    """Placeholder for label data to be drawn by :class:`HexMapWindow`.
    
    Public attributes in :class:`HexMapDataLabel` are:
    
    .. attribute:: label
       Label string.
    
    .. attribute:: offset
       A tuple with x and y offsets from hexagon center.
    
    .. attribute:: font
       :class:`wx.Font` object to be used when drawing the label.
    
    .. attribute:: colour
       :class:`wx.Colour` object to be used when drawing the label.
       
    """
    
    def __init__(self, label, offset=(0,0), font=None, colour=None):
        """Class constructor."""
        
        self.label = label
        self.offset = offset
        self.font = font
        self.colour = colour
        

class HexMapDataHex():
    """Interface to hold data for an :class:`HexMapWindow` hex.
    
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
    
    def get_labels(self):
        """Return the labels to be drawn on the hexagon.
        
        :return: a list of :class:`HexMapDataLabel` objects.
        
        """
        raise NotImplementedError('method must be defined')

    def get_location(self):
        """Return hexagon location.
        
        :return: A two elements tuple with hexagon location within its
            level.
            
        """
        raise NotImplementedError('method must be defined')


class HexMapData():
    """Interface to hold data for an :class:`HexMapWindow` map.
    
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

    def use_hex_math(self, hex_math):
        """Set hex math object.
        
        Set the :class:`atlantis.helpers.hex_math.HexMath` object used
        by :class:`HexMapDataHex` themed class to choose with elements
        have to be shown (in case some of them are only shown in inner
        zoom values) and to resize bitmaps if needed.
        
        :param hex_math: :class:`~atlantis.helpers.hex_math.HexMath`
            object.
        
        """
        raise NotImplementedError('method must be defined')
    
    def get_rect(self):
        """Get map rect.
        
        Return a four elements tuple determining the rectangle which
        encloses all known regions in the level. First two elements are
        the upper left corner (x, y), and the last two elements the
        lower right corner (x, y).
        
        :return: a tuple with the rectangle which encloses known
            regions.
        
        """
        raise NotImplementedError('method must be defined')
    
    def wraps_horizontally(self):
        """Check if map wraps horizontally.
        
        :return: *True* if map wraps horizontally, *False* otherwise.
        
        """
        raise NotImplementedError('method must be defined')
    
    def wraps_vertically(self):
        """Check if map wraps vertically.
        
        :return: *True* if map wraps vertically, *False* otherwise.
        
        """
        raise NotImplementedError('method must be defined')
    

class HexMapWindow(wx.Window):
    """Hex map window.
    
    Implements a scrollable :class:`wx.Window` that shows an hex-based
    map.
    
    """
    
    def __init__(self, *args, **kwargs):
        kwargs['style'] = kwargs.setdefault('style',
                                            wx.NO_FULL_REPAINT_ON_RESIZE) | \
                          wx.FULL_REPAINT_ON_RESIZE
        wx.Window.__init__(self, *args, **kwargs)
        
        self.SetDoubleBuffered(True)
        
        self._hex_math = HexMath()
        
        self._map_data = None
        
        self._current_hex = None
        self._select_pen = wx.Pen(wx.RED, 3, wx.PENSTYLE_SOLID)
        self._thin_pen = wx.GREY_PEN
        self._start_position = None
        self._dragging = False
        self._view_start = (0, 0)
        self._buffer = None

        self.Bind(wx.EVT_PAINT, self._OnPaint)
        self.Bind(wx.EVT_SIZE, self._OnSize)
        self.Bind(wx.EVT_MOTION, self._OnMouseMove)
        self.Bind(wx.EVT_LEFT_DOWN, self._OnMouseStartDrag)
        self.Bind(wx.EVT_LEFT_UP, self._OnMouseClick)
        self.Bind(wx.EVT_MOUSEWHEEL, self._OnMouseWheel)
        
        self.zoom_and_center(ZOOM_IN)
        
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
        self._map_data.use_hex_math(self._hex_math)
        self._hex_math.set_map_rect(map_data.get_rect())
        self.zoom_and_center()
    
    # Zoom    
    def zoom_and_center(self, zoom=None, centered_pos=None, centered_hex=None):
        """Set map zoom.
        
        :param zoom: zoom value. It must be one value from ``ZOOM_OUT``
            to ``ZOOM_IN``.
        
        """
        if zoom is None:
            zoom = self._hex_math.get_zoom()
        else:
            self._hex_math.set_zoom(zoom)
        
        if not centered_pos:
            sx, sy = self.GetClientSize()
            centered_pos = (sx / 2, sy / 2)
            
        if not centered_hex:
            centered_hex = self._hex_math.get_center_hex() 
            
        self._center_at(centered_pos, centered_hex)
        
        self._redraw()

    # Event handlers
    def _OnPaint(self, event):
        dc = wx.BufferedPaintDC(self, self._buffer, wx.BUFFER_CLIENT_AREA)
        del dc

    def _OnSize(self, event):
        self._redraw()
    
    def _OnMouseClick(self, event):
        """Handle mouse clicks."""
        self._start_position = None
        if self._dragging:
            self._stop_dragging()
        else:
            target_hex = self._hex_math.get_position_hex(
                    self._event_logical_position(event))
            if not self._current_hex or target_hex != self._current_hex:
                self._current_hex = target_hex
                self._redraw()
                event = HexSelected(self.GetId())
                event.hexagon = target_hex
                wx.QueueEvent(self, event)
                
    def _start_dragging(self):
        try:
            self._mouse_timer.Stop()
            del(self._mouse_timer)
        except AttributeError:
            pass
        if self._start_position:
            self.SetCursor(resources.get_drag_cursor())
            self._dragging = True
            
    def _stop_dragging(self):
        if self._dragging:
            self._dragging = False
            self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
    
    def _OnMouseStartDrag(self, event):
        """Start dragging the mouse.
        
        Drag will only start once the mouse is moved while button is
        not released.
        
        """
        self._start_position = event.GetPosition()
        self._mouse_timer = wx.CallLater(200, self._start_dragging)
        event.Skip()
        
    def _OnMouseMove(self, event):
        if event.Dragging():
            if not self._dragging:
                self._start_dragging()
                
            x0, y0 = self._start_position
            x1, y1 = event.GetPosition()
            dx = x1 - x0
            dy = y1 - y0
            sx, sy = self._view_start
            self._start_position = (x1, y1)
            self._view_start = (sx+dx, sy+dy)
            self._redraw()
            
    def _OnMouseWheel(self, event):
        rotation = event.GetWheelRotation()
        centered_hex = self._hex_math.get_position_hex(
                self._event_logical_position(event))
        centered_pos = event.GetPosition()
        
        print('wheel on', self._event_logical_position(event), centered_hex, centered_pos)
        
        if rotation > 0:
            if self._hex_math.get_zoom() < ZOOM_IN:
                self.zoom_and_center(self._hex_math.get_zoom() + 1,
                                     centered_pos, centered_hex)
        else:
            if self._hex_math.get_zoom() > ZOOM_OUT:
                self.zoom_and_center(self._hex_math.get_zoom() - 1,
                                     centered_pos, centered_hex)
        

    # Operations with DC
    def _DoPrepareDC(self, dc):
        """Set DC origin"""
        dc.SetDeviceOrigin(*self._view_start)
    
    def _event_logical_position(self, event):
        """Return event logical position"""
        dc = wx.ClientDC(self)
        self._DoPrepareDC(dc)
        return event.GetLogicalPosition(dc)
    
    # Drawing methods. These do all the hard work.
    def _logical_position(self, pos):
        """Return logical position"""
        x, y = pos
        sx, sy = self._view_start
        return (x + sx, y + sy)
    
    def _center_at(self, pos, hexagon):
        """Scroll and center view to ``hexagon``.
        
        :param pos: position in the view where the hexagon must be at.
        :param hexagon: hexagon position as an (x, y) tuple.
        
        """
        x, y = self._hex_math.get_hex_position(hexagon)
        px, py = pos
        self._view_start = (px - x, py - y)
        self._redraw()
        
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
        self._buffer = wx.Bitmap.FromRGBA(w, h, 0xff, 0xff, 0xff,
                                          wx.IMAGE_ALPHA_OPAQUE)
        
        dc = wx.BufferedDC(wx.ClientDC(self), self._buffer,
                           wx.BUFFER_CLIENT_AREA)
        self._DoPrepareDC(dc)
        
        self._draw_map(dc)
        
        self.Update()

    def _draw_map(self, dc):
        if self._map_data:
            for h in self._map_data:
                self._draw_hex(dc, h)
            for h in self._map_data:
                self._draw_hex_labels(dc, h)
        
        self._draw_selected_hex(dc)
        del dc
    
    def _draw_hex(self, dc, hexagon):
        xoffset, yoffset = self._hex_math.get_hex_position(
                hexagon.get_location())
        dc.SetPen(self._thin_pen)
        for br in hexagon.get_brushes():
            dc.SetBrush(br)
            dc.DrawPolygon(
                self._hex_math.get_hex_polygon(),
                xoffset=xoffset, yoffset=yoffset)

        for bm in hexagon.get_bitmaps():
            dc.DrawBitmap(bm, xoffset - bm.GetWidth() / 2,
                          yoffset - bm.GetHeight() / 2)
            
    def _draw_hex_labels(self, dc, hexagon):
        xoffset, yoffset = self._hex_math.get_hex_position(
                hexagon.get_location())
        for label in hexagon.get_labels():
            print(dc.GetFullTextExtent(label.label, label.font))
            width, height = dc.GetFullTextExtent(label.label, label.font)[:2]
            xlabel, ylabel = label.offset
            if label.font:
                dc.SetFont(label.font)
            if label.colour:
                dc.SetTextForeground(label.colour)
            dc.DrawText(label.label,
                        xoffset + xlabel - width / 2,
                        yoffset + ylabel - height / 2)

    
    def _draw_selected_hex(self, dc):
        if not self._current_hex:
            return
        xoffset, yoffset = self._hex_math.get_hex_position(self._current_hex)
        dc.SetPen(self._select_pen)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawPolygon(
                self._hex_math.get_hex_polygon(),
                xoffset=xoffset, yoffset=yoffset)

