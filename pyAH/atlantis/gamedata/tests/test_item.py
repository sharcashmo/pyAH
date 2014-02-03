"""Unit tests for module atlantis.gamedata.item."""

from atlantis.gamedata.item import Item, ItemAmount, ItemMarket, ItemUnit

from io import StringIO

import json
import unittest


class TestItem(unittest.TestCase):
    """Test Item class."""
    
    def test_constructor(self):
        """Test Item constructor.
        
        Test both forms of constructors, with ``name`` and ``names`` as
        parameters. Added a new test without ``abr`` used for fleets,
        where ``names`` or ``name`` is given, but no ``abr``.
        
        """
        it = Item('HORS', names='horses')
        self.assertEqual(it.abr, 'HORS')
        self.assertEqual(it.names, 'horses')
        self.assertIsNone(it.name)
        
        
        it = Item('HORS', name='horse')
        self.assertEqual(it.abr, 'HORS')
        self.assertEqual(it.name, 'horse')
        self.assertIsNone(it.names)
        
        it = Item(names='Galleons')
        self.assertEqual(it.names, 'Galleons')
        self.assertIsNone(it.abr)
        self.assertIsNone(it.name)

    def test_json_methods(self):
        """Test implementation of JsonSerializable interface."""
        io = StringIO()
        
        it = Item('SWOR', name='sword')
        json.dump(it, io, default=Item.json_serialize)
        io.seek(0)
        it_new = Item.json_deserialize(json.load(io))
        
        self.assertEqual(it, it_new)
        

class TestItemAmount(unittest.TestCase):
    """Test ItemAmount class."""
    
    def test_constructor(self):
        """Test ItemAmount constructor.
        
        Test both forms of constructors, with ``name`` and ``names`` as
        parameters, with and without the ``amt`` parameter. Added a new
        test without ``abr`` used for fleets, where ``names`` or
        ``name`` is given, but no ``abr``.
        
        """
        it = ItemAmount('HORS', amt=5, names='horses')
        self.assertEqual(it.abr, 'HORS')
        self.assertEqual(it.amt, 5)
        self.assertEqual(it.names, 'horses')
        self.assertIsNone(it.name)
        
        it = ItemAmount('HORS', name='horse')
        self.assertEqual(it.abr, 'HORS')
        self.assertEqual(it.amt, 1)
        self.assertEqual(it.name, 'horse')
        self.assertIsNone(it.names)
        
        it = ItemAmount(amt=2, names='Galleons')
        self.assertEqual(it.amt, 2)
        self.assertEqual(it.names, 'Galleons')
        self.assertIsNone(it.abr)
        self.assertIsNone(it.name)

    def test_json_methods(self):
        """Test implementation of JsonSerializeble interface."""
        io = StringIO()
        
        it = ItemAmount('SWOR', amt=10, names='swords')
        json.dump(it, io, default=ItemAmount.json_serialize)
        io.seek(0)
        it_new = ItemAmount.json_deserialize(json.load(io))
        self.assertEqual(it, it_new)
        
        io.seek(0)
        io.truncate()
        it2 = ItemAmount('SWOR', amt=5, names='swords')
        json.dump(it2, io, default=ItemAmount.json_serialize)
        io.seek(0)
        it_new = ItemAmount.json_deserialize(json.load(io))
        self.assertEqual(it2, it_new)
        self.assertNotEqual(it, it_new)
        

class TestItemMarket(unittest.TestCase):
    """Test ItemMarket class."""
    
    def test_constructor(self):
        """Test ItemMarket constructor.
        
        Test both forms of constructors, with ``name`` and ``names`` as
        parameters.
        
        """
        it = ItemMarket('HORS', 5, 64, names='horses')
        self.assertEqual(it.abr, 'HORS')
        self.assertEqual(it.amt, 5)
        self.assertEqual(it.price, 64)
        self.assertEqual(it.names, 'horses')
        self.assertIsNone(it.name)

    def test_json_methods(self):
        """Test implementation of JsonSerializeble interface."""
        io = StringIO()
        
        it = ItemMarket('SWOR', 10, 72, names='swords')
        json.dump(it, io, default=ItemMarket.json_serialize)
        io.seek(0)
        it_new = ItemMarket.json_deserialize(json.load(io))
        self.assertEqual(it, it_new)
        

class TestItemUnit(unittest.TestCase):
    """Test ItemUnit class."""
    
    def test_constructor(self):
        """Test ItemUnit constructor.
        
        Test both forms of constructors, with ``name`` and ``names`` as
        parameters.
        
        """
        it = ItemUnit('HORS', 5, names='horses')
        self.assertEqual(it.abr, 'HORS')
        self.assertEqual(it.amt, 5)
        self.assertEqual(it.names, 'horses')
        self.assertIsNone(it.name)
        self.assertEqual(it.unfinished, 0)
        self.assertFalse(it.illusion)
        
        it = ItemUnit('GALL', 1, name='galleon', unfinished=3)
        self.assertEqual(it.abr, 'GALL')
        self.assertEqual(it.amt, 1)
        self.assertEqual(it.name, 'galleon')
        self.assertIsNone(it.names)
        self.assertEqual(it.unfinished, 3)
        self.assertFalse(it.illusion)
        
        it = ItemUnit('IWOLF', 3, names='wolves', illusion=True)
        self.assertEqual(it.abr, 'IWOLF')
        self.assertEqual(it.amt, 3)
        self.assertEqual(it.names, 'wolves')
        self.assertIsNone(it.name)
        self.assertEqual(it.unfinished, 0)
        self.assertTrue(it.illusion)

    def test_json_methods(self):
        """Test implementation of JsonSerializeble interface."""
        io = StringIO()
        
        it = ItemUnit('HORS', 5, names='horses')
        json.dump(it, io, default=ItemUnit.json_serialize)
        io.seek(0)
        it_new = ItemUnit.json_deserialize(json.load(io))
        self.assertEqual(it, it_new)
        
        io.seek(0)
        io.truncate()
        it = ItemUnit('GALL', 1, name='galleon', unfinished=3)
        json.dump(it, io, default=ItemUnit.json_serialize)
        io.seek(0)
        it_new = ItemUnit.json_deserialize(json.load(io))
        self.assertEqual(it, it_new)
        
        io.seek(0)
        io.truncate()
        it = ItemUnit('IWOLF', 3, names='wolves', illusion=True)
        json.dump(it, io, default=ItemUnit.json_serialize)
        io.seek(0)
        it_new = ItemUnit.json_deserialize(json.load(io))
        self.assertEqual(it, it_new)


if __name__ == '__main__':
    unittest.main()
