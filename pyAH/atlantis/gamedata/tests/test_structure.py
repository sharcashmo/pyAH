"""Unit tests for atlantis.gamedata.structure module."""

from atlantis.gamedata.structure import Structure

from io import StringIO

import json
import unittest

class TestStructure(unittest.TestCase):
    """Test Structure class."""
    
    def test_constructor(self):
        """Test Region constructor."""
        structure = Structure(1, 'Tomasa', 'Mine', incomplete=4)
        self.assertEqual(structure.num, 1)
        self.assertEqual(structure.name, 'Tomasa')
        self.assertEqual(structure.structure_type, 'Mine')
        self.assertEqual(structure.items, [])
        self.assertEqual(structure.incomplete, 4)
        self.assertFalse(structure.about_to_decay)
        self.assertFalse(structure.needs_maintenance)
        self.assertFalse(structure.inner_location)
        self.assertFalse(structure.has_runes)
        self.assertTrue(structure.can_enter)
        
        structure = Structure(2, 'Shaft', 'Shaft', inner_location=True)
        self.assertEqual(structure.num, 2)
        self.assertEqual(structure.name, 'Shaft')
        self.assertEqual(structure.structure_type, 'Shaft')
        self.assertEqual(structure.items, [])
        self.assertFalse(structure.incomplete)
        self.assertFalse(structure.about_to_decay)
        self.assertFalse(structure.needs_maintenance)
        self.assertTrue(structure.inner_location)
        self.assertFalse(structure.has_runes)
        self.assertTrue(structure.can_enter)
        
    
    def test_append_report_description(self):
        """Test Structure.append_report_description method."""
        structure = Structure(1, 'Crypt', 'Crypt', can_enter=False)
        
        lines = ['+ Crypt [1] : Crypt, closed to player units.']
        
        for l in lines:
            structure.append_report_description(l)
        
        self.assertEqual(structure.report, lines)

    def test_json_methods(self):
        """Test implementation of JsonSerializable interface."""
        io = StringIO()
        
        structure = Structure(1, 'Crypt', 'Crypt', can_enter=False)
        
        lines = ['+ Crypt [1] : Crypt, closed to player units.']
        for l in lines:
            structure.append_report_description(l)
            
        json.dump(structure, io, default=Structure.json_serialize)
        io.seek(0)
        structure_new = Structure.json_deserialize(json.load(io))
        self.assertEqual(structure, structure_new)

if __name__ == '__main__':
    unittest.main()
