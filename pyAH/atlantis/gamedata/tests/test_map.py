"""Unit tests for :mod:`atlantis.gamedata.map`."""

from atlantis.gamedata.map import MapHex, MapLevel, Map, \
    HEX_CURRENT, HEX_OLD, HEX_EXITS, SEEN_CURRENT
from atlantis.gamedata.region import Region

from io import StringIO

import json
import unittest

class TestMapHex(unittest.TestCase):
    """Test :class:`atlantis.gamedata.map.MapHex`."""
    
    def test_constructor(self):
        """Test :class:`~atlantis.gamedata.map.MapHex` constructor."""
        
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
        """Test :meth:`~atlantis.gamedata.map.MapHex.get_region_info`."""
        r = Region((21, 93, None), 'plain', 'Isshire', 9836, 'vikings', 11016,
                   {'name': 'Durshire', 'type': 'town'})
        mh = MapHex(r, HEX_CURRENT)
        
        r2 = mh.get_region_info()
        self.assertEqual(r, r2)
    
    def test_get_last_seen(self):
        """Test :meth:`~atlantis.gamedata.map.MapHex.get_last_seen`."""
        r = Region((21, 93, None), 'plain', 'Isshire', 9836, 'vikings', 11016,
                   {'name': 'Durshire', 'type': 'town'})
        mh = MapHex(r, HEX_OLD, (1, 12))
        
        self.assertEqual(mh.get_last_seen(), (1, 12))
    
    def test_is_current(self):
        """Test :meth:`~atlantis.gamedata.map.MapHex.is_current`."""
        r = Region((21, 93, None), 'plain', 'Isshire', 9836, 'vikings', 11016,
                   {'name': 'Durshire', 'type': 'town'})
        
        mh = MapHex(r, HEX_OLD, (1, 12))
        self.assertFalse(mh.is_current())
        
        mh = MapHex(r, HEX_CURRENT)
        self.assertTrue(mh.is_current())
        
        mh = MapHex(r, HEX_EXITS)
        self.assertFalse(mh.is_current())
    
    def test_is_complete(self):
        """Test :meth:`~atlantis.gamedata.map.MapHex.is_complete`."""
        r = Region((21, 93, None), 'plain', 'Isshire', 9836, 'vikings', 11016,
                   {'name': 'Durshire', 'type': 'town'})
        
        mh = MapHex(r, HEX_OLD, (1, 12))
        self.assertTrue(mh.is_complete())
        
        mh = MapHex(r, HEX_CURRENT)
        self.assertTrue(mh.is_complete())
        
        mh = MapHex(r, HEX_EXITS)
        self.assertFalse(mh.is_complete())
        

    def test_json_methods(self):
        """Test implementation of 
        :meth:`~atlantis.helpers.json.JsonSerializeble` interface."""
        io = StringIO()
        
        r = Region((21, 93, None), 'plain', 'Isshire', 9836, 'vikings', 11016,
                   {'name': 'Durshire', 'type': 'town'})
        mh = MapHex(r, HEX_CURRENT)
        json.dump(mh, io, default=MapHex.json_serialize)
        io.seek(0)
        mh_new = MapHex.json_deserialize(json.load(io))
        
        self.assertEqual(mh, mh_new)

class TestMapLevel(unittest.TestCase):
    """Test :class:`~atlantis.gamedata.game.MapLevel`."""
    
    def test_contructor(self):
        """Test :class:`~atlantis.gamedata.game.MapLevel` constructor."""
        
        lvl = MapLevel('surface')
        self.assertEqual(lvl.name, 'surface')
        self.assertEqual(lvl.hexes, dict())
        
    def test_set_region(self):
        """Test :meth:`~atlantis.gamedata.game.MapLevel.set_region`."""
        
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
        """Test :meth:`~atlantis.gamedata.game.MapLevel.get_region`."""
        
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
        """Test :meth:`~atlantis.gamedata.game.MapLevel.__iter__`."""
        
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
        
        self.assertSameElements(my_list, other_list)

    def test_json_methods(self):
        """Test implementation of 
        :meth:`~atlantis.helpers.json.JsonSerializeble` interface."""
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
    """Test :class:`~atlantis.gamedata.game.Map`."""
    
    def test_add_region_info(self):
        """Test :meth:`~atlantis.gamedata.game.Map.add_region_info`."""
        
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
        """Test :class:`~atlantis.gamedata.game.Map` constructor."""
        m = Map()
        r = Region((21, 93, None), 'plain', 'Isshire', 9836, 'vikings', 11016,
                   {'name': 'Durshire', 'type': 'town'})
        m.add_region_info(r)
        
        mh = m.get_region((21, 93, 'surface'))
        self.assertEqual(mh.region, r)
        
        mh = m.get_region((21, 93, None))
        self.assertEqual(mh.region, r)

    def test_json_methods(self):
        """Test implementation of 
        :meth:`~atlantis.helpers.json.JsonSerializeble` interface."""
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
