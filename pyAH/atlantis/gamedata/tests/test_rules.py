"""Unit tests for :mod:`atlantis.gamedata.rules`."""

from atlantis.gamedata.rules import TerrainType
from atlantis.gamedata.rules import AtlantisRules

import json

from io import StringIO
import unittest

class TestTerrainType(unittest.TestCase):
    """Test class :class:`atlantis.gamedata.rules.TerrainType`."""

    def test_json_methods(self):
        """Test implementation of 
        :meth:`~atlantis.helpers.json.JsonSerializeble` interface."""
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
    """Test class :class:`atlantis.gamedata.rules.AtlantisRules`."""

    def test_json_methods(self):
        """Test implementation of 
        :meth:`~atlantis.helpers.json.JsonSerializeble` interface."""
        io = StringIO()
        with open('../../../rulesets/havilah_1.0.0.json') as f:
            ar = AtlantisRules.json_deserialize(json.load(f))
        
        json.dump(ar, io, default=AtlantisRules.json_serialize)
        io.seek(0)
        ar_new = AtlantisRules.json_deserialize(json.load(io))
        
        self.assertEqual(ar, ar_new)

if __name__ == '__main__':
    unittest.main()
