"""Unit tests for :mod:`atlantis.helpers.hex_math`."""

from atlantis.helpers.hex_math import HexMath
from atlantis.helpers.hex_math import ZOOM_25, ZOOM_50, ZOOM_100, ZOOM_200

import unittest


class TestHexMath(unittest.TestCase):
    """Test HexMath class."""

    def test_constructor(self):
        """Test HexMathConstructor."""
        
        hm = HexMath(8, (0, 0, 15, 15), ZOOM_200)
        
        self.assertEqual(hm._min_size, 8)
        self.assertEqual(hm._map_rect, (0, 0, 15, 15))
        self.assertEqual(hm._zoom, ZOOM_200)
    
    def test_set_zoom(self):
        """Test HexMath.set_zoom method."""
        
        hm = HexMath(8, (0, 0, 15, 15), ZOOM_200)
        hm.set_zoom(ZOOM_50)
        
        self.assertEqual(hm._zoom, ZOOM_50)
    
    def test_set_map_rect(self):
        """Test HexMath.set_map_rect method."""
        
        hm = HexMath(8, (0, 0, 15, 15), ZOOM_200)
        hm.set_map_rect((16, 16, 31, 31))
        
        self.assertEqual(hm._map_rect, (16, 16, 31, 31))
    
    def test_set_min_size(self):
        """Test HexMath.set_min_size method."""
        
        hm = HexMath(8, (0, 0, 15, 15), ZOOM_200)
        hm.set_min_size(6)
        
        self.assertEqual(hm._min_size, 6)
    
    def test_get_zoom(self):
        """Test HexMath.get_zoom method."""
        
        hm = HexMath(8, (0, 0, 15, 15), ZOOM_200)
        
        self.assertEqual(hm.get_zoom(), ZOOM_200)
        
    def test_get_size(self):
        """Test HexMath.get_size method.
        
        Test map is 16x16 hexes size. Hex side size is 24 pixels, hex
        width is 24x2 pixels so its center is 24 pixels away from
        border. Hexes have an horizontal separation between them
        of 24x1.5 pixels, that's 36 pixels. So map width should be:
        
        15x36 + 2x24 = 294 pixels.
        
        Hexes have a height of 2xsin(60)x24, so their center is
        24xsin(60) away from the border. Vertical separation between
        them is 24xsin(60). 24xsin(60) is 21. So map height should be:
        
        15x21 + 2x21 = 357 pixels.
        
        """
        
        hm = HexMath(6, (0, 0, 15, 15), ZOOM_100)
        
        width, height = hm.get_size()
        
        self.assertEqual(width, 588)
        self.assertEqual(height, 357)
    
    def test_get_center_hex(self):
        """Test HexMath.get_center_hex method."""
        
        hm = HexMath(6, (16, 0, 31, 31), ZOOM_100)
        
        self.assertEqual(hm.get_center_hex(), (24, 16))
    
    def test_get_hex_position(self):
        """Test HexMath.get_hex_position method.
        
        Hex side size is 24 pixels. Half the height of an hex is 21
        pixels."""
        
        hm = HexMath(6, (16, 16, 31, 31), ZOOM_100)
        
        self.assertEqual(hm.get_hex_position((19, 21)), (24 + 3*36, 21 + 5*21))
    
    def test_get_position_hex(self):
        """Test HexMath.get_position_hex method."""
        
        hm = HexMath(6, (16, 16, 31, 31), ZOOM_100)
        
        self.assertEqual(hm.get_position_hex((37 + 3*36, 18 + 5*21)), (19, 21))
    
    def test_get_hex_polygon(self):
        """Test HexMath.get_hex_polygon method."""
        
        hm = HexMath(6, (16, 16, 31, 31), ZOOM_100)
        
        expectedHex = ((-12, -21), (12, -21), (24, 0),
                       (12, 21), (-12, 21), (-24, 0))
        
        self.assertEqual(hm.get_hex_polygon(), expectedHex)
    
    def test_get_hex_bounding_size(self):
        """Test HexMath.get_hex_bounding_size method."""
        
        hm = HexMath(6, (16, 16, 31, 31), ZOOM_100)
        
        self.assertEqual(hm.get_hex_bounding_size(), (49, 43))
    
    def test_get_scale(self):
        """Test HexMath.get_scale method."""
        
        hm = HexMath(6, (16, 16, 31, 31), ZOOM_200)
        
        self.assertEqual(hm.get_scale(), 2)
        
        hm.set_zoom(ZOOM_25)
        
        self.assertEqual(hm.get_scale(), .25)
    
    def test_point_in_hex(self):
        """Test HexMath.point_in_hex method."""
        
        hm = HexMath(6, (16, 16, 31, 31), ZOOM_100)
        
        self.assertTrue(hm.point_in_hex((37 + 3*36, 18 + 5*21), (19, 21)))
        self.assertFalse(hm.point_in_hex((37 + 3*36, 18 + 5*21), (20, 20)))
        

if __name__ == '__main__':
    unittest.main()
