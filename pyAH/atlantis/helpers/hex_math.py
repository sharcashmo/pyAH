"""This module implements :class:`HexMath`, that is in charge of all
the math related with hexagonal shapes.

This class will be used by any class willing to draw hexagonal maps.

But :class:`HexMath` does not only manages math formulas, but also
manages some dynamic functionality as zoom values and sizes.
    
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

import math

ZOOM_VALUES = 6
ZOOM_25, ZOOM_50, ZOOM_75, ZOOM_100, ZOOM_150, ZOOM_200 = range(ZOOM_VALUES)
ZOOM_OUT = ZOOM_25
ZOOM_IN = ZOOM_200

# Relative sizes for each zoom value
_zoom_sizes = [1, 2, 3, 4, 6, 8]

class HexMath:
    """Handle all hex map math"""
    
    # Half the height of a side 1 hexagon
    _ratio = math.sin(math.radians(60))
    
    # Skeleton of an hexagon polygon.
    #
    # x values have to be multiplied by hexside size, and y values by
    # its half height value (sin(60) + hexside).
    _normalized_hexagon = ((-.5, -1), (.5, -1), (1, 0),
                           (.5, 1), (-.5, 1), (-1, 0))
    
    def __init__(self, min_size=6, map_rect=(0,0,127,127), zoom=ZOOM_100):
        """Default constructor.
        
        :param min_size: side size when zoomed out, in pixels.
        
        """
        self._min_size = min_size
        self._map_rect = map_rect
        self._zoom = zoom
        self._set_hex_sizes()
        
    def _set_hex_sizes(self):
        """Compute internal size values"""
        self._hex_sizes = [r * self._min_size for r in _zoom_sizes]
        self._hex_long_side = self._hex_sizes[self._zoom]
        self._hex_short_side = round(self._hex_long_side * self._ratio)
                
        self._hexagon = tuple([(int(x * self._hex_long_side),
                                int(y * self._hex_short_side)) \
                               for (x, y) in self._normalized_hexagon])
    
    def set_zoom(self, zoom):
        """Set zoom level.
        
        :param zoom: zoom level.
        
        """
        self._zoom = zoom
        self._set_hex_sizes()
    
    def set_map_rect(self, rect):
        """Set map enclosing rectangle in coordinates.
        
        :param rect: enclosing rectangle in coordinates.
        
        """
        self._map_rect = rect
    
    def set_min_size(self, min_size):
        """Set size of hexagon side when zoomed out.
        
        :param min_size: hexagon side size when zoomed out.
        
        """
        self._min_size = min_size
        self._set_hex_sizes()
    
    def get_zoom(self):
        """Get current zoom.
        
        :return: current zoom level.
        
        """
        return self._zoom
    
    def get_size(self):
        """Get map size in pixels.
        
        :return: map size in pixels.
        
        """
        x_size = self._map_rect[2] - self._map_rect[0] + 1
        y_size = self._map_rect[3] - self._map_rect[1] + 1
        width = (x_size * 1.5 + .5) * self._hex_long_side
        height = (y_size + 1) * self._hex_short_side
        
        return (width, height)
    
    def get_center_hex(self):
        """Return hexagon coordinates of the centered hex.
        
        :return: center hexagon coordinates.
        
        """
        
        return ((self._map_rect[2] + self._map_rect[0] + 1) / 2,
                (self._map_rect[3] + self._map_rect[1] + 1) / 2)
    
    def get_hex_position(self, hexagon):
        """Return hex position in pixels.
        
        This method return position of hex center as an (x, y) tuple
        from hexagon coordinates.
        
        :param hexagon: hexagon coordinates as an (x, y) tuple.
        
        :return: a tuple with the position of hexagon center in pixels.
        
        """
        
        x, y = hexagon
        x, y = x - self._map_rect[0], y - self._map_rect[1]
        xoffset = (1.5 * x + 1) * self._hex_long_side
        yoffset = self._hex_short_side * (y + 1)
        return (xoffset, yoffset)
    
    def get_position_hex(self, point):
        """Return in which hexagon is a point.
        
        This method return the hexagon coordinates in which the point
        is located.
        
        :param point: point coordinates in pixels as an (x, y) tuple.
        
        :return: a tuple with enclosing hexagon coordinates.
        
        """
        xe, ye = point
        x = xe - self._hex_long_side
        y = ye - self._hex_short_side
        x = round(x / 1.5 / self._hex_long_side)
        if x % 2:
            y = round(y / self._hex_short_side / 2 - .5) * 2 + 1
        else:
            y = round(y / self._hex_short_side / 2) * 2
        # Check if it's valid hex and, finally, if point is inside
        for xr in (x-1, x, x+1):
            for yr in (y-1, y, y+1):
                if (xr + yr) % 2 == 0 and \
                   self.point_in_hex((xe, ye),
                                     (xr + self._map_rect[0],
                                      yr + self._map_rect[1])):
                    return (xr + self._map_rect[0], yr + self._map_rect[1])
        else:
            return None
    
    def get_hex_polygon(self):
        """Return an hexagonal polygon.
        
        :return: an hexagonal polygon if size according to zoom.
        
        """
        return self._hexagon
    
    def get_hex_bounding_size(self):
        """Return the size of an hex bounding rectangle.
        
        :return: a tuple with (width, height) of the bounding rectangle.
        
        """
        width = self._hexagon[2][0] * 2 + 1
        height = self._hexagon[3][1] * 2 + 1
        return (width, height)
    
    def point_in_hex(self, point, hexagon):
        """Check if a point is inside an hexagon.
        
        This method returns *True* if point is inside the hex, and
        *False* otherwise.
        
        :param point: point to check, as an (x, y) tuple.
        :param hexagon: hexagon against the check is done, as (x, y)
            coordinates.
        
        :return: *True* if the point is inside the hex, *False*
            otherwise.
        
        """
        
        xhex, yhex = self.get_hex_position(hexagon)
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