"""Unit tests for atlantis.gamedata.map module."""

from atlantis.gamedata.map import MapHex, MapLevel, Map, \
    HEX_CURRENT, HEX_OLD, HEX_EXITS, SEEN_CURRENT, \
    LEVEL_SURFACE, LEVEL_UNDERWORLD, LEVEL_UNDERDEEP
from atlantis.gamedata.region import Region
from atlantis.gamedata.rules import DIR_NORTHWEST

from io import StringIO

import json
import unittest

class TestMapHex(unittest.TestCase):
    """Test MapHex class."""
    
    def test_constructor(self):
        """Test MapHex constructor."""
        
        r = Region((21, 93, None), 'plain', 'Isshire', 9836, 'vikings', 11016,
                   {'name': 'Durshire', 'type': 'town'})
        mh = MapHex(r, HEX_CURRENT)
        self.assertEqual(mh.region, r)
        self.assertEqual(mh.status, HEX_CURRENT)
        self.assertEqual(mh.last_seen, SEEN_CURRENT)
        
        
        r = Region((21, 93, None), 'plain', 'Isshire',
                   town={'name': 'Durshire', 'type': 'town'})
        mh = MapHex(r, HEX_EXITS, (1, 12))
        self.assertEqual(mh.region, r)
        self.assertEqual(mh.status, HEX_EXITS)
        self.assertEqual(mh.last_seen, (1, 12))
    
    def test_get_region_info(self):
        """Test MapHex.get_region_info method."""
        r = Region((21, 93, None), 'plain', 'Isshire', 9836, 'vikings', 11016,
                   {'name': 'Durshire', 'type': 'town'})
        mh = MapHex(r, HEX_CURRENT)
        
        r2 = mh.get_region_info()
        self.assertEqual(r, r2)
    
    def test_get_last_seen(self):
        """Test MapHex.get_last_seen method."""
        r = Region((21, 93, None), 'plain', 'Isshire', 9836, 'vikings', 11016,
                   {'name': 'Durshire', 'type': 'town'})
        mh = MapHex(r, HEX_OLD, (1, 12))
        
        self.assertEqual(mh.get_last_seen(), (1, 12))
    
    def test_is_current(self):
        """Test MapHex.is_current method."""
        r = Region((21, 93, None), 'plain', 'Isshire', 9836, 'vikings', 11016,
                   {'name': 'Durshire', 'type': 'town'})
        
        mh = MapHex(r, HEX_OLD, (1, 12))
        self.assertFalse(mh.is_current())
        
        mh = MapHex(r, HEX_CURRENT)
        self.assertTrue(mh.is_current())
        
        mh = MapHex(r, HEX_EXITS)
        self.assertFalse(mh.is_current())
    
    def test_is_complete(self):
        """Test MapHex.is_complete method."""
        r = Region((21, 93, None), 'plain', 'Isshire', 9836, 'vikings', 11016,
                   {'name': 'Durshire', 'type': 'town'})
        
        mh = MapHex(r, HEX_OLD, (1, 12))
        self.assertTrue(mh.is_complete())
        
        mh = MapHex(r, HEX_CURRENT)
        self.assertTrue(mh.is_complete())
        
        mh = MapHex(r, HEX_EXITS)
        self.assertFalse(mh.is_complete())
        

    def test_json_methods(self):
        """Test implementation of JsonSerializable interface."""
        io = StringIO()
        
        r = Region((21, 93, None), 'plain', 'Isshire', 9836, 'vikings', 11016,
                   {'name': 'Durshire', 'type': 'town'})
        mh = MapHex(r, HEX_CURRENT)
        json.dump(mh, io, default=MapHex.json_serialize)
        io.seek(0)
        mh_new = MapHex.json_deserialize(json.load(io))
        
        self.assertEqual(mh, mh_new)

class TestMapLevel(unittest.TestCase):
    """Test MapLevel class."""
    
    def test_contructor(self):
        """Test MapLevel constructor."""
        
        lvl = MapLevel('surface')
        self.assertEqual(lvl.name, 'surface')
        self.assertEqual(lvl.hexes, dict())
        self.assertEqual(lvl.level_type, (LEVEL_SURFACE, 0))
        
        lvl = MapLevel('very very very deep underdeep')
        self.assertEqual(lvl.name, 'very very very deep underdeep')
        self.assertEqual(lvl.hexes, dict())
        self.assertEqual(lvl.level_type, (LEVEL_UNDERDEEP, 4))
        
        self.assertRaises(KeyError, MapLevel, 'very very deep surface')
        self.assertRaises(KeyError, MapLevel, 'bad level')
        
    def test_set_region(self):
        """Test MapLevel.set_region method."""
        
        lvl = MapLevel('surface')
        self.assertEqual(lvl.name, 'surface')
        self.assertEqual(lvl.hexes, dict())
        
        r = Region((21, 93, None), 'plain', 'Isshire', 9836, 'vikings', 11016,
                   {'name': 'Durshire', 'type': 'town'})
        mh = MapHex(r, HEX_CURRENT)
        lvl.set_region(mh)
        self.assertEqual(lvl.hexes, {(21, 93): mh})
        
        r = Region((21, 93, 'underworld'), 'plain', 'Isshire', 9836, 'vikings',
                   11016, {'name': 'Durshire', 'type': 'town'})
        mh = MapHex(r, HEX_CURRENT)
        self.assertRaises(KeyError, lvl.set_region, mh)
    
    def test_get_region(self):
        """Test MapLevel.get_region method."""
        
        lvl = MapLevel('surface')
        self.assertEqual(lvl.name, 'surface')
        self.assertEqual(lvl.hexes, dict())
        
        r = Region((21, 93, None), 'plain', 'Isshire', 9836, 'vikings', 11016,
                   {'name': 'Durshire', 'type': 'town'})
        mh = MapHex(r, HEX_CURRENT)
        lvl.hexes[(21,93)] = mh
        
        mh_new = lvl.get_region((21,93))
        self.assertIs(mh, mh_new)
        
        self.assertIsNone(lvl.get_region((1,1)))
    
    def test_iter(self):
        """Test MapLevel.__iter__ method."""
        
        lvl = MapLevel('surface')
        self.assertEqual(lvl.name, 'surface')
        self.assertEqual(lvl.hexes, dict())
        
        r = Region((21, 93, None), 'plain', 'Isshire', 9836, 'vikings', 11016,
                   {'name': 'Durshire', 'type': 'town'})
        mh = MapHex(r, HEX_CURRENT)
        lvl.hexes[(21,93)] = mh
        
        r2 = Region((21, 95, None), 'plain', 'Isshire', 2836, 'sea elves',
                    3016, None)
        mh2 = MapHex(r2, HEX_CURRENT)
        lvl.hexes[(21,95)] = mh2
        
        my_list = [h for h in lvl]
        other_list = [mh2, mh]
        
        self.assertEqual(my_list, other_list)
    
    def test_get_type(self):
        """Test MapLevel.get_type method."""
        
        lvl = MapLevel('surface')
        self.assertEqual(lvl.get_type(), LEVEL_SURFACE)
        
        lvl = MapLevel('very very very deep underworld')
        self.assertEqual(lvl.get_type(), LEVEL_UNDERWORLD)
    
    def test_get_depth(self):
        """Test MapLevel.get_depth method."""
        
        lvl = MapLevel('surface')
        self.assertEqual(lvl.get_depth(), 0)
        
        lvl = MapLevel('very very very deep underworld')
        self.assertEqual(lvl.get_depth(), 4)
    
    def test_get_rect(self):
        """Test MapLevel.get_rect method."""
        
        lvl = MapLevel('surface')
        self.assertEqual(lvl.name, 'surface')
        self.assertEqual(lvl.hexes, dict())
        
        r = Region((21, 93, None), 'plain', 'Isshire', 9836, 'vikings', 11016,
                   {'name': 'Durshire', 'type': 'town'})
        mh = MapHex(r, HEX_CURRENT)
        lvl.set_region(mh)
        
        r2 = Region((18, 104, None), 'plain', 'Isshire', 2836, 'sea elves',
                    3016, None)
        mh2 = MapHex(r2, HEX_CURRENT)
        lvl.set_region(mh2)
        
        self.assertEqual(lvl.get_rect(), (16, 88, 23, 111))
    
    def test_wraps_horizontally(self):
        """Test MapLevel.wraps_horizontally method."""
        
        lvl = MapLevel('surface')
        r = Region((0, 14, None), 'plain', 'Isshire', 9836, 'vikings', 11016,
                   {'name': 'Durshire', 'type': 'town'})
        r.set_exit(DIR_NORTHWEST, (15, 13))
        mh = MapHex(r, HEX_CURRENT)
        lvl.set_region(mh)
        
        r2 = Region((15, 13, None), 'desert', 'Poljom')
        mh2 = MapHex(r2, HEX_EXITS)
        lvl.set_region(mh2)
        
        self.assertTrue(lvl.wraps_horizontally())
        
        lvl = MapLevel('surface')
        r = Region((10, 14, None), 'plain', 'Isshire', 9836, 'vikings', 11016,
                   {'name': 'Durshire', 'type': 'town'})
        r.set_exit(DIR_NORTHWEST, (9, 13))
        mh = MapHex(r, HEX_CURRENT)
        lvl.set_region(mh)
        
        r2 = Region((9, 13, None), 'desert', 'Poljom')
        mh2 = MapHex(r2, HEX_EXITS)
        lvl.set_region(mh2)
        
        self.assertFalse(lvl.wraps_horizontally())
    
    def test_wraps_vertically(self):
        """Test MapLevel.wraps_vertically method."""
        
        lvl = MapLevel('surface')
        self.assertFalse(lvl.wraps_vertically())
        
        lvl = MapLevel('nexus')
        self.assertFalse(lvl.wraps_vertically())

    def test_json_methods(self):
        """Test implementation of JsonSerializable interface."""
        io = StringIO()
        
        lvl = MapLevel('surface')
        r = Region((21, 93, None), 'plain', 'Isshire', 9836, 'vikings', 11016,
                   {'name': 'Durshire', 'type': 'town'})
        mh = MapHex(r, HEX_CURRENT)
        lvl.set_region(mh)
        
        json.dump(lvl, io, default=MapLevel.json_serialize)
        io.seek(0)
        lvl_new = MapLevel.json_deserialize(json.load(io))
        
        self.assertEqual(lvl, lvl_new)


class TestMap(unittest.TestCase):
    """Test Map class."""
    
    def test_add_region_info(self):
        """Test Map.add_region_info method."""
        
        m = Map()
        r = Region((21, 93, None), 'plain', 'Isshire', 9836, 'vikings', 11016,
                   {'name': 'Durshire', 'type': 'town'})
        m.add_region_info(r)
        
        self.assertEqual(list(m.levels.keys()), ['surface'])
        lvl = m.levels['surface']
        self.assertEqual(list(lvl.hexes.keys()), [(21, 93)])
        mh = lvl.hexes[(21, 93)]
        self.assertEqual(mh.region, r)
        self.assertEqual(mh.status, HEX_CURRENT)
        self.assertEqual(mh.last_seen, SEEN_CURRENT)
    
        r2 = Region((21, 93, None), 'plain', 'Isshire',
                    town={'name': 'Durshire', 'type': 'town'})
        m.add_region_info(r2, HEX_EXITS)
        
        self.assertEqual(list(m.levels.keys()), ['surface'])
        lvl = m.levels['surface']
        self.assertEqual(list(lvl.hexes.keys()), [(21, 93)])
        mh = lvl.hexes[(21, 93)]
        self.assertEqual(mh.region, r)
        self.assertEqual(mh.status, HEX_CURRENT)
        self.assertEqual(mh.last_seen, SEEN_CURRENT)
        
        mh.status = HEX_OLD
        mh.last_seen = (2, 1)
        r3 = Region((21, 93, None), 'plain', 'Isshire', 9856, 'vikings', 11116,
                    {'name': 'Durshire', 'type': 'town'})
        m.add_region_info(r3, HEX_CURRENT)
        
        self.assertEqual(list(m.levels.keys()), ['surface'])
        lvl = m.levels['surface']
        self.assertEqual(list(lvl.hexes.keys()), [(21, 93)])
        mh = lvl.hexes[(21, 93)]
        self.assertEqual(mh.region, r3)
        self.assertEqual(mh.status, HEX_CURRENT)
        self.assertEqual(mh.last_seen, SEEN_CURRENT)
    
    def test_get_region(self):
        """Test Map constructor."""
        m = Map()
        r = Region((21, 93, None), 'plain', 'Isshire', 9836, 'vikings', 11016,
                   {'name': 'Durshire', 'type': 'town'})
        m.add_region_info(r)
        
        mh = m.get_region((21, 93, 'surface'))
        self.assertEqual(mh.region, r)
        
        mh = m.get_region((21, 93, None))
        self.assertEqual(mh.region, r)

    def test_json_methods(self):
        """Test implementation of JsonSerializable interface."""
        io = StringIO()
         
        m = Map()
        r = Region((21, 93, None), 'plain', 'Isshire', 9836, 'vikings', 11016,
                   {'name': 'Durshire', 'type': 'town'})
        m.add_region_info(r)
         
        json.dump(m, io, default=Map.json_serialize)
        io.seek(0)
        m_new = Map.json_deserialize(json.load(io))
         
        self.assertEqual(m, m_new)

if __name__ == '__main__':
    unittest.main()
