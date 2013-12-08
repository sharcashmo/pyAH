"""Unit tests for module atlantis.gamedata.rules."""

from atlantis.gamedata.rules import TerrainType
from atlantis.gamedata.rules import AtlantisRules
from atlantis.gamedata.rules import DIR_NORTH, DIR_NORTHWEST

import json

from io import StringIO
import unittest

class TestTerrainType(unittest.TestCase):
    """Test TerrainType class."""

    def test_json_methods(self):
        """Test implementation of JsonSerializable interface."""
        io = StringIO()
        
        tt = TerrainType(
                name='forest', riding_mounts=False, flying_mounts=True,
                products=[{'product': 'wood', 'chance': 100, 'amount': 20},
                          {'product': 'fur', 'chance': 100, 'amount': 10},
                          {'product': 'herb', 'chance': 100, 'amount': 10},
                          {'product': 'irwd', 'chance': 25, 'amount': 5},
                          {'product': 'yew', 'chance': 25, 'amount': 5}],
                normal_races=['viki', 'welf'], coastal_races=['self'])
        json.dump(tt, io, default=TerrainType.json_serialize)
        io.seek(0)
        tt_new = TerrainType.json_deserialize(json.load(io))
        
        self.assertEqual(tt, tt_new)

class TestAtlantisRules(unittest.TestCase):
    """Test AtlantisRules class."""
    
    def test_get_direction(self):
        """Test AtlantisRules.get_direction method"""
        ar = AtlantisRules()
        ar.strings['directions'] = [['n', 'north'],
                                    ['ne', 'northeast'],
                                    ['se', 'southeast'],
                                    ['s', 'south'],
                                    ['sw', 'southwest'],
                                    ['nw', 'northwest']]
        
        self.assertEqual(ar.get_direction('n'), DIR_NORTH)
        self.assertEqual(ar.get_direction('northwest'), DIR_NORTHWEST)
        self.assertRaises(KeyError, ar.get_direction, 'baddirection')

    def test_json_methods(self):
        """Test implementation of JsonSerializeble interface."""
        io = StringIO()
        
        tt = TerrainType(
                name='forest', riding_mounts=False, flying_mounts=True,
                products=[{'product': 'wood', 'chance': 100, 'amount': 20},
                          {'product': 'fur', 'chance': 100, 'amount': 10},
                          {'product': 'herb', 'chance': 100, 'amount': 10},
                          {'product': 'irwd', 'chance': 25, 'amount': 5},
                          {'product': 'yew', 'chance': 25, 'amount': 5}],
                normal_races=['viki', 'welf'], coastal_races=['self'])
        
        str_ = {'months': ['january', 'february', 'march', 'april', 'may',
                           'june', 'july', 'august', 'september', 'october',
                           'november', 'december'],
                'directions': [['n', 'north'],
                               ['ne', 'northeast'],
                               ['se', 'southeast'],
                               ['s', 'south'],
                               ['sw', 'southwest'],
                               ['nw', 'northwest']]}
        
        ar = AtlantisRules()
        ar.terrain_types['forest'] = tt
        ar.strings = str_
        
        json.dump(ar, io, default=AtlantisRules.json_serialize)
        io.seek(0)
        ar_new = AtlantisRules.json_deserialize(json.load(io))
        
        self.assertEqual(ar, ar_new)

if __name__ == '__main__':
    unittest.main()
